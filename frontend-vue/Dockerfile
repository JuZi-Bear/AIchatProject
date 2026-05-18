FROM node:20-alpine AS build

WORKDIR /app

ARG VITE_API_MODE=java
ARG VITE_JAVA_API_BASE_URL=http://localhost:8088/api
ARG VITE_PYTHON_API_BASE_URL=http://localhost:8001

ENV VITE_API_MODE=$VITE_API_MODE
ENV VITE_JAVA_API_BASE_URL=$VITE_JAVA_API_BASE_URL
ENV VITE_PYTHON_API_BASE_URL=$VITE_PYTHON_API_BASE_URL

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
