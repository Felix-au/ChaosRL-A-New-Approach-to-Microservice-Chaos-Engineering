# ChaosRL Executive Presentation Deck Outline

This outline specifies an 8-to-10 slide presentation deck summarizing ChaosRL for technical conferences, executive leadership, and system engineering panels.

---

### Slide 1: The Failure of Random Chaos
- **Title:** Beyond Chaos Monkey: Autonomous RL for Microservice Vulnerability Discovery
- **Visuals:** Architectural diagram contrasting random pod termination vs. intelligent targeted multi-fault injection.
- **Key Message:** Modern microservices suffer from subtle cascading failure modes (retry storms, missing timeouts, co-location risks). Blind random killing (Chaos Monkey) is inefficient and causes unnecessary production damage.
- **Data Callout:** Random Chaos Monkey finds only kill-type weaknesses and misses $>70\%$ of complex architectural defects.

---

### Slide 2: Research Questions & Core Hypotheses
- **Title:** Formulating the Problem: Can RL Outperform Random Chaos?
- **Visuals:** [Table: stage1_hypotheses](tables/stage1_hypotheses.md) listing RQ1 to RQ4 and formal decision criteria.
- **Key Message:** We set out to answer whether learned agents can discover more weaknesses with less damage, which algorithm family excels, whether diverse ensembles beat single agents, and if policies generalize zero-shot to unseen topologies.

---

### Slide 3: Grounded in Reality: Data-Calibrated Simulation
- **Title:** The ChaosRL Discrete-Time Aggregate Simulator
- **Visuals:** [Figure: stage1_architecture_flow](figures/stage1_architecture_flow.png) and calibration distribution fits.
- **Key Message:** Fast discrete-time simulation ($> 1,000$ experiments/min) calibrated against empirical telemetry from 375 real microservice outage cases (RCAEval: Sock Shop, Train Ticket, Online Boutique).
- **Takeaway:** Enables thorough multi-seed RL training and rigorous benchmarking without million-dollar cloud bills.

---

### Slide 4: Candidate Pool & Diverse Algorithm Families
- **Title:** 12 Candidates Across 5 Learning Paradigms
- **Visuals:** Master candidate architecture overview table comparing Policy Gradient (PPO, A2C), GNNs, Q-Learning (DQN), Evolution Strategies, and Contextual Bandits.
- **Key Message:** Broad exploration of inductive biases ensures we do not overfit to a single RL flavor.

---

### Slide 5: The Top-5 Selection & Ensembling
- **Title:** Combining Diverse Strengths: Soft Voting, Borda Ranks, and RF Gating
- **Visuals:** Validation AUDC ranking chart and RF-gated controller architecture.
- **Key Message:** Selecting the top 5 agents under a diversity constraint (maximum 2 per family) prevents shared blind spots. The Random Forest Gated Controller (E3) dynamically selects the best policy for each system state.

---

### Slide 6: Main Evaluation Results (RQ1 & RQ2)
- **Title:** Empirical Discovery Performance Across Scales 20, 100, and 300
- **Visuals:** Main discovery curves (AUDC) with 95% bootstrap confidence intervals and damage comparison scatter plot.
- **Key Message:** ChaosRL agents achieve higher weakness discovery recall in fewer experiments while causing substantially lower cumulative SLO damage than Chaos Monkey and Random-All.

---

### Slide 7: Out-of-Distribution Generalization (RQ4)
- **Title:** Zero-Shot Generalization: Scale 500 & Unseen Mesh Topologies
- **Visuals:** Generalization retention bar chart comparing in-distribution Family L performance against out-of-distribution Family M.
- **Key Message:** Graph-structured and per-service representations allow models trained on small layered systems to generalize effectively to large, unseen mesh topologies.

---

### Slide 8: What Did the Agents Learn? (Interpretability)
- **Title:** Policy Interpretability & Failure Mode Analysis
- **Visuals:** Feature correlation heatmap (targeting probability vs. in-degree, replica count, co-location, and failure history).
- **Key Message:** Agents actively learn to avoid well-fortified decoys and systematically probe unshielded critical dependencies, isolating vulnerabilities without causing catastrophic collateral outages.

---

### Slide 9: Integrity, Limitations, and Future Horizons
- **Title:** Rigorous Methodology and Practical Roadmaps
- **Visuals:** Test set lock verification, ablation studies, and roadmap diagram toward live Kubernetes integration.
- **Key Message:** All results are produced under a strict test-set lock with pre-registered hypotheses. Future work will extend the framework to open-telemetry distributed tracing and continuous action throttling.

