.PHONY:	help

help:
		@echo ""
		@echo "Usage: make <target>"
		@echo ""
		@echo "Targets:"
		@echo "-----------"
		@echo "  help 			- Show this help message"
		@echo "  run 			- Run the application"
		@echo "  lint 			- Run linting"
		@echo "  format 		- Run formatting"
		@echo "  test 			- Run tests"
		@echo "  build 		- Build the application"
		@echo "  deploy 		- Deploy the application"
		@echo "  clean 		- Clean the application"
		@echo "  db-migrate		- Run database migrations"
		@echo "  db-rollback		- Rollback database migrations"
		@echo "  db-reset 		- Reset database"
		@echo "-----------"

rundry:
		.venv/bin/python3.12 main.py

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
	
