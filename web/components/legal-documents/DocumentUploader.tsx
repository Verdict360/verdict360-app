import { useState } from "react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { UploadCloud } from "lucide-react";

const documentTypes = [
  { value: "judgment", label: "Court Judgment" },
  { value: "statute", label: "Statute or Act" },
  { value: "contract", label: "Legal Contract" },
  { value: "pleading", label: "Pleading Document" },
  { value: "opinion", label: "Legal Opinion" },
];

export function DocumentUploader() {
  const [documentType, setDocumentType] = useState("");
  const [title, setTitle] = useState("");
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-primary">Upload Document</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          className="border-2 border-dashed rounded-md p-6 flex flex-col items-center cursor-pointer hover:border-primary/50 transition-colors"
        >
          <UploadCloud className="h-10 w-10 text-muted-foreground mb-2" />
          <p className="text-sm font-medium">Drag and drop file here, or click to select</p>
          <p className="text-xs text-muted-foreground mt-1">Supports PDF, DOCX, and TXT (Max 10MB)</p>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="title">Document Title</Label>
          <Input
            id="title"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Enter document title"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="documentType">Document Type</Label>
          <Select value={documentType} onValueChange={setDocumentType}>
            <SelectTrigger id="documentType">
              <SelectValue placeholder="Select document type" />
            </SelectTrigger>
            <SelectContent>
              {documentTypes.map(type => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full" disabled={!title || !documentType}>
          Upload Document
        </Button>
      </CardFooter>
    </Card>
  );
}
