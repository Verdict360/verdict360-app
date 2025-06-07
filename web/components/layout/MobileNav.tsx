"use client"
import { useState } from "react";
import Link from "next/link";
import { Menu, X, Book, Gavel, Mic, MessageSquare, Briefcase, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

export function MobileNav() {
  const [open, setOpen] = useState(false);

  const navigationItems = [
    { href: "/legal-documents", label: "Documents", icon: Book },
    { href: "/case-law", label: "Case Law", icon: Gavel },
    { href: "/audio-recordings", label: "Recordings", icon: Mic },
    { href: "/legal-chat", label: "Legal Chat", icon: MessageSquare },
    { href: "/matters", label: "Matters", icon: Briefcase },
  ];

  return (
    <header className="sticky top-0 z-40 border-b bg-background">
      <div className="container flex h-14 items-center">
        <div className="flex items-center justify-between w-full">
          <Link href="/" className="flex items-center space-x-2">
            <span className="font-bold text-xl text-primary">Verdict360</span>
          </Link>
          
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0">
              <div className="flex flex-col h-full">
                <div className="p-4 border-b">
                  <div className="flex items-center justify-between">
                    <Link
                      href="/"
                      className="flex items-center space-x-2"
                      onClick={() => setOpen(false)}
                    >
                      <span className="font-bold text-xl text-primary">Verdict360</span>
                    </Link>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setOpen(false)}
                    >
                      <X className="h-5 w-5" />
                      <span className="sr-only">Close menu</span>
                    </Button>
                  </div>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                  {navigationItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setOpen(false)}
                        className="flex items-center py-2 px-3 rounded-md text-sm font-medium hover:bg-muted"
                      >
                        <Icon className="h-5 w-5 mr-3" />
                        {item.label}
                      </Link>
                    );
                  })}
                </nav>
                <div className="p-4 border-t">
                  <Link
                    href="/profile"
                    onClick={() => setOpen(false)}
                    className="flex items-center py-2 px-3 rounded-md text-sm font-medium hover:bg-muted"
                  >
                    <User className="h-5 w-5 mr-3" />
                    Profile
                  </Link>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
