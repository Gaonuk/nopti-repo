import sys
import os

# Get the absolute path to the repository root
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the repository root to the Python path
sys.path.append(repo_root)
from scraper.get_updated_news import get_update_news
import json
date = get_update_news() #conten the news data

with open('update_data_base/just_receved_news_data.json', 'w') as file:
    json.dump( date, file)

def init_data_base():
    """Initialize the database with news data."""

    #add id
    for ind,element in enumerate(date["news_list"]):
        element["id"]=ind+1

    with open('update_data_base/current_news_data.json', 'w') as file:
        json.dump( date, file)
init_data_base()

