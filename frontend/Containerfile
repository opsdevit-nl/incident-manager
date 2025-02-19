# Use Node 18 slim
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy all project files
# COPY ./package.json /app/package.json
COPY ./package.json /app/

# Ensure proper permissions
RUN chmod -R 755 /app

# Set environment to development
ENV NODE_ENV=development

# Remove previous node_modules (if any)
RUN rm -rf node_modules package-lock.json

# Install dependencies
RUN npm cache clean --force

# RUN npm init svelte my-first-svelte-app
#  RUN npm create svelte@latest /app/
# RUN yes | npx sv create --no-add-ons  /app --template minimal --no-types --no-install

RUN npm install

RUN npm install quill

RUN npm install socket.io-client

# You can also install these packages via npm (e.g., run npm install jquery moment daterangepicker)
# and then import them in your component. However, since daterangepicker expects jQuery to be globally
# available, adding the script tags to your app.html is usually simpler.
# This way, when your NavBar component initializes the daterangepicker in the onMount hook,
# the required libraries are already loaded and available globally.
# RUN npm install jquery moment daterangepicker

# Run svelte-kit sync to generate type definitions and internal files
# RUN npm run sync

# Expose port 5000 (as set in vite.config.js)
EXPOSE 5000

# Start the dev server using the local svelte-kit binary
CMD ["npm", "run", "dev"]