"""
Módulo para geração automática de relatórios técnicos
Usa Google Gemini API para analisar scripts e python-docx para gerar o documento
"""

import google.generativeai as genai
import os
import json
import re
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

class GeradorRelatorio:
    def __init__(self, api_key=None):
        """Inicializa o gerador com a API key do Google"""
        # Tenta obter a chave do argumento ou da variável de ambiente (suporta ambos os nomes)
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("API Key não encontrada! Define GOOGLE_API_KEY no ficheiro .env")
        
        genai.configure(api_key=self.api_key)
        # Configuração do modelo
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analisar_scripts(self, scripts_content, contexto=""):
        """
        Usa Gemini para analisar os scripts e gerar conteúdo estruturado
        """
        
        scripts_text = "\n\n".join([
            f"=== {script['tipo']}: {script['nome']} ===\n{script['conteudo']}"
            for script in scripts_content
        ])
        
        prompt = f"""Atua como um especialista em infraestrutura Linux e redes. Analisa os scripts bash fornecidos e gera um relatório técnico.

CONTEXTO DO PROJETO:
{contexto if contexto else "Implementação de serviços Linux (DNS-BIND e DHCP-KEA)"}

SCRIPTS A ANALISAR:
{scripts_text}

Gera um JSON válido com a seguinte estrutura exata (sem formatação Markdown ```json):
{{
    "RESUMO_EXECUTIVO": "Texto do resumo...",
    "METODOLOGIA": "Texto da metodologia...",
    "COMANDOS_DETALHADOS": "Texto explicativo passo a passo...",
    "CHECKLIST_SEGURANCA": "Lista de itens de segurança (separados por quebras de linha)...",
    "DIFICULDADES": "Texto sobre dificuldades...",
    "CONCLUSAO": "Texto da conclusão..."
}}

Requisitos de conteúdo:
1. RESUMO_EXECUTIVO: Objetivos e resultados.
2. METODOLOGIA: Abordagem seguida (2-3 parágrafos).
3. COMANDOS_DETALHADOS: Para cada script, lista e explica comandos principais (Formato: 'Passo X - Título [quebra de linha] O que faz: ... [quebra de linha] Comando: ...').
4. CHECKLIST_SEGURANCA: Medidas de segurança (Firewall, permissões, validação de sintaxe).
5. DIFICULDADES: Desafios e soluções.
6. CONCLUSAO: Conclusão profissional.

Escreve em Português de Portugal (PT-PT). Sê técnico e profissional."""

        try:
            # Chamada à API do Gemini
            response = self.model.generate_content(prompt)
            texto_resposta = response.text
            
            # Limpeza para garantir que é JSON válido (remove ```json e ``` se existirem)
            texto_limpo = re.sub(r'```json\s*|\s*```', '', texto_resposta)
            
            try:
                dados = json.loads(texto_limpo)
            except json.JSONDecodeError:
                # Fallback se o JSON falhar
                dados = self._parse_resposta_manual(texto_resposta)
            
            return dados
            
        except Exception as e:
            raise Exception(f"Erro ao analisar scripts com Gemini: {str(e)}")
    
    def _parse_resposta_manual(self, resposta):
        """Fallback básico"""
        return {
            "RESUMO_EXECUTIVO": "Ocorreu um erro na formatação automática. Resumo do conteúdo gerado abaixo.",
            "METODOLOGIA": "Ver conteúdo detalhado.",
            "COMANDOS_DETALHADOS": resposta,
            "CHECKLIST_SEGURANCA": "• Verificar configurações manualmente",
            "DIFICULDADES": "Não foi possível estruturar automaticamente.",
            "CONCLUSAO": "Análise concluída."
        }
    
    def gerar_documento(self, dados_relatorio, info_projeto, output_path="relatorio.docx"):
        """Gera o documento DOCX (Lógica mantida igual ao original)"""
        doc = Document()
        self._configurar_estilos(doc)
        
        # CAPA
        self._adicionar_capa(doc, info_projeto)
        doc.add_page_break()
        
        # ÍNDICE
        doc.add_heading('Índice', 0)
        doc.add_paragraph('[O índice deve ser atualizado no Word: Referências > Índice]')
        doc.add_page_break()
        
        # SECÇÕES
        seccoes = [
            ('Resumo Executivo', 'RESUMO_EXECUTIVO'),
            ('Metodologia', 'METODOLOGIA'),
            ('Comandos Utilizados', 'COMANDOS_DETALHADOS'),
            ('Checklist de Segurança', 'CHECKLIST_SEGURANCA'),
            ('Dificuldades', 'DIFICULDADES'),
            ('Conclusão', 'CONCLUSAO')
        ]

        for titulo, chave in seccoes:
            doc.add_heading(titulo, 1)
            conteudo = dados_relatorio.get(chave, '')
            
            if chave == 'COMANDOS_DETALHADOS':
                self._adicionar_comandos(doc, conteudo)
            elif chave == 'CHECKLIST_SEGURANCA':
                for item in conteudo.split('\n'):
                    if item.strip():
                        item_limpo = item.strip().lstrip('•- ')
                        doc.add_paragraph(item_limpo, style='List Bullet')
            else:
                doc.add_paragraph(conteudo)
            
            if chave != 'CONCLUSAO':
                doc.add_page_break()
        
        doc.save(output_path)
        return output_path
    
    def _configurar_estilos(self, doc):
        styles = doc.styles
        if 'Code' not in [s.name for s in styles]:
            code_style = styles.add_style('Code', WD_STYLE_TYPE.PARAGRAPH)
            code_font = code_style.font
            code_font.name = 'Courier New'
            code_font.size = Pt(9)
    
    def _adicionar_capa(self, doc, info):
        titulo = doc.add_heading(info['nome_projeto'], 0)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("\n\n")
        
        sintese = doc.add_heading('SÍNTESE', level=2)
        sintese.alignment = WD_ALIGN_PARAGRAPH.CENTER
        texto_sintese = doc.add_paragraph(
            'Este Projeto consistiu na realização de scripts Bash com o objetivo '
            'da configuração de uma infraestrutura de rede completa.'
        )
        texto_sintese.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        doc.add_paragraph("\n\n")
        
        autor_para = doc.add_paragraph()
        autor_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        autor_run = autor_para.add_run(f"Autor: {info['autor']}\nN.º: {info['codigo']}")
        autor_run.bold = True
        
        formador_para = doc.add_paragraph()
        formador_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        formador_para.add_run(f"Formador: {info['formador']}").italic = True
        
        data_para = doc.add_paragraph()
        data_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        data_para.add_run(f"Data: {info['data'].strftime('%d/%m/%Y')}")

    def _adicionar_comandos(self, doc, comandos_text):
        # Tenta separar por "Passo"
        partes = re.split(r'(Passo \d+)', comandos_text)
        
        for parte in partes:
            if not parte.strip(): continue
            
            if parte.strip().startswith("Passo"):
                doc.add_heading(parte.strip(), 2)
            else:
                linhas = parte.strip().split('\n')
                for linha in linhas:
                    if linha.strip():
                        if "Comando:" in linha or linha.strip().startswith('$') or linha.strip().startswith('sudo'):
                            p = doc.add_paragraph(linha.strip(), style='Code')
                        else:
                            p = doc.add_paragraph(linha.strip())

    def gerar_relatorio_completo(self, scripts_content, info_projeto, contexto="", output_path="relatorio.docx"):
        dados = self.analisar_scripts(scripts_content, contexto)
        return self.gerar_documento(dados, info_projeto, output_path)

def gerar_relatorio_streamlit(scripts_content, info_projeto, contexto=""):
    gerador = GeradorRelatorio()
    output_path = f"/tmp/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    return gerador.gerar_relatorio_completo(scripts_content, info_projeto, contexto, output_path)

from datetime import datetime
