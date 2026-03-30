#!/bin/sh
set -e

# MODE
: "${PRODUCTION_MODE:?Environment variable PRODUCTION_MODE is required}"
: "${LOGLEVEL:?Environment variable LOGLEVEL is required}"

# DB
: "${POSTGRES_USER:?Environment variable POSTGRES_USER is required}"
: "${POSTGRES_DB:?Environment variable POSTGRES_DB is required}"

# PORT API
: "${PORT_CORE:?Environment variable PORT_CORE is required}"

# CORS DIRECT API
: "${PUBLIC_ORIGINS:?Environment variable PUBLIC_ORIGINS is required}"

# CORS FRONTEND ONLY
: "${PRIVATE_ORIGINS:?Environment variable PRIVATE_ORIGINS is required}"

: "${BASE_UPLOAD_DIR:?Environment variable BASE_UPLOAD_DIR is required}"

: "${PASS_ROOT_USER:?Environment variable PASS_ROOT_USER is required}"
: "${KEY_API_GEMINI:?Environment variable KEY_API_GEMINI is required}"

# echo "================================================="
# echo "  DIAGNOSTIC: PYTHON ENVIRONMENT CHECK"
# echo "================================================="
# echo "Using interpreter: $(which python)"
# python -c 'import sys; from pprint import pprint; pprint(sys.path)'

# ls /api


# If validation passes, run the CMD
exec "$@"
