#encoding=utf-8

from __future__ import print_function
import requests
import re
from log_utils import setup_logger
import sys
from queue import Queue
from utils import match_twitter,match_facebook, match_google_play, match_itunes_store

logger = setup_logger()

def get_result(url, greedy=False):
	"""
		url: input url
		greedy: used to control if we use the greedy approach
		return value: jason type extracted from url
	"""
	response =  get_url_static_content(url)
	if response == None:
		logger.info('No response get from {}'.format(url))
		pass
	elif response.status_code>400:
		pass
	else:
		html_text = response.text
		extract_dict = extract_res_from_hmtl(url, html_text, greedy=greedy)
		return extract_dict


def extract_res_from_hmtl(url, html_text, greedy=False, extrators=[match_twitter, match_facebook, 
		match_google_play, match_itunes_store]):
	"""
		html_text: str, text of html
		greedy: some of the urls may transfer to other urls for advertising purposes,
			    we can try to catch these urls if we set 'greedy' to be True.
				Eg: 
				One url
				URL = http://ad.apsalar.com/api/v1/ad?re=0&a=naturalmotion&i=
					  com.naturalmotion.dawnoftitans&ca=Social_DoT_Websites_GP&an=Social&p=Android&pl=Social_DoT_Websites_
					  DoT_GP&h=fa9dd2e58a8ce1b50cfbb5af086e315a8b4dd84a
				may be actually 
				URL_REAL = com.naturalmotion.dawnoftitans
				after several transfers.
		extrators: list	
	"""
	if greedy:
		link_urls = find_all_urls_in_html(html_text)
		for link_url in link_urls:
			real_url = get_real_url(link_url)
			if real_url!=link_url:
				html_text += ' ' + real_url
	extract_dict = {'url': url} #return string in format like '{url:xxx, google:xxx}'
	for extrator in extrators:
		content = extrator(html_text)
		if content is None:
			continue
		elif isinstance(content, list):
			names = []
			for c in content:
				name_type = c.keys()[0]
				names.append(c.values()[0])
			names = list(set(names))
			if len(names)==1:
				names = names[0]
			extract_dict[name_type] = names
		elif isinstance(content, dict):
			name_type = content.keys()[0]
			name = content.values()[0]
			extract_dict[name_type] = name
	return extract_dict


def get_url_static_content(url, param=None, timeout_time=3, retry_times=3):
	"""
		url: the input url 
		param: dict, the parameters pass to url
		greedy: some of the urls may transfer to other urls for advertising purposes,
			    we can try to catch these urls if we set 'greedy' to be True.
		timeout: max time of timeout allowed
		retry_times: max times of retry allowed
	
	"""
	response = None
	retry_count = 0
	NETWORK_STATUS = False
	REQUEST_TIMEOUT = False
	def retry_again():
		if retry_count==0:
			return True
		if retry_count>retry_times:
			return False
		if response==None:
			return False
		if response.status_code>400:
			return True
	while retry_again():
		try:
			response = requests.get(url, params=param, timeout=timeout_time)
			NETWORK_STATUS = False
			REQUEST_TIMEOUT = False
		except requests.exceptions.ConnectTimeout:
		    NETWORK_STATUS = True
		except requests.exceptions.Timeout:
		    REQUEST_TIMEOUT = True
		except Exception as e:
			logger.info('Exception {} catches when try to connect to {}'.format(e,url))
		retry_count += 1
	if REQUEST_TIMEOUT:
		logger.info('Connection to {} timeout after retrying {} times.'.format(url, retry_times))
	if NETWORK_STATUS:
		logger.info('Connection to {} failed because of network status problem'.format(url))
	if response == None:
		logger.info('Fail to connect to {}'.format(url))
		return None
	if response.status_code>400:
		logger.info('Connection to {} failed with return code {}'.format(url, response.status_code))

	return response	


def get_real_url(url, try_count = 1, timeout=3):
	"""
	helper function for greedy
	"""
	MAX_TRYCOUNT = 3
	if try_count > MAX_TRYCOUNT: # 
	    return url
	try:
	    rs = requests.get(url, timeout=timeout)
	    if rs.status_code > 400:
	        return get_real_url(url,try_count+1, timeout)
	    return rs.url
	except:
	    return get_real_url(url, try_count + 1, timeout)


def find_all_urls_in_html(html_text):
	url_regex = r'https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'
	urls = re.findall(url_regex, html_text)
	return urls

