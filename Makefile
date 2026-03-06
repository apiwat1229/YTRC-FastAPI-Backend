.PHONY: help \
        deploy-staging deploy-prod \
        stop-staging stop-prod \
        logs-staging logs-prod \
        ps restart-staging restart-prod \
        db-staging db-prod

# ─── Default ─────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  YTRC Backend — Make Commands"
	@echo "  ─────────────────────────────────────────"
	@echo "  make deploy-staging    Deploy / update Staging  (port 2531)"
	@echo "  make deploy-prod       Deploy / update Production (port 2530)"
	@echo "  make stop-staging      Stop Staging containers"
	@echo "  make stop-prod         Stop Production containers"
	@echo "  make restart-staging   Restart Staging API only"
	@echo "  make restart-prod      Restart Production API only"
	@echo "  make logs-staging      Follow Staging API logs"
	@echo "  make logs-prod         Follow Production API logs"
	@echo "  make ps                Show all running containers"
	@echo "  make db-staging        Open psql shell (Staging DB)"
	@echo "  make db-prod           Open psql shell (Production DB)"
	@echo ""

# ─── Deploy ──────────────────────────────────────────────────────────────────
deploy-staging:
	docker compose -p ytrc-staging \
	  -f docker-compose.yml \
	  -f docker-compose.staging.yml \
	  --env-file .env.staging \
	  up -d --build --remove-orphans
	docker image prune -f

deploy-prod:
	docker compose -p ytrc-prod \
	  -f docker-compose.yml \
	  -f docker-compose.prod.yml \
	  --env-file .env.production \
	  up -d --build --remove-orphans
	docker image prune -f

# ─── Stop ────────────────────────────────────────────────────────────────────
stop-staging:
	docker compose -p ytrc-staging \
	  -f docker-compose.yml \
	  -f docker-compose.staging.yml \
	  down

stop-prod:
	docker compose -p ytrc-prod \
	  -f docker-compose.yml \
	  -f docker-compose.prod.yml \
	  down

# ─── Restart API only ────────────────────────────────────────────────────────
restart-staging:
	docker restart ytrc-staging-api

restart-prod:
	docker restart ytrc-fastapi-api

# ─── Logs ────────────────────────────────────────────────────────────────────
logs-staging:
	docker compose -p ytrc-staging logs -f api

logs-prod:
	docker compose -p ytrc-prod logs -f api

# ─── Status ──────────────────────────────────────────────────────────────────
ps:
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# ─── Database shell ──────────────────────────────────────────────────────────
db-staging:
	docker exec -it ytrc-staging-db psql -U postgres -d ytrc_staging

db-prod:
	docker exec -it ytrc-fastapi-db psql -U postgres -d ytrc_prod
