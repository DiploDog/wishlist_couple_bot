.PHONY:	help

help:
		@echo ""
		@echo "Usage: make <target>"
		@echo ""
		@echo "Targets:"
		@echo "-----------"
		@echo "  help 			- Show this help message"
		@echo "  run 			- Run the application in production mode"
		@echo "  lint 			- Run linting"
		@echo "  lint-fix 		- Run linting with PEP fixes"
		@echo "  test 			- [Not yet implemented] Run tests"
		@echo "  build 			- Build the application"
		@echo "  migrate		- Run database migrations"
		@echo "-----------"

run-dev-infra:
		docker compose down && docker compose -f docker-compose.dev.yaml up -d

run-local:
		DYNACONF_ENV=development .venv/bin/python3.12 main.py

run:
		DYNACONF_ENV=development production docker compose up -d

lint: 
		.venv/bin/ruff check

lint-fix:
		.venv/bin/ruff check --fix

firstrun-prepare:
		docker compose up -d postgres redis
		docker compose run --rm migrate python -m alembic revision --autogenerate -m 'Initial revision'
		docker compose run --rm migrate python -m alembic upgrade head

migrate:
		docker compose run --rm migrate python -m alembic revision --autogenerate -m '$(MSG)'
		docker compose run --rm migrate python -m alembic upgrade head
	
stop:
		docker compose down

dev:
		export DYNACONF_ENV=development

prod:
		export DYNACONF_ENV=production

venv:
		source .venv/bin/activate