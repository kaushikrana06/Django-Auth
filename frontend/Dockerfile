# ---- Build stage ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Runtime stage (no Nginx) ----
FROM node:20-alpine
WORKDIR /app

# Copy built assets
COPY --from=build /app/dist ./dist

# Install a tiny static server
RUN npm i -g serve

# Runtime env injection (creates /app/dist/env.js at container start)
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
