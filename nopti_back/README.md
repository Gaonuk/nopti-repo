# Installation
`pip install -r requirements.txt`

Download : llama-3.2-1b-instruct-q8_0.gguf

# Run the local llama3.2 1B server

```sh
python3 -m llama_cpp.server \
    --model complete_path_to_model/llama-3.2-1b-instruct-q8_0.gguf \
    --host localhost    --port 8111
```

# Run principale app server : 
`uvicorn server:app --reload`


## Use scraper module : 

```python
from scraper.get_updated_news import get_update_news

date = get_update_news() #conten the news data

```
