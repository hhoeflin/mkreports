#! /usr/bin/env bash
export PROJECT_DIR=$(dirname "$(realpath -s "${BASH_SOURCE[0]}")")
nix shell --impure $PROJECT_DIR
