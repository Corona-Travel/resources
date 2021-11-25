resources
=========

Example:
--------

to create facts:

to build:
```sh
docker build --build-arg SRC_PATH="./src/facts" --build-arg APP_PATH="./facts" --build-arg ASGI_APP="facts.app:app" -t cts-facts:latest .
```
to run:
```sh
docker run -dt --name facts-test -p 1234:1234 cts-facts:latest
docker logs -f facts-test
```
