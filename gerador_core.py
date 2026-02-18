"""
Módulo para geração automática de relatórios técnicos
Usa Google Gemini API (com auto-descoberta de modelo)
"""

import google.generativeai as genai
import os
import json
import re
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import streamlit as st  # Importante para mostrar erros na sidebar se necessário

class GeradorRelatorio:
    def __init__(self, api_key=None):
        """Inicializa o gerador com a API key do Google e descobre o modelo"""
        # 1. Configurar API Key
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            # Tenta buscar aos secrets do Streamlit se não estiver no env
            try:
                self.api_key = st.secrets["GOOGLE_API_KEY"]
            except:
                raise ValueError("API Key não encontrada! Verifica os Secrets do Streamlit.")
        
        genai.configure(api_key=self.api_key)
        
        # 2. AUTO-DESCOBERTA DE MODELO (A Magia acontece aqui)
        # Em vez de adivinhar o nome, vamos perguntar à API o que ela tem.
        modelo_para_usar = 'gemini-1.5-flash' # Fallback padrão
        
        try:
            modelos_disponiveis = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_disponiveis.append(m.name)
            
            # Tenta encontrar o melhor modelo na lista
            # Ordem de preferência: Flash (rápido) -> Pro (padrão) -> Qualquer outro
            encontrado = None
            for m in modelos_disponiveis:
                if 'gemini-1.5-flash' in m:
                    encontrado = m
                    break
            
            if not encontrado:
                for m in modelos_disponiveis:
                    if 'gemini-pro' in m:
                        encontrado = m
                        break
            
            if encontrado:
                modelo_para_usar = encontrado
                # Descomenta a linha abaixo se quiseres ver qual foi escolhido na sidebar
                # st.sidebar.success(f"Modelo conectado: {modelo_para_usar}")
                
        except Exception as e:
            # Se a listagem falhar, usa o padrão e reza
            print(f"Aviso: Não foi possível listar modelos. Usando {modelo_para_usar}")

        self.model = genai.GenerativeModel(modelo_para_usar)
    
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
            response = self.model.generate_content(prompt)
            texto = response.text
            
            # Limpeza do JSON
            texto = re.sub(r'```json\s*|\s*```', '', texto)
            
            try:
                return json.loads(texto)
            except:
                return self._parse_resposta_manual(texto)
                
        except Exception as e:
            raise Exception(f"Erro Gemini: {str(e)}")
    
    def _parse_resposta_manual(self, resposta):
        return {
            "RESUMO_EXECUTIVO": "Erro no formato JSON. Conteúdo gerado abaixo.",
            "METODOLOGIA": "Ver conteúdo.",
            "COMANDOS_DETALHADOS": resposta,
            "CHECKLIST_SEGURANCA": "Verificar manualmente",
            "DIFICULDADES": "-",
            "CONCLUSAO": "-"
        }
    
    def gerar_relatorio_completo(self, scripts_content, info_projeto, contexto="", output_path="relatorio.docx"):
        dados = self.analisar_scripts(scripts_content, contexto)
        
        doc = Document()
        self._configurar_estilos(doc)
        
        # Estrutura simples do documento
        doc.add_heading(info_projeto['nome_projeto'], 0)
        doc.add_paragraph(f"Autor: {info_projeto['autor']}")
        doc.add_paragraph("\n")
        
        mapa = {
            'Resumo Executivo': 'RESUMO_EXECUTIVO',
            'Metodologia': 'METODOLOGIA',
            'Comandos': 'COMANDOS_DETALHADOS',
            'Segurança': 'CHECKLIST_SEGURANCA',
            'Dificuldades': 'DIFICULDADES',
            'Conclusão': 'CONCLUSAO'
        }
        
        for titulo, chave in mapa.items():
            doc.add_heading(titulo, 1)
            doc.add_paragraph(str(dados.get(chave, '')))
            
        doc.save(output_path)
        return output_path

    def _configurar_estilos(self, doc):
        styles = doc.styles
        if 'Code' not in [s.name for s in styles]:
            style = styles.add_style('Code', WD_STYLE_TYPE.PARAGRAPH)
            style.font.name = 'Courier New'
            style.font.size = Pt(9)

# Função Wrapper para o Streamlit usar
def gerar_relatorio_streamlit(scripts_content, info_projeto, contexto=""):
    from datetime import datetime
    gerador = GeradorRelatorio()
    output_path = f"/tmp/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return gerador.gerar_relatorio_completo(scripts_content, info_projeto, contexto, output_path)
