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

from core.models import Magia
import google.generativeai as genai

def extrair_capitulo_4():
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        print("Erro: LLM_API_KEY não encontrada.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

    with open('livro_texto/livro.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    match_inicio = re.search(r'===== PAGINA 259 =====', text)
    match_fim = re.search(r'===== PAGINA 303 =====', text)

    if not match_inicio or not match_fim:
        print("Páginas do Capítulo 4 não encontradas.")
        return

    cap4_text = text[match_inicio.start():match_fim.start()]
    print(f"Capítulo 4 isolado com sucesso. Tamanho: {len(cap4_text)} caracteres.")

    # Lista de magias costuma começar depois de uma introdução. 
    # Vamos processar tudo fatiando
    chunk_size = 15000
    chunks = [cap4_text[i:i+chunk_size] for i in range(0, len(cap4_text), chunk_size)]
    
    print(f"Texto dividido em {len(chunks)} partes. Iniciando extração de Magias...")

    prompt = """
Você é um extrator de dados de RPG. Leia o trecho abaixo do livro de regras do Skyfall RPG e extraia TODAS as descrições de Magias.
Devolva EXCLUSIVAMENTE um JSON com uma lista chamada "magias".
Exemplo de formato:
{
  "magias": [
    {
      "nome": "Bola de Fogo",
      "camada": "3",
      "tipo": "Evocação",
      "execucao": "Ação Padrão",
      "custo_enfase": 3,
      "descricao": "Texto detalhado da magia, alcance, alvos e dano."
    }
  ]
}
Se não houver magias no trecho, retorne {"magias": []}.
Importante: camada (círculo) é string numérica ("1", "2") e custo_enfase é inteiro.
Trecho:
"""

    total_added = 0
    for idx, chunk in enumerate(chunks):
        print(f"Processando parte {idx+1}/{len(chunks)} (Magias)...")
        try:
            response = model.generate_content(prompt + chunk)
            data = json.loads(response.text)
            
            for m in data.get("magias", []):
                obj, created = Magia.objects.get_or_create(
                    nome=m.get("nome", "Sem Nome")[:100],
                    defaults={
                        "camada": str(m.get("camada", "1"))[:50],
                        "tipo": m.get("tipo", "Mágica")[:50],
                        "execucao": m.get("execucao", "Ação Padrão")[:50],
                        "custo_enfase": int(m.get("custo_enfase", 0)),
                        "descricao": m.get("descricao", "")
                    }
                )
                if created:
                    print(f"  + Adicionada: {obj.nome}")
                    total_added += 1
            
            time.sleep(2) # Respeita o rate limit
        except Exception as e:
            print(f"Erro no chunk {idx+1}: {e}")

    print(f"\nFinalizado! {total_added} novas Magias do Capítulo 4 foram salvas no banco de dados!")

if __name__ == "__main__":
    extrair_capitulo_4()
