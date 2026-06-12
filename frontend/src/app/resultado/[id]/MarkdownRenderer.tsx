"use client";

import { useMemo } from "react";

interface Props {
  content: string;
}

/**
 * Converte o Markdown estruturado retornado pela IA em JSX estilizado.
 * Suporta o conjunto exato de elementos gerados pelo nosso prompt:
 *   ## h2  |  ### h3  |  **bold**  |  `code`  |  | table |  |  > quote  |  ---  |  listas  |  parágrafos
 */
export default function MarkdownRenderer({ content }: Props) {
  const html = useMemo(() => parseMarkdown(content), [content]);

  return (
    <div
      className="markdown-body"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

/* ─── Parser ─────────────────────────────────────────────────────────────── */

function parseMarkdown(raw: string): string {
  const lines = raw.split("\n");
  const out: string[] = [];

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    // Horizontal rule
    if (/^---+$/.test(line.trim())) {
      out.push("<hr />");
      i++;
      continue;
    }

    // h2
    if (line.startsWith("## ")) {
      out.push(`<h2>${inlineFormat(line.slice(3))}</h2>`);
      i++;
      continue;
    }

    // h3
    if (line.startsWith("### ")) {
      out.push(`<h3>${inlineFormat(line.slice(4))}</h3>`);
      i++;
      continue;
    }

    // Blockquote (collects consecutive > lines)
    if (line.startsWith("> ")) {
      const bqLines: string[] = [];
      while (i < lines.length && lines[i].startsWith("> ")) {
        bqLines.push(inlineFormat(lines[i].slice(2)));
        i++;
      }
      out.push(`<blockquote>${bqLines.join("<br/>")}</blockquote>`);
      continue;
    }

    // Table (header row contains |)
    if (line.startsWith("|") && line.endsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      out.push(buildTable(tableLines));
      continue;
    }

    // Unordered list
    if (/^[-*] /.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*] /.test(lines[i])) {
        items.push(`<li>${inlineFormat(lines[i].slice(2))}</li>`);
        i++;
      }
      out.push(`<ul>${items.join("")}</ul>`);
      continue;
    }

    // Ordered list
    if (/^\d+\. /.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(`<li>${inlineFormat(lines[i].replace(/^\d+\. /, ""))}</li>`);
        i++;
      }
      out.push(`<ol>${items.join("")}</ol>`);
      continue;
    }

    // Empty line — skip
    if (line.trim() === "") {
      i++;
      continue;
    }

    // Paragraph
    out.push(`<p>${inlineFormat(line)}</p>`);
    i++;
  }

  return out.join("\n");
}

function buildTable(rows: string[]): string {
  // Filter separator rows (e.g. |---|---|)
  const dataRows = rows.filter(r => !/^\|[-| :]+\|$/.test(r.trim()));
  if (dataRows.length === 0) return "";

  const parseRow = (r: string) =>
    r
      .split("|")
      .slice(1, -1)
      .map(cell => cell.trim());

  const [headerRow, ...bodyRows] = dataRows;
  const headers = parseRow(headerRow);

  const thead = `<thead><tr>${headers.map(h => `<th>${inlineFormat(h)}</th>`).join("")}</tr></thead>`;
  const tbody = bodyRows.length
    ? `<tbody>${bodyRows
        .map(r => `<tr>${parseRow(r).map(c => `<td>${inlineFormat(c)}</td>`).join("")}</tr>`)
        .join("")}</tbody>`
    : "";

  return `<table>${thead}${tbody}</table>`;
}

function inlineFormat(text: string): string {
  return (
    text
      // escape HTML
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      // **bold**
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      // *italic*
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      // `code`
      .replace(/`([^`]+)`/g, "<code>$1</code>")
  );
}
