import os
import json
import time
import csv
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cargamos el prompt desde un archivo de texto
def load_prompt():
    with open("prompts/main_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()


# Función para ejecutar la consulta a la API de OpenAI
def response_question(question: str) -> tuple:
    system_prompt = load_prompt()

    start_time = time.time()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
        max_tokens=200
    )

    latency_ms = round((time.time() - start_time) * 1000, 2)

    return response, latency_ms


# Parear y validar JSON
def parse_response(response) -> dict:
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError:
        return {"answer": "Error: el modelo no devolvió un JSON válido.", "confidence": 0.0, "actions": ["revisar_manualmente"]}


INPUT_PRICE_1K = 0.00015  # Precio por cada 1,000 tokens para gpt-4o-mini    
OUTPUT_PRICE_1K = 0.0006  # Precio por cada 1,000 tokens para gpt-4o-mini

def calculate_cost(usage) -> float:
    cost = (usage.prompt_tokens / 1000) * INPUT_PRICE_1K + \
        (usage.completion_tokens / 1000) * OUTPUT_PRICE_1K
    return round(cost, 6)

def safe_metrics(usage, latency_ms, costo):
    archive = "metrics/metrics.csv"
    exist = os.path.exists(archive)
    with open(archive, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exist:
            writer.writerow(["timestamp", "tokens_prompt", "tokens_completion", "total_tokens", "latency_ms", "estimated_cost_usd"])
        writer.writerow([
            datetime.now().isoformat(),
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
            latency_ms,
            costo
        ])

if __name__ == "__main__":
    pregunta = input("Escribe la pregunta del cliente: ")
    
    response, latency_ms = response_question(pregunta)
    resultado = parse_response(response)
    costo = calculate_cost(response.usage)
    
    safe_metrics(response.usage, latency_ms, costo)
    
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
