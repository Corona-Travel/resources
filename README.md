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

TODO:
-----
- places: move to new db function
- places: fix patch with position
- quiz: add pos
- quiz: add examples to mongo-init.js (should be 5 of each entity)
- quiz: add examples to pydantic model (in types)
