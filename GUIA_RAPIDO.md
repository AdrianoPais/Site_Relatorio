# 🚀 Guia Rápido - 5 Minutos até ao Teu Primeiro Relatório

## ⚡ Setup Ultra-Rápido (Uma Vez)

```bash
# 1. Navega para a pasta
cd caminho/para/gerador_relatorios

# 2. Executa o setup automático
bash setup.sh

# 3. Configura a API Key
cp .env.example .env
nano .env  # ou vim, ou qualquer editor
# Cola a tua API key do Anthropic
```

## 🎯 Usar o Gerador (Sempre)

```bash
# Executar
streamlit run gerador_relatorios.py
```

**O browser vai abrir automaticamente!** 🎉

## 📝 Fluxo de Trabalho

```
1. Arrasta scripts para a interface
   ↓
2. Preenche nome, autor, etc.
   ↓
3. Clica "Gerar Relatório"
   ↓
4. Espera 2-3 minutos ☕
   ↓
5. Download do DOCX pronto! 📄
```

## 🔑 Obter API Key do Anthropic

1. Vai a: https://console.anthropic.com/
2. Clica em **"API Keys"**
3. **"Create Key"** ou copia uma existente
4. Cola no ficheiro `.env`

```bash
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXX...
```

## ✅ Verificar se Está Tudo OK

```bash
# Teste rápido
python3 -c "import streamlit; import anthropic; print('✅ Tudo OK!')"
```

## 🆘 Problemas?

### Erro: `ModuleNotFoundError`
```bash
pip3 install -r requirements.txt
```

### Erro: `ANTHROPIC_API_KEY not found`
```bash
# Verifica o .env
cat .env

# Deve mostrar:
# ANTHROPIC_API_KEY=sk-ant-...
```

### Streamlit não abre
```bash
# Abre manualmente no browser:
# http://localhost:8501
```

## 💡 Dica Pro

Cria um alias no teu `.bashrc` ou `.zshrc`:

```bash
alias relatorio='cd ~/gerador_relatorios && streamlit run gerador_relatorios.py'
```

Depois só precisas de fazer:
```bash
relatorio
```

🎉 **É só isso! Diverte-te a criar relatórios automáticos!**
