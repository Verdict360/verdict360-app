import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/AuthService';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => Promise<boolean>;
  logout: () => Promise<boolean>;
  user: any;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  isLoading: true,
  login: async () => false,
  logout: async () => false,
  user: null,
  hasRole: () => false,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(authService.getUserInfo());

  useEffect(() => {
    const unsubscribe = authService.addAuthStateListener(() => {
      setIsAuthenticated(authService.isAuthenticated());
      setUser(authService.getUserInfo());
      setIsLoading(false);
    });

    // Initial check
    setIsAuthenticated(authService.isAuthenticated());
    setUser(authService.getUserInfo());
    setIsLoading(false);

    return unsubscribe;
  }, []);

  const login = async () => {
    const result = await authService.login();
    return result;
  };

  const logout = async () => {
    const result = await authService.logout();
    return result;
  };

  const hasRole = (role: string) => {
    return authService.hasRole(role);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        login,
        logout,
        user,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
