docker:
	@docker build -t value-vroom/api .

lint:
	@echo " - black" && \
	black -q --check app  && \
	echo " - isort" && \
	isort --check app && \
	echo " - ruff" && \
	ruff app && \
	echo " - mypy" && \
	mypy app && \
	echo "Passed all linting checks!"

reformat:
	@echo " - ruff" && \
	ruff --fix app && \
	echo " - black" && \
	black -q app && \
	echo " - isort" && \
	isort app && \
	echo "Reformatted code!"

run:
	@ruff app && \
	venv/bin/python app

dev: run