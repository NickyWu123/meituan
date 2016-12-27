#coding:utf-8
from lxml import etree
from io import StringIO
import requests
import json
import codecs
import time
from collections import OrderedDict


def get_entertainment_urls(url,headers,entertainment_urls):
	print('Try to request the url:%s'%url)
	response=requests.get(url=url,headers=headers).text
	parser=etree.HTMLParser()
	tree=etree.parse(StringIO(response),parser)
	print('Time to scrape the shop urls according to this page')
	data_json=tree.xpath('*//div[@class="J-scrollloader cf J-hub"]')[0].get('data-async-params')
	data_total=json.loads(data_json,encoding="utf-8")
	data=json.loads(data_total['data'],encoding="utf-8")
	for i in data['poiidList']:
		entertainment_urls.append(i)
	print('Scraping the shop urls according to this page finished')
	next_page=tree.xpath('//*[@gaevent="content/page/next"]')
	print('Try to find and request the next page')
	if next_page:
		next_page_url=next_page[0].get('href')
		next_url="http://fz.meituan.com%s"%next_page_url
		time.sleep(5)
		get_entertainment_urls(url=next_url,headers=headers,entertainment_urls=entertainment_urls)
	else:
		print('No the next page,try to request the shop urls')
		file = codecs.open('entertainment_data_utf8.json', 'w', encoding='utf-8')
		shop_urls=set(entertainment_urls)
		for i in shop_urls:
			shop_url='http://fz.meituan.com/shop/%s'%i
			print(shop_url)
			time.sleep(5)
			entertainment_info=get_entertainment_info(url=shop_url,headers=headers)
			print(entertainment_info)
			line = json.dumps(OrderedDict(entertainment_info), ensure_ascii=False, sort_keys=False) + "\n"
			file.write(line)
		print('Working finished')
		file.close()
		
def get_entertainment_info(url,headers):
	entertainment_info={}
	entertainment_url=url
	entertainment_response=requests.get(url=entertainment_url,headers=headers).text
	#print meishi_response
	parser=etree.HTMLParser()
	tree=etree.parse(StringIO(entertainment_response),parser)
	title=tree.xpath('//*[@class="fs-section__left"]/h2/span/text()')[0]
	entertainment_info['title']=title
	address=tree.xpath('//*[@class="geo"]/text()')[0]
	entertainment_info['address']=address
	tel=tree.xpath('//*[@class="summary biz-box fs-section cf"]/div/p[2]/text()')
	if tel:
		tel=tel[0]
	else:
		tel='no tel'
	entertainment_info['tel']=tel
	general=tree.xpath('//*[@class="info"]/div[2]/a/text()')[0]
	entertainment_info['general']=general
	entertainment_info['groupbuying_items']=[]
	on_sale_items=tree.xpath('//*[@class="item cf "]')
	for i in on_sale_items:
		item={}
		title=i.xpath('a[@class="item__title"]/span[@class="title"]/text()')[0]
		item['title']=title
		group_price=i.xpath('span[@class="item__price"]/span[1]/em/strong/text()')[0]
		item['group_price']=group_price
		store_price=i.xpath('span[@class="item__price"]/span[2]/del/text()')[0]
		item['store_price']=store_price
		count_sale=i.xpath('a[@class="item__title"]/span[@class="sale"]/text()')[0]
		item['count_sale']=count_sale
		entertainment_info['groupbuying_items'].append(item)
	return entertainment_info
if __name__ == '__main__':
	url='http://fz.meituan.com/category/xiuxianyule'
	headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
	}
	entertainment_urls=[]
	get_entertainment_urls(url=url,headers=headers,entertainment_urls=entertainment_urls)