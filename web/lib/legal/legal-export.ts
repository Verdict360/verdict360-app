/**
 * Legal Export Utilities
 * Functions for exporting legal conversations and documents to PDF and Word formats
 */

export interface ExportOptions {
  title: string;
  author?: string;
  firm?: string;
  matter?: string;
  date?: Date;
  includeHeader?: boolean;
  includeFooter?: boolean;
}

export interface LegalMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
  sources?: Array<{
    id: string;
    title: string;
    citation?: string;
    document_type?: string;
  }>;
}

/**
 * Export legal conversation to PDF format (simplified version using browser print)
 */
export async function exportConversationToPdf(
  messages: LegalMessage[],
  options: ExportOptions
): Promise<void> {
  try {
    // Create a formatted HTML version for printing
    const htmlContent = generateExportHtml(messages, options);
    
    // Open in new window and trigger print dialog
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      throw new Error('Failed to open print window. Please allow popups.');
    }
    
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    
    // Wait for content to load then print
    setTimeout(() => {
      printWindow.focus();
      printWindow.print();
      printWindow.close();
    }, 100);
    
  } catch (error) {
    console.error('Error exporting to PDF:', error);
    throw new Error('Failed to export conversation to PDF');
  }
}

/**
 * Export legal conversation to Word format (HTML format that opens in Word)
 */
export async function exportConversationToWord(
  messages: LegalMessage[],
  options: ExportOptions
): Promise<void> {
  try {
    const htmlContent = generateExportHtml(messages, options, 'word');
    
    // Create and download the file
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    const filename = `${options.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${new Date().toISOString().split('T')[0]}.html`;
    link.download = filename;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Error exporting to Word:', error);
    throw new Error('Failed to export conversation to Word format');
  }
}

/**
 * Generate HTML content for export
 */
function generateExportHtml(
  messages: LegalMessage[],
  options: ExportOptions,
  format: 'pdf' | 'word' = 'pdf'
): string {
  const isWord = format === 'word';
  
  let htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>${options.title}</title>
    <style>
        body { 
            font-family: ${isWord ? "'Times New Roman', serif" : "'Arial', sans-serif"}; 
            line-height: 1.6; 
            margin: ${isWord ? '1in' : '20px'}; 
            color: #333;
            font-size: ${isWord ? '12pt' : '11pt'};
        }
        .header { 
            text-align: center; 
            border-bottom: 2px solid #333; 
            padding-bottom: 20px; 
            margin-bottom: 30px; 
        }
        .title { 
            font-size: ${isWord ? '18pt' : '20px'}; 
            font-weight: bold; 
            margin-bottom: 10px; 
        }
        .metadata { 
            font-size: ${isWord ? '10pt' : '12px'}; 
            color: #666; 
        }
        .message { 
            margin-bottom: 25px; 
            page-break-inside: avoid; 
        }
        .message-header { 
            font-weight: bold; 
            font-size: ${isWord ? '14pt' : '14px'}; 
            margin-bottom: 8px; 
            color: #2c5aa0; 
        }
        .message-content { 
            margin-left: 20px; 
            text-align: justify; 
            white-space: pre-wrap;
        }
        .sources { 
            margin-top: 15px; 
            margin-left: 20px; 
            background-color: #f8f9fa; 
            padding: 10px; 
            border-left: 4px solid #2c5aa0; 
            page-break-inside: avoid;
        }
        .sources-title { 
            font-weight: bold; 
            margin-bottom: 8px; 
            color: #2c5aa0; 
        }
        .source-item { 
            margin-bottom: 5px; 
            font-size: ${isWord ? '10pt' : '11px'}; 
        }
        .citation { 
            font-style: italic; 
            color: #666; 
        }
        .footer { 
            text-align: center; 
            font-size: ${isWord ? '9pt' : '10px'}; 
            color: #666; 
            border-top: 1px solid #ccc; 
            padding-top: 10px; 
            margin-top: 30px;
        }
        @page { 
            margin: ${isWord ? '1in' : '0.5in'}; 
        }
        @media print {
            .no-print { display: none; }
            body { margin: 0; }
        }
    </style>
</head>
<body>
`;

  // Header
  if (options.includeHeader !== false) {
    htmlContent += `
    <div class="header">
        <div class="title">${options.title}</div>
        <div class="metadata">
            <div>Generated: ${new Date().toLocaleDateString()}</div>
            ${options.firm ? `<div>Firm: ${options.firm}</div>` : ''}
            ${options.matter ? `<div>Matter: ${options.matter}</div>` : ''}
            <div>Verdict360 Legal Intelligence Platform</div>
        </div>
    </div>
`;
  }
  
  // Messages
  for (const message of messages) {
    const speaker = message.type === 'user' ? 'Client/Attorney' : 'Verdict360 Legal Assistant';
    const timeStr = message.timestamp.toLocaleTimeString();
    
    htmlContent += `
    <div class="message">
        <div class="message-header">${speaker} (${timeStr})</div>
        <div class="message-content">${message.content}</div>
`;
    
    if (message.sources && message.sources.length > 0) {
      htmlContent += `
        <div class="sources">
            <div class="sources-title">Legal Sources:</div>
`;
      
      for (const source of message.sources) {
        htmlContent += `
            <div class="source-item">
                " ${source.title}
                ${source.citation ? `<span class="citation">(${source.citation})</span>` : ''}
                ${source.document_type ? `[${source.document_type}]` : ''}
            </div>
`;
      }
      
      htmlContent += `        </div>`;
    }
    
    htmlContent += `    </div>`;
  }
  
  // Footer
  if (options.includeFooter !== false) {
    htmlContent += `
    <div class="footer">
        Verdict360 Legal Intelligence Platform<br>
        Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}<br>
        South African Legal Context " AI-Powered Research
    </div>
`;
  }
  
  htmlContent += `
</body>
</html>
`;
  
  return htmlContent;
}

/**
 * Copy legal conversation to clipboard
 */
export async function copyConversationToClipboard(
  messages: LegalMessage[],
  options: Partial<ExportOptions> = {}
): Promise<void> {
  try {
    let text = '';
    
    if (options.title) {
      text += `${options.title}\n`;
      text += `Generated: ${new Date().toLocaleDateString()}\n`;
      if (options.firm) text += `Firm: ${options.firm}\n`;
      if (options.matter) text += `Matter: ${options.matter}\n`;
      text += '\n' + '='.repeat(50) + '\n\n';
    }
    
    for (const message of messages) {
      const speaker = message.type === 'user' ? 'Client/Attorney' : 'Verdict360 Legal Assistant';
      const timeStr = message.timestamp.toLocaleTimeString();
      
      text += `${speaker} (${timeStr}):\n`;
      text += `${message.content}\n`;
      
      if (message.sources && message.sources.length > 0) {
        text += '\nLegal Sources:\n';
        for (const source of message.sources) {
          text += `" ${source.title}`;
          if (source.citation) text += ` (${source.citation})`;
          if (source.document_type) text += ` [${source.document_type}]`;
          text += '\n';
        }
      }
      
      text += '\n' + '-'.repeat(30) + '\n\n';
    }
    
    text += `\nGenerated by Verdict360 Legal Intelligence Platform\n`;
    text += `${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}`;
    
    await navigator.clipboard.writeText(text);
    
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    throw new Error('Failed to copy conversation to clipboard');
  }
}