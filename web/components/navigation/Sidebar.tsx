'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  Home, 
  Upload, 
  Mic, 
  Search,
  FileText, 
  Settings, 
  User,
  Scale,
  BarChart3,
  MessageSquare
} from 'lucide-react';

const navigationItems = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: Home,
  },
  {
    title: 'Legal Documents',
    href: '/legal-documents',
    icon: FileText,
  },
  {
    title: 'Legal Search',
    href: '/legal-search',
    icon: Search,
  },
  {
    title: 'Legal Chat',
    href: '/legal-chat',
    icon: MessageSquare,
  },
  {
    title: 'Upload Document',
    href: '/upload',
    icon: Upload,
  },
  {
    title: 'Record Audio',
    href: '/record',
    icon: Mic,
  },
];

const secondaryItems = [
  {
    title: 'Settings',
    href: '/settings',
    icon: Settings,
  },
  {
    title: 'Profile',
    href: '/profile',
    icon: User,
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col border-r bg-background">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <Scale className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold text-primary">Verdict360</span>
        </Link>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 space-y-2 p-4">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon className="mr-3 h-4 w-4" />
                {item.title}
              </Link>
            );
          })}
        </div>

        {/* Secondary Navigation */}
        <div className="pt-6">
          <div className="space-y-1">
            {secondaryItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon className="mr-3 h-4 w-4" />
                  {item.title}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <div className="text-xs text-muted-foreground">
          <p>Verdict360 Legal Platform</p>
          <p>AI-Powered Legal Intelligence</p>
        </div>
      </div>
    </div>
  );
}
