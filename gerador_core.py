"""
Módulo para geração automática de relatórios técnicos
Usa Google Gemini 1.5 Flash (Versão Fixa e Rápida)
"""

import google.generativeai as genai
import os
import json
import re
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import streamlit as st

class GeradorRelatorio:
    def __init__(self, api_key=None):
        """Inicializa o gerador com a API key do Google"""
        
        # 1. Configurar API Key (Prioridade: Argumento > Env > Secrets)
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        
        if not self.api_key:
            try:
                self.api_key = st.secrets["GOOGLE_API_KEY"]
            except:
                raise ValueError("API Key não encontrada! Verifica os Secrets do Streamlit.")
        
        genai.configure(api_key=self.api_key)
        
        # 2. DEFINIÇÃO DIRETA DO MODELO
        # Não vamos mais tentar adivinhar. Vamos usar o Flash diretamente.
        # Este modelo é rápido e tem uma quota gratuita generosa.
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            # Fallback de último recurso para o modelo legado
            self.model = genai.GenerativeModel('gemini-pro')
    
    def analisar_scripts(self, scripts_content, contexto=""):
        """Usa Gemini para analisar os scripts"""
        
        scripts_text = "\n\n".join([
            f"=== {script['tipo']}: {script['nome']} ===\n{script['conteudo']}"
            for script in scripts_content
        ])
        
        prompt = f"""Atua como um especialista em infraestrutura Linux. Analisa os scripts e gera um JSON.

CONTEXTO: {contexto if contexto else "Serviços Linux"}

SCRIPTS:
{scripts_text}

Gera APENAS um JSON válido (sem markdown) com estas chaves:
{{
    "RESUMO_EXECUTIVO": "Resumo do projeto...",
    "METODOLOGIA": "Como foi feito...",
    "COMANDOS_DETALHADOS": "Explicação passo a passo...",
    "CHECKLIST_SEGURANCA": "Itens de segurança...",
    "DIFICULDADES": "Desafios...",
    "CONCLUSAO": "Conclusão..."
}}
"""
        try:
            # Configuração para resposta mais criativa mas segura
            response = self.model.generate_content(prompt)
            texto = response.text
            
            # Limpeza do JSON (remove ```json se existir)
            texto = re.sub(r'```json\s*|\s*```', '', texto)
            
            try:
                return json.loads(texto)
            except:
                return self._parse_resposta_manual(texto)
                
        except Exception as e:
            # Se der erro de quota ou modelo, lança exceção clara
            raise Exception(f"Erro Gemini: {str(e)}")
    
    def _parse_resposta_manual(self, resposta):
        return {
            "RESUMO_EXECUTIVO": "Ocorreu um erro na formatação JSON. O conteúdo foi gerado abaixo.",
            "METODOLOGIA": "Consultar secção de comandos.",
            "COMANDOS_DETALHADOS": resposta,
            "CHECKLIST_SEGURANCA": "Verificar scripts manualmente",
            "DIFICULDADES": "Não processado",
            "CONCLUSAO": "Não processado"
        }
    
    def gerar_relatorio_completo(self, scripts_content, info_projeto, contexto="", output_path="relatorio.docx"):
        # 1. Obter dados do AI
        dados = self.analisar_scripts(scripts_content, contexto)
        
        # 2. Criar Documento
        doc = Document()
        self._configurar_estilos(doc)
        
        # Capa Simples
        doc.add_heading(info_projeto['nome_projeto'], 0)
        p = doc.add_paragraph()
        p.add_run(f"Autor: {info_projeto['autor']}\n").bold = True
        p.add_run(f"Data: {info_projeto['data']}")
        doc.add_page_break()
        
        # Conteúdo
        mapa = {
            'Resumo Executivo': 'RESUMO_EXECUTIVO',
            'Metodologia': 'METODOLOGIA',
            'Comandos Utilizados': 'COMANDOS_DETALHADOS',
            'Checklist de Segurança': 'CHECKLIST_SEGURANCA',
            'Dificuldades': 'DIFICULDADES',
            'Conclusão': 'CONCLUSAO'
        }
        
        for titulo, chave in mapa.items():
            doc.add_heading(titulo, 1)
            conteudo = str(dados.get(chave, ''))
            
            # Formatação especial para comandos ou listas
            if chave == 'CHECKLIST_SEGURANCA':
                for item in conteudo.split('\n'):
                    if item.strip():
                        doc.add_paragraph(item.strip(), style='List Bullet')
            else:
                doc.add_paragraph(conteudo)
            
        doc.save(output_path)
        return output_path

    def _configurar_estilos(self, doc):
        styles = doc.styles
        if 'Code' not in [s.name for s in styles]:
            style = styles.add_style('Code', WD_STYLE_TYPE.PARAGRAPH)
            style.font.name = 'Courier New'
            style.font.size = Pt(9)

# Wrapper para o Streamlit
def gerar_relatorio_streamlit(scripts_content, info_projeto, contexto=""):
    from datetime import datetime
    gerador = GeradorRelatorio()
    output_path = f"/tmp/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return gerador.gerar_relatorio_completo(scripts_content, info_projeto, contexto, output_path)
