'use client';

import { AuthProvider } from '@/lib/auth/auth-provider';

export function AuthWrapper({ children }: { children: React.ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}
