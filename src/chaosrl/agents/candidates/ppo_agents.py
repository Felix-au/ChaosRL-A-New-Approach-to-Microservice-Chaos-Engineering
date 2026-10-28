"""Policy-gradient and PPO-based candidate agents (C01, C02, C03, C07, C08, C09)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical

from chaosrl.agents.candidates.base_candidate import BaseCandidateAgent, mask_logits
from chaosrl.agents.candidates.networks import (
    CriticNetwork,
    GNNScorer,
    GRUScorer,
    MLPScorer,
    RNDModule,
)

torch.set_num_threads(1)


class PPOAgent(BaseCandidateAgent):
    """PPO Agent with modular Scorer (MLP, GNN, or GRU)."""

    def __init__(
        self,
        candidate_id: str = "C01",
        name: str = "PPO-MLP",
        scorer_type: str = "mlp",
        lr: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_ratio: float = 0.2,
        entropy_coef: float = 0.01,
        value_coef: float = 0.5,
    ) -> None:
        super().__init__(candidate_id, name)
        self.scorer_type = scorer_type
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_ratio = clip_ratio
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef

        # Initialize policy scorer
        if scorer_type == "gnn":
            self.actor = GNNScorer(node_dim=16, hidden_dim=64)
        elif scorer_type == "gru":
            self.actor = GRUScorer(node_dim=16, hidden_dim=64)
        else:
            self.actor = MLPScorer(node_dim=16, hidden_dim=64)

        self.critic = CriticNetwork(hidden_dim=64, global_dim=5)
        self.optimizer = optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            lr=lr,
        )

        self.gru_hidden: Optional[torch.Tensor] = None

    def reset_episode(self) -> None:
        self.gru_hidden = None

    def select_action(
        self,
        obs: Dict[str, np.ndarray],
        deterministic: bool = False,
    ) -> int:
        self.actor.eval()
        with torch.no_grad():
            x = torch.from_numpy(obs["node_features"]).float()
            adj = torch.from_numpy(obs["adjacency"]).float()
            g = torch.from_numpy(obs["global_features"]).float()
            mask = torch.from_numpy(obs["action_mask"]).float()

            if self.scorer_type == "gru":
                logits, _, self.gru_hidden = self.actor(x, adj, g, self.gru_hidden)
            elif self.scorer_type == "gnn":
                logits, _ = self.actor(x, adj)
            else:
                logits, _ = self.actor(x)

            masked_logits = mask_logits(logits, mask)
            dist = Categorical(logits=masked_logits)

            if deterministic:
                action = int(torch.argmax(masked_logits).item())
            else:
                action = int(dist.sample().item())

        return action

    def evaluate_step(
        self,
        obs: Dict[str, np.ndarray],
        action: int,
    ) -> Tuple[float, float, float]:
        """Compute action log-prob, value estimate, and entropy for a single step."""
        x = torch.from_numpy(obs["node_features"]).float()
        adj = torch.from_numpy(obs["adjacency"]).float()
        g = torch.from_numpy(obs["global_features"]).float()
        mask = torch.from_numpy(obs["action_mask"]).float()

        if self.scorer_type == "gru":
            logits, emb, _ = self.actor(x, adj, g, None)
        elif self.scorer_type == "gnn":
            logits, emb = self.actor(x, adj)
        else:
            logits, emb = self.actor(x)

        masked_logits = mask_logits(logits, mask)
        dist = Categorical(logits=masked_logits)
        log_prob = float(dist.log_prob(torch.tensor(action)).item())
        entropy = float(dist.entropy().item())
        value = float(self.critic(emb, g).item())

        return log_prob, value, entropy

    def update_on_trajectories(
        self,
        trajectories: List[Dict[str, Any]],
        epochs: int = 4,
        batch_size: int = 32,
    ) -> Dict[str, float]:
        """Train PPO on collected rollout trajectories."""
        self.actor.train()
        self.critic.train()

        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_entropy = 0.0
        n_updates = 0

        for traj in trajectories:
            obs_list = traj["obs"]
            actions = traj["actions"]
            rewards = traj["rewards"]
            dones = traj["dones"]
            old_log_probs = traj["log_probs"]
            values = traj["values"]

            # Compute GAE and returns
            t_len = len(rewards)
            returns = np.zeros(t_len, dtype=np.float32)
            advantages = np.zeros(t_len, dtype=np.float32)

            last_gae = 0.0
            for t in reversed(range(t_len)):
                next_val = values[t + 1] if t + 1 < t_len else 0.0
                next_non_terminal = 1.0 - dones[t]
                clipped_r = float(np.clip(rewards[t], -10.0, 10.0))
                delta = clipped_r + self.gamma * next_val * next_non_terminal - values[t]
                last_gae = delta + self.gamma * self.gae_lambda * next_non_terminal * last_gae
                advantages[t] = last_gae
                returns[t] = np.clip(advantages[t] + values[t], -50.0, 50.0)

            adv_mean = np.mean(advantages)
            adv_std = np.std(advantages) + 1e-8
            norm_advantages = (advantages - adv_mean) / adv_std

            # Optimization epochs with trajectory batch accumulation
            for _ in range(epochs):
                self.optimizer.zero_grad()
                for t in range(t_len):
                    obs_t = obs_list[t]
                    act_t = actions[t]
                    old_lp = old_log_probs[t]
                    ret_t = returns[t]
                    adv_t = norm_advantages[t]

                    x = torch.from_numpy(obs_t["node_features"]).float()
                    adj = torch.from_numpy(obs_t["adjacency"]).float()
                    g = torch.from_numpy(obs_t["global_features"]).float()
                    mask = torch.from_numpy(obs_t["action_mask"]).float()

                    if self.scorer_type == "gru":
                        logits, emb, _ = self.actor(x, adj, g, None)
                    elif self.scorer_type == "gnn":
                        logits, emb = self.actor(x, adj)
                    else:
                        logits, emb = self.actor(x)

                    masked_logits = mask_logits(logits, mask)
                    dist = Categorical(logits=masked_logits)
                    new_lp = dist.log_prob(torch.tensor(act_t))
                    ent = dist.entropy()

                    v_pred = self.critic(emb, g)
                    v_loss = F.mse_loss(v_pred.view(-1), torch.tensor([ret_t]).float())

                    ratio = torch.exp(new_lp - old_lp)
                    surr1 = ratio * adv_t
                    surr2 = torch.clamp(ratio, 1.0 - self.clip_ratio, 1.0 + self.clip_ratio) * adv_t
                    pi_loss = -torch.min(surr1, surr2)

                    step_loss = (pi_loss + self.value_coef * v_loss - self.entropy_coef * ent) / max(1, t_len)
                    step_loss.backward()

                    total_policy_loss += float(pi_loss.item())
                    total_value_loss += float(v_loss.item())
                    total_entropy += float(ent.item())
                    n_updates += 1

                nn.utils.clip_grad_norm_(self.actor.parameters(), max_norm=0.5)
                nn.utils.clip_grad_norm_(self.critic.parameters(), max_norm=0.5)
                self.optimizer.step()

        return {
            "policy_loss": total_policy_loss / max(1, n_updates),
            "value_loss": total_value_loss / max(1, n_updates),
            "entropy": total_entropy / max(1, n_updates),
        }

    def save(self, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "actor": self.actor.state_dict(),
            "critic": self.critic.state_dict(),
            "optimizer": self.optimizer.state_dict(),
        }, p)

    def load(self, path: Union[str, Path]) -> None:
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        self.actor.load_state_dict(checkpoint["actor"])
        self.critic.load_state_dict(checkpoint["critic"])
        if "optimizer" in checkpoint:
            self.optimizer.load_state_dict(checkpoint["optimizer"])


class CurriculumPPOAgent(PPOAgent):
    """C07: Curriculum Learning PPO transferring across scales (N=20 -> 50 -> 100)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            candidate_id="C07",
            name="Curriculum-PPO",
            scorer_type="gnn",
            **kwargs,
        )
        self.current_stage = 0
        self.curriculum_scales = [20, 50, 100]

    def advance_stage(self) -> int:
        if self.current_stage < len(self.curriculum_scales) - 1:
            self.current_stage += 1
        return self.curriculum_scales[self.current_stage]


class BCPPOAgent(PPOAgent):
    """C08: Behavioral Cloning Pretraining on Heuristic Expert + PPO Fine-tuning."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            candidate_id="C08",
            name="BC-PPO",
            scorer_type="mlp",
            **kwargs,
        )

    def pretrain_on_demonstrations(
        self,
        demonstrations: List[Tuple[Dict[str, np.ndarray], int]],
        epochs: int = 5,
        lr: float = 1e-3,
    ) -> float:
        """Supervised cross-entropy pre-training on expert action selections."""
        self.actor.train()
        bc_opt = optim.Adam(self.actor.parameters(), lr=lr)
        total_loss = 0.0

        for _ in range(epochs):
            for obs, target_action in demonstrations:
                x = torch.from_numpy(obs["node_features"]).float()
                mask = torch.from_numpy(obs["action_mask"]).float()

                logits, _ = self.actor(x)
                masked_logits = mask_logits(logits, mask)
                target = torch.tensor([target_action], dtype=torch.long)

                loss = F.cross_entropy(masked_logits.unsqueeze(0), target)
                bc_opt.zero_grad()
                loss.backward()
                bc_opt.step()
                total_loss += float(loss.item())

        return total_loss / max(1, len(demonstrations) * epochs)


class PPORNDAgent(PPOAgent):
    """C09: PPO with Random Network Distillation (RND) Curiosity Exploration."""

    def __init__(self, intrinsic_weight: float = 0.1, **kwargs: Any) -> None:
        super().__init__(
            candidate_id="C09",
            name="PPO-RND",
            scorer_type="mlp",
            **kwargs,
        )
        self.rnd = RNDModule(node_dim=16, hidden_dim=64)
        self.rnd_opt = optim.Adam(self.rnd.predictor.parameters(), lr=1e-3)
        self.intrinsic_weight = intrinsic_weight

    def compute_bonus(self, obs: Dict[str, np.ndarray]) -> float:
        x = torch.from_numpy(obs["node_features"]).float()
        return self.intrinsic_weight * self.rnd.compute_intrinsic_reward(x)
