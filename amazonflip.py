"""Amazon and FlipKart will block the ip because we are scrapping their data which is not allowed so we 
will be using Google's bot user agent or else we can use proxy to bypass their restrictions"""


import requests
import json
import re

from bs4 import BeautifulSoup
""" TODO
- Offers and its price
"""

def query_string_remove(url):
	return url[:url.find('?')]
#### FlipKart
def flipkart(url):
	clean_url = query_string_remove(url)
	r = requests.get(url)
	soup = BeautifulSoup(r.content,"lxml")
	title_tag = soup.find("h1",{"itemprop":"name"})
	subtitle_tag = soup.find("h1",{"itemprop":"name"}).findNext('span')
	price_tag = soup.find("meta",{"itemprop":"price"})
	currency_tag = soup.find("meta",{"itemprop":"priceCurrency"})
	img_tag = soup.find("div",{"class":"imgWrapper"}).findAll('img',{'class':'productImage'})
	out_of_stock_tag = soup.find("div",{"class":"out-of-stock-status"})
	li = {}
	li['name'] = title_tag.text + ' ' + subtitle_tag.text
	li['price'] = price_tag['content'].replace(',', '')
	li['currency'] = currency_tag['content']
	li['img'] = []
	for item in img_tag:
		li['img'].append(item['data-src'])
	li['url'] = clean_url
	li['in_stock'] = False if out_of_stock_tag else True
	return json.dumps(li,sort_keys=True)

def amazon_com(url):
	clean_url = query_string_remove(url)
	r = requests.get(url,headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'})
	soup = BeautifulSoup(r.content,"lxml")
	li = {}

	title_tag = soup.find("span",{"id":"productTitle"})
	deal_price_tag = soup.find("span",{"id":"priceblock_dealprice"})
	img_tag = soup.find("img",{"id":"landingImage"})
	li['is_deal_price'] = True
	if not deal_price_tag:
		deal_price_tag = soup.find("span",{"id":"priceblock_ourprice"})
		li['is_deal_price'] = False
	in_stock_tag = soup.find("div",{"id":"availability"}).find("span")

	li['name'] = title_tag.text
	li['price'] = deal_price_tag.text
	li['currency'] = 'USD'
	li['url'] = clean_url
	li['img']  = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', img_tag['data-a-dynamic-image'])[0]
	li['in_stock'] = True if 'In Stock' in in_stock_tag.text  else False


	return json.dumps(li,sort_keys=True)