"""
Módulo para geração automática de relatórios técnicos
Usa Google Gemini 1.5 Flash (Forçado)
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
        
        # 1. Configurar API Key
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            try:
                self.api_key = st.secrets["GOOGLE_API_KEY"]
            except:
                raise ValueError("API Key não encontrada! Verifica os Secrets.")
        
        genai.configure(api_key=self.api_key)
        
        # 2. CONFIGURAÇÃO DO MODELO
        # Vamos usar o 'gemini-1.5-flash'. 
        # É o modelo mais rápido e com maior quota gratuita atualmente.
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            raise RuntimeError(f"Erro ao inicializar modelo Gemini: {e}")

    def analisar_scripts(self, scripts_content, contexto=""):
        """Usa Gemini para analisar os scripts"""
        
        scripts_text = "\n\n".join([
            f"=== {script['tipo']}: {script['nome']} ===\n{script['conteudo']}"
            for script in scripts_content
        ])
        
        # Prompt otimizado para gastar menos tokens
        prompt = f"""És um sysadmin Linux experiente.
CONTEXTO: {contexto if contexto else "Serviços de Rede Linux"}
CODIGO:
{scripts_text}

Tarefa: Cria um relatório técnico JSON com esta estrutura exata:
{{
    "RESUMO_EXECUTIVO": "Resumo curto e profissional.",
    "METODOLOGIA": "Explicação da abordagem.",
    "COMANDOS_DETALHADOS": "Lista explicada dos principais comandos usados.",
    "CHECKLIST_SEGURANCA": "Pontos de segurança identificados ou recomendados.",
    "DIFICULDADES": "Possíveis pontos de falha ou complexidade.",
    "CONCLUSAO": "Conclusão final."
}}
"""
        try:
            # Configuração para resposta rápida
            response = self.model.generate_content(prompt)
            texto = response.text
            
            # Limpeza cirúrgica do JSON
            texto = re.sub(r'```json\s*|\s*```', '', texto)
            
            try:
                return json.loads(texto)
            except:
                return self._parse_resposta_manual(texto)
                
        except Exception as e:
            raise Exception(f"Erro no Modelo ({self.model.model_name}): {str(e)}")
    
    def _parse_resposta_manual(self, resposta):
        return {
            "RESUMO_EXECUTIVO": "Erro ao processar JSON. Texto gerado abaixo.",
            "METODOLOGIA": "-",
            "COMANDOS_DETALHADOS": resposta,
            "CHECKLIST_SEGURANCA": "-",
            "DIFICULDADES": "-",
            "CONCLUSAO": "-"
        }
    
    def gerar_relatorio_completo(self, scripts_content, info_projeto, contexto="", output_path="relatorio.docx"):
        dados = self.analisar_scripts(scripts_content, contexto)
        doc = Document()
        self._configurar_estilos(doc)
        
        # Capa
        doc.add_heading(info_projeto['nome_projeto'], 0)
        doc.add_paragraph(f"Autor: {info_projeto['autor']}")
        doc.add_paragraph(f"Data: {info_projeto['data']}")
        doc.add_page_break()
        
        # Secções
        mapa = {
            'Resumo Executivo': 'RESUMO_EXECUTIVO',
            'Metodologia': 'METODOLOGIA',
            'Comandos Utilizados': 'COMANDOS_DETALHADOS',
            'Segurança': 'CHECKLIST_SEGURANCA',
            'Dificuldades': 'DIFICULDADES',
            'Conclusão': 'CONCLUSAO'
        }
        
        for titulo, chave in mapa.items():
            doc.add_heading(titulo, 1)
            conteudo = str(dados.get(chave, ''))
            
            if chave == 'CHECKLIST_SEGURANCA':
                for item in conteudo.split('\n'):
                    item = item.strip().lstrip('-•* ')
                    if item:
                        doc.add_paragraph(item, style='List Bullet')
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

def gerar_relatorio_streamlit(scripts_content, info_projeto, contexto=""):
    from datetime import datetime
    gerador = GeradorRelatorio()
    output_path = f"/tmp/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return gerador.gerar_relatorio_completo(scripts_content, info_projeto, contexto, output_path)
