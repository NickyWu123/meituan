#coding:utf-8
from lxml import etree
from io import StringIO
import requests
import json
import codecs
import time
from collections import OrderedDict


def get_pc_ktv_urls(url,headers,pc_ktv_urls):
	print('Try to request the url:%s'%url)
	response=requests.get(url=url,headers=headers).text
	parser=etree.HTMLParser()
	tree=etree.parse(StringIO(response),parser)
	print('Time to scrape the shop urls according to this page')
	data_json=tree.xpath('*//div[@class="J-scrollloader cf J-hub"]')[0].get('data-async-params')
	data_total=json.loads(data_json,encoding="utf-8")
	data=json.loads(data_total['data'],encoding="utf-8")
	for i in data['poiidList']:
		pc_ktv_urls.append(i)
	print('Scraping the shop urls according to this page finished')
	next_page=tree.xpath('//*[@gaevent="content/page/next"]')
	print('Try to find and request the next page')
	if next_page:
		next_page_url=next_page[0].get('href')
		next_url="http://fz.meituan.com%s"%next_page_url
		time.sleep(5)
		get_pc_ktv_urls(url=next_url,headers=headers,pc_ktv_urls=pc_ktv_urls)
	else:
		print('No the next page,try to request the shop urls')
		file = codecs.open('pc_ktv_data_utf8.json', 'w', encoding='utf-8')
		shop_urls=set(pc_ktv_urls)
		for i in shop_urls:
			shop_url='http://fz.meituan.com/shop/%s'%i
			print(shop_url)
			time.sleep(5)
			pc_ktv_info=get_pc_ktv_info(url=shop_url,headers=headers)
			print(pc_ktv_info)
			line = json.dumps(OrderedDict(pc_ktv_info), ensure_ascii=False, sort_keys=False) + "\n"
			file.write(line)
		print('Working finished')
		file.close()
		
def get_pc_ktv_info(url,headers):
	pc_ktv_info={}
	pc_ktv_url=url
	pc_ktv_response=requests.get(url=pc_ktv_url,headers=headers).text
	#print meishi_response
	parser=etree.HTMLParser()
	tree=etree.parse(StringIO(pc_ktv_response),parser)
	title=tree.xpath('//*[@class="fs-section__left"]/h2/span/text()')[0]
	pc_ktv_info['title']=title
	address=tree.xpath('//*[@class="geo"]/text()')[0]
	pc_ktv_info['address']=address
	tel=tree.xpath('//*[@class="summary biz-box fs-section cf"]/div/p[2]/text()')
	if tel:
		tel=tel[0]
	else:
		tel='no tel'
	pc_ktv_info['tel']=tel
	general=tree.xpath('//*[@class="info"]/div[2]/a/text()')[0]
	pc_ktv_info['general']=general
	pc_ktv_info['groupbuying_items']=[]
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
		pc_ktv_info['groupbuying_items'].append(item)
	return pc_ktv_info
if __name__ == '__main__':
	url='http://fz.meituan.com/category/pc_ktv'
	headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
	}
	pc_ktv_urls=[]
	get_pc_ktv_urls(url=url,headers=headers,pc_ktv_urls=pc_ktv_urls)