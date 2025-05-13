import { Metadata } from "next";
import { DocumentUploader } from "@/components/legal-documents/DocumentUploader";
import { Button } from "@/components/ui/button";
import { PlusCircle, Filter } from "lucide-react";

export const metadata: Metadata = {
  title: "Legal Documents | Verdict360",
  description: "Manage your legal documents with AI-powered insights",
};

export default function LegalDocumentsPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-primary">Legal Documents</h1>
          <p className="text-muted-foreground">
            Upload, manage and analyze your legal documents
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button size="sm">
            <PlusCircle className="h-4 w-4 mr-2" />
            Upload Document
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          {/* Document list will go here */}
          <div className="rounded-lg border bg-card p-6 h-[600px]">
            <p className="text-center text-muted-foreground">
              Your legal documents will appear here
            </p>
          </div>
        </div>
        <div>
          <DocumentUploader />
        </div>
      </div>
    </div>
  );
}
