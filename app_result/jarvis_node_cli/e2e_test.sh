#!/bin/bash
# E2E Test para Jarvis Node Manager CLI
set -e

echo "🚀 Iniciando pruebas End-to-End para jarvis-node-cli..."

# Exportar PYTHONPATH para que Python encuentre el módulo
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 1. Test comando 'info'
echo "[1/3] Probando comando 'info'..."
python3 -m app_result.jarvis_node_cli.cli info

# 2. Test comando 'register'
echo "[2/3] Probando comando 'register'..."
python3 -m app_result.jarvis_node_cli.cli register --output app_result/jarvis_node_cli/e2e_ledger.json
if [ -f "app_result/jarvis_node_cli/e2e_ledger.json" ]; then
    echo "✅ Ledger generado correctamente."
else
    echo "❌ Fallo al generar el ledger."
    exit 1
fi

# 3. Test comando 'check'
echo "[3/3] Probando comando 'check'..."
python3 -m app_result.jarvis_node_cli.cli check

echo "✨ Todas las pruebas E2E han pasado exitosamente (Costo: 0 tokens)."
