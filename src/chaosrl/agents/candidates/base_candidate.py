"""Base interface and common utilities for all ChaosRL candidate agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical

# Pin PyTorch threads to 1 per machine constraints
torch.set_num_threads(1)


def mask_logits(logits: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Mask illegal actions with -1e9 before softmax."""
    # mask: 1 for valid, 0 for illegal
    masked = logits.clone()
    masked[mask == 0] = -1e9
    return masked


class BaseCandidateAgent(ABC):
    """Abstract base class for all learned ChaosRL candidate agents."""

    def __init__(self, candidate_id: str, name: str) -> None:
        self.candidate_id = candidate_id
        self.name = name

    @abstractmethod
    def select_action(
        self,
        obs: Dict[str, np.ndarray],
        deterministic: bool = False,
    ) -> Union[int, List[int]]:
        """Select action index or compound action indices given observation."""
        pass

    def reset_episode(self) -> None:
        """Reset internal state (e.g. GRU hidden state) at start of episode."""
        pass

    def train_step(self, *args: Any, **kwargs: Any) -> Dict[str, float]:
        """Execute one training update step and return training loss metrics."""
        return {}

    @abstractmethod
    def save(self, path: Union[str, Path]) -> None:
        """Save model parameters to disk."""
        pass

    @abstractmethod
    def load(self, path: Union[str, Path]) -> None:
        """Load model parameters from disk."""
        pass

