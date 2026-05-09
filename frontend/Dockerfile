# Stage 1: Build React/Vite App with Node.js
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy the rest of the frontend files
COPY . .

# Build the production bundle
RUN npm run build

# Stage 2: Serve built assets with Nginx
FROM nginx:alpine

# Copy static assets from build stage to nginx html folder
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for serving the app
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
