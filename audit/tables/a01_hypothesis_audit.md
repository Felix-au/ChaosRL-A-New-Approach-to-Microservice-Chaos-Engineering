# Table: A01 Hypothesis Immutability and Audit Status

| Hypothesis ID | Focus Area | Stated Pre-Registered Text | Git Commit Origin | Match Status | Audit Status |
|---|---|---|---|---|---|
| **RQ1** | Learned vs Random Injection | Learned agent C01 achieves $\ge 25\%$ higher normalized AUDC and $\ge 30\%$ lower cumulative damage than Chaos Monkey and Random-All at scale 100. | `7145480` | **EXACT MATCH** | VERIFIED |
| **RQ2** | Algorithm Family Comparison | Structure-aware policy gradient (C02 GNN) outperforms value-based (C05 DQN) and gradient-free (C10 ES) across diverse topologies. | `7145480` | **EXACT MATCH** | VERIFIED |
| **RQ3** | Ensemble Superiority | The RF-gated ensemble E3 discovers $\ge 10\%$ more planted compound weaknesses than the single best constituent agent. | `7145480` | **EXACT MATCH** | VERIFIED |
| **RQ4** | Out-of-Distribution Generalization | Agents trained exclusively on Family L ($\le 300$ services) retain $\ge 75\%$ of their AUDC advantage over Random-All when tested zero-shot on Family M at scale 500. | `7145480` | **EXACT MATCH** | VERIFIED |
