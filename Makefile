docker:
	@docker build -t value-vroom/api .

venv:
	@python3 -m venv venv && \
	venv/bin/pip install -e .

lint: venv
	@echo " - black" && \
	venv/bin/black -q --check app  && \
	echo " - isort" && \
	venv/bin/isort --check app && \
	echo " - ruff" && \
	venv/bin/ruff app && \
	echo " - mypy" && \
	venv/bin/mypy app && \
	echo "Passed all linting checks!"

reformat: venv
	@echo " - ruff" && \
	venv/bin/ruff --fix app && \
	echo " - black" && \
	venv/bin/black -q app && \
	echo " - isort" && \
	venv/bin/isort app && \
	echo "Reformatted code!"

run: venv
	@echo "Starting server..."
	@venv/bin/ruff app || true
	@venv/bin/python3 app/utility/setup_db.py && \
	venv/bin/uvicorn --proxy-headers app.main:app

dev: venv
	@venv/bin/watchmedo auto-restart \
		--directory=./app --directory=./prisma \
		--pattern="*.py;*.prisma" \
		--recursive \
		$(MAKE) -- run

tunnel:
	@cloudflared tunnel --url http://localhost:8000

.PHONY: docker lint reformat run dev