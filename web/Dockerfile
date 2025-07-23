FROM node:18-alpine as development

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose the development port
EXPOSE 5173

# Set environment variables for development
ENV NODE_ENV=development
ENV VITE_API_URL=http://localhost:8000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production runtime
FROM node:18-alpine as production

WORKDIR /app

# Copy package files and install production dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application
COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "build"]