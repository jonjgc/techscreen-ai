# Frontend Dockerfile — Next.js with hot reload for development
FROM node:20-alpine

WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./

RUN npm ci

# Copy source code
COPY . .

EXPOSE 3000

# Start Next.js development server
CMD ["npm", "run", "dev"]
