// Function to validate required environment variables
const validateEnv = (): void => {
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
    throw new Error(
      `Missing required environment variables: ${missingEnvVars.join(', ')}`
    );
  }
};

// Run validation
validateEnv();

// Export environment variables
export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL!,
  keycloak: {
    url: process.env.NEXT_PUBLIC_KEYCLOAK_URL!,
    realm: process.env.NEXT_PUBLIC_KEYCLOAK_REALM!,
    clientId: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID!,
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
