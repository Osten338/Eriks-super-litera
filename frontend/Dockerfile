FROM node:20-alpine AS build
WORKDIR /app
COPY package.json /app/package.json
RUN npm install --no-audit --no-fund || yarn install --frozen-lockfile || true
COPY . /app
RUN npm run build || yarn build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


