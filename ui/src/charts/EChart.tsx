import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';
import { Maximize2, Minimize2, Download, Table, BarChart2 } from 'lucide-react';

export interface EChartProps {
  option: any;
  style?: React.CSSProperties;
  className?: string;
  title?: string;
  tableData?: Array<Record<string, any>>;
  tableColumns?: Array<{ key: string; label: string }>;
}

export const EChart: React.FC<EChartProps> = ({
  option,
  style = { height: '360px', width: '100%' },
  className = '',
  title,
  tableData,
  tableColumns
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showTable, setShowTable] = useState(false);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, 'dark', {
        renderer: 'canvas'
      });
    }

    // Apply dark styling defaults
    const customizedOption = {
      backgroundColor: 'transparent',
      textStyle: {
        fontFamily: 'Inter, system-ui, sans-serif'
      },
      ...option
    };

    chartInstance.current.setOption(customizedOption, true);

    const resizeObserver = new ResizeObserver(() => {
      chartInstance.current?.resize();
    });

    resizeObserver.observe(chartRef.current);

    return () => {
      resizeObserver.disconnect();
    };
  }, [option]);

  const handleDownload = () => {
    if (!chartInstance.current) return;
    const url = chartInstance.current.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#0a0f1d'
    });
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title ? title.toLowerCase().replace(/\s+/g, '_') : 'chart'}.png`;
    a.click();
  };

  return (
    <div className={`relative rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm ${className}`}>
      {/* Chart Toolbar */}
      <div className="flex items-center justify-between pb-3 mb-2 border-b border-slate-800/80">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          {title && <span>{title}</span>}
        </h3>
        <div className="flex items-center gap-1.5">
          {tableData && tableColumns && (
            <button
              onClick={() => setShowTable(!showTable)}
              className={`p-1.5 rounded text-xs flex items-center gap-1 transition-colors ${
                showTable ? 'bg-brand-500/20 text-brand-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
              title={showTable ? 'Show Chart' : 'Show Data Table'}
            >
              {showTable ? <BarChart2 size={15} /> : <Table size={15} />}
            </button>
          )}
          <button
            onClick={handleDownload}
            className="p-1.5 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            title="Download PNG"
          >
            <Download size={15} />
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
          </button>
        </div>
      </div>

      {/* Main Content: Chart or Accessible Table */}
      {showTable && tableData && tableColumns ? (
        <div className="overflow-x-auto max-h-[360px] overflow-y-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="bg-slate-950 text-slate-300 border-b border-slate-800 sticky top-0">
                {tableColumns.map((col) => (
                  <th key={col.key} className="py-2 px-3 font-semibold">
                    {col.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableData.map((row, idx) => (
                <tr key={idx} className="border-b border-slate-800/40 hover:bg-slate-800/40">
                  {tableColumns.map((col) => (
                    <td key={col.key} className="py-2 px-3 text-slate-300 font-mono">
                      {typeof row[col.key] === 'number'
                        ? Number(row[col.key]).toFixed(4)
                        : String(row[col.key] ?? '')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div
          ref={chartRef}
          style={style}
          className={`${isFullscreen ? 'fixed inset-4 z-50 bg-slate-950 p-6 rounded-2xl shadow-2xl border border-slate-700' : ''}`}
        />
      )}
    </div>
  );
};
