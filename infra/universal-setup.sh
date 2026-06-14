#!/bin/bash
# SWARMTEAM OS: UNIVERSAL SETUP SCRIPT (v1.0)
# Para Ubuntu Server (Pentium), Local Desktop o Codespaces.

set -e

echo "🤖 SwarmTeam OS: Iniciando instalación del chasis físico..."

# 1. Detección de Entorno
ARCH=$(uname -m)
OS=$(lsb_release -is)
echo "📍 Detectado: $OS on $ARCH"

# 2. Instalación de Dependencias Base
sudo apt update
sudo apt install -y curl git python3-pip python3-venv npm nodejs

# 3. Instalación de Hermes Agent (Core del Sistema)
if ! command -v hermes &> /dev/null; then
    echo "📦 Instalando Hermes Agent via NousResearch..."
    curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
    # Añadir al PATH para esta sesión
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "✅ Hermes ya está instalado."
fi

# 4. Preparación del Entorno Virtual de Python
echo "🐍 Configurando entorno de Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Configuración de Docker (Si no existe)
if ! command -v docker &> /dev/null; then
    echo "🐳 Instalando Docker..."
    sudo apt install -y docker.io docker-compose-v2
    sudo usermod -aG docker $USER
    echo "⚠️ Docker instalado. Por favor, reinicia sesión después del setup para usarlo sin sudo."
fi

# 6. Inicialización de Memoria SGA (Solo si es Pentium/Servidor)
if [[ "$1" == "--server" ]]; then
    echo "🧠 Levantando Memoria SGA (PostgreSQL + pgvector)..."
    docker compose up -d postgres sga
fi

echo "✨ SETUP COMPLETADO."
echo "Próximos pasos:"
echo "1) Configura tus API Keys en 'config/api_orchestrator.json'"
echo "2) Lanza Jarvis con: python jarvis.py"
