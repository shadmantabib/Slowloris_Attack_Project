FROM debian:bullseye

RUN apt-get update && \
    apt-get install -y apache2 apache2-utils && \
    a2dismod mpm_event && \
    a2enmod mpm_prefork && \
    a2dismod reqtimeout && \
    echo "ServerName localhost" >> /etc/apache2/apache2.conf

EXPOSE 80

CMD ["apachectl", "-D", "FOREGROUND"] 