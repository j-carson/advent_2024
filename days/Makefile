YEAR = 2024

# From https://gist.github.com/prwhite/8168133
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


get-day-%: ## Print the problem for day "%" and wait for answers
	aoc -y $(YEAR) -d $(@:get-day-%=%)

solve-day-%: ## Start solving day "%"
	source ../.venv/bin/activate && aoc start  -y $(YEAR) -d $(@:solve-day-%=%) python
