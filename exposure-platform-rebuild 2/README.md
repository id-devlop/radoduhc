
# Exposure Platform - Full Set

## Run
```bash
docker-compose up --build
# Frontend http://localhost:5173
# Backend  http://localhost:8080/docs
```

## Generate TS types from OpenAPI
```bash
cd frontend
npm run gen:api
```

## Alembic
```bash
cd backend
make makemigrations
make migrate
```
