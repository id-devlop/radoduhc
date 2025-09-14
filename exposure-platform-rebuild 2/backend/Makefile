
.PHONY: makemigrations migrate
makemigrations:
	autorevision=$$(date +%s) && alembic revision --autogenerate -m "auto-$$autorevision"
migrate:
	alembic upgrade head
