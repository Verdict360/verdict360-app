'use client';

import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/auth/auth-provider';
import { ShieldX } from 'lucide-react';
import Link from 'next/link';

export default function UnauthorizedPage() {
  const { logout } = useAuth();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 py-12 bg-background">
      <div className="mx-auto max-w-md text-center">
        <div className="flex justify-center mb-6">
          <div className="p-3 rounded-full bg-destructive/10">
            <ShieldX className="w-12 h-12 text-destructive" />
          </div>
        </div>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Access Denied</h1>
        <p className="mt-3 text-base text-muted-foreground">
          You don't have permission to access this page. Please contact your administrator if you believe this is a
          mistake.
        </p>
        <div className="mt-6 flex flex-col sm:flex-row justify-center gap-3">
          <Link href="/">
            <Button variant="outline">Return to Home</Button>
          </Link>
          <Button variant="default" onClick={logout}>
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}
