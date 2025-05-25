import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authorize, refresh, revoke, AuthConfiguration } from 'react-native-app-auth';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: any;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  token: string | null;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  isLoading: true,
  user: null,
  login: async () => {},
  logout: async () => {},
  token: null,
});

// Keycloak configuration for mobile
const keycloakConfig: AuthConfiguration = {
  issuer: 'http://10.0.2.2:8080/realms/Verdict360', // Android emulator localhost
  clientId: 'Verdict360-mobile',
  redirectUrl: 'com.verdict360.mobile://auth',
  scopes: ['openid', 'profile', 'email'],
  additionalParameters: {},
  customHeaders: {},
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('auth_token');
      const storedUser = await AsyncStorage.getItem('user_info');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Error checking auth state:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async () => {
    try {
      setIsLoading(true);
      
      // Perform authorization request
      const result = await authorize(keycloakConfig);
      
      // Store tokens and user info
      await AsyncStorage.setItem('auth_token', result.accessToken);
      await AsyncStorage.setItem('refresh_token', result.refreshToken || '');
      
      // For now, create a basic user object from the token
      // In production, you'd decode the JWT or make an API call
      const userInfo = {
        name: 'Legal Professional',
        email: 'user@verdict360.org',
        role: 'attorney'
      };
      
      await AsyncStorage.setItem('user_info', JSON.stringify(userInfo));
      
      setToken(result.accessToken);
      setUser(userInfo);
      setIsAuthenticated(true);
      
    } catch (error) {
      console.error('Login failed:', error);
      Alert.alert('Login Failed', 'Unable to authenticate with Verdict360. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      
      if (refreshToken) {
        await revoke(keycloakConfig, {
          tokenToRevoke: refreshToken,
          sendClientId: true,
        });
      }
      
      // Clear stored data
      await AsyncStorage.multiRemove(['auth_token', 'refresh_token', 'user_info']);
      
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      
    } catch (error) {
      console.error('Logout error:', error);
      Alert.alert('Logout Error', 'There was an issue logging out. Please try again.');
    }
  };

  const value = {
    isAuthenticated,
    isLoading,
    user,
    login,
    logout,
    token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
