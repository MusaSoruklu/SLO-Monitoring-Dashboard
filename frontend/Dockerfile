# Stage 1: Build the Angular application

# Use an official Node.js runtime as a parent image with Node.js 18.x
FROM node:18-alpine AS build

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install the project dependencies
RUN npm install

# Install Angular CLI globally to avoid permission issues
RUN npm install -g @angular/cli

# Copy the rest of the application files
COPY . .

# Build the Angular application in production mode
RUN ng build --configuration production

# Stage 2: Serve the Angular application using Nginx
FROM nginx:alpine

# Copy the built Angular application from the build stage
COPY --from=build /app/dist/slo-monitoring-dashboard-frontend /usr/share/nginx/html

# Copy the custom Nginx configuration
COPY ../nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
