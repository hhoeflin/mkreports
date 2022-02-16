MAKEFILE_DIR=$(realpath $(dir $(firstword $(MAKEFILE_LIST))))

create_mkdocs:
	cd ${MAKEFILE_DIR}/docs && python -m staging.main ${MAKEFILE_DIR}/docs/final

create_mkdocsi_del:
	cd ${MAKEFILE_DIR}/docs && rm -rf final && python -m staging.main ${MAKEFILE_DIR}/docs/final

create_site:
	cd ${MAKEFILE_DIR}/docs/final && mkdocs gh-deploy
