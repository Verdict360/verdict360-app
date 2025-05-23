// Function to validate required environment variables
const validateEnv = (): void => {
  // Skip validation during server-side rendering build time
  if (typeof window === 'undefined' && process.env.NODE_ENV === 'production') {
    return;
  }
  
  const requiredEnvVars = [
    'NEXT_PUBLIC_API_URL',
    'NEXT_PUBLIC_KEYCLOAK_URL',
    'NEXT_PUBLIC_KEYCLOAK_REALM',
    'NEXT_PUBLIC_KEYCLOAK_CLIENT_ID'
  ];
  
  const missingEnvVars = requiredEnvVars.filter(
    (envVar) => !process.env[envVar]
  );
  
  if (missingEnvVars.length > 0) {
    console.warn(
      `Missing required environment variables: ${missingEnvVars.join(', ')}`
    );
    // Don't throw in development to prevent hydration issues
    if (process.env.NODE_ENV === 'production') {
      throw new Error(
        `Missing required environment variables: ${missingEnvVars.join(', ')}`
      );
    }
  }
};

// Only run validation if we're not in build time
if (typeof window !== 'undefined' || process.env.NODE_ENV !== 'production') {
  validateEnv();
}

// Export environment variables with fallbacks for development
export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001',
  keycloak: {
    url: process.env.NEXT_PUBLIC_KEYCLOAK_URL || 'http://localhost:8080',
    realm: process.env.NEXT_PUBLIC_KEYCLOAK_REALM || 'Verdict360',
    clientId: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID || 'Verdict360-web',
  },
  minio: {
    endpoint: process.env.NEXT_PUBLIC_MINIO_ENDPOINT || 'localhost',
    port: parseInt(process.env.NEXT_PUBLIC_MINIO_PORT || '9000'),
    useSSL: process.env.NEXT_PUBLIC_MINIO_USE_SSL === 'true',
    accessKey: process.env.NEXT_PUBLIC_MINIO_ACCESS_KEY || 'minioadmin',
    secretKey: process.env.NEXT_PUBLIC_MINIO_SECRET_KEY || 'minioadmin',
    buckets: {
      documents: process.env.NEXT_PUBLIC_MINIO_BUCKET_DOCUMENTS || 'legal-documents',
      recordings: process.env.NEXT_PUBLIC_MINIO_BUCKET_RECORDINGS || 'legal-recordings',
      transcriptions: process.env.NEXT_PUBLIC_MINIO_BUCKET_TRANSCRIPTIONS || 'legal-transcriptions',
    }
  },
  defaultCurrency: process.env.NEXT_PUBLIC_DEFAULT_CURRENCY || 'ZAR',
  defaultLocale: process.env.NEXT_PUBLIC_DEFAULT_LOCALE || 'en-ZA',
};
