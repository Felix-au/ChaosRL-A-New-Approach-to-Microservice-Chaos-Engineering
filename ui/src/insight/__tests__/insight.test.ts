import { describe, it, expect } from 'vitest';
import { METRICS } from '../metrics';
import { getMethodRole, isPrimaryLearned, isPrimaryBaseline } from '../roles';
import { InsightEngine, MethodRow } from '../engine';

describe('Metrics Registry', () => {
  it('correctly formats numbers and units', () => {
    expect(METRICS.audc.format(0.076212)).toBe('0.0762');
    expect(METRICS.recall.format(0.2)).toBe('0.2000');
    expect(METRICS.damage.format(47157.5)).toBe('47.2k');
    expect(METRICS.damage.format(5486231.2)).toBe('5.5M');
    expect(METRICS.p_value.format(0.0037)).toBe('0.0037');
    expect(METRICS.p_value.format(0.0001)).toBe('< 0.001');
  });

  it('preserves correct metric optimization directions', () => {
    expect(METRICS.audc.direction).toBe('higher');
    expect(METRICS.recall.direction).toBe('higher');
    expect(METRICS.damage.direction).toBe('lower');
  });
});

describe('Method Role Classification', () => {
  it('identifies learned, baseline, ensemble, expert, and oracle methods', () => {
    expect(getMethodRole('ChaosRL Top-1 (TreeRanker)')).toBe('learned');
    expect(getMethodRole('C12')).toBe('learned');
    expect(getMethodRole('Chaos Monkey (Faithful)')).toBe('baseline');
    expect(getMethodRole('Heuristic Expert')).toBe('expert');
    expect(getMethodRole('ChaosRL Ensemble (Soft Vote)')).toBe('ensemble');
    expect(getMethodRole('Oracle (Upper Bound)')).toBe('oracle');
  });

  it('correctly flags primary candidates', () => {
    expect(isPrimaryLearned('ChaosRL Top-1 (TreeRanker)')).toBe(true);
    expect(isPrimaryLearned('C12')).toBe(true);
    expect(isPrimaryLearned('PPO-MLP')).toBe(false);

    expect(isPrimaryBaseline('Chaos Monkey (Faithful)')).toBe(true);
    expect(isPrimaryBaseline('Chaos Monkey-2')).toBe(false);
  });
});

describe('InsightEngine Scale-100 Analysis', () => {
  const sampleRows: MethodRow[] = [
    {
      method: 'Chaos Monkey (Faithful)',
      tag: 'chaos_monkey',
      audc: 0.0320,
      recall: 0.0833,
      damage: 137.0
    },
    {
      method: 'ChaosRL Top-1 (TreeRanker)',
      tag: 'C12',
      audc: 0.0762,
      recall: 0.0833,
      damage: 884.5
    },
    {
      method: 'Random-All',
      tag: 'random_all',
      audc: 0.0829,
      recall: 0.1417,
      damage: 47157.5
    },
    {
      method: 'Heuristic Expert',
      tag: 'heuristic',
      audc: 0.1145,
      recall: 0.2000,
      damage: 205.3
    },
    {
      method: 'ChaosRL Ensemble (Soft Vote)',
      tag: 'e1_soft',
      audc: 0.0801,
      recall: 0.0833,
      damage: 10914.3
    }
  ];

  it('generates primary AUDC win rule for TreeRanker over Chaos Monkey', () => {
    const insights = InsightEngine.analyzeScale100(sampleRows, 'post_audit');
    const top1Win = insights.find(i => i.ruleId === 'RULE-S100-TOP1-AUDC');
    expect(top1Win).toBeDefined();
    expect(top1Win?.metrics.ratio).toBeCloseTo(0.0762 / 0.0320, 2);
    expect(top1Win?.badgeText).toContain('AUDC Advantage');
    expect(top1Win?.detail).toContain('p = 0.0037');
    expect(top1Win?.detail).toContain('n=30 systems');
  });

  it('generates damage metric skew context rule showing 53x safety over Random-All', () => {
    const insights = InsightEngine.analyzeScale100(sampleRows, 'post_audit');
    const damageContext = insights.find(i => i.ruleId === 'RULE-S100-DAMAGE-SKEW-CONTEXT');
    expect(damageContext).toBeDefined();
    expect(damageContext?.headline).toContain('Safer than Unconstrained Exploration');
    expect(damageContext?.detail).toContain('pod instances (1 of 4 fault modes)');
    expect(damageContext?.metrics.ratio).toBeGreaterThan(50);
  });
});

