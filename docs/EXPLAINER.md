# ChaosRL Plain-Language Explainer

This guide explains ChaosRL, its architecture, algorithms, and evaluation metrics in accessible terms so that software engineers, researchers, and technical leaders can explain and defend the system.

---

## 1. What is the Problem?

Modern cloud software is built as **microservices**—dozens or hundreds of small, independent programs that constantly call each other over the network. When you click "Buy" on an e-commerce website, that single click might trigger calls between the payment service, inventory service, shipping calculator, recommendation engine, and user database.

Because these services depend on each other, an unexpected failure in one small service can trigger a **cascading outage**. For example:
- If a database slows down, caller services might keep retrying their requests over and over, creating a **retry storm** that overwhelms the entire system.
- If two critical services happen to run on the exact same physical server, losing that server takes down the entire application.
- If a developer forgot to set a 2-second timeout, one stalled service can hold open connection threads until the entire gateway freezes.

Historically, companies like Netflix invented **Chaos Monkey** to test resilience. Chaos Monkey randomly kills server instances during business hours. While pioneering, Chaos Monkey is essentially a "blind hammer":
1. It is **purely random**: it has no memory, cannot learn from past experiments, and cannot prioritize suspicious services.
2. It **only terminates containers**: it cannot test network latency, packet loss, or resource exhaustion.
3. It can cause **excessive damage**: random attacks frequently take down healthy services without revealing useful bugs.

---

## 2. What is ChaosRL?

**ChaosRL** replaces the random hammer with an **intelligent AI chaos engineer**. 

Using **Reinforcement Learning (RL)**, ChaosRL observes the microservice dependency graph (which service calls which, historical error rates, CPU levels, and replica counts) and learns an optimal policy for:
- **Which service to target next**
- **Which specific fault to inject** (e.g., container kill, 200ms latency, CPU spike, packet loss)
- **What intensity to use** (low, medium, high)

The agent receives a positive reward when it exposes an architectural weakness that violates the system's Service Level Objective (SLO), and receives a penalty if it causes collateral damage or repeats redundant experiments.

---

## 3. How Does the Simulator Work?

Because training RL models directly on live cloud clusters would take months and cost thousands of dollars, ChaosRL includes a **fast, discrete-time simulator**.

- **Call Graph Generation:** The simulator generates realistic architectures from 20 to 500 services across two topology families (Layered architectures and Mesh architectures).
- **Physical Nodes & Replicas:** Services have multiple replicas assigned to physical worker nodes, allowing realistic co-location failures.
- **Traffic Dynamics:** Every simulated tick calculates incoming traffic, queueing delays, timeouts, retry backoffs, and circuit breaker trips.
- **Real-World Calibration:** Fault response curves are calibrated against empirical benchmarks (RCAEval from Sock Shop, Train Ticket, and Online Boutique).

---

## 4. The Candidate Pool & Ensembles

ChaosRL does not rely on a single machine learning model. It evaluates 12 diverse candidates across 5 algorithm families:
1. **Policy Gradient:** PPO with an MLP scorer, A2C, and REINFORCE.
2. **Structure-Aware:** PPO equipped with a Graph Neural Network (GNN) that passes messages across service call edges.
3. **Value-Based:** Double Dueling DQN with action masking.
4. **Gradient-Free:** Evolution Strategies (ES) optimizing action scores without backpropagation.
5. **Non-Deep Learned:** Contextual Bandits (LinUCB) and Gradient-Boosted Decision Trees.

The top 5 performing agents are selected and combined into **ensembles**:
- **Soft Voting (E1):** Averages probability distributions across models.
- **Borda Rank Voting (E2):** Combines candidate rankings.
- **Random Forest Gating (E3):** A meta-classifier that observes graph state and predicts which agent to trust.

---

## 5. How to Read the Figures

- **Weakness Discovery Curve (Figure 1):** The horizontal axis shows the experiment budget (number of tests injected, from 0 to 100), while the vertical axis shows the cumulative percentage of planted weaknesses found. A curve that rises steeply in early experiments indicates an efficient agent.
- **Damage vs. Discovery Scatter:** Compares safety against effectiveness. The ideal agent appears in the top-left quadrant (high discovery, low cumulative damage).
- **Out-of-Distribution Generalization:** Shows whether an agent trained on smaller layered systems can discover weaknesses in large, unfamiliar mesh networks without retraining.

