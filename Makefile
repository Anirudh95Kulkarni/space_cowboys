VENV_DIR := venv
PYTHON:= /usr/local/bin/python3.12
VENV_PYTHON:= venv/bin/python3.12

setup:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install earthaccess
	echo "source $(VENV_DIR)/bin/activate"

	
version_check:
	$(VENV_PYTHON) --version

clean:
	rm -rf $(VENV_DIR)

.PHONY: setup clean