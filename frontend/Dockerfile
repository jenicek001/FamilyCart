# 1. Base Image: Use the official Node.js 20 image.
# Using a specific version is good for reproducibility.
FROM node:20-alpine AS base

# 2. Set Working Directory
WORKDIR /app

# 3. Install Dependencies
# Copy package.json and package-lock.json first to leverage Docker cache.
COPY package*.json ./
RUN npm install

# 4. Copy Application Code
# Copy the rest of your app's source code from your host to your image filesystem.
COPY . .

# 5. Build the Next.js Application
# This will create an optimized production build in the .next folder.
RUN npm run build

# 6. Production Stage
# Use a smaller, more secure base image for the final production image.
FROM node:20-alpine AS production

WORKDIR /app

# Copy package.json and install only production dependencies
COPY --from=base /app/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy the built application from the previous stage
COPY --from=base /app/.next ./.next
COPY --from=base /app/public ./public
COPY --from=base /app/next.config.* ./

# Create a non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose the port the app runs on
EXPOSE 3000

# Command to run the app
# `next start` starts the application in production mode.
CMD ["npm", "start"]
