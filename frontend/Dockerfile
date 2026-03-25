# =============================================================================
# Zonara Frontend — Dockerfile
# Multi-stage build: Node 20 build + Nginx serve
# @author  Azhar Maulana
# @date    25 Maret 2026
# =============================================================================

# Stage 1: Development (used by docker-compose for dev server)
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
COPY . .

# Expose Vite dev port
EXPOSE 5173

# Start Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
