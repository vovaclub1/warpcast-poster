import random
import requests
import os
import json
import time
import re
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Загрузка тем
with open("topics.txt", "r", encoding="utf-8") as f:
    topics = [line.strip() for line in f if line.strip()]

# Загрузка истории
history_file = "post_history.json"
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        post_history = json.load(f)
else:
    post_history = []

# Загрузка аккаунтов
with open("accounts.json", "r", encoding="utf-8") as f:
    accounts = json.load(f)

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Новый список промтов
def get_prompts(topic):
    return [
        (
            f"You are a professional social media strategist.\n"
            f"Write a short, insightful, human-like social media post (max 300 characters) about {topic}.\n"
            f"Use a subtle buzzword, a fact, a quote, or a surprising statistic.\n"
            f"Do not use hashtags, links, emojis, or phrases like 'As a professional...'.\n"
            f"End with an open-ended question to spark engagement.\n"
            f"Keep the tone natural, personal, and well-structured."
        ),
        (
            f"You are an expert in digital marketing.\n"
            f"Write a highly engaging social media post (max 300 characters) about {topic}.\n"
            f"Use storytelling or a shocking fact to hook the reader.\n"
            f"Avoid overused expressions, hashtags, links, emojis, or formal phrases like 'As an expert...'.\n"
            f"End with an open-ended question, not a direct call-to-action.\n"
            f"Make the post feel personal, conversational, and natural."
        ),
        (
            f"You are a seasoned content creator.\n"
            f"Create an attention-grabbing social media post (max 300 characters) about {topic}.\n"
            f"Start with a bold statement or a provocative question that challenges common beliefs.\n"
            f"Avoid hashtags, links, emojis, or robotic phrasing.\n"
            f"End with a thought-provoking, open-ended question.\n"
            f"Keep the text concise, impactful, and human-like."
        ),
        (
            f"Write a funny, engaging, and original social media post about {topic}. Try to make it witty or humorous.\n"
            f"Avoid formal language or serious tones.\n"
            f"Make sure the post feels natural and conversational."
        ),
        (
            f"Write a post about {topic} like a personal story.\n"
            f"Share a real-life situation or experience related to {topic}.\n"
            f"Keep the tone friendly and relatable.\n"
            f"End with an insightful reflection or lesson learned."
        )
    ]

def remove_links(text):
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\bLINK\b", "", text, flags=re.IGNORECASE)
    return text.strip()

def generate_post(topic):
    prompts = get_prompts(topic)
    prompt_index = random.randint(0, len(prompts) - 1)
    prompt = prompts[prompt_index]

    print(f"🔄 Используем промт №{prompt_index + 1}\n")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    for attempt in range(10):
        print(f"🧠 Генерация поста на тему «{topic}», попытка #{attempt + 1}")
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json={
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "max_tokens": 300
        })

        if response.status_code != 200:
            print(f"❌ Ошибка OpenAI: {response.status_code} - {response.text}")
            continue

        generated = response.json()["choices"][0]["message"]["content"].strip()
        generated = generated.strip('"').strip()

        generated = remove_links(generated)

        if generated not in post_history:
            return generated

    print("❌ Не удалось сгенерировать уникальный пост.")
    return None

def shorten_text_with_openai(text):
    print("✂️ Текст слишком длинный, отправляем на сокращение через OpenAI...")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = (
        "Shorten the following text to a maximum of 300 characters, keeping its main meaning, style, and naturalness. "
        "Do not add links, emojis, or hashtags. Just the shortened text:\n\n"
        f"{text}"
    )

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json={
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": 300
    })

    if response.status_code == 200:
        shortened_text = response.json()["choices"][0]["message"]["content"].strip()
        shortened_text = shortened_text.strip('"').strip()
        return shortened_text
    else:
        print(f"❌ Ошибка при сокращении текста: {response.status_code} - {response.text}")
        return None

def publish_post(text, signer_uuid, api_key):
    encoded_text = text.encode("utf-8")
    if len(encoded_text) > 1024:
        print(f"⚠️ Текст слишком длинный ({len(encoded_text)} байт)")
        shortened = shorten_text_with_openai(text)
        if shortened:
            text = shortened
            encoded_text = text.encode("utf-8")
            if len(encoded_text) > 1024:
                print(f"❌ Даже после сокращения текст всё ещё длинный. Пост не будет опубликован.")
                return
        else:
            print(f"❌ Ошибка при сокращении текста. Пост не будет опубликован.")
            return

    url = "https://api.neynar.com/v2/farcaster/cast"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "signer_uuid": signer_uuid,
        "text": text
    }

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 200:
        print("🚀 Пост успешно опубликован!")
    else:
        print(f"❌ Ошибка при публикации: {res.status_code} - {res.text}")

def create_schedule(posts, cycle_duration_sec, min_delay_sec, max_delay_sec):
    schedule = []
    now = datetime.now()

    for post_info in posts:
        random_offset = random.randint(0, cycle_duration_sec)
        scheduled_time = now + timedelta(seconds=random_offset)

        schedule.append({
            "time": scheduled_time,
            "account": post_info["account"],
            "text": post_info["text"]
        })

    # Сортируем посты по времени (чтобы публикации были в порядке)
    schedule.sort(key=lambda x: x["time"])
    return schedule


def post_cycle(days, min_posts_per_cycle, max_posts_per_cycle, cycle_duration_hours):
    used_topics = set()

    for day in range(days):
        print(f"🌟 День {day + 1} из {days}")
        cycle_duration_sec = cycle_duration_hours * 3600

        posts = []

        # Для каждого аккаунта генерируем количество постов
        for acc in accounts:
            posts_count = random.randint(min_posts_per_cycle, max_posts_per_cycle)
            print(f"🔹 Аккаунт {acc['signer_uuid']} получит {posts_count} постов.")

            for _ in range(posts_count):
                topic = random.choice(topics)
                used_topics.add(topic)
                text = generate_post(topic)
                if text:
                    posts.append({"account": acc, "text": text})
                    post_history.append(text)

        # Сохраняем историю постов
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(post_history[-50:], f, ensure_ascii=False, indent=2)

        # Перемешиваем посты
        random.shuffle(posts)

        # Генерируем расписание
        min_delay = 10  # минимум секунд между постами
        max_delay = cycle_duration_sec // max(len(posts), 1)
        schedule = create_schedule(posts, cycle_duration_sec, min_delay, max_delay)

        # Сохраняем расписание
        with open("schedule.json", "w", encoding="utf-8") as f:
            json.dump([
                {
                    "time": s["time"].strftime("%Y-%m-%d %H:%M:%S"),
                    "account": s["account"].get("name", s["account"]["signer_uuid"]),
                    "text": s["text"]
                }
                for s in schedule
            ], f, ensure_ascii=False, indent=2)

        # Публикуем посты по расписанию
        for item in schedule:
            now = datetime.now()
            wait_time = (item["time"] - now).total_seconds()
            if wait_time > 0:
                print(f"⏳ Ожидание {int(wait_time)} секунд до следующего поста...")
                time.sleep(wait_time)

            publish_post(item["text"], item["account"]["signer_uuid"], item["account"]["api_key"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post scheduling for Warpcast")
    parser.add_argument("days", type=int, help="Number of days to post")
    parser.add_argument("min_posts", type=int, help="Minimum posts per cycle")
    parser.add_argument("max_posts", type=int, help="Maximum posts per cycle")
    parser.add_argument("cycle_duration", type=int, help="Cycle duration in hours")

    args = parser.parse_args()

    post_cycle(args.days, args.min_posts, args.max_posts, args.cycle_duration)
