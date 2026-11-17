import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import rehypeSlug from 'rehype-slug';
import mermaid from 'mermaid';
import { Check, Copy, AlertCircle, Info, AlertTriangle, ShieldAlert, Sparkles } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  useEffect(() => {
    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
          darkMode: true,
          background: '#0f172a',
          primaryColor: '#22c55e',
          secondaryColor: '#38bdf8',
          lineColor: '#64748b',
        },
      });
    } catch (e) {
      console.error('Mermaid init error:', e);
    }
  }, []);

  // Process GitHub callout alerts like > [!NOTE], > [!WARNING], > [!IMPORTANT]
  const processedContent = React.useMemo(() => {
    return content
      .replace(/>\s*\[!NOTE\]([^\n]*)/gi, '> **NOTE:** $1')
      .replace(/>\s*\[!TIP\]([^\n]*)/gi, '> **TIP:** $1')
      .replace(/>\s*\[!IMPORTANT\]([^\n]*)/gi, '> **IMPORTANT:** $1')
      .replace(/>\s*\[!WARNING\]([^\n]*)/gi, '> **WARNING:** $1')
      .replace(/>\s*\[!CAUTION\]([^\n]*)/gi, '> **CAUTION:** $1');
  }, [content]);

  return (
    <div className={`prose prose-invert max-w-none prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-800 ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeRaw, rehypeKatex, rehypeSlug]}
        components={{
          code({ node, inline, className: codeClass, children, ...props }: any) {
            const match = /language-(\w+)/.exec(codeClass || '');
            const lang = match ? match[1] : '';
            const codeString = String(children).replace(/\n$/, '');

            if (!inline && lang === 'mermaid') {
              return <MermaidBlock chart={codeString} />;
            }

            if (!inline && lang) {
              return <CodeBlock language={lang} code={codeString} />;
            }

            return (
              <code className="bg-slate-800 text-brand-300 px-1.5 py-0.5 rounded text-xs font-mono" {...props}>
                {children}
              </code>
            );
          },
          blockquote({ children }: any) {
            return (
              <blockquote className="border-l-4 border-brand-500 bg-slate-900/60 p-4 rounded-r-lg my-4 text-slate-300 italic">
                {children}
              </blockquote>
            );
          },
          table({ children }: any) {
            return (
              <div className="overflow-x-auto my-4 rounded-lg border border-slate-800">
                <table className="w-full text-left text-sm border-collapse">{children}</table>
              </div>
            );
          },
          th({ children }: any) {
            return <th className="bg-slate-900 text-slate-200 px-4 py-2.5 font-semibold border-b border-slate-800">{children}</th>;
          },
          td({ children }: any) {
            return <td className="px-4 py-2 text-slate-300 border-b border-slate-800/60">{children}</td>;
          },
          a({ href, children }: any) {
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" className="text-brand-400 hover:text-brand-300 underline font-medium">
                {children}
              </a>
            );
          }
        }}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
};

const CodeBlock: React.FC<{ language: string; code: string }> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group rounded-lg overflow-hidden my-4 border border-slate-800 bg-slate-900">
      <div className="flex items-center justify-between px-4 py-1.5 bg-slate-950/80 border-b border-slate-800 text-xs font-mono text-slate-400">
        <span>{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-brand-400 transition-colors"
          title="Copy code"
        >
          {copied ? <Check size={14} className="text-brand-400" /> : <Copy size={14} />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-xs font-mono text-slate-200 leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
};

const MermaidBlock: React.FC<{ chart: string }> = ({ chart }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

    mermaid
      .render(id, chart)
      .then(({ svg: renderedSvg }) => {
        if (isMounted) {
          setSvg(renderedSvg);
          setError(null);
        }
      })
      .catch((err) => {
        if (isMounted) {
          console.error('Mermaid render error:', err);
          setError('Failed to render diagram');
        }
      });

    return () => {
      isMounted = false;
    };
  }, [chart]);

  if (error) {
    return <div className="p-3 my-2 text-xs text-rose-400 bg-rose-950/30 border border-rose-800 rounded">{error}</div>;
  }

  return (
    <div
      ref={containerRef}
      className="my-4 p-4 bg-slate-900/60 border border-slate-800 rounded-lg flex justify-center overflow-x-auto"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
};

