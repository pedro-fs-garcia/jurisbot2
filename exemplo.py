import os
import sys
import json
import re
from typing import List, Dict, Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

class STFScraperSimples:
    """Versão simplificada do scraper do STF"""
    
    BASE_URL = "https://jurisprudencia.stf.jus.br"
    SEARCH_URL = f"{BASE_URL}/pages/search"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def buscar_jurisprudencia(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Busca jurisprudências do STF com base em uma consulta"""
        print(f"Buscando jurisprudência para: {query}")
        
        # Preparar a URL de busca
        encoded_query = quote(query)
        search_url = f"{self.SEARCH_URL}?base=acordaos&sinonimo=true&plural=true&page=1&pageSize={max_results}&sort=_score&sortBy=desc&query={encoded_query}"
        
        try:
            # Fazer a requisição
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            # Parsear o HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair os resultados
            resultados = []
            
            # Verificar se há resultados
            result_items = soup.select('div.search-result-item')
            
            if not result_items:
                print("Nenhum resultado encontrado")
                return []
            
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
                    
                    # Extrair metadados
                    metadata_div = item.select_one('div.search-result-metadata')
                    metadata_text = metadata_div.get_text(strip=True) if metadata_div else ""
                    
                    # Extrair relator
                    relator = ""
                    relator_match = re.search(r'Relator:\s*([^,]+)', metadata_text)
                    if relator_match:
                        relator = relator_match.group(1).strip()
                    
                    # Extrair data de julgamento
                    data_julgamento = ""
                    data_match = re.search(r'Julgamento:\s*([^,]+)', metadata_text)
                    if data_match:
                        data_julgamento = data_match.group(1).strip()
                    
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
                        "ementa": ementa[:300] + "..." if len(ementa) > 300 else ementa,
                        "link": link
                    })
                    
                except Exception as e:
                    print(f"Erro ao processar item: {e}")
                    continue
            
            return resultados
            
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []


def main():
    # Criar o scraper
    scraper = STFScraperSimples()
    
    # Obter a consulta do usuário
    if len(sys.argv) > 1:
        consulta = " ".join(sys.argv[1:])
    else:
        consulta = input("Digite sua consulta de jurisprudência: ")
    
    # Buscar jurisprudência
    resultados = scraper.buscar_jurisprudencia(consulta)
    
    # Exibir resultados
    if not resultados:
        print("\nNenhum resultado encontrado para a consulta.")
        return
    
    print(f"\nResultados encontrados: {len(resultados)}")
    for i, resultado in enumerate(resultados, 1):
        print(f"\n--- Resultado {i} ---")
        print(f"Processo: {resultado.get('numero_processo', 'N/A')}")
        print(f"Título: {resultado.get('titulo', 'N/A')}")
        print(f"Relator: {resultado.get('relator', 'N/A')}")
        print(f"Data de Julgamento: {resultado.get('data_julgamento', 'N/A')}")
        print(f"Ementa: {resultado.get('ementa', 'N/A')}")
        print(f"Link: {resultado.get('link', 'N/A')}")


if __name__ == "__main__":
    main()