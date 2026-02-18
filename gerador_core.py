"""
Módulo para geração automática de relatórios técnicos
Usa Google Gemini com Seleção Inteligente de Modelo Gratuito
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
        """Inicializa e encontra o melhor modelo disponível"""
        
        # 1. Configurar API Key
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            try:
                self.api_key = st.secrets["GOOGLE_API_KEY"]
            except:
                raise ValueError("API Key não encontrada! Verifica os Secrets.")
        
        genai.configure(api_key=self.api_key)
        
        # 2. SELEÇÃO "CIRÚRGICA" DO MODELO
        # Vamos listar o que a tua conta vê e escolher um seguro.
        self.model = self._encontrar_modelo_seguro()
    
    def _encontrar_modelo_seguro(self):
        """Procura um modelo gratuito (Flash ou Pro) na lista disponível"""
        modelo_escolhido = 'gemini-pro' # Fallback final
        
        try:
            # Lista todos os modelos disponíveis para a tua chave
            modelos_disponiveis = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_disponiveis.append(m.name)
            
            # Ordem de preferência (Do mais rápido/novo para o antigo)
            # Nota: Ignoramos 'gemini-3' para não estourar a quota
            preferencias = [
                'gemini-1.5-flash',
                'gemini-1.5-flash-001',
                'gemini-1.5-flash-002',
                'gemini-1.5-flash-8b',
                'gemini-pro',
                'gemini-1.0-pro'
            ]
            
            encontrou = False
            for pref in preferencias:
                # O nome na lista vem muitas vezes como "models/gemini-..."
                # Verificamos se a preferência está contida em algum modelo disponível
                for disponivel in modelos_disponiveis:
                    if pref in disponivel:
                        modelo_escolhido = disponivel
                        encontrou = True
                        break
                if encontrou:
                    break
            
            # Mostra na sidebar qual foi o escolhido (para sabermos que funcionou)
            st.sidebar.success(f"🤖 Modelo Conectado: {modelo_escolhido.replace('models/', '')}")
            
        except Exception as e:
            st.sidebar.warning(f"Aviso: Seleção automática falhou ({str(e)}). Usando padrão.")
            
        return genai.GenerativeModel(modelo_escolhido)

    def analisar_scripts(self, scripts_content, contexto=""):
        """Usa Gemini para analisar os scripts"""
        
        scripts_text = "\n\n".join([
            f"=== {script['tipo']}: {script['nome']} ===\n{script['conteudo']}"
            for script in scripts_content
        ])
        
        prompt = f"""Atua como especialista Linux. Analisa e cria JSON.
CONTEXTO: {contexto if contexto else "Serviços Linux"}
SCRIPTS:
{scripts_text}

Gera JSON válido:
{{
    "RESUMO_EXECUTIVO": "Resumo...",
    "METODOLOGIA": "Metodologia...",
    "COMANDOS_DETALHADOS": "Passo a passo...",
    "CHECKLIST_SEGURANCA": "Itens...",
    "DIFICULDADES": "Desafios...",
    "CONCLUSAO": "Conclusão..."
}}"""

        try:
            response = self.model.generate_content(prompt)
            texto = response.text
            texto = re.sub(r'```json\s*|\s*```', '', texto) # Limpar markdown
            
            try:
                return json.loads(texto)
            except:
                return self._parse_resposta_manual(texto)
                
        except Exception as e:
            # Se der erro, mostra exatamente o que falhou
            raise Exception(f"Erro na IA ({self.model.model_name}): {str(e)}")
    
    def _parse_resposta_manual(self, resposta):
        return {
            "RESUMO_EXECUTIVO": "Erro JSON. Ver abaixo.",
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
        
        doc.add_heading(info_projeto['nome_projeto'], 0)
        doc.add_paragraph(f"Autor: {info_projeto['autor']}")
        
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

def gerar_relatorio_streamlit(scripts_content, info_projeto, contexto=""):
    from datetime import datetime
    gerador = GeradorRelatorio()
    output_path = f"/tmp/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return gerador.gerar_relatorio_completo(scripts_content, info_projeto, contexto, output_path)
