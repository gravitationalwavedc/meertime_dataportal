FROM nginx:1.17.8
COPY src/nginx/nginx.conf /etc/nginx/conf.d/default.conf
