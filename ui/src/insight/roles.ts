export type MethodRole = 'baseline' | 'learned' | 'ensemble' | 'expert' | 'oracle';

export function getMethodRole(identifier: string): MethodRole {
  const norm = identifier.toLowerCase().trim();
  if (norm.includes('oracle')) return 'oracle';
  if (norm.includes('heuristic') || norm.includes('expert')) return 'expert';
  if (norm.includes('ensemble') || norm.startsWith('e1') || norm.startsWith('e2') || norm.startsWith('e3')) return 'ensemble';
  if (
    norm.includes('top-1') ||
    norm.includes('treeranker') ||
    norm.startsWith('c12') ||
    norm.startsWith('c01') ||
    norm.startsWith('c03') ||
    norm.startsWith('c07') ||
    norm.startsWith('c09') ||
    norm.includes('ppo') ||
    norm.includes('dqn') ||
    norm.includes('linucb') ||
    norm.includes('gcn')
  ) {
    return 'learned';
  }
  return 'baseline';
}

export function isPrimaryLearned(identifier: string): boolean {
  const norm = identifier.toLowerCase().trim();
  return norm.includes('top-1') || norm.includes('treeranker') || norm === 'c12';
}

export function isPrimaryBaseline(identifier: string): boolean {
  const norm = identifier.toLowerCase().trim();
  return (norm.includes('chaos monkey') && !norm.includes('chaos monkey-2')) || norm === 'chaos_monkey';
}

export function isExpertBenchmark(identifier: string): boolean {
  const norm = identifier.toLowerCase().trim();
  return norm.includes('heuristic') || norm.includes('expert');
}

export function isEnsembleLeader(identifier: string): boolean {
  const norm = identifier.toLowerCase().trim();
  return norm.includes('soft') || norm === 'e1_soft';
}

