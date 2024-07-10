.ONESHELL:
.PHONY: create-mkdocs create-mkdocs-del create-site serve-mkdocs

# REPO
create-mkdocs:
	cd ${MAKEFILE_DIR}/docs && python -m staging.main ${MAKEFILE_DIR}/docs/final

create-mkdocs-del:
	cd ${MAKEFILE_DIR}/docs && rm -rf final && python -m staging.main ${MAKEFILE_DIR}/docs/final

create-site:
	cd ${MAKEFILE_DIR}/docs/final && mkdocs gh-deploy

serve-mkdocs:
	while true ; do cd ${MAKEFILE_DIR}/docs/final; mkdocs serve; done
