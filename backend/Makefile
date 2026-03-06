# ==============================
# SafeX PostgreSQL Docker Setup
# ==============================

DB_CONTAINER=safex-postgres
DB_NAME=safex_db
DB_USER=admin
DB_PASSWORD=password
DB_PORT=5432

# Start PostgreSQL
up:
	docker run -d \
	--name $(DB_CONTAINER) \
	-e POSTGRES_USER=$(DB_USER) \
	-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
	-e POSTGRES_DB=$(DB_NAME) \
	-p $(DB_PORT):5432 \
	postgres:16

# Stop container
down:
	docker stop $(DB_CONTAINER) || true
	docker rm $(DB_CONTAINER) || true

# Restart container
restart: down up

# View logs
logs:
	docker logs -f $(DB_CONTAINER)

# Remove everything including data
clean:
	docker stop $(DB_CONTAINER) || true
	docker rm $(DB_CONTAINER) || true
	docker volume prune -f