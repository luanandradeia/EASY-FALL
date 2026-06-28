import os
import re
import sys
import json
import django
import time

# Configura o ambiente Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyfall.settings')
django.setup()

from core.models import Habilidade
import google.generativeai as genai

def extrair_capitulo_2():
    # Puxa a chave da API do ambiente (onde o sistema hospeda)
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        print("Erro: LLM_API_KEY não encontrada.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

    with open('livro_texto/livro.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    match_inicio = re.search(r'===== PAGINA 61 =====', text)
    match_fim = re.search(r'===== PAGINA 217 =====', text)

    if not match_inicio or not match_fim:
        print("Páginas do Capítulo 2 não encontradas.")
        return

    cap2_text = text[match_inicio.start():match_fim.start()]
    print(f"Capítulo 2 isolado com sucesso. Tamanho: {len(cap2_text)} caracteres.")

    # Vamos cortar apenas as Trilhas para agilizar as habilidades faltantes
    match_classes = re.search(r'Trilhas', cap2_text, re.IGNORECASE)
    if match_classes:
        cap2_text = cap2_text[match_classes.start():]

    # Quebrar em chunks de 15.000 caracteres para não sobrecarregar
    chunk_size = 15000
    chunks = [cap2_text[i:i+chunk_size] for i in range(0, len(cap2_text), chunk_size)]
    
    print(f"Texto dividido em {len(chunks)} partes. Iniciando extração com Gemini...")

    prompt = """
Você é um extrator de dados de RPG. Leia o trecho abaixo do livro de regras do Skyfall RPG e extraia TODAS as habilidades (Características de Classe, Façanhas, Talentos, Habilidades de Trilha, etc).
Devolva EXCLUSIVAMENTE um JSON com uma lista chamada "habilidades".
Exemplo de formato:
{
  "habilidades": [
    {
      "nome": "Golpe Brutal",
      "fonte_tipo": "trilha",
      "fonte_nome": "Assassino",
      "execucao": "Ação Padrão",
      "custo_enfase": 2,
      "descricao": "Texto detalhado da habilidade..."
    }
  ]
}
Se não houver habilidades no trecho, retorne {"habilidades": []}. A propriedade custo_enfase deve ser um numero inteiro (0 se não tiver).
Trecho:
"""

    total_added = 0
    for idx, chunk in enumerate(chunks):
        print(f"Processando parte {idx+1}/{len(chunks)}...")
        try:
            response = model.generate_content(prompt + chunk)
            data = json.loads(response.text)
            
            for hab in data.get("habilidades", []):
                obj, created = Habilidade.objects.get_or_create(
                    nome=hab.get("nome", "Sem Nome")[:100],
                    defaults={
                        "fonte_tipo": hab.get("fonte_tipo", "trilha")[:50],
                        "fonte_nome": hab.get("fonte_nome", "Geral")[:50],
                        "execucao": hab.get("execucao", "Passiva")[:50],
                        "custo_enfase": int(hab.get("custo_enfase", 0)),
                        "descricao": hab.get("descricao", "")
                    }
                )
                if created:
                    print(f"  + Adicionado: {obj.nome}")
                    total_added += 1
            
            time.sleep(2) # Respeita o rate limit
        except Exception as e:
            print(f"Erro no chunk {idx+1}: {e}")

    print(f"\nFinalizado! {total_added} novas habilidades do Capítulo 2 foram salvas no banco de dados!")

if __name__ == "__main__":
    extrair_capitulo_2()
