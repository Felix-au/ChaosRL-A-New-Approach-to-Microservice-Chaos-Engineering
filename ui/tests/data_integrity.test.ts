import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const PUBLIC_DATA_DIR = path.resolve(__dirname, '../public/data');
const REPO_ROOT = path.resolve(__dirname, '../../');

describe('Data Integrity & Ground Truth Verification', () => {
  it('ensures all required JSON data files exist and are valid JSON', () => {
    const requiredFiles = [
      'methods.json',
      'architecture.json',
      'glossary.json',
      'rigor.json',
      'pre_audit.json',
      'post_audit.json',
      'curves.json',
      'docs_index.json',
      'manifest.json',
      'build_report.json'
    ];

    for (const file of requiredFiles) {
      const fullPath = path.join(PUBLIC_DATA_DIR, file);
      expect(fs.existsSync(fullPath), `Missing data file: ${file}`).toBe(true);
      const content = fs.readFileSync(fullPath, 'utf-8');
      expect(() => JSON.parse(content), `Invalid JSON in: ${file}`).not.toThrow();
    }
  });

  it('verifies post_audit.json matches facts.json ground truth numbers exactly', () => {
    const factsPath = path.join(REPO_ROOT, 'results/facts.json');
    const facts = JSON.parse(fs.readFileSync(factsPath, 'utf-8'));
    const postAudit = JSON.parse(fs.readFileSync(path.join(PUBLIC_DATA_DIR, 'post_audit.json'), 'utf-8'));

    // Check n=30 systems
    expect(postAudit.n_systems).toBe(30);

    const s100 = postAudit.scale100;
    const top1 = s100.find((r: any) => (r.tag === 'C12' || r.method.includes('Top-1')));
    const chaosMonkey = s100.find((r: any) => (r.tag === 'chaos_monkey' || r.method.includes('Chaos Monkey (Faithful)')));

    expect(top1).toBeDefined();
    expect(chaosMonkey).toBeDefined();

    // Verify AUDCs against facts.json
    const getVal = (entry: any) => typeof entry === 'object' && entry !== null && 'value' in entry ? entry.value : entry;
    expect(top1.audc).toBeCloseTo(getVal(facts['audit.scale100.combined.chaosrl_top1.audc']), 4);
    expect(chaosMonkey.audc).toBeCloseTo(getVal(facts['audit.scale100.combined.chaos_monkey.audc']), 4);
    expect(postAudit.statistical_tests[0].p_adj).toBeCloseTo(getVal(facts['audit.scale100.combined.p_value_vs_chaos_monkey']), 4);
  });

  it('confirms pre_audit.json has n=10 systems and non-empty rows', () => {
    const preAudit = JSON.parse(fs.readFileSync(path.join(PUBLIC_DATA_DIR, 'pre_audit.json'), 'utf-8'));
    expect(preAudit.n_systems).toBe(10);
    expect(preAudit.scale100.length).toBeGreaterThanOrEqual(10);
    expect(preAudit.budget_sweep.length).toBeGreaterThan(0);
    expect(preAudit.multiscale.length).toBeGreaterThan(0);
  });

  it('validates curves.json has step-by-step mean and confidence intervals', () => {
    const curves = JSON.parse(fs.readFileSync(path.join(PUBLIC_DATA_DIR, 'curves.json'), 'utf-8'));
    expect(curves.post_audit).toBeDefined();
    expect(curves.post_audit['C12']).toBeDefined();

    const top1Curve = curves.post_audit['C12'];
    expect(top1Curve.steps.length).toBeGreaterThan(10);
    expect(top1Curve.mean.length).toBe(top1Curve.steps.length);
    expect(top1Curve.ci_low.length).toBe(top1Curve.steps.length);
    expect(top1Curve.ci_high.length).toBe(top1Curve.steps.length);

    // Confidence interval bounds check: ci_low <= mean <= ci_high
    for (let i = 0; i < top1Curve.mean.length; i++) {
      expect(top1Curve.ci_low[i]).toBeLessThanOrEqual(top1Curve.mean[i] + 0.0001);
      expect(top1Curve.mean[i]).toBeLessThanOrEqual(top1Curve.ci_high[i] + 0.0001);
    }
  });

  it('ensures docs_index.json contains indexed sections with valid search snippets', () => {
    const docs = JSON.parse(fs.readFileSync(path.join(PUBLIC_DATA_DIR, 'docs_index.json'), 'utf-8'));
    expect(docs.length).toBeGreaterThanOrEqual(50);
    const firstDoc = docs[0];
    expect(firstDoc.id).toBeDefined();
    expect(firstDoc.title).toBeDefined();
    expect(firstDoc.rel_path).toBeDefined();
    expect(firstDoc.snippet).toBeDefined();
  });
});
