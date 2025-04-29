# parser_tools.py

import praw

# Парсинг трендов Reddit с расширенным списком сабреддитов
def fetch_reddit_topics(subreddits=None, limit_per_sub=20):
    if subreddits is None:
        subreddits = [
            "technology", "worldnews", "science", "crypto", "AI", "space",
            "programming", "MachineLearning", "Futurology", "Economics",
            "gadgets", "dataisbeautiful", "business", "startups", "engineering",
            "cybersecurity", "webdev", "linux", "iOSProgramming", "learnprogramming",
            "blockchain", "QuantumComputing", "stocks", "finance", "climate",
            "greenenergy", "psychology", "philosophy", "history", "artificial",
            "computervision", "robotics", "neuro", "opensource"
        ]

    reddit = praw.Reddit(
        client_id='8e1gWU3HzicjuFUcl-upRw',
        client_secret='bcAjsxcgnhVypHfSA7piVuy8JZOOlQ',
        user_agent='TopicCollector/0.1 by Vast_Lion_6309'
    )

    all_topics = []

    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            print(f"🔍 Получаем темы из /r/{subreddit_name}...")
            posts = subreddit.top(time_filter='day', limit=limit_per_sub)
            topics = [post.title for post in posts]
            all_topics.extend(topics)
        except Exception as e:
            print(f"❌ Ошибка при получении тем из /r/{subreddit_name}: {str(e)}")

    return all_topics
