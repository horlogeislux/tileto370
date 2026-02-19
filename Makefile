# Tooling
PYTHON ?= python3
SCRIPT := tileto370.py

# Conversion inputs/outputs
RESOURCE_DIR := resources/nevanda
SOURCE_IMAGE := $(RESOURCE_DIR)/nevanda-360.png
SUFFIX ?= _make
OUTPUT_IMAGE := $(RESOURCE_DIR)/nevanda-360$(SUFFIX).png
TILE_WIDTH ?= 32

# Shared converter arguments
CONVERT_ARGS := --tile-width $(TILE_WIDTH) --suffix $(SUFFIX)


$(OUTPUT_IMAGE): $(SCRIPT) $(SOURCE_IMAGE) ## Develop
	$(PYTHON) $(SCRIPT) $(SOURCE_IMAGE) $(CONVERT_ARGS)

redirect: $(SCRIPT) $(SOURCE_IMAGE) ## Develop redirect
	$(PYTHON) $(SCRIPT) $(SOURCE_IMAGE) $(CONVERT_ARGS) --mode redirect

watch: ## Run make every second. Call 'make watch' or 'make watch MODE=redirect'
	@if [ "$(MODE)" = "watch" ]; then \
		echo "ERROR: watched MODE cannot be 'watch'"; \
		exit 1; \
	fi
	while true; do \
		$(MAKE) -q $(MODE) || $(MAKE) --silent $(MODE); \
		sleep 1; \
	done

clean:
	rm -f $(OUTPUT_IMAGE) converter.log


.PHONY: redirect watch clean help


help: ## Print this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  make %-20s# %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
