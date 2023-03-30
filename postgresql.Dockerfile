FROM postgres:latest

ENV POSTGRES_USER=pinchi \
    POSTGRES_PASSWORD=Pinch0000 \
    POSTGRES_DB=song_stars

COPY /data/init.sql /docker-entrypoint-initdb.d/
