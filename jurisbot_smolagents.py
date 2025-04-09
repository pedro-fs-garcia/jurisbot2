import os
from typing import Dict, Any, List
import json

from smolagents import Agent, Tool
import openai

class STFJurisprudenciaSearch:
    """Classe para busca de jurisprudência do STF"""
    
    def buscar(self, query: str) -> List[Dict[str, Any]]:
        """
        Simula uma busca na base de jurisprudência do STF
        
        Em uma implementação real, esta função faria uma requisição à API do STF
        ou realizaria web scraping do site de jurisprudência
        """
        # Simulação usando OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em jurisprudência do STF. Gere resultados realistas para uma busca."},
                {"role": "user", "content": f"Gere 3 resultados de jurisprudência do STF sobre: {query}. Formate como JSON."}
            ],
            response_format={"type": "json_object"}
        )
        
        resultados = json.loads(response.choices[0].message.content)
        return resultados.get("resultados", [])

def main():
    # Verificar se a API key está definida
    if not os.environ.get("OPENAI_API_KEY"):
        print("Erro: OPENAI_API_KEY não definida no ambiente")
        print("Defina a variável de ambiente OPENAI_API_KEY antes de executar")
        return
    
    # Criar o buscador de jurisprudência
    stf_search = STFJurisprudenciaSearch()
    
    # Definir as ferramentas para o agente
    tools = [
        Tool(
            name="buscar_jurisprudencia_stf",
            description="Busca jurisprudências do STF com base em palavras-chave ou temas jurídicos",
            function=stf_search.buscar,
            args_schema={
                "query": {
                    "type": "string",
                    "description": "Consulta ou palavras-chave para busca de jurisprudência"
                }
            }
        )
    ]
    
    # Criar o agente JurisBot
    jurisbot = Agent(
        tools=tools,
        llm="gpt-4o",
        system_prompt="""
        Você é JurisBot, um assistente jurídico especializado em jurisprudências do Supremo Tribunal Federal (STF) do Brasil.
        
        Suas responsabilidades:
        1. Responder perguntas sobre jurisprudências, decisões e entendimentos do STF
        2. Fornecer informações precisas e atualizadas
        3. Citar os números dos processos e datas das decisões
        4. Usar linguagem formal e técnica apropriada para o contexto jurídico
        
        Quando receber uma consulta do usuário:
        1. Analise se é uma busca por jurisprudência
        2. Use a ferramenta buscar_jurisprudencia_stf para encontrar decisões relevantes
        3. Organize e apresente os resultados de forma clara e estruturada
        4. Destaque os pontos principais das decisões encontradas
        
        Quando não encontrar jurisprudência específica, indique honestamente.
        """,
        verbose=True
    )
    
    print("JurisBot inicializado com sucesso!")
    print("\n" + "="*50)
    print("🤖 JurisBot - Assistente Jurídico STF")
    print("="*50)
    print("Digite 'sair' para encerrar a conversa.\n")
    
    # Mensagem inicial
    print("🤖 JurisBot: Olá! Sou o JurisBot, seu assistente jurídico especializado em jurisprudências do STF. Como posso ajudar você hoje?")
    
    # Loop de conversa
    while True:
        # Obter entrada do usuário
        user_input = input("\n👤 Você: ")
        
        # Verificar se o usuário quer sair
        if user_input.lower() in ["sair", "exit", "quit"]:
            print("\n🤖 JurisBot: Obrigado por utilizar o JurisBot. Até a próxima!")
            break
        
        # Processar a entrada com o agente
        print("\n🤖 JurisBot está pensando...")
        response = jurisbot.run(user_input)
        
        # Exibir a resposta
        print(f"\n🤖 JurisBot: {response}")

if __name__ == "__main__":
    main()