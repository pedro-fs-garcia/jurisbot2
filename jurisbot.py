import os
import sys
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime

# Importando as bibliotecas necessárias
from smolagents import Agent, Tool
import openai

class JurisBot:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o JurisBot - Assistente Jurídico para busca de jurisprudências do STF
        
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
        
        # Definir as ferramentas disponíveis para o agente
        self.tools = [
            Tool(
                name="buscar_jurisprudencia",
                description="Busca jurisprudências do STF com base em palavras-chave ou temas",
                function=self.buscar_jurisprudencia
            ),
            Tool(
                name="detalhar_processo",
                description="Obtém detalhes específicos de um processo do STF pelo número",
                function=self.detalhar_processo
            ),
            Tool(
                name="resumir_entendimento",
                description="Resume o entendimento do STF sobre um tema específico",
                function=self.resumir_entendimento
            )
        ]
        
        # Criar o agente
        self.agent = Agent(
            tools=self.tools,
            llm="gpt-4o",
            system_prompt=self._get_system_prompt(),
            verbose=True
        )
        
        print("JurisBot inicializado com sucesso!")
        
    def _get_system_prompt(self) -> str:
        """Retorna o prompt do sistema para o agente"""
        return """
        Você é JurisBot, um assistente jurídico especializado em jurisprudências do Supremo Tribunal Federal (STF) do Brasil.
        
        Suas responsabilidades:
        1. Responder perguntas sobre jurisprudências, decisões e entendimentos do STF
        2. Fornecer informações precisas e atualizadas
        3. Citar os números dos processos e datas das decisões quando possível
        4. Usar uma linguagem formal e técnica apropriada para o contexto jurídico
        5. Organizar as informações de forma clara e estruturada
        
        Quando não souber uma resposta específica, use as ferramentas disponíveis para buscar informações.
        Se mesmo assim não encontrar a informação, indique honestamente que precisaria de uma pesquisa mais aprofundada.
        
        Hoje é {data_atual}.
        """.format(data_atual=datetime.now().strftime("%d/%m/%Y"))
    
    def buscar_jurisprudencia(self, query: str) -> Dict[str, Any]:
        """
        Busca jurisprudências do STF com base em uma consulta
        
        Args:
            query: Consulta ou palavras-chave para busca
            
        Returns:
            Dicionário com os resultados da busca
        """
        # Simulação de busca na base de jurisprudência do STF
        # Em uma implementação real, aqui seria feita uma requisição à API do STF
        # ou scraping do site de jurisprudência
        
        print(f"Buscando jurisprudências para: {query}")
        
        # Simulando tempo de processamento
        time.sleep(1.5)
        
        # Usando a OpenAI para simular resultados
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em jurisprudência do STF. Gere resultados realistas para uma busca de jurisprudência, incluindo números de processos, datas, ministros relatores e ementas."},
                {"role": "user", "content": f"Gere 3 resultados de jurisprudência do STF sobre: {query}. Formate como um JSON com campos: numero_processo, relator, data_julgamento, ementa, e link."}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extrair e retornar os resultados
        resultados = json.loads(response.choices[0].message.content)
        return resultados
    
    def detalhar_processo(self, numero_processo: str) -> Dict[str, Any]:
        """
        Obtém detalhes específicos de um processo do STF
        
        Args:
            numero_processo: Número do processo no formato do STF
            
        Returns:
            Dicionário com os detalhes do processo
        """
        print(f"Buscando detalhes do processo: {numero_processo}")
        
        # Simulando tempo de processamento
        time.sleep(1)
        
        # Usando a OpenAI para simular resultados
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em jurisprudência do STF. Gere detalhes realistas para um processo específico."},
                {"role": "user", "content": f"Gere detalhes completos para o processo {numero_processo} do STF. Formate como um JSON com campos detalhados incluindo partes, histórico processual, votos dos ministros, etc."}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extrair e retornar os resultados
        detalhes = json.loads(response.choices[0].message.content)
        return detalhes
    
    def resumir_entendimento(self, tema: str) -> Dict[str, Any]:
        """
        Resume o entendimento atual do STF sobre um tema específico
        
        Args:
            tema: Tema jurídico para resumo
            
        Returns:
            Dicionário com o resumo do entendimento
        """
        print(f"Resumindo entendimento do STF sobre: {tema}")
        
        # Simulando tempo de processamento
        time.sleep(2)
        
        # Usando a OpenAI para simular resultados
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em jurisprudência do STF. Resuma o entendimento atual da corte sobre temas jurídicos específicos."},
                {"role": "user", "content": f"Resuma o entendimento atual do STF sobre o tema: {tema}. Inclua a evolução jurisprudencial, principais decisões e entendimento atual. Formate como um JSON com campos: tema, entendimento_atual, evolucao_jurisprudencial, decisoes_relevantes."}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extrair e retornar os resultados
        resumo = json.loads(response.choices[0].message.content)
        return resumo
    
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
            
            # Processar a entrada com o agente
            print("\n🤖 JurisBot está pensando...")
            response = self.agent.run(user_input)
            
            # Exibir a resposta
            print(f"\n🤖 JurisBot: {response}")


if __name__ == "__main__":
    # Verificar se a API key foi fornecida como argumento ou está no ambiente
    api_key = os.getenv('OPENAI_API_KEY', None)
    
    try:
        # Inicializar o JurisBot
        jurisbot = JurisBot(api_key)
        
        # Iniciar conversa
        jurisbot.conversar()
    except ValueError as e:
        print(f"Erro: {e}")
        print("Uso: python jurisbot.py [OPENAI_API_KEY]")
        print("Ou defina a variável de ambiente OPENAI_API_KEY")
    except KeyboardInterrupt:
        print("\nJurisBot encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Exemplo de saída:
# JurisBot inicializado com sucesso!
# ==================================================
# 🤖 JurisBot - Assistente Jurídico STF
# ==================================================
# Digite 'sair' para encerrar a conversa.
#
# 🤖 JurisBot: Olá! Sou o JurisBot, seu assistente jurídico especializado em jurisprudências do STF. Como posso ajudar você hoje?
#
# 👤 Você: Qual o entendimento do STF sobre aborto em caso de anencefalia?
#
# 🤖 JurisBot está pensando...
# Buscando jurisprudências para: aborto em caso de anencefalia
# Resumindo entendimento do STF sobre: aborto em caso de anencefalia
#
# 🤖 JurisBot: O STF decidiu na ADPF 54, julgada em 2012, que a interrupção da gravidez de feto anencefálico não configura crime de aborto. O relator foi o Ministro Marco Aurélio, e a decisão foi por maioria (8 votos a 2).
#
# A Corte entendeu que a anencefalia torna inviável a vida extrauterina, e obrigar a mulher a manter a gestação configuraria tortura e violação à sua dignidade, autonomia e direitos reprodutivos.
#
# Processos relevantes:
# - ADPF 54 (12/04/2012) - Relator Min. Marco Aurélio
# - HC 84.025/RJ (2004) - Caso que motivou a posterior ADPF
#
# Esta decisão representou um marco na jurisprudência brasileira sobre direitos reprodutivos, estabelecendo que não há crime quando o feto é anencefálico, por não haver potencialidade de vida extrauterina.