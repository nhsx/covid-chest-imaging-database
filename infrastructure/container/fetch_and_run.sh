#!/bin/bash
# fetch-and-run.sh is building on
# https://github.com/awslabs/aws-batch-helpers/blob/94cca77a5854941353d6b1bf5cfaaf08ca273fa4/fetch-and-run/fetch_and_run.sh
# which is released under Apache 2.0 license

PATH="/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin:/usr/local/sbin:/home/pipeline/.local/bin"
BASENAME="${0##*/}"
REPOSITORY="https://github.com/nhsx/covid-chest-imaging-database"
CODE_FOLDER="warehouse-loader"

usage () {
  if [ "${#@}" -ne 0 ]; then
    echo "* ${*}"
    echo
  fi
  cat <<ENDUSAGE
Usage:
export COMMIT="master"
${BASENAME} <command> [ <script arguments> ]
ENDUSAGE

  exit 2
}

# Standard function to print an error and exit with a failing return code
error_exit () {
  echo "${BASENAME} - ${1}" >&2
  exit 1
}

if [ -z "${COMMIT}" ]; then
    usage "COMMIT not set, unable to determine version of code to pull."
fi

git clone "${REPOSITORY}" code || error_exit "Failed to clone repository: ${REPOSITORY}"
cd code || error_exit "Failed to enter code folder."
git checkout -b run "${COMMIT}" || error_exit "Failed to check out relevant commitish: ${COMMIT}"
cd "${CODE_FOLDER}" || error_exit "Failed to enter code folder ${CODE_FOLDER}"
echo "Installing code & dependencies..."
python3 -m pip install --user -q . || error_exit "Failed to install Python dependencies."

script="${1}"; shift
which "${script}" >/dev/null 2>&1 || error_exit "Unable to find the required script: ${script}"

if [ -n "$DEBUG" ]; then
  echo "Environment:"
  env
  echo "Get caller identity:"
  aws sts get-caller-identity
fi

# Main task
echo "Running ${script}..."
exec "${script}" "${@}" || error_exit " Failed to execute script."