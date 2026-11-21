# ChaosRL Presentation Kitchen-Sink Markdown Test

This document exercises all rich Markdown syntax elements supported by the ChaosRL presentation layer.

## 1. Mathematical Formulas (KaTeX)

The normalized Area Under the Discovery Curve (AUDC) is defined as:

$$\text{AUDC} = \frac{1}{B} \int_{0}^{B} R(t) \, dt \approx \frac{1}{B} \sum_{t=1}^{B} R(t)$$

Where $B$ is the step budget and $R(t) \in [0, 1]$ represents cumulative weakness recall at step $t$.

The action space is parameterized as:

$$\mathcal{A} = \mathcal{S} \times \mathcal{F} \times \mathcal{I}$$

Where $|\mathcal{S}| = 100$ services, $|\mathcal{F}| = 4$ fault types, and $|\mathcal{I}| = 3$ intensity levels.

## 2. GitHub-Style Alert Callouts

> [!NOTE]
> This is a background note explaining that all models are evaluated across identical DAG seeds.

> [!TIP]
> Use the Presentation Mode (`P`) with projector high-contrast mode when presenting on large conference screens.

> [!IMPORTANT]
> The top 5 models were cryptographically frozen via SHA-256 signatures prior to test set exposure.

> [!WARNING]
> Random-All exploration incurs catastrophic collateral damage ($47,157.5$ points) on production telemetry.

> [!CAUTION]
> Do not evaluate uncalibrated agents directly against production clusters without circuit breaker guardrails.

## 3. Code Blocks with Syntax Highlighting

```python
import numpy as np

def calculate_audc(recall_trajectory, budget):
    """Computes normalized area under discovery curve."""
    return float(np.sum(recall_trajectory) / budget)

# Example verification:
audc = calculate_audc([0.0, 0.05, 0.1, 0.15], budget=4)
print(f"Computed AUDC: {audc:.4f}")
```

## 4. Benchmark Summary Table

| Method Name | Paradigm Family | Normalized AUDC | Weakness Recall | Collateral Damage | Status |
|---|---|---|---|---|---|
| **ChaosRL Top-1 (TreeRanker)** | Tabular / Tree | **0.0762** | 0.0833 | 884.5 | **Champion (p=0.0037)** |
| Heuristic Expert | Expert Rules | 0.1145 | 0.2000 | 205.3 | Benchmark Leader |
| Chaos Monkey (Faithful) | Baseline | 0.0320 | 0.0833 | 137.0 | Baseline |
| Random-All | Baseline | 0.0829 | 0.1417 | 47157.5 | High Damage |

## 5. Mermaid Architecture Diagram

```mermaid
graph LR
    A[Empirical Traces] --> B[Gym Simulator]
    B --> C[Candidate Model Pool]
    C --> D[Top-5 Cryptographic Freeze]
    D --> E[Ensemble Aggregation]
    E --> F[Audited Evaluation n=30]
```

