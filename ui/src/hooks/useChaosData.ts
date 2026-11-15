import { useState, useEffect } from 'react';
import {
  DataSetCohort,
  CohortData,
  DiscoveryCurvesData,
  MethodMetadata,
  ArchitectureStage,
  RigorData,
  GlossaryItem,
  SearchDocEntry
} from '../types';

export interface ChaosDataContextType {
  loading: boolean;
  error: string | null;
  cohort: DataSetCohort;
  setCohort: (c: DataSetCohort) => void;
  activeData: CohortData | null;
  preAuditData: CohortData | null;
  postAuditData: CohortData | null;
  curves: DiscoveryCurvesData | null;
  methods: MethodMetadata[];
  architecture: { title: string; stages: ArchitectureStage[] } | null;
  rigor: RigorData | null;
  glossary: Record<string, GlossaryItem>;
  docsIndex: SearchDocEntry[];
}

export function useChaosData(): ChaosDataContextType {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cohort, setCohort] = useState<DataSetCohort>('post_audit');

  const [preAuditData, setPreAuditData] = useState<CohortData | null>(null);
  const [postAuditData, setPostAuditData] = useState<CohortData | null>(null);
  const [curves, setCurves] = useState<DiscoveryCurvesData | null>(null);
  const [methods, setMethods] = useState<MethodMetadata[]>([]);
  const [architecture, setArchitecture] = useState<{ title: string; stages: ArchitectureStage[] } | null>(null);
  const [rigor, setRigor] = useState<RigorData | null>(null);
  const [glossary, setGlossary] = useState<Record<string, GlossaryItem>>({});
  const [docsIndex, setDocsIndex] = useState<SearchDocEntry[]>([]);

  useEffect(() => {
    async function loadAllData() {
      try {
        setLoading(true);
        const [
          preRes,
          postRes,
          curvesRes,
          methodsRes,
          archRes,
          rigorRes,
          glossaryRes,
          docsIndexRes
        ] = await Promise.all([
          fetch('/data/pre_audit.json'),
          fetch('/data/post_audit.json'),
          fetch('/data/curves.json'),
          fetch('/data/methods.json'),
          fetch('/data/architecture.json'),
          fetch('/data/rigor.json'),
          fetch('/data/glossary.json'),
          fetch('/data/docs_index.json')
        ]);

        if (!preRes.ok || !postRes.ok) {
          throw new Error('Failed to load primary dataset files');
        }

        const pre = await preRes.json();
        const post = await postRes.json();
        const crv = await curvesRes.json();
        const mtd = await methodsRes.json();
        const arc = await archRes.json();
        const rig = await rigorRes.json();
        const glo = await glossaryRes.json();
        const docIdx = await docsIndexRes.json();

        setPreAuditData(pre);
        setPostAuditData(post);
        setCurves(crv);
        setMethods(mtd);
        setArchitecture(arc);
        setRigor(rig);
        setGlossary(glo);
        setDocsIndex(docIdx);
      } catch (err: any) {
        console.error('Data loading error:', err);
        setError(err.message || 'Unknown data loading error');
      } finally {
        setLoading(false);
      }
    }

    loadAllData();
  }, []);

  const activeData = cohort === 'post_audit' ? postAuditData : preAuditData;

  return {
    loading,
    error,
    cohort,
    setCohort,
    activeData,
    preAuditData,
    postAuditData,
    curves,
    methods,
    architecture,
    rigor,
    glossary,
    docsIndex
  };
}

