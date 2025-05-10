# Expo Environment Setup for Verdict360 Mobile

## Environment Files

This project uses environment variables to configure different aspects of the application. The environment files are:

- `.env.development`: Used for local development
- `.env.production`: Used for production builds

## Running with Different Environments

To run the app with a specific environment:

```bash
# Development (default)
npm run start
npm run android
npm run ios

# Explicitly set development environment
npm run start:dev
npm run android:dev
npm run ios:dev

# Production environment
EXPO_ENV=production expo start
EXPO_ENV=production expo start --android
EXPO_ENV=production expo start --ios
```

## Accessing Environment Variables

Access environment variables in your code using the environment helper:

```javascript
import { ENV } from '@/utils/environment';

// Usage example
const apiUrl = ENV.API_URL;
const keycloakRealm = ENV.KEYCLOAK.REALM;
```

## Building for Production

When building for production, ensure you set the EXPO_ENV variable:

```bash
EXPO_ENV=production expo build:android
EXPO_ENV=production expo build:ios
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| API_URL | Base URL for the API | http://10.0.2.2:3001 |
| KEYCLOAK_URL | Keycloak server URL | http://10.0.2.2:8080 |
| KEYCLOAK_REALM | Keycloak realm name | Verdict360 |
| KEYCLOAK_CLIENT_ID | Keycloak client ID | Verdict360-mobile |
| MINIO_ENDPOINT | MinIO server endpoint | 10.0.2.2 |
| MINIO_PORT | MinIO server port | 9000 |
| MINIO_USE_SSL | Use SSL for MinIO | false |
| DEFAULT_CURRENCY | Default currency | ZAR |
| DEFAULT_LOCALE | Default locale | en-ZA |
