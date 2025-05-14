'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Keycloak from 'keycloak-js';
import { env } from '@/lib/env';

interface AuthContextType {
  keycloak: Keycloak | null;
  initialized: boolean;
  isAuthenticated: boolean;
  token: string | undefined;
  user: any;
  login: () => void;
  logout: () => void;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  keycloak: null,
  initialized: false,
  isAuthenticated: false,
  token: undefined,
  user: null,
  login: () => {},
  logout: () => {},
  hasRole: () => false,
  hasPermission: () => false,
  isLoading: true,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [keycloak, setKeycloak] = useState<Keycloak | null>(null);
  const [initialized, setInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    // Initialize Keycloak
    const initKeycloak = async () => {
      try {
        const keycloakInstance = new Keycloak({
          url: env.keycloak.url,
          realm: env.keycloak.realm,
          clientId: env.keycloak.clientId,
        });

        const authenticated = await keycloakInstance.init({
          onLoad: 'check-sso',
          silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
          pkceMethod: 'S256',
        });

        setKeycloak(keycloakInstance);
        setInitialized(true);

        if (authenticated) {
          // Set up token refresh
          setInterval(() => {
            keycloakInstance
              .updateToken(70)
              .then((refreshed) => {
                if (refreshed) {
                  console.log('Token refreshed');
                }
              })
              .catch(() => {
                console.error('Failed to refresh token');
                keycloakInstance.logout();
              });
          }, 60000);

          // Fetch user info
          try {
            const userProfile = await keycloakInstance.loadUserProfile();
            setUser({
              ...userProfile,
              roles: keycloakInstance.realmAccess?.roles || [],
            });
          } catch (error) {
            console.error('Failed to load user profile', error);
          }
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Failed to initialize Keycloak', error);
        setIsLoading(false);
        setInitialized(true);
      }
    };

    initKeycloak();

    // Cleanup
    return () => {
      // Clear interval if needed
    };
  }, []);

  const login = () => {
    if (keycloak) {
      keycloak.login();
    }
  };

  const logout = () => {
    if (keycloak) {
      keycloak.logout({ redirectUri: window.location.origin });
    }
  };

  const hasRole = (role: string): boolean => {
    return keycloak?.hasRealmRole(role) || false;
  };

  const hasPermission = (permission: string): boolean => {
    if (!keycloak?.resourceAccess) {
      return false;
    }

    // Check if the permission exists in any client
    return Object.values(keycloak.resourceAccess).some((client: any) => {
      return client.roles?.includes(permission) || false;
    });
  };

  const value = {
    keycloak,
    initialized,
    isAuthenticated: !!keycloak?.authenticated,
    token: keycloak?.token,
    user,
    login,
    logout,
    hasRole,
    hasPermission,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
