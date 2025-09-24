FROM ubuntu:latest
LABEL authors="ihansol"

ENTRYPOINT ["top", "-b"]