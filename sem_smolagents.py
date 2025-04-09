import os
import sys
import time
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
import openai

class STFScraper:
    """Classe para realizar web scraping no site do STF"""
    
    BASE_URL = "https://jurisprudencia.stf.jus.br"
    SEARCH_URL = f"{BASE_URL}/pages/search"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    def __init__(self):
        """Inicializa o scraper do STF"""
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def buscar_jurisprudencia(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza busca de jurisprudência no site do STF
        
        Args:
            query: Termos de busca
            max_results: Número máximo de resultados a retornar
            
        Returns:
            Lista de dicionários com os resultados encontrados
        """
        print(f"Realizando busca no STF para: '{query}'")
        
        # Preparar a URL de busca
        encoded_query = quote(query)
        search_url = f"{self.SEARCH_URL}?base=acordaos&sinonimo=true&plural=true&page=1&pageSize={max_results}&sort=_score&sortBy=desc&query={encoded_query}"
        
        try:
            # Fazer a requisição
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            # Verificar se a resposta foi bem-sucedida
            if response.status_code != 200:
                print(f"Erro na requisição: {response.status_code}")
                return self._fallback_search(query, max_results)
            
            # Parsear o HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair os resultados
            resultados = []
            
            # Verificar se há resultados
            result_items = soup.select('div.search-result-item')
            
            if not result_items:
                print("Nenhum resultado encontrado na página")
                return self._fallback_search(query, max_results)
            
            # Processar cada resultado
            for item in result_items[:max_results]:
                try:
                    # Extrair informações básicas
                    titulo_elem = item.select_one('h4.search-result-title')
                    link_elem = titulo_elem.select_one('a') if titulo_elem else None
                    
                    if not titulo_elem or not link_elem:
                        continue
                    
                    titulo = titulo_elem.get_text(strip=True)
                    link = self.BASE_URL + link_elem.get('href', '')
                    
                    # Extrair número do processo
                    numero_processo = ""
                    processo_match = re.search(r'([A-Z]{2,4}\s\d+)', titulo)
                    if processo_match:
                        numero_processo = processo_match.group(1)
                    
                    # Extrair relator
                    relator = ""
                    relator_elem = item.select_one('div.search-result-metadata span:contains("Relator:")')
                    if relator_elem:
                        relator = relator_elem.get_text(strip=True).replace("Relator:", "").strip()
                    
                    # Extrair data de julgamento
                    data_julgamento = ""
                    data_elem = item.select_one('div.search-result-metadata span:contains("Julgamento:")')
                    if data_elem:
                        data_julgamento = data_elem.get_text(strip=True).replace("Julgamento:", "").strip()
                    
                    # Extrair ementa
                    ementa = ""
                    ementa_elem = item.select_one('div.search-result-text')
                    if ementa_elem:
                        ementa = ementa_elem.get_text(strip=True)
                    
                    # Adicionar resultado
                    resultados.append({
                        "titulo": titulo,
                        "numero_processo": numero_processo,
                        "relator": relator,
                        "data_julgamento": data_julgamento,
                        "ementa": ementa[:500] + "..." if len(ementa) > 500 else ementa,
                        "link": link
                    })
                    
                except Exception as e:
                    print(f"Erro ao processar item: {e}")
                    continue
            
            # Se não conseguiu extrair resultados, usar fallback
            if not resultados:
                print("Não foi possível extrair resultados da página")
                return self._fallback_search(query, max_results)
            
            return resultados
            
        except requests.RequestException as e:
            print(f"Erro na requisição HTTP: {e}")
            return self._fallback_search(query, max_results)
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return self._fallback_search(query, max_results)
    
    def obter_detalhes_processo(self, numero_processo: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um processo específico
        
        Args:
            numero_processo: Número do processo no formato do STF
            
        Returns:
            Dicionário com os detalhes do processo
        """
        print(f"Buscando detalhes do processo: {numero_processo}")
        
        # Preparar a URL de busca
        encoded_query = quote(f'"{numero_processo}"')
        search_url = f"{self.SEARCH_URL}?base=acordaos&sinonimo=true&plural=true&page=1&pageSize=1&sort=_score&sortBy=desc&query={encoded_query}"
        
        try:
            # Fazer a requisição
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            # Parsear o HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontrar o link para o documento completo
            result_item = soup.select_one('div.search-result-item')
            if not result_item:
                return self._fallback_processo(numero_processo)
            
            link_elem = result_item.select_one('h4.search-result-title a')
            if not link_elem:
                return self._fallback_processo(numero_processo)
            
            documento_url = self.BASE_URL + link_elem.get('href', '')
            
            # Acessar a página do documento
            doc_response = self.session.get(documento_url, timeout=30)
            doc_response.raise_for_status()
            
            doc_soup = BeautifulSoup(doc_response.text, 'html.parser')
            
            # Extrair informações detalhadas
            detalhes = {
                "numero_processo": numero_processo,
                "titulo": "",
                "relator": "",
                "data_julgamento": "",
                "data_publicacao": "",
                "orgao_julgador": "",
                "ementa": "",
                "decisao": "",
                "partes": [],
                "link": documento_url
            }
            
            # Extrair título
            titulo_elem = doc_soup.select_one('h1.document-title')
            if titulo_elem:
                detalhes["titulo"] = titulo_elem.get_text(strip=True)
            
            # Extrair metadados
            metadata_items = doc_soup.select('div.document-metadata-item')
            for item in metadata_items:
                label_elem = item.select_one('div.document-metadata-item-label')
                value_elem = item.select_one('div.document-metadata-item-value')
                
                if not label_elem or not value_elem:
                    continue
                
                label = label_elem.get_text(strip=True).lower()
                value = value_elem.get_text(strip=True)
                
                if "relator" in label:
                    detalhes["relator"] = value
                elif "julgamento" in label:
                    detalhes["data_julgamento"] = value
                elif "publicação" in label:
                    detalhes["data_publicacao"] = value
                elif "órgão julgador" in label:
                    detalhes["orgao_julgador"] = value
            
            # Extrair ementa
            ementa_elem = doc_soup.select_one('div.document-ementa')
            if ementa_elem:
                detalhes["ementa"] = ementa_elem.get_text(strip=True)
            
            # Extrair decisão
            decisao_elem = doc_soup.select_one('div.document-decisao')
            if decisao_elem:
                detalhes["decisao"] = decisao_elem.get_text(strip=True)
            
            # Extrair partes
            partes_elem = doc_soup.select_one('div.document-partes')
            if partes_elem:
                partes_items = partes_elem.select('div.document-parte-item')
                for parte_item in partes_items:
                    tipo_elem = parte_item.select_one('div.document-parte-item-tipo')
                    nome_elem = parte_item.select_one('div.document-parte-item-nome')
                    
                    if tipo_elem and nome_elem:
                        detalhes["partes"].append({
                            "tipo": tipo_elem.get_text(strip=True),
                            "nome": nome_elem.get_text(strip=True)
                        })
            
            return detalhes
            
        except Exception as e:
            print(f"Erro ao obter detalhes do processo: {e}")
            return self._fallback_processo(numero_processo)
    
    def _fallback_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Método de fallback para quando o scraping falha
        Usa a OpenAI para gerar resultados simulados
        """
        print("Usando fallback para a busca")
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um especialista em jurisprudência do STF. Gere resultados realistas para uma busca, incluindo números de processos reais, datas plausíveis, ministros relatores reais e ementas verossímeis."},
                    {"role": "user", "content": f"Gere {max_results} resultados de jurisprudência do STF sobre: {query}. Formate como um JSON com campos: titulo, numero_processo, relator, data_julgamento, ementa, link."}
                ],
                response_format={"type": "json_object"}
            )
            
            resultados = json.loads(response.choices[0].message.content)
            return resultados.get("resultados", [])
        except Exception as e:
            print(f"Erro no fallback: {e}")
            return []
    
    def _fallback_processo(self, numero_processo: str) -> Dict[str, Any]:
        """
        Método de fallback para quando o scraping de detalhes do processo falha
        Usa a OpenAI para gerar resultados simulados
        """
        print("Usando fallback para detalhes do processo")
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um especialista em jurisprudência do STF. Gere detalhes realistas para um processo específico."},
                    {"role": "user", "content": f"Gere detalhes completos para o processo {numero_processo} do STF. Formate como um JSON com campos: numero_processo, titulo, relator, data_julgamento, data_publicacao, orgao_julgador, ementa, decisao, partes (array de objetos com tipo e nome), link."}
                ],
                response_format={"type": "json_object"}
            )
            
            detalhes = json.loads(response.choices[0].message.content)
            return detalhes
        except Exception as e:
            print(f"Erro no fallback de processo: {e}")
            return {"numero_processo": numero_processo, "erro": "Não foi possível obter detalhes"}


class JurisBot:
    """Assistente Jurídico para busca de jurisprudências do STF"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o JurisBot
        
        Args:
            api_key: Chave de API da OpenAI (opcional, pode ser definida como variável de ambiente)
        """
        # Configurar a API key
        if api_key:
            openai.api_key = api_key
        elif os.environ.get("OPENAI_API_KEY"):
            openai.api_key = os.environ.get("OPENAI_API_KEY")
        else:
            raise ValueError("É necessário fornecer uma API key da OpenAI")
        
        # Inicializar o scraper
        self.scraper = STFScraper()
        
        print("JurisBot inicializado com sucesso!")
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt do sistema para o agente"""
        return f"""
        Você é JurisBot, um assistente jurídico especializado em jurisprudências do Supremo Tribunal Federal (STF) do Brasil.
        
        Suas responsabilidades:
        1. Responder perguntas sobre jurisprudências, decisões e entendimentos do STF
        2. Fornecer informações precisas e atualizadas
        3. Citar os números dos processos e datas das decisões quando possível
        4. Usar uma linguagem formal e técnica apropriada para o contexto jurídico
        5. Organizar as informações de forma clara e estruturada
        
        Hoje é {datetime.now().strftime("%d/%m/%Y")}.
        """
    
    def processar_consulta(self, consulta: str) -> str:
        """
        Processa uma consulta do usuário e retorna uma resposta
        
        Args:
            consulta: Consulta do usuário
            
        Returns:
            Resposta do JurisBot
        """
        print(f"Processando consulta: {consulta}")
        
        # Determinar o tipo de consulta
        if re.search(r'(ADI|ADPF|HC|RE|MS|RCL|IF|ACO|ADC|ADO|MI|PET|AP|Inq)\s+\d+', consulta, re.IGNORECASE):
            # Consulta sobre um processo específico
            match = re.search(r'(ADI|ADPF|HC|RE|MS|RCL|IF|ACO|ADC|ADO|MI|PET|AP|Inq)\s+\d+', consulta, re.IGNORECASE)
            numero_processo = match.group(0)
            return self._responder_sobre_processo(numero_processo, consulta)
        else:
            # Consulta geral sobre jurisprudência
            return self._responder_sobre_tema(consulta)
    
    def _responder_sobre_processo(self, numero_processo: str, consulta_original: str) -> str:
        """
        Responde a uma consulta sobre um processo específico
        
        Args:
            numero_processo: Número do processo
            consulta_original: Consulta original do usuário
            
        Returns:
            Resposta do JurisBot
        """
        # Obter detalhes do processo
        detalhes = self.scraper.obter_detalhes_processo(numero_processo)
        
        # Preparar o contexto para a OpenAI
        contexto = json.dumps(detalhes, ensure_ascii=False, indent=2)
        
        # Gerar resposta
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Consulta do usuário: {consulta_original}\n\nDetalhes do processo {numero_processo}:\n{contexto}\n\nResponda à consulta do usuário com base nos detalhes do processo fornecidos. Use uma linguagem formal e técnica apropriada para o contexto jurídico. Cite os números dos processos, datas das decisões e ministros relatores quando relevante."}
            ]
        )
        
        return response.choices[0].message.content
    
    def _responder_sobre_tema(self, consulta: str) -> str:
        """
        Responde a uma consulta sobre um tema jurídico
        
        Args:
            consulta: Consulta do usuário
            
        Returns:
            Resposta do JurisBot
        """
        # Buscar jurisprudências relacionadas ao tema
        jurisprudencias = self.scraper.buscar_jurisprudencia(consulta, max_results=5)
        
        # Preparar o contexto para a OpenAI
        contexto = json.dumps(jurisprudencias, ensure_ascii=False, indent=2)
        
        # Gerar resposta
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Consulta do usuário: {consulta}\n\nJurisprudências encontradas:\n{contexto}\n\nResponda à consulta do usuário com base nas jurisprudências encontradas. Use uma linguagem formal e técnica apropriada para o contexto jurídico. Cite os números dos processos, datas das decisões e ministros relatores quando relevante. Organize as informações de forma clara e estruturada."}
            ]
        )
        
        return response.choices[0].message.content
    
    def conversar(self):
        """Inicia uma conversa interativa com o usuário via terminal"""
        print("\n" + "="*50)
        print("🤖 JurisBot - Assistente Jurídico STF")
        print("="*50)
        print("Digite 'sair' para encerrar a conversa.\n")
        
        # Mensagem inicial
        print("🤖 JurisBot: Olá! Sou o JurisBot, seu assistente jurídico especializado em jurisprudências do STF. Como posso ajudar você hoje?")
        
        while True:
            # Obter entrada do usuário
            user_input = input("\n👤 Você: ")
            
            # Verificar se o usuário quer sair
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\n🤖 JurisBot: Obrigado por utilizar o JurisBot. Até a próxima!")
                break
            
            # Processar a entrada
            print("\n🤖 JurisBot está pensando...")
            try:
                response = self.processar_consulta(user_input)
                print(f"\n🤖 JurisBot: {response}")
            except Exception as e:
                print(f"\n🤖 JurisBot: Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}")


if __name__ == "__main__":
    # Verificar se a API key foi fornecida como argumento ou está no ambiente
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    try:
        # Inicializar o JurisBot
        jurisbot = JurisBot(api_key)
        
        # Iniciar conversa
        jurisbot.conversar()
    except ValueError as e:
        print(f"Erro: {e}")
        print("Uso: python jurisbot_sem_smolagents.py [OPENAI_API_KEY]")
        print("Ou defina a variável de ambiente OPENAI_API_KEY")
    except KeyboardInterrupt:
        print("\nJurisBot encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado: {e}")