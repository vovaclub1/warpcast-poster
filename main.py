import random
import requests
import os
import json
import re
import time
from dotenv import load_dotenv  # Импортируем библиотеку для загрузки переменных окружения

# Загружаем переменные окружения из файла .env
load_dotenv()

# ==== Темы ====
topics_file = "topics.txt"
with open(topics_file, "r", encoding="utf-8") as f:
    topics = [line.strip() for line in f if line.strip()]
topic = random.choice(topics)
print("📌 Выбрана тема:", topic)

# ==== История постов ====
history_file = "post_history.json"
if os.path.exists(history_file):
    with open(history_file, "r") as f:
        post_history = json.load(f)
else:
    post_history = []

# ==== Hugging Face ====
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Получаем API-ключ из переменной окружения
HF_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

huggingface_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
    "Content-Type": "application/json"
}

prompt_template = (
    f"<|system|>You are a professional social media strategist.\n"
    f"<|user|>Write a short, insightful, human-like social media post (max 300 characters) about {topic}. "
    f"Use subtle buzzwords, a fact, quote, or stat. Avoid hashtags, links, emojis. End with a question to spark engagement.\n"
    f"Keep it natural and well-structured.<|assistant|>"
)

# ==== Генерация ====
post_text = None
MAX_ATTEMPTS = 10

for attempt in range(MAX_ATTEMPTS):
    print(f"🧠 Попытка генерации #{attempt + 1}")
    response = requests.post(huggingface_url, headers=headers, json={
        "inputs": prompt_template,
        "parameters": {
            "max_new_tokens": 180,
            "temperature": 0.9,
            "top_p": 0.95,
            "repetition_penalty": 1.4
        }
    })

    if response.status_code != 200:
        print(f"❌ Ошибка Hugging Face: {response.status_code} - {response.text}")
        continue

    generated = response.json()[0]["generated_text"].strip()

    # Удаляем промт, если он затесался в ответ
    if generated.startswith(prompt_template):
        generated = generated[len(prompt_template):].strip()

    # Убираем кавычки и лишние пробелы
    generated = generated.strip('"').strip()

    # Проверка на повтор
    if generated in post_history:
        print("⚠️ Повтор или неподходящий пост. Генерация нового...")
        continue

    post_text = generated
    break

if not post_text:
    print("❌ Не удалось сгенерировать подходящий пост после нескольких попыток.")
    exit()

print("📢 Предпросмотр поста:\n", post_text)

# Добавить в историю
post_history.append(post_text)
with open(history_file, "w") as f:
    json.dump(post_history[-50:], f)

# ==== Публикация в Warpcast через Neynar ====
NEYNAR_API_KEY = "FC0A77EE-4A1E-431F-9A73-21F2619CA27B"
SIGNER_UUID = "7b628d8d-8b22-4d11-9dce-1cf8f1a11e53"

publish_url = "https://api.neynar.com/v2/farcaster/cast"
publish_headers = {
    "x-api-key": NEYNAR_API_KEY,
    "Content-Type": "application/json"
}
publish_payload = {
    "signer_uuid": SIGNER_UUID,
    "text": post_text
}

res = requests.post(publish_url, json=publish_payload, headers=publish_headers)

if res.status_code == 200:
    print("🚀 Пост успешно опубликован в Warpcast!")
else:
    print(f"❌ Ошибка при публикации: {res.status_code} - {res.text}")
