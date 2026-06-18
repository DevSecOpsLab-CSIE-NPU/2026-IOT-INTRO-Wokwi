THIS_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ROOT     := $(abspath $(THIS_DIR)/../../../..)

# 跨平台 Python：Windows 用 python，其餘(macOS/Linux)優先 python3，可用 make PYTHON=... 覆寫
ifeq ($(OS),Windows_NT)
  PYTHON ?= python
else
  PYTHON ?= $(shell command -v python3 2>/dev/null || echo python)
endif

PORT   ?= 4000
SCRIPT := main.py

.PHONY: run send flash

run:
	@echo ">>> 請確認 VS Code 中 Wokwi 模擬器已啟動"
	$(PYTHON) $(ROOT)/tools/wokwi_run.py --port $(PORT) $(SCRIPT)

send: run

flash: run
