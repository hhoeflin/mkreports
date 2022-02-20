MAKEFILE_DIR=$(realpath $(dir $(firstword $(MAKEFILE_LIST))))

create_mkdocs:
	cd ${MAKEFILE_DIR}/docs && python -m staging.main ${MAKEFILE_DIR}/docs/final

create_mkdocs_del:
	cd ${MAKEFILE_DIR}/docs && rm -rf final && python -m staging.main ${MAKEFILE_DIR}/docs/final

create_site:
	cd ${MAKEFILE_DIR}/docs/final && mkdocs gh-deploy

serve_mkdocs:
	while true ; do cd ${MAKEFILE_DIR}/docs/final; mkdocs serve; done
