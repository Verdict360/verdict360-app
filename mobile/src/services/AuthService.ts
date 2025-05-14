import { Platform } from 'react-native';
import { authorize, refresh, revoke, AuthConfiguration } from 'react-native-app-auth';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ENV } from '../utils/environment';

// Keys for AsyncStorage
const AUTH_STATE_KEY = 'auth_state';
const AUTH_CONFIG_KEY = 'auth_config';

// Keycloak configuration
const getKeycloakConfig = (): AuthConfiguration => {
  // Get base values from environment
  const keycloakUrl = ENV.KEYCLOAK.URL;
  const keycloakRealm = ENV.KEYCLOAK.REALM;
  const keycloakClientId = ENV.KEYCLOAK.CLIENT_ID;

  return {
    issuer: `${keycloakUrl}/realms/${keycloakRealm}`,
    clientId: keycloakClientId,
    redirectUrl: 'verdict360://callback',
    scopes: ['openid', 'profile', 'email', 'offline_access'],
    serviceConfiguration: {
      authorizationEndpoint: `${keycloakUrl}/realms/${keycloakRealm}/protocol/openid-connect/auth`,
      tokenEndpoint: `${keycloakUrl}/realms/${keycloakRealm}/protocol/openid-connect/token`,
      revocationEndpoint: `${keycloakUrl}/realms/${keycloakRealm}/protocol/openid-connect/logout`,
    },
  };
};

class AuthService {
  private authState: any = null;
  private authConfig: AuthConfiguration;
  private listeners: Set<() => void> = new Set();

  constructor() {
    this.authConfig = getKeycloakConfig();
    this.loadPersistedAuth();
  }

  private async loadPersistedAuth() {
    try {
      // Load saved auth state
      const authStateString = await AsyncStorage.getItem(AUTH_STATE_KEY);
      if (authStateString) {
        this.authState = JSON.parse(authStateString);
      }

      // Load saved configuration
      const authConfigString = await AsyncStorage.getItem(AUTH_CONFIG_KEY);
      if (authConfigString) {
        this.authConfig = JSON.parse(authConfigString);
      } else {
        this.authConfig = getKeycloakConfig();
        await AsyncStorage.setItem(AUTH_CONFIG_KEY, JSON.stringify(this.authConfig));
      }

      // Refresh token if needed
      if (this.authState && this.authState.refreshToken) {
        this.refreshAccessToken();
      }

      // Notify any listeners
      this.notifyListeners();
    } catch (error) {
      console.error('Failed to load auth state', error);
    }
  }

  private async persistAuthState() {
    if (this.authState) {
      await AsyncStorage.setItem(AUTH_STATE_KEY, JSON.stringify(this.authState));
    } else {
      await AsyncStorage.removeItem(AUTH_STATE_KEY);
    }
    this.notifyListeners();
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener());
  }

  public addAuthStateListener(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  public async login(): Promise<boolean> {
    try {
      const result = await authorize(this.authConfig);
      this.authState = result;
      await this.persistAuthState();
      return true;
    } catch (error) {
      console.error('Login failed', error);
      return false;
    }
  }

  public async logout(): Promise<boolean> {
    try {
      if (this.authState) {
        await revoke(this.authConfig, {
          tokenToRevoke: this.authState.accessToken,
          sendClientId: true,
        });
      }
      this.authState = null;
      await this.persistAuthState();
      return true;
    } catch (error) {
      console.error('Logout failed', error);
      return false;
    }
  }

  public async refreshAccessToken(): Promise<boolean> {
    try {
      if (!this.authState?.refreshToken) {
        return false;
      }

      const result = await refresh(this.authConfig, {
        refreshToken: this.authState.refreshToken,
      });

      this.authState = result;
      await this.persistAuthState();
      return true;
    } catch (error) {
      console.error('Token refresh failed', error);
      // If refresh fails, user needs to log in again
      this.authState = null;
      await this.persistAuthState();
      return false;
    }
  }

  public getAccessToken(): string | null {
    if (this.authState && this.authState.accessToken) {
      return this.authState.accessToken;
    }
    return null;
  }

  public isAuthenticated(): boolean {
    if (!this.authState || !this.authState.accessToken) {
      return false;
    }

    // Check if token is expired
    const expirationTime = this.authState.accessTokenExpirationDate;
    if (!expirationTime) {
      return false;
    }

    return new Date(expirationTime) > new Date();
  }

  public getUserInfo(): any {
    if (!this.authState) {
      return null;
    }

    return this.authState.tokenAdditionalParameters || {};
  }

  public hasRole(role: string): boolean {
    if (!this.authState || !this.authState.tokenAdditionalParameters) {
      return false;
    }

    const roles = this.authState.tokenAdditionalParameters.realm_access?.roles || [];
    return roles.includes(role);
  }
}

// Export singleton instance
export const authService = new AuthService();
