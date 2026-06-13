#!/bin/bash
set -e

if [ -z "${TELEGRAM_BOT_TOKEN}" ]; then
  echo "ERROR: TELEGRAM_BOT_TOKEN is required"
  exit 1
fi

mkdir -p /root/.hermes
cp /app/infra/hermes/SOUL.md /root/.hermes/SOUL.md || true
rm -f /root/.hermes/.env
cat > /root/.hermes/.env <<EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
GATEWAY_ALLOW_ALL_USERS=${GATEWAY_ALLOW_ALL_USERS:-false}
EOF


if [ -n "${GEMINI_API_KEY}" ]; then
  CLEAN_KEY=$(echo "${GEMINI_API_KEY}" | sed -E 's/^[a-zA-Z0-9_]+://')
  echo "GEMINI_API_KEY=${CLEAN_KEY}" >> /root/.hermes/.env
fi

if [ -n "${DATABASE_URL}" ]; then
  echo "DATABASE_URL=${DATABASE_URL}" >> /root/.hermes/.env
fi
if [ -n "${NODE_ID}" ]; then
  echo "NODE_ID=${NODE_ID}" >> /root/.hermes/.env
fi
if [ -n "${NODE_TOKEN}" ]; then
  CLEAN_TOKEN=$(echo "${NODE_TOKEN}" | sed -E 's/^[a-zA-Z0-9_]+://')
  echo "NODE_TOKEN=${CLEAN_TOKEN}" >> /root/.hermes/.env
fi


if [ -n "${GEMINI_API_KEYS}" ]; then
  echo "GEMINI_API_KEYS=${GEMINI_API_KEYS}" >> /root/.hermes/.env
fi

if [ -n "${GOOGLE_API_KEY}" ]; then
  CLEAN_KEY=$(echo "${GOOGLE_API_KEY}" | sed -E 's/^[a-zA-Z0-9_]+://')
  echo "GOOGLE_API_KEY=${CLEAN_KEY}" >> /root/.hermes/.env
fi

if [ -n "${GOOGLE_API_KEYS}" ]; then
  echo "GOOGLE_API_KEYS=${GOOGLE_API_KEYS}" >> /root/.hermes/.env
fi

if [ -n "${API_KEY_LIMITS}" ]; then
  echo "API_KEY_LIMITS=${API_KEY_LIMITS}" >> /root/.hermes/.env
fi

if [ -n "${TELEGRAM_ALLOWED_USERS}" ]; then
  echo "TELEGRAM_ALLOWED_USERS=${TELEGRAM_ALLOWED_USERS}" >> /root/.hermes/.env
fi

chmod 600 /root/.hermes/.env

hermes config set model.provider gemini || true
hermes config set model.default gemini-3.5-flash || true
hermes config set model.base_url https://generativelanguage.googleapis.com/v1beta/openai || true

# Auto-configure fallback chain if not present
/usr/local/lib/hermes-agent/venv/bin/python3 -c "
import yaml
path = '/root/.hermes/config.yaml'
try:
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    if 'fallback_providers' not in cfg or not cfg['fallback_providers']:
        cfg['fallback_providers'] = [
            {'provider': 'gemini', 'model': 'gemini-3.1-flash-lite', 'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai'},
            {'provider': 'gemini', 'model': 'gemini-2.5-flash-lite', 'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai'}
        ]
        with open(path, 'w') as f:
            yaml.safe_dump(cfg, f, default_flow_style=False)
except Exception:
    pass
" || true


if [ "$#" -gt 0 ]; then
  exec "$@"
else
  exec hermes gateway run
fi
