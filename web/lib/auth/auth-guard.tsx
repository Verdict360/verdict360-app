'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from './auth-provider';
import { Loader2 } from 'lucide-react';

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRoles?: string[];
  requiredPermissions?: string[];
}

export function AuthGuard({ children, requiredRoles = [], requiredPermissions = [] }: AuthGuardProps) {
  const { isAuthenticated, isLoading, hasRole, hasPermission, login } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      login();
      return;
    }

    // Check if the user has the required roles
    if (!isLoading && isAuthenticated) {
      const hasRequiredRoles = requiredRoles.length === 0 || requiredRoles.some(role => hasRole(role));
      const hasRequiredPermissions = 
        requiredPermissions.length === 0 || requiredPermissions.some(permission => hasPermission(permission));

      if (!hasRequiredRoles || !hasRequiredPermissions) {
        router.push('/unauthorized');
      }
    }
  }, [isLoading, isAuthenticated, hasRole, hasPermission, requiredRoles, requiredPermissions, router, login]);

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2 text-lg">Loading...</span>
      </div>
    );
  }

  return <>{children}</>;
}
