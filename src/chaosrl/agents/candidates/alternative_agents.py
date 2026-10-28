"""Alternative candidate agents: Evolutionary Strategy (C10), Contextual Bandit (C11), Supervised Ranker (C12)."""

from __future__ import annotations

import copy
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestClassifier

from chaosrl.agents.candidates.base_candidate import BaseCandidateAgent, mask_logits
from chaosrl.agents.candidates.networks import MLPScorer

torch.set_num_threads(1)


class ESAgent(BaseCandidateAgent):
    """C10: Simple Natural Evolutionary Strategy (ES) optimizing policy weights."""

    def __init__(
        self,
        candidate_id: str = "C10",
        name: str = "ES-Policy",
        pop_size: int = 16,
        sigma: float = 0.05,
        lr: float = 0.02,
    ) -> None:
        super().__init__(candidate_id, name)
        self.pop_size = pop_size
        self.sigma = sigma
        self.lr = lr

        self.model = MLPScorer(node_dim=16, hidden_dim=32)
        self.param_vec = self._get_params(self.model)

    def _get_params(self, model: nn.Module) -> np.ndarray:
        return torch.cat([p.data.view(-1) for p in model.parameters()]).cpu().numpy()

    def _set_params(self, model: nn.Module, params: np.ndarray) -> None:
        idx = 0
        for p in model.parameters():
            numel = p.numel()
            p.data.copy_(torch.from_numpy(params[idx : idx + numel]).view_as(p.data))
            idx += numel

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = False) -> int:
        self.model.eval()
        with torch.no_grad():
            x = torch.from_numpy(obs["node_features"]).float()
            mask = torch.from_numpy(obs["action_mask"]).float()
            logits, _ = self.model(x)
            masked = mask_logits(logits, mask)
            if deterministic:
                return int(torch.argmax(masked).item())
            probs = torch.softmax(masked, dim=-1).cpu().numpy()
            return int(np.random.choice(len(probs), p=probs))

    def update_population(self, perturbations: List[np.ndarray], returns: List[float]) -> float:
        """Update central policy parameters using fitness returns."""
        returns_arr = np.array(returns)
        # Normalize returns
        norm_returns = (returns_arr - np.mean(returns_arr)) / (np.std(returns_arr) + 1e-8)

        # Gradient estimate: sum(R_i * eps_i) / (P * sigma)
        grad = np.zeros_like(self.param_vec)
        for eps, r in zip(perturbations, norm_returns):
            grad += r * eps
        grad /= (len(perturbations) * self.sigma)

        self.param_vec += self.lr * grad
        self._set_params(self.model, self.param_vec)
        return float(np.mean(returns_arr))

    def sample_perturbation(self) -> np.ndarray:
        return np.random.randn(len(self.param_vec))

    def get_perturbed_agent(self, eps: np.ndarray) -> ESAgent:
        perturbed = copy.deepcopy(self)
        perturbed_params = self.param_vec + self.sigma * eps
        self._set_params(perturbed.model, perturbed_params)
        return perturbed

    def save(self, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), p)

    def load(self, path: Union[str, Path]) -> None:
        self.model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
        self.param_vec = self._get_params(self.model)


class LinUCBBanditAgent(BaseCandidateAgent):
    """C11: Contextual Bandit (LinUCB) using node features and fault embeddings."""

    def __init__(
        self,
        candidate_id: str = "C11",
        name: str = "LinUCB-Contextual",
        feature_dim: int = 16,
        alpha: float = 0.5,
    ) -> None:
        super().__init__(candidate_id, name)
        self.d = feature_dim
        self.alpha = alpha
        # Maintain ridge regression matrices A and b for each of the 6 fault types
        self.A = [np.eye(self.d) for _ in range(6)]
        self.b = [np.zeros(self.d) for _ in range(6)]

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = False) -> int:
        mask = obs["action_mask"]
        valid_indices = np.where(mask == 1)[0]
        if len(valid_indices) == 0:
            return 0

        node_feat = obs["node_features"]  # (N, 16)
        n_services = node_feat.shape[0]

        best_score = -float("inf")
        best_act = valid_indices[0]

        # Score candidate actions
        for act in valid_indices:
            svc_id = act // 18
            slot = act % 18
            ft_idx = slot // 3  # fault type 0..5

            x = node_feat[svc_id]  # (16,)
            A_inv = np.linalg.pinv(self.A[ft_idx])
            theta = A_inv @ self.b[ft_idx]

            expected_reward = float(x @ theta)
            confidence_bound = float(self.alpha * np.sqrt(x @ A_inv @ x))
            score = expected_reward + (confidence_bound if not deterministic else 0.0)

            if score > best_score:
                best_score = score
                best_act = act

        return int(best_act)

    def update(self, action: int, obs: Dict[str, np.ndarray], reward: float) -> None:
        svc_id = action // 18
        slot = action % 18
        ft_idx = slot // 3

        x = obs["node_features"][svc_id]
        self.A[ft_idx] += np.outer(x, x)
        self.b[ft_idx] += reward * x

    def save(self, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump({"A": self.A, "b": self.b, "alpha": self.alpha}, f)

    def load(self, path: Union[str, Path]) -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.A = data["A"]
            self.b = data["b"]
            self.alpha = data.get("alpha", 0.5)


class SupervisedRankerAgent(BaseCandidateAgent):
    """C12: Supervised Ranking Model (Random Forest) trained to predict vulnerability discovery."""

    def __init__(
        self,
        candidate_id: str = "C12",
        name: str = "TreeRanker",
        n_estimators: int = 50,
    ) -> None:
        super().__init__(candidate_id, name)
        self.clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=8, random_state=42)
        self.is_fitted = False

    def select_action(self, obs: Dict[str, np.ndarray], deterministic: bool = False) -> int:
        mask = obs["action_mask"]
        valid_indices = np.where(mask == 1)[0]
        if len(valid_indices) == 0:
            return 0

        if not self.is_fitted:
            # Fallback to random valid action before fitting
            return int(np.random.choice(valid_indices))

        node_feat = obs["node_features"]
        g_feat = obs["global_features"]

        # Vectorized feature construction for valid candidates
        features = []
        for act in valid_indices:
            svc_id = act // 18
            slot = act % 18
            ft_idx = slot // 3
            inten_idx = slot % 3

            # Combined feature: node (16) + global (5) + fault type one-hot (6) + intensity (3) = 30
            ft_onehot = np.zeros(6)
            ft_onehot[ft_idx] = 1.0
            inten_onehot = np.zeros(3)
            inten_onehot[inten_idx] = 1.0

            vec = np.concatenate([node_feat[svc_id], g_feat, ft_onehot, inten_onehot])
            features.append(vec)

        features_arr = np.array(features)
        probs = self.clf.predict_proba(features_arr)[:, 1] if self.clf.n_classes_ > 1 else np.zeros(len(valid_indices))

        if deterministic or np.random.random() < 0.8:
            best_idx = np.argmax(probs)
            return int(valid_indices[best_idx])
        else:
            return int(np.random.choice(valid_indices))

    def train_dataset(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit random forest classifier on historical transition data."""
        if len(np.unique(y)) > 1:
            self.clf.fit(X, y)
            self.is_fitted = True

    def save(self, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump({"clf": self.clf, "is_fitted": self.is_fitted}, f)

    def load(self, path: Union[str, Path]) -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.clf = data["clf"]
            self.is_fitted = data["is_fitted"]
