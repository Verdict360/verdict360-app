'use client';

import { Button, ButtonProps } from '@/components/ui/button';
import { useAuth } from '@/lib/auth/auth-provider';
import { Loader2 } from 'lucide-react';

interface LoginButtonProps extends ButtonProps {
  children: React.ReactNode;
}

export function LoginButton({ children, ...props }: LoginButtonProps) {
  const { login, isAuthenticated, isLoading } = useAuth();

  const handleLogin = () => {
    login();
  };

  if (isLoading) {
    return (
      <Button disabled {...props}>
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Loading...
      </Button>
    );
  }

  if (isAuthenticated) {
    return null;
  }

  return (
    <Button onClick={handleLogin} {...props}>
      {children}
    </Button>
  );
}
