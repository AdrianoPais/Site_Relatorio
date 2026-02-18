#!/bin/bash

# Script de Setup Automático do Gerador de Relatórios
# Execute: bash setup.sh

echo "🚀 Gerador Automático de Relatórios - Setup"
echo "==========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "Por favor instala Python 3.8+ antes de continuar"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Instalar dependências
echo "📦 A instalar dependências..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

echo ""

# Verificar .env
if [ ! -f .env ]; then
    echo "⚠️  Ficheiro .env não encontrado!"
    echo ""
    echo "Precisas de criar um ficheiro .env com a tua API key:"
    echo "1. Copia o ficheiro de exemplo:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. Edita .env e adiciona a tua ANTHROPIC_API_KEY"
    echo ""
    echo "Para obter a API key:"
    echo "👉 https://console.anthropic.com/"
    echo ""
else
    echo "✅ Ficheiro .env encontrado"
fi

echo ""
echo "==========================================="
echo "✨ Setup concluído!"
echo ""
echo "Para executar a aplicação:"
echo "  streamlit run gerador_relatorios.py"
echo ""
echo "A aplicação vai abrir no browser automaticamente"
echo "==========================================="
