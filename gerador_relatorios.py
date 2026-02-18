import streamlit as st
import os
from datetime import datetime
from gerador_core import gerar_relatorio_streamlit

# Configuração da página
st.set_page_config(
    page_title="Gerador Automático de Relatórios Técnicos",
    page_icon="📋",
    layout="wide"
)

# CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E75B6;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E75B6;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        border-left: 5px solid #2E75B6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📋 Gerador Automático de Relatórios Técnicos</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <strong>Como funciona:</strong><br>
    1️⃣ Faz upload dos teus scripts bash (.sh)<br>
    2️⃣ Preenche as informações do projeto<br>
    3️⃣ Clica em "Gerar Relatório"<br>
    4️⃣ Descarrega o documento DOCX pronto! ✨
</div>
""", unsafe_allow_html=True)

# Sidebar com informações do projeto
st.sidebar.markdown("### 📝 Informações do Projeto")

nome_projeto = st.sidebar.text_input("Nome do Projeto", "Desenvolvimento e Implementação de Serviços Linux")
autor = st.sidebar.text_input("Autor", "Sérgio Correia")
codigo_aluno = st.sidebar.text_input("Código de Aluno", "0925GRSC")
formador = st.sidebar.text_input("Formador", "Dário Quental")
data_projeto = st.sidebar.date_input("Data do Projeto", datetime.now())

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Configurações Avançadas")
incluir_checklist = st.sidebar.checkbox("Incluir Checklist de Segurança", value=True)
incluir_dificuldades = st.sidebar.checkbox("Incluir Secção de Dificuldades", value=True)
incluir_anexos = st.sidebar.checkbox("Incluir Anexos", value=True)

# Área principal - Upload de scripts
st.markdown('<div class="section-header">📤 Upload de Scripts</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Script DNS-BIND**")
    dns_script = st.file_uploader("Carrega o script DNS (.sh)", type=['sh', 'txt'], key="dns")
    if dns_script:
        st.success(f"✅ {dns_script.name} carregado!")
        
with col2:
    st.markdown("**Script DHCP-KEA**")
    dhcp_script = st.file_uploader("Carrega o script DHCP (.sh)", type=['sh', 'txt'], key="dhcp")
    if dhcp_script:
        st.success(f"✅ {dhcp_script.name} carregado!")

# Área para scripts adicionais
st.markdown("**Scripts Adicionais (opcional)**")
scripts_adicionais = st.file_uploader(
    "Podes carregar scripts extras aqui", 
    type=['sh', 'txt', 'conf', 'json'],
    accept_multiple_files=True,
    key="extras"
)

if scripts_adicionais:
    st.info(f"📂 {len(scripts_adicionais)} ficheiro(s) adicional(is) carregado(s)")

# Notas adicionais
st.markdown('<div class="section-header">📝 Informações Adicionais</div>', unsafe_allow_html=True)

contexto_extra = st.text_area(
    "Contexto ou observações adicionais para o relatório (opcional)",
    height=150,
    placeholder="Ex: Este projeto foi desenvolvido para uma infraestrutura de rede empresarial..."
)

# Botão para gerar relatório
st.markdown("---")

if st.button("🚀 Gerar Relatório Completo", type="primary", use_container_width=True):
    if not dns_script and not dhcp_script and not scripts_adicionais:
        st.error("❌ Por favor, carrega pelo menos um script!")
    else:
        with st.spinner("🔄 A analisar scripts e a gerar relatório... Isto pode demorar alguns minutos..."):
            try:
                # Preparar conteúdo dos scripts
                scripts_content = []
                
                if dns_script:
                    dns_content = dns_script.read().decode('utf-8')
                    scripts_content.append({
                        'nome': dns_script.name,
                        'tipo': 'DNS-BIND',
                        'conteudo': dns_content
                    })
                
                if dhcp_script:
                    dhcp_content = dhcp_script.read().decode('utf-8')
                    scripts_content.append({
                        'nome': dhcp_script.name,
                        'tipo': 'DHCP-KEA',
                        'conteudo': dhcp_content
                    })
                
                for script in scripts_adicionais:
                    content = script.read().decode('utf-8')
                    scripts_content.append({
                        'nome': script.name,
                        'tipo': 'Adicional',
                        'conteudo': content
                    })
                
                # Preparar informações do projeto
                info_projeto = {
                    'nome_projeto': nome_projeto,
                    'autor': autor,
                    'codigo': codigo_aluno,
                    'formador': formador,
                    'data': data_projeto
                }
                
                # GERAR O RELATÓRIO!
                output_path = gerar_relatorio_streamlit(
                    scripts_content,
                    info_projeto,
                    contexto_extra
                )
                
                st.markdown("""
                <div class="success-box">
                    <strong>✅ Relatório gerado com sucesso!</strong><br><br>
                    O teu relatório técnico está pronto para download. Inclui:<br>
                    • Resumo Executivo profissional<br>
                    • Metodologia detalhada<br>
                    • Explicação de todos os comandos<br>
                    • Checklist de segurança<br>
                    • Conclusão e recomendações<br><br>
                    <strong>Clica no botão abaixo para descarregar!</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão de download do DOCX
                with open(output_path, 'rb') as f:
                    st.download_button(
                        label="📥 Descarregar Relatório (DOCX)",
                        data=f,
                        file_name=f"Relatorio_{nome_projeto.replace(' ', '_')}_{data_projeto.strftime('%Y%m%d')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                
            except Exception as e:
                st.error(f"❌ Erro ao processar scripts: {str(e)}")
                st.exception(e)  # Mostrar traceback completo para debug

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>Gerador Automático de Relatórios Técnicos</strong></p>
        <p>Desenvolvido para automatizar a criação de documentação profissional de projetos técnicos</p>
        <p>Versão 1.0 - Beta</p>
    </div>
""", unsafe_allow_html=True)
