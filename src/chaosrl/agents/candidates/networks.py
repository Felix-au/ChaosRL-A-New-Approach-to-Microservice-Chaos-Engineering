"""Topology-agnostic neural network architectures for ChaosRL candidates.

Implements shared Scorer networks:
- MLPScorer: Shared per-node multi-layer perceptron.
- GNNScorer: 2-layer Graph Convolutional Network message passing.
- GRUScorer: Recurrent policy with GRU memory of episode history.
- CriticNetwork: State-value network with permutation-invariant global pooling.
- RNDModule: Random Network Distillation module for intrinsic exploration.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Pin PyTorch threads to 1 per machine constraints
torch.set_num_threads(1)


def normalize_adjacency(adj: torch.Tensor) -> torch.Tensor:
    """Compute symmetric normalized adjacency matrix: D^{-1/2} (A + I) D^{-1/2}."""
    # adj: (B, N, N) or (N, N)
    is_batched = adj.dim() == 3
    if not is_batched:
        adj = adj.unsqueeze(0)

    b, n, _ = adj.shape
    eye = torch.eye(n, device=adj.device).unsqueeze(0).expand(b, -1, -1)
    a_tilde = adj + eye

    deg = torch.sum(a_tilde, dim=-1)  # (b, n)
    deg_inv_sqrt = torch.pow(torch.clamp(deg, min=1.0), -0.5)
    d_mat = torch.diag_embed(deg_inv_sqrt)  # (b, n, n)

    norm_adj = torch.bmm(torch.bmm(d_mat, a_tilde), d_mat)
    return norm_adj if is_batched else norm_adj.squeeze(0)


class MLPScorer(nn.Module):
    """Shared per-node MLP mapping (N, 16) node features to (N, 18) action logits."""

    def __init__(self, node_dim: int = 16, hidden_dim: int = 64, num_actions_per_node: int = 18) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(node_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_actions_per_node),
        )
        self.embedding_net = nn.Sequential(
            nn.Linear(node_dim, hidden_dim),
            nn.ReLU(),
        )

    def forward(self, x: torch.Tensor, adj: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass.
        
        Args:
            x: (B, N, 16) or (N, 16)
            adj: unused, present for uniform interface
            
        Returns:
            logits: (B, N * 18) or (N * 18,)
            embeddings: (B, N, hidden_dim) or (N, hidden_dim)
        """
        is_batched = x.dim() == 3
        if not is_batched:
            x = x.unsqueeze(0)

        b, n, _ = x.shape
        embeddings = self.embedding_net(x)
        logits = self.net(x)  # (b, n, 18)
        flat_logits = logits.view(b, -1)  # (b, n * 18)

        if not is_batched:
            return flat_logits.squeeze(0), embeddings.squeeze(0)
        return flat_logits, embeddings


class GNNScorer(nn.Module):
    """2-layer Graph Convolutional Network mapping graph state to (N, 18) action logits."""

    def __init__(self, node_dim: int = 16, hidden_dim: int = 64, num_actions_per_node: int = 18) -> None:
        super().__init__()
        self.hidden_dim = hidden_dim
        # Layer 1
        self.w_self1 = nn.Linear(node_dim, hidden_dim)
        self.w_neigh1 = nn.Linear(node_dim, hidden_dim)
        self.ln1 = nn.LayerNorm(hidden_dim)

        # Layer 2
        self.w_self2 = nn.Linear(hidden_dim, hidden_dim)
        self.w_neigh2 = nn.Linear(hidden_dim, hidden_dim)
        self.ln2 = nn.LayerNorm(hidden_dim)

        # Output head
        self.out_head = nn.Linear(hidden_dim, num_actions_per_node)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass with normalized graph message passing."""
        is_batched = x.dim() == 3
        if not is_batched:
            x = x.unsqueeze(0)
            adj = adj.unsqueeze(0)

        b, n, _ = x.shape
        norm_adj = normalize_adjacency(adj)

        # Layer 1
        neigh1 = torch.bmm(norm_adj, x)
        h1 = F.relu(self.ln1(self.w_self1(x) + self.w_neigh1(neigh1)))

        # Layer 2
        neigh2 = torch.bmm(norm_adj, h1)
        h2 = F.relu(self.ln2(self.w_self2(h1) + self.w_neigh2(neigh2)))

        logits = self.out_head(h2)  # (b, n, 18)
        flat_logits = logits.view(b, -1)

        if not is_batched:
            return flat_logits.squeeze(0), h2.squeeze(0)
        return flat_logits, h2


class GRUScorer(nn.Module):
    """Recurrent policy network maintaining GRU memory across injection steps."""

    def __init__(self, node_dim: int = 16, hidden_dim: int = 64, num_actions_per_node: int = 18) -> None:
        super().__init__()
        self.hidden_dim = hidden_dim
        self.node_encoder = nn.Sequential(
            nn.Linear(node_dim, hidden_dim),
            nn.ReLU(),
        )
        # GRU cell operates on global pooled graph embedding
        self.gru = nn.GRUCell(hidden_dim + 5, hidden_dim)

        # Node action head combining node representation and recurrent state
        self.head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_actions_per_node),
        )

    def forward(
        self,
        x: torch.Tensor,
        adj: Optional[torch.Tensor],
        global_feat: torch.Tensor,
        hidden: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass with GRU recurrent update."""
        is_batched = x.dim() == 3
        if not is_batched:
            x = x.unsqueeze(0)
            global_feat = global_feat.unsqueeze(0)
            if hidden is not None:
                hidden = hidden.unsqueeze(0)

        b, n, _ = x.shape
        node_emb = self.node_encoder(x)  # (b, n, hidden_dim)

        # Global pooled representation
        pooled = torch.mean(node_emb, dim=1)  # (b, hidden_dim)
        gru_in = torch.cat([pooled, global_feat], dim=-1)  # (b, hidden_dim + 5)

        if hidden is None:
            hidden = torch.zeros(b, self.hidden_dim, device=x.device)

        new_hidden = self.gru(gru_in, hidden)  # (b, hidden_dim)

        # Broadcast hidden to all nodes
        hidden_expanded = new_hidden.unsqueeze(1).expand(-1, n, -1)
        node_combined = torch.cat([node_emb, hidden_expanded], dim=-1)

        logits = self.head(node_combined)  # (b, n, 18)
        flat_logits = logits.view(b, -1)

        if not is_batched:
            return flat_logits.squeeze(0), node_emb.squeeze(0), new_hidden.squeeze(0)
        return flat_logits, node_emb, new_hidden


class CriticNetwork(nn.Module):
    """Permutation-invariant state value critic network."""

    def __init__(self, hidden_dim: int = 64, global_dim: int = 5) -> None:
        super().__init__()
        # Input: pooled mean (hidden_dim) + pooled max (hidden_dim) + global_feat (global_dim)
        in_dim = hidden_dim * 2 + global_dim
        self.v_net = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, node_embeddings: torch.Tensor, global_feat: torch.Tensor) -> torch.Tensor:
        """Estimate state value V(s)."""
        is_batched = node_embeddings.dim() == 3
        if not is_batched:
            node_embeddings = node_embeddings.unsqueeze(0)
            global_feat = global_feat.unsqueeze(0)

        # Graph readout: mean + max pooling over nodes
        mean_pool = torch.mean(node_embeddings, dim=1)
        max_pool, _ = torch.max(node_embeddings, dim=1)
        graph_repr = torch.cat([mean_pool, max_pool, global_feat], dim=-1)

        value = self.v_net(graph_repr)  # (b, 1)
        return value if is_batched else value.squeeze(0)


class RNDModule(nn.Module):
    """Random Network Distillation (RND) module for curiosity-driven exploration."""

    def __init__(self, node_dim: int = 16, hidden_dim: int = 64) -> None:
        super().__init__()
        # Target network is fixed randomly initialized
        self.target = nn.Sequential(
            nn.Linear(node_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 32),
        )
        for param in self.target.parameters():
            param.requires_grad = False

        # Predictor network is trained to predict target embeddings
        self.predictor = nn.Sequential(
            nn.Linear(node_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 32),
        )

    def compute_intrinsic_reward(self, node_feat: torch.Tensor) -> float:
        """Compute MSE prediction error as intrinsic reward."""
        if node_feat.dim() == 2:
            # Pool graph state into summary vector (mean + max)
            mean_f = torch.mean(node_feat, dim=0)
            max_f, _ = torch.max(node_feat, dim=0)
            pooled = torch.cat([mean_f, max_f], dim=-1).unsqueeze(0)
        else:
            mean_f = torch.mean(node_feat, dim=1)
            max_f, _ = torch.max(node_feat, dim=1)
            pooled = torch.cat([mean_f, max_f], dim=-1)

        with torch.no_grad():
            target_feat = self.target(pooled)
        pred_feat = self.predictor(pooled)
        loss = F.mse_loss(pred_feat, target_feat)
        return float(loss.item())
