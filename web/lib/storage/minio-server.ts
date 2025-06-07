import { Client } from 'minio';

// Server-side MinIO client (Node.js only)
let minioClient: Client | null = null;

// Initialize MinIO client on server-side only
if (typeof window === 'undefined') {
  minioClient = new Client({
    endPoint: process.env.MINIO_ENDPOINT || 'localhost',
    port: parseInt(process.env.MINIO_PORT || '9000'),
    useSSL: process.env.MINIO_USE_SSL === 'true',
    accessKey: process.env.MINIO_ACCESS_KEY || 'minioadmin',
    secretKey: process.env.MINIO_SECRET_KEY || 'minioadmin',
  });
}

export { minioClient };
