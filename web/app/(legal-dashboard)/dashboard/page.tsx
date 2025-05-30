import { Metadata } from "next";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, Mic, Search, FileText, BarChart3, Plus, ArrowRight } from "lucide-react";

export const metadata: Metadata = {
  title: "Dashboard | Verdict360",
  description: "AI-powered legal intelligence platform dashboard",
};

const quickActions = [
  {
    title: "Upload Document",
    description: "Upload and process legal documents with AI analysis",
    href: "/upload",
    icon: Upload,
    color: "bg-blue-500",
  },
  {
    title: "Legal Search",
    description: "Search through documents using semantic similarity",
    href: "/legal-search",
    icon: Search,
    color: "bg-green-500",
  },
  {
    title: "Record Audio",
    description: "Record and transcribe legal proceedings or notes",
    href: "/record",
    icon: Mic,
    color: "bg-purple-500",
  },
  {
    title: "View Documents",
    description: "Browse and manage your legal document library",
    href: "/documents",
    icon: FileText,
    color: "bg-orange-500",
  },
];

const recentActivity = [
  {
    action: "Document uploaded",
    item: "Employment Contract - ABC Corp",
    time: "2 hours ago",
    type: "upload"
  },
  {
    action: "Search performed",
    item: "constitutional rights property",
    time: "4 hours ago",
    type: "search"
  },
  {
    action: "Audio transcribed",
    item: "Client meeting recording",
    time: "1 day ago",
    type: "audio"
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-primary">Welcome to Verdict360</h1>
        <p className="text-muted-foreground mt-2">
          Your AI-powered legal intelligence platform for South African legal professionals
        </p>
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <Link key={action.href} href={action.href}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                <CardHeader className="pb-3">
                  <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mb-3`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-lg">{action.title}</CardTitle>
                  <CardDescription className="text-sm">
                    {action.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <Button variant="ghost" size="sm" className="w-full justify-between">
                    Get Started
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      {/* Dashboard Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Documents Processed
            </CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">247</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Citations Detected
            </CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">1,429</div>
            <p className="text-xs text-muted-foreground">
              South African case law
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Search Queries
            </CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">89</div>
            <p className="text-xs text-muted-foreground">
              This week
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity & Quick Search */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Your latest interactions with the platform
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">{activity.item}</p>
                  </div>
                  <p className="text-xs text-muted-foreground">{activity.time}</p>
                </div>
              ))}
            </div>
            <Button variant="ghost" className="w-full mt-4" asChild>
              <Link href="/analytics">
                View All Activity
                <ArrowRight className="h-4 w-4 ml-2" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Quick Search */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Legal Search</CardTitle>
            <CardDescription>
              Start searching your legal documents instantly
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <h4 className="text-sm font-medium">Popular Search Terms:</h4>
              <div className="flex flex-wrap gap-2">
                {[
                  "constitutional rights",
                  "employment law",
                  "property disputes",
                  "contract breach",
                  "labour relations"
                ].map((term) => (
                  <Button key={term} variant="outline" size="sm" asChild>
                    <Link href={`/legal-search?q=${encodeURIComponent(term)}`}>
                      {term}
                    </Link>
                  </Button>
                ))}
              </div>
            </div>
            
            <Button className="w-full" asChild>
              <Link href="/legal-search">
                <Search className="h-4 w-4 mr-2" />
                Open Legal Search
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Platform Features Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Features</CardTitle>
          <CardDescription>
            Explore what Verdict360 can do for your legal practice
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium">Document Intelligence</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• South African citation detection</li>
                <li>• Legal term extraction</li>
                <li>• Document structure analysis</li>
                <li>• Semantic search capabilities</li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium">Audio Processing</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• High-quality transcription</li>
                <li>• Speaker identification</li>
                <li>• Legal terminology recognition</li>
                <li>• Secure cloud storage</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
