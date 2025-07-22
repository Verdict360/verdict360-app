import Keycloak from 'keycloak-js';
import { env } from '$env/dynamic/public';

export interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  roles: string[];
  law_firm?: string;
  practice_areas?: string[];
}

class AuthService {
  private keycloak: Keycloak | null = null;
  private initialized = false;

  async init(): Promise<void> {
    if (this.initialized || typeof window === 'undefined') return;

    const keycloakConfig = {
      url: env.VITE_KEYCLOAK_URL || 'http://localhost:8080',
      realm: env.VITE_KEYCLOAK_REALM || 'Verdict360',
      clientId: env.VITE_KEYCLOAK_CLIENT_ID || 'legal-chatbot-web',
    };

    this.keycloak = new Keycloak(keycloakConfig);

    try {
      const authenticated = await this.keycloak.init({
        onLoad: 'check-sso',
        silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
        checkLoginIframe: false,
      });

      this.initialized = true;
      
      if (authenticated) {
        this.setupTokenRefresh();
      }
    } catch (error) {
      console.error('Keycloak initialization failed:', error);
      this.initialized = false;
    }
  }

  async login(): Promise<void> {
    if (!this.keycloak) throw new Error('Auth service not initialized');
    
    await this.keycloak.login({
      redirectUri: window.location.origin + '/dashboard',
    });
  }

  async logout(): Promise<void> {
    if (!this.keycloak) throw new Error('Auth service not initialized');
    
    await this.keycloak.logout({
      redirectUri: window.location.origin,
    });
  }

  isAuthenticated(): boolean {
    return this.keycloak?.authenticated || false;
  }

  getUser(): User | null {
    if (!this.keycloak?.tokenParsed) return null;

    const token = this.keycloak.tokenParsed;
    
    return {
      id: token.sub || '',
      username: token.preferred_username || '',
      email: token.email || '',
      firstName: token.given_name,
      lastName: token.family_name,
      roles: token.realm_access?.roles || [],
      law_firm: token.law_firm,
      practice_areas: token.practice_areas,
    };
  }

  getToken(): string | null {
    return this.keycloak?.token || null;
  }

  hasRole(role: string): boolean {
    const user = this.getUser();
    return user?.roles.includes(role) || false;
  }

  isLawyer(): boolean {
    return this.hasRole('lawyer') || this.hasRole('legal-professional');
  }

  isAdmin(): boolean {
    return this.hasRole('admin') || this.hasRole('legal-admin');
  }

  private setupTokenRefresh(): void {
    if (!this.keycloak) return;

    // Refresh token when it's about to expire
    setInterval(() => {
      if (this.keycloak?.isTokenExpired(30)) {
        this.keycloak.updateToken(30).catch((error) => {
          console.error('Token refresh failed:', error);
          this.logout();
        });
      }
    }, 10000); // Check every 10 seconds
  }

  // Add authorization header to fetch requests
  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}

export const authService = new AuthService();