test:
	ruff .
	# cd tests && pytest -v

pip-update:
	python -m pip install --upgrade pip

pip-editable:
	pip install -e . --config-settings editable_mode=compat