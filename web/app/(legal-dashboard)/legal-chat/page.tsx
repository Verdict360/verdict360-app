import { Metadata } from "next";
import LegalChatInterface from "@/components/legal-chat/LegalChatInterface";

export const metadata: Metadata = {
  title: "Legal Assistant | Verdict360",
  description: "AI-powered legal assistant with South African legal expertise for research and analysis",
};

export default function LegalChatPage() {
  return (
    <div className="container mx-auto py-6 h-full">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-primary">Legal Assistant</h1>
        <p className="text-muted-foreground mt-2">
          Get AI-powered legal assistance with South African legal expertise. 
          Ask questions about case law, statutes, legal procedures, and get responses with proper citations.
        </p>
      </div>
      
      <LegalChatInterface />
    </div>
  );
}