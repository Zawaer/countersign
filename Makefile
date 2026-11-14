# Shortcuts. Each target needs only Python 3.11+ and uv (https://docs.astral.sh/uv/).
.PHONY: demo test site

demo:  ## the 2234 story in 9 steps, offline, from the committed evidence (scripts/demo.sh --step to pause)
	scripts/demo.sh

test:  ## the test suite
	uv sync --frozen --inexact --extra dev --quiet
	uv run --frozen pytest -q

site:  ## regenerate site/ from measurement/, evidence/, reviews/, packs/, ledger/ (stdlib only)
	python3 site/build.py
