PYTHON = python3
VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP = $(VENV_PYTHON) -m pip
VENV_PRE_COMMIT = $(VENV)/bin/pre-commit
VENV_BLACK = $(VENV)/bin/black
VENV_FLAKE8 = $(VENV)/bin/flake8

.PHONY: help setup create_environment requirements format lint clean test data train predict

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup              - Cria a venv, instala dependências e configura o pre-commit"
	@echo "  make format             - Formata o código"
	@echo "  make lint               - Verifica o estilo"
	@echo "  make test               - Executa os testes"
	@echo "  make clean              - Remove caches"

create_environment:
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)

requirements: create_environment
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

setup: requirements
	$(VENV_PRE_COMMIT) install
	@echo "Ambiente configurado com sucesso!"
	@echo "Ative-o com: source $(VENV)/bin/activate"

format: requirements
	$(VENV_BLACK) src/ notebooks/

lint: requirements
	$(VENV_FLAKE8) src/

test: requirements
	$(VENV_PYTHON) -m pytest tests

data: requirements
	$(VENV_PYTHON) src/dataset.py

train: requirements
	$(VENV_PYTHON) src/modeling/train.py

predict: requirements
	$(VENV_PYTHON) src/modeling/predict.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf .built_models/
