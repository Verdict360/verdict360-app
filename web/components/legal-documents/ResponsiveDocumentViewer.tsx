import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ChevronLeft, ChevronRight, Maximize, Minimize, Download, Share } from "lucide-react";
import { LegalCitation } from "@/components/ui/typography";

interface ResponsiveDocumentViewerProps {
  documentTitle: string;
  documentType: string;
  content: string;
  citations?: { text: string; reference: string }[];
}

export function ResponsiveDocumentViewer({
  documentTitle,
  documentType,
  content,
  citations = [],
}: ResponsiveDocumentViewerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [fontSize, setFontSize] = useState("md");

  // Replace citations in content with highlighted spans
  const highlightCitations = (text: string) => {
    let highlightedText = text;
    
    citations.forEach(citation => {
      highlightedText = highlightedText.replace(
        citation.text,
        `<span class="bg-primary/10 text-primary px-1 rounded cursor-pointer">${citation.text}</span>`
      );
    });
    
    return highlightedText;
  };

  return (
    <div className={`flex flex-col ${isFullscreen ? 'fixed inset-0 z-50 bg-background p-4' : 'relative'}`}>
      {/* Document Viewer Header */}
      <div className="flex items-center justify-between border-b pb-2 mb-4">
        <div>
          <h3 className="font-medium truncate">{documentTitle}</h3>
          <p className="text-xs text-muted-foreground">{documentType}</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="ghost" size="sm" onClick={() => setFontSize(fontSize === "md" ? "lg" : "md")}>
            {fontSize === "md" ? "A+" : "A-"}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setIsFullscreen(!isFullscreen)}>
            {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Document Content */}
      <div className={`overflow-y-auto flex-1 ${fontSize === "lg" ? "text-lg" : "text-base"}`}>
        <div className="prose prose-neutral dark:prose-invert max-w-none prose-headings:scroll-mt-28 prose-h2:font-heading prose-h2:text-xl lg:prose-h2:text-2xl">
          <div dangerouslySetInnerHTML={{ __html: highlightCitations(content) }} />
        </div>
      </div>

      {/* Mobile Pagination Controls - Visible only on small screens */}
      <div className="md:hidden flex justify-between mt-4 pt-2 border-t">
        <Button variant="outline" size="sm">
          <ChevronLeft className="h-4 w-4 mr-1" /> Previous
        </Button>
        <Button variant="outline" size="sm">
          Next <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>

      {/* Citations Panel - Changes layout on mobile vs desktop */}
      {citations.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="font-medium mb-2">Citations</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {citations.map((citation, index) => (
              <Card key={index} className="p-2 text-sm">
                <LegalCitation>{citation.text}</LegalCitation>
                <p className="mt-1 text-xs text-muted-foreground">{citation.reference}</p>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
