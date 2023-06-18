# Build the react app to generate a clean production build
FROM node:18 as build

WORKDIR /app

RUN npm install -g pnpm

COPY ./frontend/package.json ./frontend/pnpm-lock.yaml /app/

RUN pnpm install

COPY ./frontend /app/

RUN pnpm run relay
RUN pnpm run build


# Run the app
FROM nginx:1.17.8

COPY --from=build /app/dist /react_app/
ADD ./nginx/react_app.conf /etc/nginx/conf.d/nginx.conf

EXPOSE 3000
