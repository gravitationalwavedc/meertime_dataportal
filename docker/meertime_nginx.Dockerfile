FROM nginx:1.17.8
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
