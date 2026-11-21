import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import fs from 'fs';
import path from 'path';
import { MarkdownRenderer } from '../src/markdown/MarkdownRenderer';

describe('MarkdownRenderer Component', () => {
  it('renders kitchen-sink markdown without throwing exceptions', () => {
    const fixturePath = path.resolve(__dirname, 'fixtures/kitchen-sink.md');
    const content = fs.readFileSync(fixturePath, 'utf-8');

    const { container } = render(React.createElement(MarkdownRenderer, { content }));

    // Check header
    expect(screen.getByText('ChaosRL Presentation Kitchen-Sink Markdown Test')).toBeInTheDocument();

    // Check table elements
    expect(screen.getByText('Method Name')).toBeInTheDocument();
    expect(screen.getByText('ChaosRL Top-1 (TreeRanker)')).toBeInTheDocument();

    // Check transformed callouts (NOTE, IMPORTANT, WARNING, CAUTION)
    expect(container.innerHTML).toContain('NOTE:');
    expect(container.innerHTML).toContain('IMPORTANT:');
    expect(container.innerHTML).toContain('WARNING:');

    // Check code blocks
    expect(container.querySelector('pre')).toBeInTheDocument();
  });
});

