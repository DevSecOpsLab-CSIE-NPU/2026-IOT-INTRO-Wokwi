THIS_DIR := $(shell dirname "$(realpath $(lastword $(MAKEFILE_LIST)))")
ROOT     := $(shell cd "$(THIS_DIR)/../../.." && pwd)

ifeq ($(OS),Windows_NT)
  PYTHON ?= python
else
  PYTHON ?= $(shell command -v python3 2>/dev/null || echo python)
endif

PORT   ?= 4020
SCRIPT := main.py

.PHONY: run
run:
	@echo ">>> 請確認 VS Code 中 Wokwi 模擬器已啟動"
	$(PYTHON) "$(ROOT)/tools/wokwi_run.py" --port $(PORT) $(SCRIPT)
