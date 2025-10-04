VENV_DIR := venv
PYTHON:= /usr/local/bin/python3.12
VENV_PYTHON:= venv/bin/python3.12

setup:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install earthaccess
	$(VENV_DIR)/bin/pip install h5py
	$(VENV_DIR)/bin/pip install xarray
	$(VENV_DIR)/bin/pip install pandas
	$(VENV_DIR)/bin/pip install	numpy
	$(VENV_DIR)/bin/pip install json
	echo "source $(VENV_DIR)/bin/activate"

	
version_check:
	$(VENV_PYTHON) --version

run:
	$(VENV_PYTHON) fetch_data.py

run2:
	$(VENV_PYTHON) fetch_2.py

clean:
	rm -rf $(VENV_DIR)

.PHONY: setup clean