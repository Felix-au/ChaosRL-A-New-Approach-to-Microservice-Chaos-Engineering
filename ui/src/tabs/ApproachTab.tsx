import React from 'react';
import { Cpu, Server, Activity, Sliders, CheckCircle2, Shield, AlertTriangle, Layers } from 'lucide-react';
import { CohortData } from '../types';

interface ApproachTabProps {
  data: CohortData | null;
}

export const ApproachTab: React.FC<ApproachTabProps> = ({ data }) => {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Overview Banner */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-3">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Server className="text-brand-400" size={22} />
          <span>The ChaosRL Simulator & Gymnasium Environment</span>
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-4xl">
          To train reinforcement learning agents without bringing down production clusters, we engineered a
          <strong className="text-brand-300"> 12,000 steps/sec discrete-event microservice simulator</strong> adhering to the standard OpenAI/Farama Gymnasium interface.
          Every queue dynamic, retry storm, timeout backoff, and cascading degradation curve is mathematically calibrated on empirical traces from real microservice deployments.
        </p>
      </div>

      {/* Multi-Fault Action Space vs Chaos Monkey 1-Fault Limitation */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Sliders className="text-brand-400" size={18} />
              <span>Multi-Dimensional Action Space vs. Chaos Monkey Limitation</span>
            </h3>
            <p className="text-xs text-slate-400">Chaos Monkey only terminates instances. Real production outages are multi-dimensional.</p>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-950 text-brand-300 border border-slate-800">
            |A| = 1,200 discrete actions (N=100)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-200">1. Pod Termination</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300">Chaos Monkey Only</span>
            </div>
            <p className="text-xs text-slate-400">
              Immediately terminates healthy container replicas, triggering Kubernetes pod restarts and rescheduling delays.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-brand-500/30 bg-brand-950/20 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-brand-200">2. Latency Injection</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-500/30 text-brand-300">ChaosRL</span>
            </div>
            <p className="text-xs text-slate-400">
              Injects +50ms to +1,000ms delay into upstream service RPC handlers, exposing missing timeouts and thread starvation.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-brand-500/30 bg-brand-950/20 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-brand-200">3. Packet Loss</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-500/30 text-brand-300">ChaosRL</span>
            </div>
            <p className="text-xs text-slate-400">
              Drops 5% to 50% of ingress packets, triggering aggressive retry storms and multiplier effects across dependent tiers.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-brand-500/30 bg-brand-950/20 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-brand-200">4. CPU / Resource Stress</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-500/30 text-brand-300">ChaosRL</span>
            </div>
            <p className="text-xs text-slate-400">
              Simulates thread pool saturation and CPU starvation, degrading garbage collection and queue drain latencies.
            </p>
          </div>
        </div>
      </div>

      {/* Trace Calibration & Physics Accuracy */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Empirical Fitting */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Activity className="text-sky-400" size={18} />
            <span>Empirical Calibration Traces</span>
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Calibrated on over 500,000 real HTTP trace spans collected from the industry-standard
            <strong className="text-slate-100"> Sock-Shop</strong> and <strong className="text-slate-100">Train-Ticket</strong> benchmark deployments under synthetic locust workloads.
          </p>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-300 font-medium">Baseline Service Latencies</span>
              <span className="font-mono text-brand-400">Log-Normal(μ=2.1, σ=0.45)</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-300 font-medium">Cascading Delay Tail Distribution</span>
              <span className="font-mono text-brand-400">Pareto(α=1.65, x_m=12.4ms)</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-300 font-medium">Circuit Breaker Trip Threshold</span>
              <span className="font-mono text-brand-400">5 consecutive 504 errors / 10s</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-300 font-medium">Simulation Execution Throughput</span>
              <span className="font-mono text-brand-400">12,450 steps / second</span>
            </div>
          </div>
        </div>

        {/* State Observation Tensor Spec */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Layers className="text-purple-400" size={18} />
            <span>Agent Observation Space</span>
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            At each decision step, agents receive a rich telemetric tensor encoding both graph topology and real-time degradation signals.
          </p>

          <div className="space-y-2.5 text-xs">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between font-semibold text-slate-200">
                <span>1. Structural Graph Centrality</span>
                <span className="font-mono text-purple-400">Dim: [N, 4]</span>
              </div>
              <p className="text-slate-400">In-degree, out-degree, betweenness centrality, and downstream fan-out ratio.</p>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between font-semibold text-slate-200">
                <span>2. Dynamic Telemetry Status</span>
                <span className="font-mono text-purple-400">Dim: [N, 6]</span>
              </div>
              <p className="text-slate-400">p50/p99 latency, HTTP 5xx error rate, CPU utilization, thread queue depth, active replica count.</p>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between font-semibold text-slate-200">
                <span>3. Global System Context</span>
                <span className="font-mono text-purple-400">Dim: [4]</span>
              </div>
              <p className="text-slate-400">Remaining step budget B, cumulative collateral damage, gateway SLO margin, step index.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

