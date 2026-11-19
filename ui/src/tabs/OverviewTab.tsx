import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, AlertTriangle, ShieldCheck, Activity, Cpu, ArrowRight, Zap, Database, Globe, CheckCircle2 } from 'lucide-react';
import { CohortData, ArchitectureStage } from '../types';

interface OverviewTabProps {
  data: CohortData | null;
  stages: ArchitectureStage[];
  onNavigateTab: (tab: any) => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ data, stages, onNavigateTab }) => {
  // Interactive Microservice Failure-Cascade Simulator State
  const [cascadeStep, setCascadeStep] = useState<number>(0);
  const [isRunningCascade, setIsRunningCascade] = useState<boolean>(false);
  const [faultType, setFaultType] = useState<'pod_kill' | 'latency_injection' | 'packet_loss'>('latency_injection');

  // Interactive nodes in microservice call graph
  const services = [
    { id: 'gateway', name: 'API Gateway', role: 'Entrypoint', tier: 1 },
    { id: 'auth', name: 'Auth Service', role: 'Security', tier: 2 },
    { id: 'orders', name: 'Order Service', role: 'Business Logic', tier: 2 },
    { id: 'payments', name: 'Payment Gateway', role: 'Critical Choke', tier: 3 },
    { id: 'inventory', name: 'Inventory DB', role: 'State Store', tier: 3 },
    { id: 'notifications', name: 'Notifier Queue', role: 'Async Queue', tier: 3 }
  ];

  useEffect(() => {
    let timer: any = null;
    if (isRunningCascade) {
      timer = setInterval(() => {
        setCascadeStep((prev) => {
          if (prev >= 4) {
            setIsRunningCascade(false);
            return 4;
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isRunningCascade]);

  const startSimulation = () => {
    setCascadeStep(1);
    setIsRunningCascade(true);
  };

  const resetSimulation = () => {
    setIsRunningCascade(false);
    setCascadeStep(0);
  };

  const getNodeStatus = (serviceId: string) => {
    if (cascadeStep === 0) return 'healthy';
    if (serviceId === 'payments') {
      return cascadeStep >= 1 ? 'fault_injected' : 'healthy';
    }
    if (serviceId === 'orders') {
      return cascadeStep >= 2 ? 'cascading_timeout' : 'healthy';
    }
    if (serviceId === 'gateway') {
      return cascadeStep >= 3 ? 'slo_breach' : 'healthy';
    }
    if (serviceId === 'inventory' && cascadeStep >= 3) {
      return 'degraded';
    }
    return 'healthy';
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Pitch Section */}
      <div className="relative rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900/90 to-brand-950/30 p-8 overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-3xl space-y-4 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/15 border border-brand-500/30 text-brand-300 text-xs font-semibold">
            <Zap size={14} className="text-brand-400" />
            <span>Autonomous Chaos Engineering Research</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Replacing Random Chaos Monkey with <span className="text-brand-400">Intelligent Learned Policies</span>
          </h1>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Netflix Chaos Monkey terminates random instances with no memory and only a single fault dimension.
            <strong className="text-slate-100 font-semibold"> ChaosRL</strong> trains autonomous reinforcement learning and decision tree agents to explore multi-fault cascades, exposing critical microservice vulnerabilities <strong className="text-brand-300">2.38× faster</strong> while reducing collateral damage by <strong className="text-brand-300">98%</strong> compared to unconstrained exploration.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => onNavigateTab('results')}
              className="flex items-center gap-2 px-5 py-2.5 bg-brand-500 hover:bg-brand-400 text-slate-950 font-bold rounded-xl text-xs transition-all shadow-lg shadow-brand-500/20"
            >
              <span>Explore Headline Results</span>
              <ArrowRight size={15} />
            </button>
            <button
              onClick={() => onNavigateTab('approach')}
              className="flex items-center gap-2 px-5 py-2.5 bg-slate-800/80 hover:bg-slate-700 text-slate-200 font-medium rounded-xl text-xs border border-slate-700 transition-all"
            >
              <span>Simulator Architecture</span>
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Failure-Cascade Visualizer */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Activity className="text-brand-400" size={20} />
              <span>Interactive Microservice Failure-Cascade Simulation</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Observe how targeted fault injection on critical path bottlenecks triggers cascading upstream SLO violations.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={faultType}
              onChange={(e) => setFaultType(e.target.value as any)}
              className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-brand-500"
            >
              <option value="latency_injection">Fault: Latency Spike (+450ms)</option>
              <option value="packet_loss">Fault: Packet Drop (25%)</option>
              <option value="pod_kill">Fault: Pod Kill (Chaos Monkey style)</option>
            </select>

            <button
              onClick={startSimulation}
              disabled={isRunningCascade || cascadeStep === 4}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isRunningCascade
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-brand-500 hover:bg-brand-400 text-slate-950 shadow-md shadow-brand-500/20'
              }`}
            >
              <Play size={13} />
              <span>Inject & Cascade</span>
            </button>

            <button
              onClick={resetSimulation}
              className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg border border-slate-800 transition-colors"
              title="Reset Simulation"
            >
              <RotateCcw size={15} />
            </button>
          </div>
        </div>

        {/* Live Call-Graph Topology Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {services.map((svc) => {
            const status = getNodeStatus(svc.id);
            const isTarget = svc.id === 'payments';

            let statusBg = 'bg-slate-950/80 border-slate-800 text-slate-300';
            let statusBadge = <span className="text-[10px] text-emerald-400 flex items-center gap-1"><CheckCircle2 size={11} /> Healthy (p99 &lt; 25ms)</span>;

            if (status === 'fault_injected') {
              statusBg = 'bg-rose-950/40 border-rose-500 text-rose-200 animate-pulse';
              statusBadge = <span className="text-[10px] text-rose-400 font-bold flex items-center gap-1"><AlertTriangle size={11} /> Fault Injected: {faultType}</span>;
            } else if (status === 'cascading_timeout') {
              statusBg = 'bg-amber-950/40 border-amber-500 text-amber-200';
              statusBadge = <span className="text-[10px] text-amber-400 font-bold flex items-center gap-1"><Activity size={11} /> Thread Pool Exhausted (Retry Storm)</span>;
            } else if (status === 'slo_breach') {
              statusBg = 'bg-red-950/60 border-red-500 text-red-100';
              statusBadge = <span className="text-[10px] text-red-400 font-bold flex items-center gap-1"><ShieldCheck size={11} /> Gateway SLO Breached (p99 &gt; 500ms)</span>;
            } else if (status === 'degraded') {
              statusBg = 'bg-slate-900 border-amber-800 text-amber-300';
              statusBadge = <span className="text-[10px] text-amber-400 flex items-center gap-1"><Activity size={11} /> Connection Backlog Spike</span>;
            }

            return (
              <div
                key={svc.id}
                className={`p-4 rounded-xl border transition-all relative ${statusBg} ${
                  isTarget ? 'ring-2 ring-brand-500/40' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-100">{svc.name}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                    Tier {svc.tier}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 mb-3">{svc.role}</div>
                <div className="pt-2 border-t border-slate-800/60">{statusBadge}</div>
              </div>
            );
          })}
        </div>

        {/* Timeline Status Bar */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-300">Propagation Phase:</span>
            <span className="font-mono text-brand-400">
              {cascadeStep === 0 && 'Steady State (All SLOs Met)'}
              {cascadeStep === 1 && 'Step 1: Targeted Latency Injection at Payment Choke'}
              {cascadeStep === 2 && 'Step 2: Order Service Retry Storm & Thread Exhaustion'}
              {cascadeStep === 3 && 'Step 3: Gateway Queue Overflow & Gateway 504 Timeout'}
              {cascadeStep === 4 && 'Step 4: Weakness Triggered & Documented in Audit Log!'}
            </span>
          </div>
          <div className="flex gap-1.5">
            {[1, 2, 3, 4].map((step) => (
              <span
                key={step}
                className={`w-6 h-2 rounded-full transition-all ${
                  cascadeStep >= step ? 'bg-brand-500' : 'bg-slate-800'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Research Execution Pipeline (Stage 1 to 7) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-100">End-to-End Scientific Architecture</h2>
            <p className="text-xs text-slate-400">From empirical trace calibration to cryptographic freeze and independent audit.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stages.slice(0, 4).map((stage) => (
            <div
              key={stage.id}
              className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 hover:border-slate-700 transition-all space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-950 text-brand-400 border border-slate-800">
                  {stage.number}
                </span>
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: stage.color }} />
              </div>
              <h3 className="text-sm font-bold text-slate-100">{stage.name}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{stage.description}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
          {stages.slice(4).map((stage) => (
            <div
              key={stage.id}
              className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 hover:border-slate-700 transition-all space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-950 text-brand-400 border border-slate-800">
                  {stage.number}
                </span>
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: stage.color }} />
              </div>
              <h3 className="text-sm font-bold text-slate-100">{stage.name}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{stage.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

