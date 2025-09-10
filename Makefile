.PHONY: help build up down logs test clean deploy

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker containers
	docker compose build

up: ## Start all services in detached mode
	docker compose up -d

down: ## Stop and remove all containers
	docker compose down

logs: ## Follow logs for all services
	docker compose logs -f

test: ## Run tests for all services
	@echo "Running tests for all services..."
	@for service in mcp_RealWorldDataIngestor mcp_EHRConnector mcp_ClaimsDataParser mcp_SiteFeasibilityPredictor mcp_DiversityIndexMapper mcp_ProtocolComplexityScorer mcp_SoA_Comparator orchestrator; do \
		echo "Testing $$service..."; \
		docker compose run --rm $$service pytest || exit 1; \
	done
	@echo "All tests passed!"

test-service: ## Test specific service (usage: make test-service SERVICE=orchestrator)
	docker compose run --rm $(SERVICE) pytest

restart: ## Restart all services
	docker compose restart

restart-service: ## Restart specific service (usage: make restart-service SERVICE=orchestrator)
	docker compose restart $(SERVICE)

ps: ## Show running containers
	docker compose ps

clean: ## Remove all containers, networks, and volumes
	docker compose down -v
	docker system prune -f

frontend-dev: ## Start frontend in development mode
	cd frontend && npm install && npm start

backend-shell: ## Open shell in orchestrator container
	docker compose exec orchestrator /bin/bash

service-shell: ## Open shell in specific service (usage: make service-shell SERVICE=mcp_protocolscorer)
	docker compose exec $(SERVICE) /bin/bash

check-health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8250/service_status | python -m json.tool

quick-test: ## Run a quick test of the orchestrator
	@echo "Running quick assessment..."
	@curl -X POST http://localhost:8250/quick_assessment \
		-H "Content-Type: application/json" \
		-d '{"protocol_text": "Test protocol for Phase III study"}' \
		| python -m json.tool

full-test: ## Run a full study planning test
	@echo "Running full study planning..."
	@curl -X POST http://localhost:8250/plan_rwe_study \
		-H "Content-Type: application/json" \
		-d '{ \
			"protocol_text": "Phase III randomized controlled trial", \
			"disease_area": "Diabetes", \
			"target_countries": ["USA", "UK"], \
			"target_enrollment": 500, \
			"inclusion_criteria": ["Age > 18"], \
			"exclusion_criteria": ["Pregnant"], \
			"study_duration_months": 12, \
			"primary_endpoints": ["HbA1c"], \
			"secondary_endpoints": ["Weight"] \
		}' \
		| python -m json.tool

deploy-azure: ## Deploy to Azure (requires Azure CLI login)
	cd azure && bash deploy.sh

# Development shortcuts
dev: up logs ## Start services and follow logs

stop: down ## Alias for down

rebuild: ## Rebuild and restart all services
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "Services rebuilt and started. Check logs with 'make logs'"