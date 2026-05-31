.PHONY: dev-run dev-run-backend dev-run-frontend dev-run-db dev-stop dev-stop-backend dev-stop-frontend dev-stop-db

dev-run:
	docker-compose up -d

dev-run-backend:
	docker-compose up -d backend

dev-run-frontend:
	docker-compose up -d frontend

dev-run-db:
	docker-compose up -d db

dev-stop:
	docker-compose down

dev-stop-backend:
	docker-compose stop backend

dev-stop-frontend:
	docker-compose stop frontend

dev-stop-db:
	docker-compose stop db
