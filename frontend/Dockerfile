# Stage 1: Build the Angular application
FROM node:18-alpine AS build

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install the project dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Build the Angular application in production mode
RUN npm run build  # 'npm run build --prod' is deprecated in newer Angular versions

# Stage 2: Serve the Angular application using Nginx
FROM nginx:alpine

# Remove the default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy the built Angular application from the build stage
COPY --from=build /app/dist/slo-monitoring-dashboard-frontend /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
