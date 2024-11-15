# Use Node.js as the base image
FROM node:20

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json for caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy all project files
COPY . .

# Expose the Angular dev server port
EXPOSE 4200

# Run Angular in watch mode
CMD ["npm", "run", "start"]