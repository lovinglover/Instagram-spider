import requests
from requests.exceptions import RequestException
import re
import json
import os
import threading

header = {
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
	#'cookie': 'mid=XHOezAALAAFXStunLD5nmZHE_-FW; shbid=8077; csrftoken=axe1KTS713IFdk8baS2LHPvXWioIIgft; ds_user_id=12375481575; sessionid=12375481575%3AAr9jkQN6ODPW07%3A28; shbts=1557040078.636566; ig_sdc=12375481575; rur=FTW; urlgen="{\"96.45.182.201\": 25820}:1hNUme:gR5wh74KR5kCqas_o1vjt6PwbaE"''
}

proxy = {
	'http':'http://127.0.0.1:1080',
	'https':'https://127.0.0.1:1080'
}


name = input('>>name:')
if not os.path.exists('G:\instagram'):
	os.mkdir('G:\instagram')
os.chdir('G:\instagram')
if not os.path.exists(name):
	os.mkdir(name)

def parse_first_page(url):
	try:
		response = requests.get(url, headers=header, proxies=proxy)
		if response.status_code == 200:
			# print(response.text)
			html = response.text
	except RequestException:
		return None
	partten = re.compile('.*window._sharedData = (.*?);</script>', re.S)
	item = re.findall(partten, html)
	# print(item[0])
	data = json.loads(item[0])
	urls = []
	u_id = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
	after = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"][
		"end_cursor"]
	next_judge = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"][
		"has_next_page"]
	# print(data)
	edges = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
	for edge in edges:
		display_url = edge["node"]["display_url"]
		urls.append(display_url)
		# print(display_url)
	save_by_thread(urls)
	return u_id,after,next_judge

def get_next_page(url):
	res = requests.get(url, headers=header, proxies=proxy)
	if res.status_code == 200:
		return res.text
	# print(html)
	else:
		print(url)
		return None

def get_urls(html):
	data = json.loads(html)
	# u_id = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
	after = data["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
	next_judge = data["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
	# print(data)
	urls = []
	edges = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
	for edge in edges:
		url = edge["node"]["display_url"]
		# print(url)
		urls.append(url)
	save_by_thread(urls)
	return after,next_judge

def save_by_thread(urls):
	t_objs = []
	for url in urls:
		t = threading.Thread(target=save_iamges, args=(url,))
		t.start()
		t_objs.append(t)
	for t in t_objs:
		t.join()

def save_iamges(url):
	# if not os.path.exists('G:\instagram'):
	# 	os.mkdir('G:\instagram')
	# os.chdir('G:\instagram')
	# if not os.path.exists(name):
	# 	os.mkdir(name)
	os.chdir('G:\instagram\\' + name)
	# print(url)
	res = requests.get(url, headers=header, proxies=proxy)
	file_name = str(url[-65:-48]) + '.jpg'
	print('downloading...' + url)
	with open(file_name, 'wb') as f:
		f.write(res.content)

def main():

	url = 'https://www.instagram.com/' + name +'/'
	u_id, after, next_judge = parse_first_page(url)
	variables = {
		"id": u_id,
		"first": 48,
		"after": after
	}
	for i in range(10):
		next_url = 'https://www.instagram.com/graphql/query/?' + 'query_hash=f2405b236d85e8296cf30347c9f08c2a&' + 'variables={0}'.format(json.dumps(variables))
		html =get_next_page(next_url)
		after1,next_judge = get_urls(html)
		variables['after'] = after1

if __name__ == '__main__':
	main()
	# t_objs = []
	# for url in urls:
	# 	t = threading.Thread(target=save_iamges,args=(url,))
	# 	t.start()
	# 	t_objs.append(t)
	# for t in t_objs:
	# 	t.join()
