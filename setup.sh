#!/bin/bash

echo "🚀 Configurando PersonajeIA..."

# Instalar dependencias Node.js
echo "📦 Instalando dependencias frontend..."
cd frontend
npm install

echo "📦 Instalando dependencias backend Node.js..."
cd ../backend-node
npm install

# Instalar dependencias Python
echo "🐍 Instalando dependencias backend Python..."
cd ../backend-python
pip install -r requirements.txt

# Verificar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg no encontrado. Instálalo desde https://ffmpeg.org/download.html"
else
    echo "✅ FFmpeg encontrado"
fi

echo "🎉 Configuración completa!"
echo ""
echo "Para ejecutar:"
echo "1. Backend Python: cd backend-python && uvicorn main:app --reload"
echo "2. Backend Node.js: cd backend-node && npm start"
echo "3. Frontend: cd frontend && npm start"