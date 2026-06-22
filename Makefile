# Safer shell settings
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.DELETE_ON_ERROR:

# === CORE CONFIG ===
TEXLIVE_IMAGE = maxkratz/texlive:2026-python
MERMAID_IMAGE = ghcr.io/mermaid-js/mermaid-cli/mermaid-cli:10.6.1
DOCKER_TEX = docker run --rm -v $(PWD):/workspace -w /workspace/tex $(TEXLIVE_IMAGE)
DOCKER_SCRIPTS = docker run --rm -v $(PWD):/workspace -w /workspace/scripts $(TEXLIVE_IMAGE)
DOCKER_MERMAID = docker run --rm -v $(PWD):/workspace $(MERMAID_IMAGE)
BUILD_CMD = rm -f *.log *.fls *.fdb_latexmk && for i in 1 2 3; do lualatex -interaction=nonstopmode

# Build artifacts
DOC_BASENAME := IT-Sicherheitsdokumentation

# === MAIN TARGETS ===
all: clean version mermaid build-all ## Build all versions with version update

build: build-standard ## Build standard version
build-standard: version ## Build standard version (PDF/A-3u)
	@echo "🐳 Building standard version..."
	$(DOCKER_TEX) sh -c "$(BUILD_CMD) -jobname=main-standard main.tex; done" || true
	@test -s tex/main-standard.pdf || (echo "❌ PDF build failed!" && exit 1)
	@echo "✅ Standard build complete: tex/main-standard.pdf"

build-accessible: version ## Build accessible version (PDF/A-3u + PDF/UA-1)
	@echo "🐳 Building accessible version..."
	$(DOCKER_TEX) sh -c "tlmgr update --self >/dev/null 2>&1; tlmgr update koma-script >/dev/null 2>&1; $(BUILD_CMD) -jobname=main-accessible '\\def\\accessible{}\\input{main}'; done" || true
	@test -s tex/main-accessible.pdf || (echo "❌ PDF build failed!" && exit 1)
	@echo "✅ Accessible build complete: tex/main-accessible.pdf"

build-printable: version ## Build printable version (PDF/X-1a for professional printing)
	@echo "🐳 Building printable version..."
	$(DOCKER_TEX) sh -c "$(BUILD_CMD) -jobname=main-printable '\\def\\printable{}\\input{main}'; done" || true
	@test -s tex/main-printable.pdf || (echo "❌ PDF build failed!" && exit 1)
	@echo "✅ Printable build complete: tex/main-printable.pdf"

build-both: build-standard build-accessible ## Build both versions
	@echo "✅ Both versions built successfully"

build-all: build-standard build-accessible build-printable ## Build all three versions
	@echo "✅ All versions built successfully"

# === SAMPLE BUILDS (Pipeline) ===
build-sample-standard: use-sample version ## Build sample standard version
	@echo "🐳 Building sample standard version..."
	$(DOCKER_TEX) sh -c "$(BUILD_CMD) -jobname=main-standard '\\def\\samplebuild{}\\input{main}'; done" || true
	@test -s tex/main-standard.pdf || (echo "❌ PDF build failed!" && exit 1)
	@echo "✅ Sample standard build complete"

build-sample-accessible: use-sample version ## Build sample accessible version
	@echo "🐳 Building sample accessible version..."
	$(DOCKER_TEX) sh -c "tlmgr update --self >/dev/null 2>&1; tlmgr update koma-script >/dev/null 2>&1; $(BUILD_CMD) -jobname=main-accessible '\\def\\accessible{}\\def\\samplebuild{}\\input{main}'; done" || true
	@test -s tex/main-accessible.pdf || (echo "❌ PDF build failed!" && exit 1)
	@echo "✅ Sample accessible build complete"

build-sample-printable: use-sample version ## Build sample printable version
	@echo "🐳 Building sample printable version..."
	$(DOCKER_TEX) sh -c "$(BUILD_CMD) -jobname=main-printable '\\def\\printable{}\\def\\samplebuild{}\\input{main}'; done" || true
	@test -s tex/main-printable.pdf || (echo "❌ PDF build failed!" && exit 1)
	@echo "✅ Sample printable build complete"

build-sample: use-sample version mermaid build-sample-all ## Build with sample data
build-sample-both: build-sample-standard build-sample-accessible ## Build both sample versions
build-sample-all: build-sample-standard build-sample-accessible build-sample-printable ## Build all sample versions

# === UTILS ===
version: ## Update version to current date
	@echo "📝 Updating version..."
ifdef VERSION_DATE
	python3 scripts/build.py --version-date $(VERSION_DATE) --no-build
else
	python3 scripts/build.py --no-build
endif
	@echo "✅ Version updated"

mermaid: ## Generate Mermaid diagrams
	@echo "🐳 Generating Mermaid diagram..."
	$(DOCKER_MERMAID) \
		-i /workspace/tex/assets/netzplan.mmd \
		-o /workspace/tex/assets/netzplan.png \
		--width 3840 --height 2160 --scale 4 --backgroundColor white
	@echo "✅ Mermaid diagram generated"

clean: ## Clean all generated files
	@echo "🧹 Cleaning up..."
	$(DOCKER_TEX) sh -c "rm -f *.aux *.log *.toc *.out *.fls *.fdb_latexmk *.synctex.gz *.bbl *.blg *.bcf *.run.xml *.auxlock main.pdf main-standard.pdf main-accessible.pdf main-printable.pdf"
	@echo "✅ Cleanup complete"

test: ## Run Python unit tests
	@echo "🧪 Running tests..."
	$(DOCKER_TEX) sh -c "cd /workspace/scripts && python3 test_build.py"
	@echo "✅ Tests complete"

# === VALIDATION (Pipeline) ===
validate: test ## Full validation (tests + build check)
	@echo "🔍 Running validation..."
	@if [ -z "$$CI" ]; then \
		echo "Testing build..."; \
		$(MAKE) build >/dev/null 2>&1 && echo "✅ Build test passed" || echo "❌ Build test failed"; \
	else \
		echo "⏭️  Skipping build test in CI"; \
	fi
	@echo "✅ Validation complete"

# === DATA SWITCH (Pipeline) ===
use-sample: ## Switch to sample data files
	@echo "🔄 Switching to sample data..."
	@cp tex/config/metadata-sample.tex tex/config/metadata.tex
	@cp tex/assets/geraeteliste-sample.csv tex/assets/geraeteliste.csv
	@cp tex/assets/netzplan-sample.mmd tex/assets/netzplan.mmd
	@echo "✅ Now using sample data"

use-real: ## Switch to real data files
	@echo "🔄 Switching to real data..."
	@cp tex/config/metadata-real.tex tex/config/metadata.tex
	@cp tex/assets/geraeteliste-real.csv tex/assets/geraeteliste.csv
	@cp tex/assets/netzplan-real.mmd tex/assets/netzplan.mmd
	@echo "✅ Now using real data"

# === RELEASE HELPERS ===
rename: ## Rename PDFs with version and generate checksums
	@v="$$(python3 scripts/build.py --print-version 2>/dev/null || echo 'unknown')"
	@test "$$v" != "unknown" || { echo "Could not determine version"; exit 1; }
	@if [ -f tex/main-standard.pdf ]; then \
		cp tex/main-standard.pdf "$(DOC_BASENAME)_v$$v.pdf"; \
		sha256sum "$(DOC_BASENAME)_v$$v.pdf" > "$(DOC_BASENAME)_v$$v.sha256"; \
		echo "✅ Created $(DOC_BASENAME)_v$$v.pdf"; \
	fi
	@if [ -f tex/main-accessible.pdf ]; then \
		cp tex/main-accessible.pdf "$(DOC_BASENAME)_v$$v-accessible.pdf"; \
		sha256sum "$(DOC_BASENAME)_v$$v-accessible.pdf" > "$(DOC_BASENAME)_v$$v-accessible.sha256"; \
		echo "✅ Created $(DOC_BASENAME)_v$$v-accessible.pdf"; \
	fi
	@if [ -f tex/main-printable.pdf ]; then \
		cp tex/main-printable.pdf "$(DOC_BASENAME)_v$$v-printable.pdf"; \
		sha256sum "$(DOC_BASENAME)_v$$v-printable.pdf" > "$(DOC_BASENAME)_v$$v-printable.sha256"; \
		echo "✅ Created $(DOC_BASENAME)_v$$v-printable.pdf"; \
	fi

# === DEVELOPMENT ===
shell: ## Open shell in LaTeX container
	docker run --rm -it -v $(PWD):/workspace -w /workspace/tex $(TEXLIVE_IMAGE) bash

help: ## Show this help message
	@echo "📚 Available targets:"
	@awk -F':|##' '/^[a-zA-Z0-9_.-]+:.*?##/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$NF}' $(MAKEFILE_LIST)

# Aliases
rebuild: clean all ## Force rebuild everything

.PHONY: all build build-standard build-accessible build-printable build-both build-all build-sample build-sample-standard build-sample-accessible build-sample-printable build-sample-both build-sample-all version mermaid clean test validate use-sample use-real rename shell help rebuild
