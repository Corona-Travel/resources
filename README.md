resources
=========

Development:
------------

During development, it may be beneficial to run current version of service underdevelopment.
To do so, run the following:
```sh
curl -O https://raw.githubusercontent.com/Corona-Travel/deploy/main/mongo-init.js
docker compose down && docker compose rm && docker compose build && docker compose up --build --force-recreate -d && docker compose logs -f
```
to restart a resource-service, you can run one of the following:
```sh
docker compose up -d --no-deps --build facts && docker compose logs -f
docker compose up -d --no-deps --build media && docker compose logs -f
docker compose up -d --no-deps --build places && docker compose logs -f
docker compose up -d --no-deps --build quizzes && docker compose logs -f
```

or, for older docker-compose versions, run the following
```sh
curl -O https://raw.githubusercontent.com/Corona-Travel/deploy/main/mongo-init.js
docker-compose down && docker-compose rm && docker-compose build && docker-compose up --build --force-recreate -d && docker-compose logs -f
```
to restart a resource-service, you can run one of the following in old style:
```sh
docker-compose up -d --no-deps --build facts && docker-compose logs -f
docker-compose up -d --no-deps --build media && docker-compose logs -f
docker-compose up -d --no-deps --build places && docker-compose logs -f
docker-compose up -d --no-deps --build quizzes && docker-compose logs -f
```
