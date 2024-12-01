.PHONY: help

# From https://gist.github.com/prwhite/8168133
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


setup: ## Create virtual environment and install pyproject.toml stuff and aoc tool
	uv venv
	source .venv/bin/activate && uv pip install -e .
	$(MAKE) install-aoc
	source .venv/bin/activate && python -m ipykernel install --user --name aoc24


clean: ## Delete virtual environment and start over
	-rm -rf .venv

install-aoc:  ## Install aoc tool step inside setup above
	source .venv/bin/activate && nodeenv -p --node=lts && source .venv/bin/activate && npm i -g @jakzo/aoc
	cp wip.py .venv/lib/node_modules/\@jakzo/aoc/templates/python

install-jupyter:  ## Install jupyter and friends
	-uv tool uninstall jupyterlab
	uv tool install jupyterlab --with jupyter-core,jupyterlab-git,jupyterlab-vim,jupyterlab-lsp,theme-darcula,catppuccin-jupyterlab,ipympl,nodeenv
	# patch httpx for now, see https://github.com/jupyterlab/jupyterlab/issues/17012
	source ~/.local/share/uv/tools/jupyterlab/bin/activate && uv pip install 'httpx<0.28.0'
	source ~/.local/share/uv/tools/jupyterlab/bin/activate && nodeenv -p --node=lts
	source ~/.local/share/uv/tools/jupyterlab/bin/activate && npm install -g pyright sql-language-server unified-language-server vscode-html-languageserver-bin vscode-json-languageserver-bin yaml-language-server


run-jupyter: ## Inject nodeenv's stuff into path and run jupyter lab
	source ~/.local/share/uv/tools/jupyterlab/bin/activate && jupyter lab

install-pre-commit: ## Set up pre-commit stuff
	-uv tool uninstall pre-commit
	uv tool install pre-commit --with pre-commit-uv
