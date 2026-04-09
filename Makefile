# Define targets
.PHONY: install test coverage-badge build publish help dev deploy frontend-dev frontend-build frontend-deploy

# Define variables
PYTHON := python

# Colors
GREEN := \033[0;32m
ORANGE := \033[0;33m
NC := \033[0m

# Default target
default: install test

# Target to install package
install:
	uv pip install -e ".[cli]"

# Target to install in termux
install-in-termux:
	pip install moviebox-api --no-deps
	pip install 'pydantic==2.9.2'
	pip install rich click bs4 httpx throttlebuster

# Target to run tests
test:
	uv run coverage run -m pytest -v

# Target to generate coverage-badge
coverage-badge:
	coverage-badge -o assets/coverage.svg -f

# target to build dist
build:
	rm build/ dist/ -rf
	uv build
	
# Target to publish dist to pypi
publish:
	uv publish --token $(shell get pypi)

# ============================================================================
# FRONTEND / WEB APP DEPLOYMENT TARGETS
# ============================================================================

help-frontend: ## Show frontend/deployment commands
	@echo "$(GREEN)Frontend & Deployment Commands$(NC)"
	@echo ""
	@echo "  $(GREEN)Development:$(NC)"
	@echo "    make frontend-install   - Install frontend dependencies"
	@echo "    make frontend-dev       - Start development server"
	@echo "    make frontend-build     - Build for production"
	@echo "    make frontend-preview   - Preview production build"
	@echo ""
	@echo "  $(GREEN)Deployment:$(NC)"
	@echo "    make frontend-deploy    - Deploy to Cloudflare Pages"
	@echo "    make deploy-worker      - Deploy Cloudflare Worker proxy"
	@echo ""
	@echo "  $(GREEN)Quality:$(NC)"
	@echo "    make frontend-lint      - Lint frontend code"
	@echo "    make frontend-type-check - TypeScript type checking"
	@echo ""
	@echo "  $(GREEN)See more:$(NC)"
	@echo "    make help-deployment    - Full deployment info"

help-deployment: ## Show deployment architecture and info
	@echo "$(GREEN)MovieBox Deployment Architecture$(NC)"
	@echo ""
	@echo "Frontend:  Cloudflare Pages"
	@echo "Backend:   Render FastAPI (https://movieb-rsoz.onrender.com)"
	@echo "Worker:    Optional API proxy"
	@echo ""
	@echo "$(ORANGE)Documentation:$(NC)"
	@echo "  - BUILD_SETUP.md"
	@echo "  - CLOUDFLARE_DEPLOYMENT.md"
	@echo "  - FRONTEND_QUICK_START.md"
	@echo "  - DEPLOYMENT_GUIDE_SUMMARY.md"
	@echo ""
	@echo "$(ORANGE)Quick Start:$(NC)"
	@echo "  1. make frontend-install"
	@echo "  2. make frontend-dev"
	@echo "  3. Open http://localhost:3000"

# Frontend development targets
frontend-install: ## Install frontend dependencies
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

frontend-dev: ## Start frontend development server
	@echo "$(GREEN)Starting development server...$(NC)"
	cd frontend && npm run dev

frontend-build: ## Build frontend for production
	@echo "$(GREEN)Building frontend...$(NC)"
	cd frontend && npm run build
	@echo "$(GREEN)✓ Build complete: frontend/.next$(NC)"

frontend-preview: ## Preview production build locally
	@echo "$(GREEN)Starting production preview...$(NC)"
	cd frontend && npm run start

frontend-lint: ## Lint frontend code
	@echo "$(GREEN)Linting frontend...$(NC)"
	cd frontend && npm run lint

frontend-type-check: ## TypeScript type checking
	@echo "$(GREEN)Type checking...$(NC)"
	cd frontend && npm run type-check

# Frontend deployment targets
frontend-deploy: frontend-build ## Deploy to Cloudflare Pages
	@echo "$(GREEN)Deploying to Cloudflare Pages...$(NC)"
	@echo "$(ORANGE)Note: Ensure Wrangler CLI is installed$(NC)"
	wrangler pages deploy frontend/.next --project-name=movieb-frontend
	@echo "$(GREEN)✓ Deployment complete$(NC)"

deploy-worker: ## Deploy Cloudflare Worker proxy
	@echo "$(GREEN)Deploying Cloudflare Worker...$(NC)"
	cd cloudflare-worker && wrangler deploy
	@echo "$(GREEN)✓ Worker deployed$(NC)"

# Frontend setup targets
frontend-env: ## Create .env.local for development
	@echo "$(GREEN)Setting up frontend environment...$(NC)"
	@if [ ! -f frontend/.env.local ]; then \
		echo "NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1" > frontend/.env.local; \
		echo "$(GREEN)✓ Created frontend/.env.local$(NC)"; \
	else \
		echo "$(ORANGE)frontend/.env.local already exists$(NC)"; \
	fi

frontend-setup: frontend-install frontend-env ## Complete frontend setup
	@echo "$(GREEN)✓ Frontend setup complete!$(NC)"
	@echo "$(ORANGE)Next: make frontend-dev$(NC)"

frontend-clean: ## Clean frontend build artifacts
	@echo "$(GREEN)Cleaning frontend...$(NC)"
	rm -rf frontend/.next frontend/out frontend/dist frontend/node_modules
	@echo "$(GREEN)✓ Clean complete$(NC)"

frontend-reinstall: frontend-clean frontend-install ## Reinstall frontend dependencies
	@echo "$(GREEN)✓ Frontend reinstall complete$(NC)"

# Quick commands
quick-deploy: frontend-build frontend-deploy ## Build and deploy to Cloudflare
	@echo "$(GREEN)✓ Frontend deployed$(NC)"

# Information targets
status: ## Show deployment status
	@echo "$(GREEN)MovieBox Status$(NC)"
	@echo ""
	@echo "Backend API: https://movieb-rsoz.onrender.com"
	@echo "API Docs:    https://movieb-rsoz.onrender.com/docs"
	@echo "Frontend:    Check Cloudflare Pages dashboard"
	@echo ""
	@echo "$(ORANGE)Test API:$(NC)"
	@echo "curl 'https://movieb-rsoz.onrender.com/api/v1/search?q=inception&limit=5'"

.DEFAULT_GOAL := help
