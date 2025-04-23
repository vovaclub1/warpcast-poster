# parser_tools.py

from pytrends.request import TrendReq
import praw

# Парсинг трендов Google
def fetch_google_trends():
    # Инициализация pytrends
    pytrends = TrendReq(hl='en-US', tz=360)

    # Попытка получить тренды для разных регионов
    regions = ['US', 'IN', 'GB', 'DE', 'JP']  # актуальные коды регионов
    all_trends = []
    for region in regions:
        try:
            trending_searches = pytrends.trending_searches(pn=region)  # используем правильный код региона
            print(f"Тренды для {region}:")
            print(trending_searches.head())  # выводим первые строки трендов
            all_trends.extend(trending_searches.head().values.tolist())  # добавляем в список трендов
        except Exception as e:
            print(f"Ошибка при получении трендов для {region}: {e}")
    return all_trends


# Парсинг трендов Reddit
def fetch_reddit_topics(subreddit_name='technology', limit=10):
    reddit = praw.Reddit(
        client_id='8e1gWU3HzicjuFUcl-upRw',
        client_secret='bcAjsxcgnhVypHfSA7piVuy8JZOOlQ',
        user_agent='TopicCollector/0.1 by Vast_Lion_6309'
    )
    try:
        subreddit = reddit.subreddit(subreddit_name)
        topics = [post.title for post in subreddit.top(time_filter='day', limit=limit)]
    except Exception as e:
        print(f"❌ Ошибка при получении трендов Reddit: {str(e)}")
        topics = []
    return topics