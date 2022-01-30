MAKEFILE_DIR=$(realpath $(dir $(firstword $(MAKEFILE_LIST))))

create_mkdocs:
	cd ${MAKEFILE_DIR}/docs && python -m staging.main ${MAKEFILE_DIR}/docs/final
