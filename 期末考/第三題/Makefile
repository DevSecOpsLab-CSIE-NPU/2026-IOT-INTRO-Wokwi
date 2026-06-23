THIS_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

ifeq ($(OS),Windows_NT)
  PYTHON ?= python
else
  PYTHON ?= $(shell command -v python3 2>/dev/null || echo python)
endif

PORT ?= 4003

.PHONY: run
run:
	@echo ">>> Make sure the Wokwi simulator is running in VS Code."
	$(PYTHON) "$(THIS_DIR)run.py" --port $(PORT)
