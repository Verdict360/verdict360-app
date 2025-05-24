'use client';

import { useEffect } from 'react';
import { useAuth } from '@/lib/auth/auth-provider';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

export default function LoginPage() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/legal-documents');
    }
  }, [isAuthenticated, router]);

  const handleLogin = () => {
    login();
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Welcome to Verdict360</CardTitle>
          <CardDescription className="text-center">
            Sign in to access your legal workspace
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button 
            onClick={handleLogin} 
            className="w-full" 
            size="lg"
          >
            Sign in with Keycloak
          </Button>
          <p className="text-sm text-center text-muted-foreground">
            By signing in, you agree to our terms and conditions
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
