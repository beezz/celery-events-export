
.PHONY: clean update init run-worker

PYENV = .pyenv
PYTHON = python3

WORKER_ARGS = -E -A event_generator worker --config=config --loglevel=info --concurrency=10


clean:
	@echo "Cleaning up"
	@rm -rf $(PYENV)

install:
	@echo "Installing python virtual environment"
	@virtualenv -p $(PYTHON) $(PYENV)

update:
	@echo "Installing python packages"
	@$(PYENV)/bin/pip install -Ur requirements.txt

init: clean install update

run-worker:
	@echo "Starting celery worker"
	@$(PYENV)/bin/celery $(WORKER_ARGS)
