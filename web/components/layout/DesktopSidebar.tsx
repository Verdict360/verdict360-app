import Link from "next/link";
import { Book, Gavel, Mic, MessageSquare, Briefcase, Settings, Search } from "lucide-react";
import { Input } from "@/components/ui/input";

export function DesktopSidebar() {
  const navigationItems = [
    { href: "/legal-documents", label: "Documents", icon: Book },
    { href: "/case-law", label: "Case Law", icon: Gavel },
    { href: "/audio-recordings", label: "Recordings", icon: Mic },
    { href: "/legal-search", label: "Legal Search", icon: Search },
    { href: "/matters", label: "Matters", icon: Briefcase },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-6 flex items-center justify-center border-b">
        <Link href="/" className="flex items-center space-x-2">
          <span className="font-bold text-xl text-primary">Verdict360</span>
        </Link>
      </div>

      <div className="px-4 py-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search..." className="pl-8" />
        </div>
      </div>

      <nav className="flex-1 px-2 py-4">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-muted group"
              >
                <Icon className="mr-3 h-5 w-5 text-muted-foreground group-hover:text-foreground" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>

      <div className="px-4 py-4 border-t">
        <Link
          href="/settings"
          className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-muted group"
        >
          <Settings className="mr-3 h-5 w-5 text-muted-foreground group-hover:text-foreground" />
          Settings
        </Link>
      </div>
    </div>
  );
}
