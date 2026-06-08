/**
 * 简历 Markdown 格式化工具
 */

/** 统一无序列表符号为 `-` */
export function normalizeListMarkers(text: string): string {
  return text.replace(/^[\t ]*[\*\+]\s+/gm, '- ')
}

/** 规范标题：`#标题` → `# 标题` */
export function normalizeHeadings(text: string): string {
  return text.replace(/^(#{1,6})([^\s#\n])/gm, '$1 $2')
}

/** 清理行尾空格与多余空行 */
export function cleanWhitespace(text: string): string {
  return text
    .replace(/[ \t]+$/gm, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

/** 全部格式化 */
export function formatResumeMarkdown(text: string): string {
  return cleanWhitespace(normalizeHeadings(normalizeListMarkers(text)))
}

export type FormatAction = 'lists' | 'headings' | 'whitespace' | 'all'

export function applyFormatAction(text: string, action: FormatAction): string {
  switch (action) {
    case 'lists':
      return normalizeListMarkers(text)
    case 'headings':
      return normalizeHeadings(text)
    case 'whitespace':
      return cleanWhitespace(text)
    case 'all':
      return formatResumeMarkdown(text)
    default:
      return text
  }
}
