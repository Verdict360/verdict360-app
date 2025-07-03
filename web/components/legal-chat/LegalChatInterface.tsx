'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Send, MoreHorizontal, Copy, Download, Bookmark, FileText, AlertCircle, Loader2, Scale, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/lib/auth/auth-provider';
import { useToast } from '@/components/ui/use-toast';
import { 
  exportConversationToPdf, 
  exportConversationToWord, 
  copyConversationToClipboard,
  type LegalMessage as ExportMessage,
  type ExportOptions 
} from '@/lib/legal/legal-export';

type MessageType = 'user' | 'assistant';

interface Source {
  id: string;
  title: string;
  citation?: string;
  document_type?: string;
  jurisdiction?: string;
  chunk_index?: number;
  similarity_score?: number;
}

interface Message {
  id: string;
  content: string;
  type: MessageType;
  timestamp: Date;
  sources?: Source[];
  isLoading?: boolean;
  query?: string;
}

interface LegalChatResponse {
  success: boolean;
  response: string;
  sources: Source[];
  query: string;
  legal_citations?: string[];
  legal_terms?: string[];
  confidence_score?: number;
}

const commonLegalQueries = [
  "What are the requirements for a valid contract in South Africa?",
  "Explain the doctrine of precedent in South African law",
  "What are the grounds for dismissal under the Labour Relations Act?",
  "How does POPIA apply to data processing?",
  "What are the fiduciary duties of company directors?",
];

export default function LegalChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    // Scroll to bottom on new messages
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMessage(input);
  };

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || isProcessing) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageText,
      type: 'user',
      timestamp: new Date(),
    };

    const tempAssistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      type: 'assistant',
      timestamp: new Date(),
      isLoading: true,
      query: messageText,
    };

    setMessages(prev => [...prev, userMessage, tempAssistantMessage]);
    setInput('');
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('query', messageText);
      formData.append('jurisdiction', 'South Africa');

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/search/legal-query`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user?.token || 'demo'}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Legal query failed: ${response.status}`);
      }

      const data: LegalChatResponse = await response.json();

      const assistantMessage: Message = {
        id: tempAssistantMessage.id,
        content: data.response,
        type: 'assistant',
        timestamp: new Date(),
        sources: data.sources,
        query: data.query,
      };

      setMessages(prev => prev.map(msg => 
        msg.id === tempAssistantMessage.id ? assistantMessage : msg
      ));

      // Show success toast
      toast({
        title: "Legal Query Processed",
        description: `Found ${data.sources?.length || 0} relevant sources`,
      });

    } catch (error) {
      console.error('Error processing legal query:', error);

      // Replace temp message with error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === tempAssistantMessage.id
            ? {
                ...msg,
                content: 'I apologize, but I encountered an error processing your legal query. Please ensure the API is running and try again.',
                isLoading: false,
              }
            : msg
        )
      );

      toast({
        title: 'Error',
        description: 'Failed to process legal query. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExport = async (format: 'pdf' | 'docx') => {
    const exportMessages: ExportMessage[] = messages
      .filter(msg => !msg.isLoading)
      .map(msg => ({
        id: msg.id,
        content: msg.content,
        type: msg.type,
        timestamp: msg.timestamp,
        sources: msg.sources?.map(source => ({
          id: source.id,
          title: source.title,
          citation: source.citation,
          document_type: source.document_type,
        }))
      }));

    const exportOptions: ExportOptions = {
      title: `Legal Consultation - ${new Date().toLocaleDateString()}`,
      firm: user?.firm_name || 'Verdict360 User',
      date: new Date(),
      includeHeader: true,
      includeFooter: true,
    };

    try {
      if (format === 'pdf') {
        await exportConversationToPdf(exportMessages, exportOptions);
      } else {
        await exportConversationToWord(exportMessages, exportOptions);
      }
      
      toast({
        title: 'Export Successful',
        description: `Legal conversation exported as ${format.toUpperCase()}`,
      });
    } catch (error) {
      toast({
        title: 'Export Failed',
        description: 'Failed to export conversation. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: 'Copied',
        description: 'Message copied to clipboard',
      });
    } catch (error) {
      toast({
        title: 'Copy Failed',
        description: 'Failed to copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  const copyFullConversation = async () => {
    const exportMessages: ExportMessage[] = messages
      .filter(msg => !msg.isLoading)
      .map(msg => ({
        id: msg.id,
        content: msg.content,
        type: msg.type,
        timestamp: msg.timestamp,
        sources: msg.sources?.map(source => ({
          id: source.id,
          title: source.title,
          citation: source.citation,
          document_type: source.document_type,
        }))
      }));

    try {
      await copyConversationToClipboard(exportMessages, {
        title: `Legal Consultation - ${new Date().toLocaleDateString()}`,
        firm: user?.firm_name || 'Verdict360 User',
      });
      
      toast({
        title: 'Conversation Copied',
        description: 'Full legal conversation copied to clipboard',
      });
    } catch (error) {
      toast({
        title: 'Copy Failed',
        description: 'Failed to copy conversation to clipboard',
        variant: 'destructive',
      });
    }
  };

  const highlightCitations = (text: string) => {
    // Enhanced South African citation patterns
    const citationPatterns = [
      { pattern: /\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]+\)/g, style: 'bg-blue-100 text-blue-800 hover:bg-blue-200' },
      { pattern: /\[\d{4}\]\s+ZACC\s+\d+/g, style: 'bg-green-100 text-green-800 hover:bg-green-200' },
      { pattern: /\[\d{4}\]\s+ZASCA\s+\d+/g, style: 'bg-purple-100 text-purple-800 hover:bg-purple-200' },
      { pattern: /\d{4}\s+\(\d+\)\s+BCLR\s+\d+/g, style: 'bg-orange-100 text-orange-800 hover:bg-orange-200' },
      { pattern: /Act\s+No\.\s+\d+\s+of\s+\d{4}/g, style: 'bg-red-100 text-red-800 hover:bg-red-200' },
      { pattern: /Act\s+\d+\s+of\s+\d{4}/g, style: 'bg-red-100 text-red-800 hover:bg-red-200' },
      { pattern: /Constitution\s+of\s+the\s+Republic\s+of\s+South\s+Africa,?\s+1996/gi, style: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200' },
    ];

    let highlightedText = text;

    citationPatterns.forEach(({ pattern, style }) => {
      highlightedText = highlightedText.replace(
        pattern,
        match => `<span class="${style} px-1 py-0.5 rounded cursor-pointer transition-colors" title="South African Legal Citation">${match}</span>`
      );
    });

    return highlightedText;
  };

  const newConversation = () => {
    setMessages([]);
    setInput('');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] border rounded-lg shadow-sm">
      {/* Chat Header */}
      <div className="p-4 border-b flex justify-between items-center bg-card">
        <div className="flex items-center space-x-3">
          <Scale className="h-6 w-6 text-primary" />
          <div>
            <h2 className="text-lg font-semibold text-primary">Legal Assistant</h2>
            <p className="text-xs text-muted-foreground">South African Legal Expertise</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => handleExport('pdf')} 
            title="Export as PDF"
            disabled={messages.length === 0}
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>

          <Button 
            variant="outline" 
            size="sm" 
            onClick={copyFullConversation} 
            title="Copy Full Conversation"
            disabled={messages.length === 0}
          >
            <Copy className="h-4 w-4 mr-2" />
            Copy All
          </Button>

          <Button 
            variant="outline" 
            size="sm" 
            onClick={newConversation} 
            title="New Conversation"
          >
            <FileText className="h-4 w-4 mr-2" />
            New
          </Button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-muted/30">
        {messages.length === 0 ? (
          <div className="text-center p-8">
            <Scale className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="text-lg font-semibold mb-2">Welcome to Verdict360 Legal Assistant</h3>
            <p className="text-muted-foreground mb-6">
              Ask questions about South African law, case analysis, or legal research. 
              I'll provide responses with proper legal citations.
            </p>
            
            <div className="grid gap-2 max-w-md mx-auto">
              <p className="text-sm font-medium text-left mb-2">Try asking about:</p>
              {commonLegalQueries.slice(0, 3).map((query, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => sendMessage(query)}
                  className="text-left h-auto p-3 justify-start whitespace-normal"
                  disabled={isProcessing}
                >
                  {query}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          messages.map(message => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[85%] rounded-lg p-4 ${
                  message.type === 'user' 
                    ? 'bg-primary text-primary-foreground' 
                    : 'bg-card border shadow-sm'
                }`}
              >
                {message.isLoading ? (
                  <div className="flex items-center justify-center py-2">
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    <span className="text-sm">Researching South African legal context...</span>
                  </div>
                ) : (
                  <>
                    <div 
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{
                        __html: message.type === 'assistant' 
                          ? highlightCitations(message.content) 
                          : message.content,
                      }}
                    />

                    {/* Sources Section */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-4 pt-3 border-t">
                        <p className="font-semibold mb-2 text-sm flex items-center">
                          <FileText className="h-4 w-4 mr-1" />
                          Legal Sources ({message.sources.length}):
                        </p>
                        <div className="space-y-2">
                          {message.sources.map((source, index) => (
                            <div key={source.id || index} className="bg-muted/50 rounded p-3 text-sm">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <p className="font-medium">{source.title}</p>
                                  {source.citation && (
                                    <p className="text-xs font-mono text-muted-foreground mt-1">
                                      {source.citation}
                                    </p>
                                  )}
                                  <div className="flex items-center space-x-2 mt-2">
                                    {source.document_type && (
                                      <Badge variant="secondary" className="text-xs">
                                        {source.document_type}
                                      </Badge>
                                    )}
                                    {source.jurisdiction && (
                                      <Badge variant="outline" className="text-xs">
                                        {source.jurisdiction}
                                      </Badge>
                                    )}
                                    {source.similarity_score && (
                                      <Badge variant="secondary" className="text-xs">
                                        {(source.similarity_score * 100).toFixed(1)}% match
                                      </Badge>
                                    )}
                                  </div>
                                </div>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 w-6 p-0 ml-2"
                                  title="View Document"
                                >
                                  <ExternalLink className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Message Actions */}
                    <div className="mt-3 flex justify-end">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => copyToClipboard(message.content)}>
                            <Copy className="h-4 w-4 mr-2" />
                            Copy
                          </DropdownMenuItem>
                          {message.type === 'assistant' && (
                            <>
                              <DropdownMenuItem onClick={() => handleExport('pdf')}>
                                <Download className="h-4 w-4 mr-2" />
                                Export as PDF
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleExport('docx')}>
                                <FileText className="h-4 w-4 mr-2" />
                                Export as Word
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Bookmark className="h-4 w-4 mr-2" />
                                Save to Matter
                              </DropdownMenuItem>
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-4 border-t bg-card">
        <div className="flex space-x-2">
          <Textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask me about South African law, case precedents, statutory interpretation..."
            className="flex-1 resize-none min-h-[44px] max-h-32"
            rows={1}
            disabled={isProcessing}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <Button 
            type="submit" 
            size="icon" 
            disabled={isProcessing || !input.trim()}
            className="h-11 w-11"
          >
            {isProcessing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <div className="mt-2 flex justify-between items-center">
          <span className="text-xs text-muted-foreground">
            Press Enter to send, Shift+Enter for new line
          </span>
          <span className="text-xs text-muted-foreground">
            South African legal expertise " Citations verified
          </span>
        </div>
      </form>
    </div>
  );
}