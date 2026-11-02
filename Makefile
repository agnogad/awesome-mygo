# Build the list and the site
build:
	python3 scripts/merge.py
	python3 scripts/build_readme.py

# Refresh stars, licenses and push dates from the GitHub API
data:
	python3 scripts/enrich.py

# Re-import the original research file into data/curated.json
import:
	python3 scripts/parse.py

# Publish the site (surge.sh)
deploy:
	npx surge site awesome-mygo.surge.sh

# Local preview at http://localhost:8099
serve:
	python3 -m http.server 8099 --directory site

.PHONY: build data import deploy serve
