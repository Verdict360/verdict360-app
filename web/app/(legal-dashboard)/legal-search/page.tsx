import { Metadata } from "next";
import LegalSearchInterface from "@/components/legal-search/LegalSearchInterface";

export const metadata: Metadata = {
  title: "Legal Search | Verdict360",
  description: "Search through legal documents using AI-powered semantic similarity",
};

export default function LegalSearchPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-primary">Legal Document Search</h1>
        <p className="text-muted-foreground mt-2">
          Search through your legal documents using AI-powered semantic similarity. 
          Find relevant case law, contracts, and legal opinions based on meaning, not just keywords.
        </p>
      </div>
      
      <LegalSearchInterface />
    </div>
  );
}
