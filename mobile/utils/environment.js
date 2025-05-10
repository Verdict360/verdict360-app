import Constants from 'expo-constants';

import { Platform } from 'react-native';

import {
  API_URL,
  DEFAULT_CURRENCY,
  DEFAULT_LOCALE,
  KEYCLOAK_CLIENT_ID,
  KEYCLOAK_REALM,
  KEYCLOAK_URL,
  MINIO_ENDPOINT,
  MINIO_PORT,
  MINIO_USE_SSL,
} from '@env';

// Get a variable from extra or @env fallback

const getVariable = (key, fallback) => {
  // In development, use .env variables via @env

  const envValue = {
    apiUrl: API_URL,
    keycloakUrl: KEYCLOAK_URL,
    keycloakRealm: KEYCLOAK_REALM,
    keycloakClientId: KEYCLOAK_CLIENT_ID,
    minioEndpoint: MINIO_ENDPOINT,
    minioPort: MINIO_PORT,
    minioUseSsl: MINIO_USE_SSL,
    defaultCurrency: DEFAULT_CURRENCY,
    defaultLocale: DEFAULT_LOCALE,
  }[key];

  // In production builds, use Constants.expoConfig.extra

  const extraValue = Constants.expoConfig?.extra?.[key];

  // Return the environment value, or extra value, or fallback

  return envValue || extraValue || fallback;
};

// Default development values

const DEV_DEFAULTS = {
  apiUrl: 'http://10.0.2.2:3001',
  keycloakUrl: 'http://10.0.2.2:8080',
  keycloakRealm: 'Verdict360',
  keycloakClientId: 'Verdict360-mobile',
  minioEndpoint: '10.0.2.2',
  minioPort: '9000',
  minioUseSsl: 'false',
  defaultCurrency: 'ZAR',
  defaultLocale: 'en-ZA',
};

// Export environment configuration

export const ENV = {
  API_URL: getVariable('apiUrl', DEV_DEFAULTS.apiUrl),

  KEYCLOAK: {
    URL: getVariable('keycloakUrl', DEV_DEFAULTS.keycloakUrl),
    REALM: getVariable('keycloakRealm', DEV_DEFAULTS.keycloakRealm),
    CLIENT_ID: getVariable('keycloakClientId', DEV_DEFAULTS.keycloakClientId),
  },

  MINIO: {
    ENDPOINT: getVariable('minioEndpoint', DEV_DEFAULTS.minioEndpoint),
    PORT: getVariable('minioPort', DEV_DEFAULTS.minioPort),
    USE_SSL: getVariable('minioUseSsl', DEV_DEFAULTS.minioUseSsl) === 'true',
  },

  DEFAULT_CURRENCY: getVariable('defaultCurrency', DEV_DEFAULTS.defaultCurrency),
  DEFAULT_LOCALE: getVariable('defaultLocale', DEV_DEFAULTS.defaultLocale),
  IS_DEV: DEV,
};

// Helper to handle different URLs for emulator vs physical device
export const getApiUrl = () => {
  if (Platform.OS === 'android' && ENV.IS_DEV) {
    // Android emulators need special handling for localhost
    return ENV.API_URL.replace('localhost', '10.0.2.2');
  }

  return ENV.API_URL;
};
