# Variables
PYTHON = ./venv/bin/python
APP = main:app
PORT = 8001
HOST = 0.0.0.0

.PHONY: run-local
run-local:
	@echo "Starting application on http://$(HOST):$(PORT)..."
	$(PYTHON) -m uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

.PHONY: install
install:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install -r requirements.txt

.PHONY: verify
verify:
	@echo "Running verification script..."
	$(PYTHON) test/verify_extraction.py

.PHONY: docker-up
docker-up:
	@echo "Starting Docker container..."
	docker compose up -d --build

.PHONY: docker-down
docker-down:
	@echo "Stopping Docker container..."
	docker compose down

.PHONY: clean
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
