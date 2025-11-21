# AI-HR Platform Development Commands

.PHONY: help dev build test clean install

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development environment
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

build: ## Build all services
	docker-compose build

stop: ## Stop all services
	docker-compose down

clean: ## Clean up containers and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

logs: ## Show logs for all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

test: ## Run all tests
	make test-backend
	make test-frontend

test-backend: ## Run backend tests
	cd backend && python -m pytest

test-frontend: ## Run frontend tests
	cd frontend && npm test -- --watchAll=false

install: ## Install dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

lint: ## Run linting
	cd backend && flake8 app/
	cd frontend && npm run lint

format: ## Format code
	cd backend && black app/
	cd frontend && npm run format

setup: ## Initial project setup
	cp backend/.env.example backend/.env
	make install
	make dev

db-migrate: ## Run database migrations
	docker-compose exec backend alembic upgrade head

db-reset: ## Reset database
	docker-compose down -v postgres
	docker-compose up -d postgres
	sleep 5
	make db-migrate