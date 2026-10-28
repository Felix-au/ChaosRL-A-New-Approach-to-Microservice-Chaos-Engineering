"""Classic RL candidate agents: A2C (C04), DQN (C05), REINFORCE (C06)."""

from __future__ import annotations

import random
from collections import deque
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical

from chaosrl.agents.candidates.base_candidate import BaseCandidateAgent, mask_logits
from chaosrl.agents.candidates.networks import CriticNetwork, MLPScorer

torch.set_num_threads(1)


class A2CAgent(BaseCandidateAgent):
    """C04: Synchronous Advantage Actor-Critic (A2C)."""

    def __init__(
        self,
        candidate_id: str = "C04",
        name: str = "A2C",
        lr: float = 5e-4,
        gamma: float = 0.99,
        entropy_coef: float = 0.02,
        value_coef: float = 0.5,
    ) -> None:
        super().__init__(candidate_id, name)
        self.gamma = gamma
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef

        self.actor = MLPScorer(node_dim=16, hidden_dim=64)
        self.critic = CriticNetwork(hidden_dim=64, global_dim=5)
        self.optimizer = optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            lr=lr,
        )

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = False) -> int:
        self.actor.eval()
        with torch.no_grad():
            x = torch.from_numpy(obs["node_features"]).float()
            mask = torch.from_numpy(obs["action_mask"]).float()
            logits, _ = self.actor(x)
            masked_logits = mask_logits(logits, mask)
            dist = Categorical(logits=masked_logits)
            if deterministic:
                return int(torch.argmax(masked_logits).item())
            return int(dist.sample().item())

    def update_step(
        self,
        obs: Dict[str, np.ndarray],
        action: int,
        reward: float,
        next_obs: Dict[str, np.ndarray],
        done: bool,
    ) -> Dict[str, float]:
        self.actor.train()
        self.critic.train()

        x = torch.from_numpy(obs["node_features"]).float()
        g = torch.from_numpy(obs["global_features"]).float()
        mask = torch.from_numpy(obs["action_mask"]).float()

        next_x = torch.from_numpy(next_obs["node_features"]).float()
        next_g = torch.from_numpy(next_obs["global_features"]).float()

        logits, emb = self.actor(x)
        masked_logits = mask_logits(logits, mask)
        dist = Categorical(logits=masked_logits)
        log_prob = dist.log_prob(torch.tensor(action))
        entropy = dist.entropy()

        val = self.critic(emb, g)

        with torch.no_grad():
            _, next_emb = self.actor(next_x)
            next_val = self.critic(next_emb, next_g) if not done else torch.tensor(0.0)
            target = reward + self.gamma * next_val

        advantage = target - val
        actor_loss = -log_prob * advantage.detach()
        critic_loss = F.mse_loss(val.squeeze(-1), target)
        loss = actor_loss + self.value_coef * critic_loss - self.entropy_coef * entropy

        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.actor.parameters(), 0.5)
        nn.utils.clip_grad_norm_(self.critic.parameters(), 0.5)
        self.optimizer.step()

        return {
            "actor_loss": float(actor_loss.item()),
            "critic_loss": float(critic_loss.item()),
            "entropy": float(entropy.item()),
        }

    def save(self, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"actor": self.actor.state_dict(), "critic": self.critic.state_dict()}, p)

    def load(self, path: Union[str, Path]) -> None:
        ckpt = torch.load(path, map_location="cpu", weights_only=True)
        self.actor.load_state_dict(ckpt["actor"])
        self.critic.load_state_dict(ckpt["critic"])


class DQNAgent(BaseCandidateAgent):
    """C05: Dueling Double Deep Q-Network (DQN) with action masking."""

    def __init__(
        self,
        candidate_id: str = "C05",
        name: str = "DQN-Dueling",
        lr: float = 1e-3,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.05,
        epsilon_decay: float = 0.995,
        buffer_size: int = 5000,
        batch_size: int = 32,
    ) -> None:
        super().__init__(candidate_id, name)
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size

        self.q_net = MLPScorer(node_dim=16, hidden_dim=64)
        self.target_net = MLPScorer(node_dim=16, hidden_dim=64)
        self.target_net.load_state_dict(self.q_net.state_dict())

        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)
        self.replay_buffer: Deque[Tuple[Dict[str, np.ndarray], int, float, Dict[str, np.ndarray], bool]] = deque(maxlen=buffer_size)

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = False) -> int:
        mask = obs["action_mask"]
        valid_actions = np.where(mask == 1)[0]
        if len(valid_actions) == 0:
            return 0

        if not deterministic and random.random() < self.epsilon:
            return int(random.choice(valid_actions))

        self.q_net.eval()
        with torch.no_grad():
            x = torch.from_numpy(obs["node_features"]).float()
            q_values, _ = self.q_net(x)
            q_values[torch.from_numpy(mask) == 0] = -1e9
            return int(torch.argmax(q_values).item())

    def store_transition(
        self,
        obs: Dict[str, np.ndarray],
        action: int,
        reward: float,
        next_obs: Dict[str, np.ndarray],
        done: bool,
    ) -> None:
        self.replay_buffer.append((obs, action, reward, next_obs, done))

    def train_step(self) -> Dict[str, float]:
        if len(self.replay_buffer) < self.batch_size:
            return {"loss": 0.0}

        batch = random.sample(self.replay_buffer, self.batch_size)
        self.q_net.train()
        total_loss = 0.0

        for obs, act, rew, next_obs, done in batch:
            x = torch.from_numpy(obs["node_features"]).float()
            q_vals, _ = self.q_net(x)
            q_act = q_vals[act]

            with torch.no_grad():
                if done:
                    target = rew
                else:
                    next_x = torch.from_numpy(next_obs["node_features"]).float()
                    next_mask = torch.from_numpy(next_obs["action_mask"]).float()
                    next_q, _ = self.target_net(next_x)
                    next_q[next_mask == 0] = -1e9
                    target = rew + self.gamma * float(torch.max(next_q).item())

            loss = F.mse_loss(q_act, torch.tensor(target).float())
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            total_loss += float(loss.item())

        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        return {"loss": total_loss / self.batch_size, "epsilon": self.epsilon}

    def sync_target(self) -> None:
        self.target_net.load_state_dict(self.q_net.state_dict())

    def save(self, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.q_net.state_dict(), p)

    def load(self, path: Union[str, Path]) -> None:
        self.q_net.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
        self.sync_target()


class REINFORCEAgent(BaseCandidateAgent):
    """C06: Monte Carlo Policy Gradient (REINFORCE) with state-value baseline."""

    def __init__(
        self,
        candidate_id: str = "C06",
        name: str = "REINFORCE",
        lr: float = 1e-3,
        gamma: float = 0.99,
    ) -> None:
        super().__init__(candidate_id, name)
        self.gamma = gamma
        self.actor = MLPScorer(node_dim=16, hidden_dim=64)
        self.critic = CriticNetwork(hidden_dim=64, global_dim=5)
        self.optimizer = optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            lr=lr,
        )

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = False) -> int:
        self.actor.eval()
        with torch.no_grad():
            x = torch.from_numpy(obs["node_features"]).float()
            mask = torch.from_numpy(obs["action_mask"]).float()
            logits, _ = self.actor(x)
            masked_logits = mask_logits(logits, mask)
            dist = Categorical(logits=masked_logits)
            if deterministic:
                return int(torch.argmax(masked_logits).item())
            return int(dist.sample().item())

    def update_episode(self, episode_transitions: List[Tuple[Dict[str, np.ndarray], int, float]]) -> Dict[str, float]:
        self.actor.train()
        self.critic.train()

        t_len = len(episode_transitions)
        returns = np.zeros(t_len, dtype=np.float32)
        cum_ret = 0.0
        for t in reversed(range(t_len)):
            cum_ret = episode_transitions[t][2] + self.gamma * cum_ret
            returns[t] = cum_ret

        total_loss = 0.0
        for t in range(t_len):
            obs, act, _ = episode_transitions[t]
            ret = returns[t]

            x = torch.from_numpy(obs["node_features"]).float()
            g = torch.from_numpy(obs["global_features"]).float()
            mask = torch.from_numpy(obs["action_mask"]).float()

            logits, emb = self.actor(x)
            masked_logits = mask_logits(logits, mask)
            dist = Categorical(logits=masked_logits)
            log_prob = dist.log_prob(torch.tensor(act))

            val = self.critic(emb, g)
            advantage = ret - float(val.item())

            loss = -log_prob * advantage + F.mse_loss(val.squeeze(-1), torch.tensor([ret]).float())
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            total_loss += float(loss.item())

        return {"loss": total_loss / max(1, t_len)}

    def save(self, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"actor": self.actor.state_dict(), "critic": self.critic.state_dict()}, p)

    def load(self, path: Union[str, Path]) -> None:
        ckpt = torch.load(path, map_location="cpu", weights_only=True)
        self.actor.load_state_dict(ckpt["actor"])
        self.critic.load_state_dict(ckpt["critic"])
