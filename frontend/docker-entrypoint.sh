#!/bin/sh
set -e

# Accept API_BASE_URL or VITE_API_BASE_URL from the shared root .env
API_BASE_URL="${API_BASE_URL:-${VITE_API_BASE_URL:-/api}}"

cat > /app/dist/env.js <<EOF
// generated at container start
window.__ENV = {
  API_BASE_URL: "${API_BASE_URL}"
};
EOF

exec serve -s /app/dist -l 80
