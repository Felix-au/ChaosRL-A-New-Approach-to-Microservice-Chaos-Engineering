import React, { useState, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  ColumnDef,
  SortingState
} from '@tanstack/react-table';
import { ArrowUpDown, ArrowUp, ArrowDown, Download, Search, Sparkles, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
import { InsightRuleResult } from '../insight/engine';

interface DataTableProps<T extends Record<string, any>> {
  data: T[];
  columns: ColumnDef<T, any>[];
  insights?: InsightRuleResult[];
  title?: string;
  searchPlaceholder?: string;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  insights = [],
  title,
  searchPlaceholder = 'Filter rows...'
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState('');

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel()
  });

  const exportCSV = () => {
    if (!data.length) return;
    const headers = columns.map((c: any) => c.header || c.accessorKey || '').join(',');
    const rows = data.map((row) =>
      columns.map((c: any) => {
        const val = row[c.accessorKey];
        return typeof val === 'string' ? `"${val}"` : val;
      }).join(',')
    );
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers, ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${title ? title.toLowerCase().replace(/\s+/g, '_') : 'table_export'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm shadow-lg">
      {/* Table Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          {title && <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">{title}</h3>}
          <span className="text-xs text-slate-400">Displaying {table.getRowModel().rows.length} methods and baselines</span>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-2.5 text-slate-500" size={14} />
            <input
              type="text"
              value={globalFilter ?? ''}
              onChange={(e) => setGlobalFilter(e.target.value)}
              placeholder={searchPlaceholder}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>
          <button
            onClick={exportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium transition-colors"
            title="Export CSV"
          >
            <Download size={14} />
            <span>CSV</span>
          </button>
        </div>
      </div>

      {/* Main Table */}
      <div className="overflow-x-auto rounded-lg border border-slate-800">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="bg-slate-950/90 text-slate-300 border-b border-slate-800">
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="py-3 px-4 font-semibold select-none cursor-pointer hover:text-brand-400 transition-colors"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-1.5">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {{
                        asc: <ArrowUp size={12} className="text-brand-400" />,
                        desc: <ArrowDown size={12} className="text-brand-400" />
                      }[header.column.getIsSorted() as string] ?? <ArrowUpDown size={11} className="text-slate-600" />}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className="border-b border-slate-800/50 hover:bg-slate-800/40 transition-colors"
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="py-2.5 px-4 text-slate-300 font-mono">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Dynamic Grounded Insight Box */}
      {insights.length > 0 && (
        <div className="space-y-2 pt-2">
          {insights.map((ins) => (
            <div
              key={ins.ruleId}
              className={`p-3.5 rounded-lg border text-xs leading-relaxed flex items-start gap-3 transition-all ${
                ins.badgeType === 'success'
                  ? 'bg-brand-950/30 border-brand-800/60 text-brand-200'
                  : ins.badgeType === 'info'
                  ? 'bg-sky-950/30 border-sky-800/60 text-sky-200'
                  : 'bg-amber-950/30 border-amber-800/60 text-amber-200'
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {ins.badgeType === 'success' ? (
                  <Sparkles size={16} className="text-brand-400" />
                ) : ins.badgeType === 'info' ? (
                  <Info size={16} className="text-sky-400" />
                ) : (
                  <AlertCircle size={16} className="text-amber-400" />
                )}
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-100">{ins.headline}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      ins.badgeType === 'success'
                        ? 'bg-brand-500/20 text-brand-300 border border-brand-500/30'
                        : ins.badgeType === 'info'
                        ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                        : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}
                  >
                    {ins.badgeText}
                  </span>
                </div>
                <p className="text-slate-300">{ins.detail}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

