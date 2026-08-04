FROM node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL=http://localhost:18086
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 5173

HEALTHCHECK --interval=5s --timeout=3s --retries=20 \
  CMD wget -q -O /dev/null http://127.0.0.1:5173/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
