"""Meta-ensemble architectures (E1 Soft Vote, E2 Borda Rank, E3 Gated Controller)."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from sklearn.ensemble import RandomForestClassifier

from chaosrl.agents.candidates.base_candidate import BaseCandidateAgent, mask_logits

torch.set_num_threads(1)


def get_agent_action_probs(agent: Any, obs: Dict[str, np.ndarray]) -> np.ndarray:
    """Extract action probability distribution over catalog for any candidate agent."""
    mask = obs["action_mask"]
    valid_indices = np.where(mask == 1)[0]
    total_actions = len(mask)

    if hasattr(agent, "actor"):
        agent.actor.eval()
        with torch.no_grad():
            x = torch.from_numpy(obs["node_features"]).float()
            adj = torch.from_numpy(obs["adjacency"]).float()
            g = torch.from_numpy(obs["global_features"]).float()
            m = torch.from_numpy(mask).float()

            if hasattr(agent, "scorer_type") and agent.scorer_type == "gru":
                logits, _, _ = agent.actor(x, adj, g, None)
            elif hasattr(agent, "scorer_type") and agent.scorer_type == "gnn":
                logits, _ = agent.actor(x, adj)
            else:
                logits, _ = agent.actor(x)

            masked_logits = mask_logits(logits, m)
            probs = torch.softmax(masked_logits, dim=-1).cpu().numpy()
            return probs

    elif hasattr(agent, "q_net"):
        agent.q_net.eval()
        with torch.no_grad():
            x = torch.from_numpy(obs["node_features"]).float()
            m = torch.from_numpy(mask).float()
            q_vals, _ = agent.q_net(x)
            masked_q = mask_logits(q_vals, m)
            return torch.softmax(masked_q, dim=-1).cpu().numpy()

    elif hasattr(agent, "model"):
        # ES model
        agent.model.eval()
        with torch.no_grad():
            x = torch.from_numpy(obs["node_features"]).float()
            m = torch.from_numpy(mask).float()
            logits, _ = agent.model(x)
            masked = mask_logits(logits, m)
            return torch.softmax(masked, dim=-1).cpu().numpy()

    else:
        # Uniform over valid actions for non-probabilistic models
        probs = np.zeros(total_actions, dtype=np.float32)
        if len(valid_indices) > 0:
            chosen = agent.select_action(obs)
            if isinstance(chosen, (list, tuple)):
                chosen = chosen[0]
            probs[chosen] = 0.8
            probs[valid_indices] += 0.2 / len(valid_indices)
        return probs


class SoftVoteEnsemble:
    """E1: Soft Voting Ensemble averaging action probability distributions."""

    def __init__(self, models: List[Any], name: str = "Ensemble-SoftVote") -> None:
        self.models = models
        self.name = name

    def reset_episode(self) -> None:
        for m in self.models:
            if hasattr(m, "reset_episode"):
                m.reset_episode()

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = True) -> int:
        mask = obs["action_mask"]
        all_probs = [get_agent_action_probs(m, obs) for m in self.models]
        mean_probs = np.mean(all_probs, axis=0)
        mean_probs[mask == 0] = 0.0

        p_sum = np.sum(mean_probs)
        if p_sum > 0:
            mean_probs /= p_sum
        else:
            valid = np.where(mask == 1)[0]
            return int(valid[0]) if len(valid) > 0 else 0

        if deterministic:
            return int(np.argmax(mean_probs))
        return int(np.random.choice(len(mean_probs), p=mean_probs))


class BordaRankEnsemble:
    """E2: Borda Count Rank Voting Ensemble."""

    def __init__(self, models: List[Any], name: str = "Ensemble-BordaRank", top_k: int = 20) -> None:
        self.models = models
        self.name = name
        self.top_k = top_k

    def reset_episode(self) -> None:
        for m in self.models:
            if hasattr(m, "reset_episode"):
                m.reset_episode()

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = True) -> int:
        mask = obs["action_mask"]
        valid_indices = np.where(mask == 1)[0]
        if len(valid_indices) == 0:
            return 0

        borda_scores = np.zeros(len(mask), dtype=np.float32)

        for m in self.models:
            probs = get_agent_action_probs(m, obs)
            probs[mask == 0] = -1e9
            # Rank top-k actions
            k = min(self.top_k, len(valid_indices))
            top_actions = np.argsort(probs)[-k:][::-1]
            for rank_idx, act in enumerate(top_actions):
                borda_scores[act] += (k - rank_idx)

        borda_scores[mask == 0] = -1e9
        return int(np.argmax(borda_scores))


class GatedControllerEnsemble:
    """E3: Meta-Gated Controller routing execution to the optimal specialist candidate."""

    def __init__(self, models: List[Any], name: str = "Ensemble-GatedController") -> None:
        self.models = models
        self.name = name
        self.router = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
        self.is_fitted = False

    def reset_episode(self) -> None:
        for m in self.models:
            if hasattr(m, "reset_episode"):
                m.reset_episode()

    def _extract_meta_features(self, obs: Dict[str, np.ndarray]) -> np.ndarray:
        # 16 mean node features + 5 global context features = 21 features
        node_mean = np.mean(obs["node_features"], axis=0)
        return np.concatenate([node_mean, obs["global_features"]])

    def fit_gate(self, X_meta: np.ndarray, y_best_model: np.ndarray) -> None:
        if len(np.unique(y_best_model)) > 1:
            self.router.fit(X_meta, y_best_model)
            self.is_fitted = True

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = True) -> int:
        if self.is_fitted:
            meta_vec = self._extract_meta_features(obs).reshape(1, -1)
            selected_model_idx = int(self.router.predict(meta_vec)[0])
        else:
            # Fallback to round-robin or first model
            selected_model_idx = int(obs["global_features"][4]) % len(self.models)

        selected_model_idx = np.clip(selected_model_idx, 0, len(self.models) - 1)
        return self.models[selected_model_idx].select_action(obs, deterministic=deterministic)

    def save(self, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump({"router": self.router, "is_fitted": self.is_fitted}, f)

    def load(self, path: Union[str, Path]) -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.router = data["router"]
            self.is_fitted = data["is_fitted"]
