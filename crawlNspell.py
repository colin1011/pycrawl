import requests
import re
import time
import config
from bs4 import BeautifulSoup
from urllib.parse import urlparse
#from autocorrect import spell
from spellchecker import SpellChecker
from flask import Flask,request
import json
from logging import FileHandler, WARNING
import logging
from flask_debugtoolbar import DebugToolbarExtension
import sys
import queue
import random
import string




'''
trying to make a queue which implements set at its backend, so that we dont check if a url is already crawlled or in to_crawl queue

class SetQueue(queue.Queue):

    def _init(self, maxsize):
        self.maxsize = maxsize
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()

'''

#SetQueue to implement the 


#CONFIGS

#user-agents to randomize, requests
UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", 
       "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
       "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
       "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
       )

#exclude these file extesnions
file_ext_not_to_crawl = ['.png','.ts','.m3u8','.mpd','.js','.css','.jpg']


#maximum time to crawl in milliseconds
max_time_for_crawl = 10000


#maximum links to crawl
max_counter = 50

#max no of typos
no_of_typos_to_display = 10


app = Flask(__name__)


#DEBUG

'''
toolbar = DebugToolbarExtension(app)

file_handler = FileHandler('error.txt')
file_handler.setLevel("WARNING")
app.logger.addHandler(file_handler)

'''

#logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def hello():
    return "Hello Root!"



@app.route('/crawlNspellcheck/v1/input/',methods = ['GET'])
def crawl_function():
  data,to_crawl=crawl_web(request.args.get('q'))
  data=json.dumps(data)
  to_crawl=json.dumps(to_crawl)
  return "{} \n\n\n\n====================================SERPRATOR=====================================\n\n\n\n {}".format(data,to_crawl)



#process urls for the crawler
def process_url(url,current_url):
  #print("inside process_url fun",file=sys.stdout)
  if url[0] == '/':
    url = "http://"+urlparse(current_url).hostname + url

    '''
  for item in file_ext_not_to_crawl:
    if(url.find(item)):
      return False
    '''
  if( url[0:4]=='www'):
    return "http://"+url,True

  if (url[0:4]=='http'):
    return url,True
  else:
    return url,False

def process_text(text):
  print("inside process_text fun",file=sys.stdout)
  text = text.lower()
  text_list=[word.strip(string.punctuation) for word in text.split()]

  spell = SpellChecker()

  # find those words that may be misspelled
  typos = spell.unknown(text_list)
  #reducing the time taken to run this function
  typos = list(typos)[0:10]
  for word in typos:
    # Get the one `most likely` answer
    suggested = spell.correction(word)
    print("In the typos suggestion loop ",file=sys.stdout)
    #print("inside process_text functions for loop",file=sys.stdout)
    # Get a list of `likely` options
    #print(spell.candidates(word))
  print("End of process_text fun",file=sys.stdout)
  return typos, suggested




def crawl_web(initial_url):
  #logging.warning("Inside crawl_web")
  crawled  = queue.Queue()
  to_crawl = queue.Queue()
  counter=0
  data = []
  
  now=int(time.time())
  then=now+max_time_for_crawl

  to_crawl.put(initial_url)

  #checks to crawl
  while((not to_crawl.empty()) and (then>int(time.time())) and (counter<max_counter)):
    print("inside while loop",file=sys.stdout)
    current_url = to_crawl.get()

    #Get random UA so that host-webpage doesn't interpret it as bot
    ua = UAS[random.randrange(len(UAS))]
    headers = {'user-agent': ua}

    r = requests.get(current_url, headers=headers)
    counter=counter+1
    if(r.status_code==200):
      #logging.warning("Inside successful req counter {}".format(counter))
      print("inside successful response ",file=sys.stdout)
      soup = BeautifulSoup(r.content, 'html.parser')
      #typos,suggested = process_text(soup.text)

      '''
      payload = {
      "url" : current_url,
      "typos" : typos,
      "suggested" : suggested
      }
      '''

      data.append(current_url)
      crawled.put(current_url)
    for link in soup.find_all('a'):
      url=link.get('href')
      try :
        if(url is not None):
          url,val=process_url(url,current_url)
          print(url,file=sys.stdout)
          if(val and  (url not in to_crawl.queue) and (url not in crawled.queue)):
            to_crawl.put(url)
            print("URL put in to_crawl queue {}".format(url),file=sys.stdout)
      except IndexError:
        print("This URL is giving index error {}".format(url),file=sys.stdout)
  return data,list(to_crawl.queue)




'''

count_value = crawl_web('http://www.google.com')
print("crawled {0} webpages".format(count_value))

'''


if __name__ == '__main__':
   app.run(debug=True,host='0.0.0.0',port=5000)

