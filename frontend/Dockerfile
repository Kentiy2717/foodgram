# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
RUN npm install --global http-server
CMD cp -r build result_build

# FROM node:18

# RUN npm ci

# COPY . .
# RUN npm run build
# RUN npm install --global http-server

# CMD ["npx", "-y", "http-server", "-p", "8080", "/app/build"]
