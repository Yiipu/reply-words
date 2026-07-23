VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

$(VENV):
	python3 -m venv $(VENV)

install: $(VENV)
	$(PIP) install -r backend/requirements.txt

run: install
	$(PYTHON) backend/app.py

clean:
	rm -rf $(VENV) __pycache__ */__pycache__ *.pyc

.PHONY: install run clean
