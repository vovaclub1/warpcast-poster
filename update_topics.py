# update_topics.py

import os
from parser_tools import fetch_google_trends, fetch_reddit_topics

# === Основной файл для обновления тем ===

def update_topics_file(filename="topics.txt"):
    print("🔄 Обновляем темы...")

    google_trends = fetch_google_trends()
    reddit_topics = fetch_reddit_topics()

    # Проверка на наличие трендов
    if google_trends is None:
        print("❌ Не удалось получить тренды Google.")
        google_trends = []

    all_topics = set(google_trends + reddit_topics)

    # Загружаем текущие темы из файла, чтобы избежать повторений
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_topics = set(f.read().splitlines())
    else:
        existing_topics = set()

    # Добавляем только новые темы
    new_topics = all_topics - existing_topics

    if new_topics:
        with open(filename, "a", encoding="utf-8") as f:
            for topic in sorted(new_topics):
                f.write(topic.strip() + "\n")
        print(f"✅ Темы обновлены. Добавлено новых тем: {len(new_topics)}")
    else:
        print("❌ Нет новых тем для добавления.")

if __name__ == "__main__":
    update_topics_file()