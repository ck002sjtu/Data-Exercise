#encoding=utf-8

from __future__ import print_function
import requests
from io import open
import re
import time

# read url text file
def read_url_from_file(filename, bad_urls_save_dir=None, 
		url_regex=r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"):
	"""
		Read url from a text file, and filter urls based on a regex rule. 
		filename: where to read urls
		bad_urls_save_dir: where to save bad formed urls. if None, use file path as filename, but 
			with name "bad_urls_{timestamp}.txt"
		url_regex: regex used to filter urls.
	"""
	if bad_urls_save_dir is None:
		index = find_last(filename, '/')
		if index!=-1:
			bad_urls_save_dir = filename[:index] + '/' + 'bad_urls_{}.txt'.format(int(time.time()))
		else:
			bad_urls_save_dir = 'bad_urls_{}.txt'.format(int(time.time()))
	urls = []
	bad_urls = []
	prog = re.compile(url_regex)
	with open(filename, encoding='utf-8', mode='r') as f, \
			open(bad_urls_save_dir, encoding='utf-8', mode='w') as bad_url_f: 
		line = f.readline()
		while line:
			url = line.strip()	
			if prog.match(url) is None:
				#fail to find pattern
				bad_url_f.write(line)
			else:
				urls.append(url)
			line = f.readline()
	return urls

def find_last(string, str):
	"""
		find the last occurence index. 
		string: the original str
		str: string to be found in string
	"""
	last_position = -1
	while True:
	    position=string.find(str, last_position+1)
	    if position==-1:
	        return last_position
	    last_position=position

#print(read_url_from_file('url_demo.txt'))


#match each kind of urls
def get_name_dict_from_str(url_str, name_type='twitter'):
	"""
	like facebook.com/ZelloMe/ and twitter.com/Zello
	used for twitter and facebook
	"""
	solidus_index = url_str.find('/')
	tail_ = url_str[solidus_index+1:]
	last_index = len(tail_)
	if tail_.find('/"')!=-1:
		last_index -= 2
	elif tail_.find('/')!=-1 or tail_.find('"')!=-1:
		last_index -= 1
	name = tail_[:last_index]
	return {name_type: name}


def match_twitter(html_text):
	"""
		html_text: html string. Usually from response.text
	"""
	twitter_regex = r"twitter.com/[a-zA-Z0-9_]+"
	res = re.findall(twitter_regex, html_text)
	if len(res)==0:
		return None
	elif len(res)==1: 
		return get_name_dict_from_str(res[0],'twitter')
	else: # if there can be multiple results in the html_text, we return all the results for future analyse
		twitters = []
		for i in range(len(res)):
			twitters.append(get_name_dict_from_str(res[i],'twitter'))
		return twitters


def match_facebook(html_text):
	fb_regex = r"facebook.com/.+?/?\""
	res = re.findall(fb_regex, html_text)
	if len(res)==0:
		return None
	elif len(res)==1: 
		return get_name_dict_from_str(res[0], 'facebook')
	else:# if there can be multiple results in the html_text, we return all the results for future analyse
		facebooks = []
		for i in range(len(res)):
			facebooks.append(get_name_dict_from_str(res[0], 'facebook'))
		return facebooks	


def match_google_play(html_text):
	#https://developer.android.com/studio/build/application-id.html
	gg_py_regex = r"google.com/store/apps/details\?id=[a-zA-Z0-9_\.]+"
	res = re.findall(gg_py_regex, html_text)
	def process_tail(gg_py_tail_):
		gg_py_tail_ = gg_py_tail_.split('details?id=')[-1]
		if '&' in gg_py_tail_:
			return {'google': gg_py_tail_[:-1]}
		else:
			return {'google': gg_py_tail_}
	if len(res) == 0:
		return None
	elif len(res)==1:
		return process_tail(res[0])
	else:
		googles = []
		for i in range(len(res)):
			googles.append(process_tail(res[i]))
		return googles

def match_itunes_store(html_text):
	itunes_regex = r"itunes.apple.com/app/.+?/id[0-9]+"
	res = re.findall(itunes_regex, html_text)
	if len(res)==0:
		return None
	elif len(res)==1:
		tail_ = res[0].split('/')[-1]	
		return get_name_dict_from_str(tail_, 'ios')
	else:
		apples = []
		for i in range(len(res)):
			tail_ = res[0].split('/')[-1]	
			apples.append(get_name_dict_from_str(tail_, 'ios'))
		return apples

