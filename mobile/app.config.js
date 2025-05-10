import { config } from 'dotenv';

// Load the appropriate .env file based on EXPO_ENV
const envPath = process.env.EXPO_ENV === 'production' 
  ? '.env.production' 
  : '.env.development';

// Load environment variables from the appropriate file
config({ path: envPath });

export default {
  name: "Verdict360 Mobile",
  slug: "verdict360-mobile",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  splash: {
    image: "./assets/splash.png",
    resizeMode: "contain",
    backgroundColor: "#4F46E5"
  },
  updates: {
    fallbackToCacheTimeout: 0
  },
  assetBundlePatterns: [
    "**/*"
  ],
  ios: {
    supportsTablet: true,
    bundleIdentifier: "com.verdict360.mobile"
  },
  android: {
    adaptiveIcon: {
      foregroundImage: "./assets/adaptive-icon.png",
      backgroundColor: "#4F46E5"
    },
    package: "com.verdict360.mobile"
  },
  web: {
    favicon: "./assets/favicon.png"
  },
  extra: {
    apiUrl: process.env.API_URL,
    keycloakUrl: process.env.KEYCLOAK_URL,
    keycloakRealm: process.env.KEYCLOAK_REALM,
    keycloakClientId: process.env.KEYCLOAK_CLIENT_ID,
    minioEndpoint: process.env.MINIO_ENDPOINT,
    minioPort: process.env.MINIO_PORT,
    minioUseSsl: process.env.MINIO_USE_SSL === 'true',
    defaultCurrency: process.env.DEFAULT_CURRENCY || 'ZAR',
    defaultLocale: process.env.DEFAULT_LOCALE || 'en-ZA',
    // Include a variable that specifies which environment we're in
    environment: process.env.EXPO_ENV || 'development'
  }
};
