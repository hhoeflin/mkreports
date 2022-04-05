MAKEFILE_DIR=$(realpath $(dir $(firstword $(MAKEFILE_LIST))))

CONDA_ENV:=${MAKEFILE_DIR}/.conda_env
REPO_NAME:=mkreports

# ENVIRONMENT
create-base-env:
	conda env create --prefix ${CONDA_ENV} --file conda_env.yaml \
	&& conda run --prefix ${CONDA_ENV} flit install -s

lock-env:
	conda env export --prefix ${CONDA_ENV} | grep -v ${REPO_NAME} > conda_env.lock.yaml

create-lock-env:
	conda env create --prefix ${CONDA_ENV} --file conda_env.lock.yaml \
	&& conda run --prefix ${CONDA_ENV} flit install -s


# REPO
create-mkdocs:
	cd ${MAKEFILE_DIR}/docs && python -m staging.main ${MAKEFILE_DIR}/docs/final

create-mkdocs-del:
	cd ${MAKEFILE_DIR}/docs && rm -rf final && python -m staging.main ${MAKEFILE_DIR}/docs/final

create-site:
	cd ${MAKEFILE_DIR}/docs/final && mkdocs gh-deploy

serve-mkdocs:
	while true ; do cd ${MAKEFILE_DIR}/docs/final; mkdocs serve; done
