THIS_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ROOT     := $(abspath $(THIS_DIR)/../../../..)

ifeq ($(OS),Windows_NT)
  PYTHON ?= python
else
  PYTHON ?= $(shell command -v python3 2>/dev/null || echo python)
endif

PORT   ?= 4000
SCRIPT := main.py

.PHONY: run send flash

run:
	@echo ">>> Make sure the Wokwi simulator is running in VS Code"
	$(PYTHON) $(ROOT)/tools/wokwi_run.py --port $(PORT) $(SCRIPT)

send: run

flash: run
