VENV = .venv
PYTHON = python3


install-venv:
	@echo "Installing Python virtualenv"
	@virtualenv -p $(PYTHON) $(VENV)


install-test-reqs:
	@echo "Installing test requirements"
	@$(VENV)/bin/pip install -r test-requirements.txt


install-self:
	@echo "Installing as editable package"
	@$(VENV)/bin/pip install -e .


develop: install-venv install-self install-test-reqs


clean:
	@echo "Cleaning Python virtualenv"
	@rm -rf $(VENV)

test-unit:
	@echo "Running unit tests"
	@$(VENV)/bin/python -m pytest -xv tests


run-worker:
	@make -C devtools/event-generator run-worker


run-docker:
	@cd devtools && docker-compose up -d


restart-docker:
	@cd devtools && docker-compose restart

stop-docker:
	@cd devtools && docker-compose stop

down-docker:
	@cd devtools && docker-compose down

logs-docker:
	@cd devtools && docker-compose logs -f
