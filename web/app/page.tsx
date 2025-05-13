// web/app/page.tsx (updated)
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Gavel, BookOpen, Mic, MessageSquare, Scale } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <Container className="flex items-center justify-between h-16">
          <div className="font-bold text-2xl text-primary">Verdict360</div>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/features" className="text-muted-foreground hover:text-foreground">Features</Link>
            <Link href="/pricing" className="text-muted-foreground hover:text-foreground">Pricing</Link>
            <Link href="/about" className="text-muted-foreground hover:text-foreground">About</Link>
          </nav>
          <div className="flex items-center gap-2">
            <Link href="/login">
              <Button variant="outline">Log in</Button>
            </Link>
            <Link href="/signup">
              <Button>Sign up</Button>
            </Link>
          </div>
        </Container>
      </header>

      <main className="flex-1">
        <section className="py-20 md:py-32">
          <Container>
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
                South African Legal Intelligence Platform
              </h1>
              <p className="text-xl md:text-2xl text-muted-foreground mb-8">
                Streamline your legal work with AI-powered document analysis, case law research, and legal citations.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg">
                  Get Started
                </Button>
                <Button size="lg" variant="outline">
                  Book a Demo
                </Button>
              </div>
            </div>
          </Container>
        </section>

        <section className="py-20 bg-muted/30">
          <Container>
            <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-card p-6 rounded-lg border flex flex-col items-center text-center">
                <div className="bg-primary/10 p-3 rounded-full mb-4">
                  <BookOpen className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-medium mb-2">Legal Document Intelligence</h3>
                <p className="text-muted-foreground">Extract insights from contracts, judgments, and legal documents with AI assistance.</p>
              </div>
              <div className="bg-card p-6 rounded-lg border flex flex-col items-center text-center">
                <div className="bg-primary/10 p-3 rounded-full mb-4">
                  <Gavel className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-medium mb-2">South African Case Law</h3>
                <p className="text-muted-foreground">Access and analyze South African legal precedents with proper citation tracking.</p>
              </div>
              <div className="bg-card p-6 rounded-lg border flex flex-col items-center text-center">
                <div className="bg-primary/10 p-3 rounded-full mb-4">
                  <Mic className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-medium mb-2">Audio Recording & Transcription</h3>
                <p className="text-muted-foreground">Record client meetings and court proceedings with automatic transcription.</p>
              </div>
            </div>
          </Container>
        </section>
      </main>

      <footer className="border-t py-12">
        <Container>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-medium mb-4">Product</h3>
              <ul className="space-y-2">
                <li><Link href="/features" className="text-muted-foreground hover:text-foreground">Features</Link></li>
                <li><Link href="/pricing" className="text-muted-foreground hover:text-foreground">Pricing</Link></li>
                <li><Link href="/roadmap" className="text-muted-foreground hover:text-foreground">Roadmap</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium mb-4">Resources</h3>
              <ul className="space-y-2">
                <li><Link href="/documentation" className="text-muted-foreground hover:text-foreground">Documentation</Link></li>
                <li><Link href="/guides" className="text-muted-foreground hover:text-foreground">Guides</Link></li>
                <li><Link href="/api" className="text-muted-foreground hover:text-foreground">API</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium mb-4">Company</h3>
              <ul className="space-y-2">
                <li><Link href="/about" className="text-muted-foreground hover:text-foreground">About</Link></li>
                <li><Link href="/blog" className="text-muted-foreground hover:text-foreground">Blog</Link></li>
                <li><Link href="/contact" className="text-muted-foreground hover:text-foreground">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium mb-4">Legal</h3>
              <ul className="space-y-2">
                <li><Link href="/terms" className="text-muted-foreground hover:text-foreground">Terms</Link></li>
                <li><Link href="/privacy" className="text-muted-foreground hover:text-foreground">Privacy</Link></li>
                <li><Link href="/compliance" className="text-muted-foreground hover:text-foreground">POPIA Compliance</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t text-center text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} Verdict360. All rights reserved.</p>
          </div>
        </Container>
      </footer>
    </div>
  );
}
