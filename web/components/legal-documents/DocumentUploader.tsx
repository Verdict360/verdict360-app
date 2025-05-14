'use client';

import { useState } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FileUploader } from './FileUploader';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/lib/auth/auth-provider';

const documentTypes = [
  { value: 'judgment', label: 'Court Judgment' },
  { value: 'statute', label: 'Statute or Act' },
  { value: 'contract', label: 'Legal Contract' },
  { value: 'pleading', label: 'Pleading Document' },
  { value: 'opinion', label: 'Legal Opinion' },
  { value: 'article', label: 'Legal Article' },
  { value: 'other', label: 'Other Legal Document' },
];

const jurisdictions = [
  { value: 'south_africa', label: 'South Africa' },
  { value: 'international', label: 'International' },
];

interface DocumentUploaderProps {
  matterId?: string;
  onDocumentUploaded?: (documentData: any) => void;
}

export function DocumentUploader({ matterId, onDocumentUploaded }: DocumentUploaderProps) {
  const { user } = useAuth();
  
  const [title, setTitle] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [jurisdiction, setJurisdiction] = useState('south_africa');
  const [description, setDescription] = useState('');
  const [uploadedFile, setUploadedFile] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  const handleFileUploaded = (fileInfo: { name: string; size: number; path: string }) => {
    setUploadedFile(fileInfo);
  };

  const handleSubmit = async () => {
    if (!title || !documentType || !uploadedFile || !user) return;
    
    setSubmitting(true);
    
    try {
      // Create document metadata
      const documentData = {
        title,
        documentType,
        jurisdiction,
        description,
        storagePath: uploadedFile.path,
        fileName: uploadedFile.name,
        fileSize: uploadedFile.size,
        matterId: matterId || undefined,
        createdBy: user.sub,
        createdAt: new Date().toISOString(),
      };
      
      // Here you would typically send this to your API
      // For now, we'll simulate a successful submission
      setTimeout(() => {
        setSubmitting(false);
        setIsComplete(true);
        
        if (onDocumentUploaded) {
          onDocumentUploaded(documentData);
        }
        
        // Reset form after 2 seconds
        setTimeout(() => {
          setTitle('');
          setDocumentType('');
          setJurisdiction('south_africa');
          setDescription('');
          setUploadedFile(null);
          setIsComplete(false);
        }, 2000);
      }, 1000);
    } catch (error) {
      console.error('Error submitting document metadata', error);
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-primary">Upload Legal Document</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="title">Document Title</Label>
          <Input
            id="title"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Enter document title"
            disabled={submitting || isComplete}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="documentType">Document Type</Label>
          <Select 
            value={documentType} 
            onValueChange={setDocumentType}
            disabled={submitting || isComplete}
          >
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
        
        <div className="space-y-2">
          <Label htmlFor="jurisdiction">Jurisdiction</Label>
          <Select 
            value={jurisdiction} 
            onValueChange={setJurisdiction}
            disabled={submitting || isComplete}
          >
            <SelectTrigger id="jurisdiction">
              <SelectValue placeholder="Select jurisdiction" />
            </SelectTrigger>
            <SelectContent>
              {jurisdictions.map(j => (
                <SelectItem key={j.value} value={j.value}>
                  {j.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="description">Description (Optional)</Label>
          <Textarea
            id="description"
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Enter document description"
            rows={3}
            disabled={submitting || isComplete}
          />
        </div>
        
        <div className="space-y-2">
          <Label>Document File</Label>
          <FileUploader 
            onUploadComplete={handleFileUploaded}
            allowedFileTypes={['.pdf', '.docx', '.doc', '.txt']}
            maxSize={20 * 1024 * 1024}
            matterId={matterId}
          />
        </div>
      </CardContent>
      <CardFooter>
        <Button 
          className="w-full" 
          onClick={handleSubmit}
          disabled={!title || !documentType || !uploadedFile || submitting || isComplete}
        >
          {isComplete ? 'Document Saved!' : submitting ? 'Saving...' : 'Save Document'}
        </Button>
      </CardFooter>
    </Card>
  );
}
