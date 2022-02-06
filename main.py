from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime as dt
import numpy as np
import yaml
import os


def preprocess_dates(data):
    mapping = {'января':'01', 'февраля':'02','марта':'03',
       'апреля':'04', 'мая':'05', 'июня':'06',
       'июля':'07', 'августа':'08', 'сентября':'09',
       'октября':'10','ноября':'11', 'декабря':'12'}
    
    data.loc[data['date'].str.contains('Сегодня'), 'date'] = dt.date.today().strftime('20%y-%m-%d')
    data.loc[data['date'].str.contains('Вчера'), 'date'] = dt.date(2021, 12, 27).strftime('20%y-%m-%d')
    data.loc[data['date'].str.contains('в'), 'date'] = \
        data.loc[data['date'].str.contains('в'), 'date'].apply(lambda x: x[:-7])
    
    data.loc[data['date'].str.contains(' '), 'date'] = \
        data.loc[data['date'].str.contains(' '), 'date'].apply(
                        lambda a: a.split()[2] + '-' + mapping[a.split()[1]] + '-' + a.split()[0])
    return data

def parse_stock(stock, max_page_len, sleep, max_messages, save_every):
    print(f'Parsing ${stock}...')
    driver.get(f'https://www.tinkoff.ru/invest/stocks/{stock}/pulse/')
    driver.execute_script(f"window.scrollTo(0, 5000);")
    page_length = driver.execute_script("return document.body.scrollHeight")
    cnt =  0
    msgs_cnt = 0
    while page_length < max_page_len:
        if cnt % 30 ==0:
            time.sleep(np.random.uniform(0.5,2))
        time.sleep(sleep)
        driver.execute_script(f"window.scrollTo(0, {page_length-2000});")
        page_length = driver.execute_script("return document.body.scrollHeight")
        cnt += 1 
        if ((max_page_len - page_length) <= 6000) or (cnt % save_every == 0):
            source_data = driver.page_source
            soup = bs(source_data, 'lxml')
            texts = soup.find_all('div', {'class':'pulse-posts-by-ticker__fPAgaP pulse-posts-by-ticker__iPAgaP'}) 
            logins = soup.find_all('div', {'class':'pulse-posts-by-ticker__bvN--xH'})
            dates = soup.find_all('div', {'class':'pulse-posts-by-ticker__dvN--xH'})
            logins = [login.text for login in logins]
            texts = [text.text for text in texts]
            dates = [date.text for date in dates]
            msgs_cnt = len(texts)
            df = pd.DataFrame({'logins':logins, 'date':dates, 'text':texts})
            df.to_csv(f'output/{stock}.csv', index=False)         
            if msgs_cnt >= max_messages:
                break
        
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Params
max_page_len= config['max_page_length']
sleep = config['sleep']
stocks = config['stocks']
max_messages = config['max_messages']
save_every = config['save_every']

if __name__ == "__main__":
    driver = webdriver.Chrome(ChromeDriverManager().install()) 
    data = pd.DataFrame()
    for i, stock in enumerate(stocks):
        parse_stock(stock, max_page_len, sleep, max_messages, save_every)
        print(f'Saving ${stock}. {i+1} of {len(stocks)}')
    
    for stock in stocks:
        temp = pd.read_csv(f'output/{stock}.csv')
        temp['ticker'] = stock
        data = data.append(temp, ignore_index=True)
        
    data = preprocess_dates(data)
    data.to_csv('output/all_data.csv', index=False)
    