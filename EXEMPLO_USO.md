# 📋 Exemplo de Uso do Gerador

## Cenário: Relatório DNS + DHCP

### Scripts a Usar:
- `config_dns_bind.sh` - Script de configuração DNS
- `config_dhcp_kea.sh` - Script de configuração DHCP

### Passo a Passo:

#### 1. Abrir a Aplicação
```bash
streamlit run gerador_relatorios.py
```

#### 2. Preencher Informações (Sidebar)
- **Nome do Projeto**: "Implementação de Serviços de Rede"
- **Autor**: "João Silva"
- **Código**: "1234ABCD"
- **Formador**: "Prof. Maria Santos"
- **Data**: (data atual)

#### 3. Upload dos Scripts
- Arrasta `config_dns_bind.sh` para o campo "Script DNS-BIND"
- Arrasta `config_dhcp_kea.sh` para o campo "Script DHCP-KEA"

#### 4. Contexto Adicional (Opcional)
```
Este projeto implementa uma infraestrutura de rede completa
para uma empresa com 50 utilizadores. Inclui servidor DNS 
autoritativo interno e servidor DHCP com reservas para 
dispositivos críticos.
```

#### 5. Gerar Relatório
Clica no botão **"🚀 Gerar Relatório Completo"**

⏱️ Tempo estimado: 2-4 minutos

#### 6. Download
Clica em **"📥 Descarregar Relatório (DOCX)"**

---

## 📄 O Que Vais Receber

Um documento Word profissional com:

### Capa
- Título do projeto
- Síntese
- Nome do autor e código
- Nome do formador

### Conteúdo Completo
1. **Índice** automático
2. **Resumo Executivo** - Visão geral do projeto
3. **Metodologia** - Abordagem seguida
4. **Comandos Utilizados** - Cada comando explicado em detalhe:
   - Passo 1 - Instalação do BIND
   - Passo 2 - Configuração das Zonas
   - Passo 3 - Instalação do KEA
   - ... (todos os passos identificados automaticamente)
5. **Checklist de Segurança** - Medidas implementadas
6. **Dificuldades** - Desafios e soluções
7. **Conclusão** - Resultados e recomendações

### Formatação Profissional
- ✅ Estilos de título consistentes
- ✅ Código formatado adequadamente
- ✅ Margens e espaçamento profissionais
- ✅ Pronto para impressão ou entrega digital

---

## 🎯 Casos de Uso

### Estudantes
- Relatórios de projetos de curso
- Documentação de laboratórios
- Trabalhos práticos

### Profissionais
- Documentação de implementações
- Relatórios para clientes
- Documentação interna

### Formadores
- Material de exemplo para alunos
- Documentação de demonstrações
- Templates de projeto

---

## 💡 Dicas para Melhores Resultados

### Scripts Bem Comentados
```bash
# ✅ BOM
# Passo 1 - Instalação do BIND
echo "A instalar BIND..."
sudo dnf install -y bind bind-utils

# ❌ EVITAR
sudo dnf install -y bind bind-utils
```

### Nomes Descritivos
- ✅ `config_dns_servidor_principal.sh`
- ❌ `script1.sh`

### Contexto Detalhado
Quanto mais contexto deres, mais personalizado fica o relatório!

---

## 📊 Comparação: Manual vs Automático

| Aspecto | Manual | Com Gerador |
|---------|--------|-------------|
| Tempo | 4-6 horas | 3-5 minutos |
| Consistência | Variável | Sempre profissional |
| Formatação | Trabalhosa | Automática |
| Análise Técnica | Manual | IA-powered |
| Retrabalho | Comum | Mínimo |

---

## 🚀 Próximos Passos

1. Experimenta com os teus próprios scripts
2. Ajusta as configurações na sidebar
3. Compara com relatórios que fazias manualmente
4. Feedback? Melhora o prompt no `gerador_core.py`!

**Diverte-te e poupa HORAS de trabalho! ⚡**
