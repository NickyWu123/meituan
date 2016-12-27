#coding:utf-8
from lxml import etree
from io import StringIO
import requests
import json
import codecs
import time
from collections import OrderedDict
import xlwt
import xlrd
import xlwt
workbook = xlwt.Workbook()
sheet1 = workbook.add_sheet(u'美团团购数据',cell_overwrite_ok=True)
sheet1.write(0,0,u'商店')
sheet1.write(0,1,u'地址')
sheet1.write(0,2,u'电话')
sheet1.write(0,3,u'类别')
sheet1.write(0,4,u'团购商品')
sheet1.write(0,5,u'团购已售')
sheet1.write(0,6,u'团购门店价')
sheet1.write(0,7,u'团购价')




def get_meishi_urls(url,headers,meishi_urls):
	print('Try to request the url:%s'%url)
	response=requests.get(url=url,headers=headers).text
	parser=etree.HTMLParser()
	tree=etree.parse(StringIO(response),parser)
	print('Time to scrape the shop urls according to this page')
	data_json=tree.xpath('*//div[@class="J-scrollloader cf J-hub"]')[0].get('data-async-params')
	data_total=json.loads(data_json,encoding="utf-8")
	data=json.loads(data_total['data'],encoding="utf-8")
	for i in data['poiidList']:
		meishi_urls.append(i)
	print('Scraping the shop urls according to this page finished')
	next_page=tree.xpath('//*[@gaevent="content/page/next"]')
	print('Try to find and request the next page')
	if next_page:
		next_page_url=next_page[0].get('href')
		next_url="http://fz.meituan.com%s"%next_page_url
		time.sleep(5)
		get_meishi_urls(url=next_url,headers=headers,meishi_urls=meishi_urls)
	else:
		print('No the next page,try to request the shop urls')
		file = codecs.open('meishi_data_utf8.json', 'w', encoding='utf-8')
		shop_urls=set(meishi_urls)
		meishi_info_csv=[]
		for i,j in enumerate(shop_urls):
			shop_url='http://fz.meituan.com/shop/%s'%j
			print(shop_url)
			time.sleep(5)
			meishi_info=get_meishi_info(url=shop_url,headers=headers)
			print(meishi_info)
			# meishi_info_csv.append(meishi_info)
			print ('Put the data into the json file')
			line = json.dumps(OrderedDict(meishi_info), ensure_ascii=False, sort_keys=False) + "\n"
			file.write(line)

			print ('Put the data into the csv file')
			sheet1.write(i+1,0,meishi_info['title'])
			sheet1.write(i+1,1,meishi_info['address'])
			sheet1.write(i+1,2,meishi_info['tel'])
			sheet1.write(i+1,3,meishi_info['general'])
			title=u''
			count_sale=u''
			store_price=u''
			group_price=u''
			for j,k in enumerate(meishi_info['groupbuying_items']):
				if j!=len(meishi_info['groupbuying_items'])-1:
					title+=k['title']+u'/'
					count_sale+=k['count_sale']+u'/'
					store_price+=k['store_price']+u'/'
					group_price+=k['group_price']+u'/'
				else:
					title+=k['title']
					count_sale+=k['count_sale']
					store_price+=k['store_price']
					group_price+=k['group_price']
				sheet1.write(i+1,4,title)
				sheet1.write(i+1,5,count_sale)
				sheet1.write(i+1,6,store_price)
				sheet1.write(i+1,7,group_price)
		workbook.save('meituan_meishi.xls')
		print('Working finished')
		file.close()
		

		
def get_meishi_info(url,headers):
	meishi_info={}
	meishi_url=url
	meishi_response=requests.get(url=meishi_url,headers=headers).text
	#print meishi_response
	parser=etree.HTMLParser()
	tree=etree.parse(StringIO(meishi_response),parser)
	title=tree.xpath('//*[@class="fs-section__left"]/h2/span/text()')[0]
	meishi_info['title']=title
	address=tree.xpath('//*[@class="geo"]/text()')[0]
	meishi_info['address']=address
	tel=tree.xpath('//*[@class="summary biz-box fs-section cf"]/div/p[2]/text()')
	if tel:
		tel=tel[0]
	else:
		tel='no tel'
	meishi_info['tel']=tel
	general=tree.xpath('//*[@class="info"]/div[2]/a/text()')[0]
	meishi_info['general']=general
	meishi_info['groupbuying_items']=[]
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
		meishi_info['groupbuying_items'].append(item)
	return meishi_info
if __name__ == '__main__':
	url='http://fz.meituan.com/category/meishi'
	headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
	}
	meishi_urls=[]
	get_meishi_urls(url=url,headers=headers,meishi_urls=meishi_urls)