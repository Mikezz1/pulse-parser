# pulse-scrapper - load posts from Tinkoff Pulse
Scipt to parse posts for specified stocks from pulse
### Setup:
- Specify `max_messages` to define number of messages to parse. Since frequency  of messages vary depending on ticker, you may need to increase `max_page_len` to deal with less popular stocks.
- Specify list of stocks with `stocks` parameter 
### Run:
```
pip install -r requirements.txt
python3 run main.py
```

