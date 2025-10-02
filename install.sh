#!/bin/bash

echo "🏥 Bot de Ortopedia para WhatsApp - Instalación"
echo "=============================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Copiar template de .env
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.template .env
    echo "⚠️  Por favor, edita el archivo .env con tus credenciales"
fi

echo ""
echo "=============================================="
echo "✅ Instalación completada!"
echo ""
echo "Próximos pasos:"
echo "1. Edita el archivo .env con tus credenciales"
echo "2. Ejecuta: python bot_ortopedia.py"
echo ""
