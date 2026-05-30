#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python -c "
import os, sys
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "PostgreSQL unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is ready"

python scripts/seed.py
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
