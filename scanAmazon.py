#!/usr/bin/env python
# -*- encoding: latin1 -*-

import BeautifulSoup

from urllib import urlencode
import urllib2
import cookielib
import re
import time
import sys
import random

# http://www.xpbargains.com/wii_locator.php

def findIt(s, toFind):
  return s.fetchText(text=re.compile(toFind), limit=1)

COOKIEJAR = '/home/scottkirkwood/.mozilla/firefox/j2p2ankk.default/cookies.txt'

class CheckAmazon:
  def __init__(self):
    self.URLS = [
      #{'title' : 'Wii Fit', 'percent' : 1, 'url' : 'http://www.amazon.com/o/ASIN/B000VJRU44', },
      {'title' : 'Wii Console', 'percent' : 1, 'url' : 'http://www.amazon.com/o/ASIN/B0009VXBAQ', },
    ]
    #~ self.URLS = [
      #~ # Monkey Balls
      #~ 'http://www.amazon.com/o/ASIN/B000GHLBUA/ref=pd_rvi_gw_3/104-8780360-5170306'
    #~ ]
    self.outFilename = "out.html"
    self.COOKIEJAR = COOKIEJAR
    cj = cookielib.MozillaCookieJar()
    cj.load(self.COOKIEJAR)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    
  def fetch(self, url, txdata = None):
    # Note to self: this becomes a POST if you pass txdata
    txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    response = ''
    try:
      req = urllib2.Request(url, txdata, txheaders)
      response = urllib2.urlopen(req)
    except IOError, e:
      print 'We failed to open "%s".' % url
      if hasattr(e, 'code'):
        print 'We failed with error code - %s.' % e.code
      elif hasattr(e, 'reason'):
        print "The error object has the following 'reason' attribute :"
        print e.reason
        print "This usually means the server doesn't exist,',"
        print "is down, or we don't have an internet connection."
    return response

  def checkPage(self, url):
    page = self.fetch(url)
    soup = BeautifulSoup.BeautifulSoup(page)
    open(self.outFilename, "w").write(str(soup))
    if len(findIt(soup, "Scott")) == 0:
      print "You've lost your cookie, didn't find Scott"
      return False
    if len(findIt(soup, "Fit")) == 0:
      print "Something's changed, didn't find the Wii text"
    ret = False
    if len(findIt(soup, "This item is currently not available")) > 0:
      print time.ctime(),"Not available"
    else:
      form = soup.fetch('form', attrs={'name' : 'handleBuy'})
      form = form[0]
      tmpSoup = BeautifulSoup.BeautifulSoup(str(form))
      list = tmpSoup.fetch('input', attrs={
        'name' : 'submit.add-to-cart', 'alt' : 'Add to Shopping Cart'})
      open('maybe-available.html', 'w').write(str(tmpSoup))
      if len(list) > 0:
        print time.ctime(),"Available!"
        self.tryToAdd(tmpSoup)
        ret = True
      else:
        print time.ctime(), "Not available 2"

    return ret

  def tryToAdd(self, soup):
    form = soup.fetch('form', attrs={'name' : 'handleBuy' })
    form = form[0]
    postdata = []
    for intag in form.fetchNext('input'):
      if intag['type'] == 'hidden':
        postdata.append((intag['name'], intag['value']))
      elif intag['type'] == 'password':
        postdata.append((intag['name'], 'password'))
      elif intag['type'] == 'submit':
        if intag.has_key(['name']):
          postdata.append((intag['name'], intag['value']))
        else:
          postdata.append(('submit', intag['value']))
    
    for select in form.fetchNext('select'):
      for option in select.fetchNext('option', attrs={'selected' : 'selected' }):
          postdata.append((select['name'], option['value']))
          
    page = self.fetch("http://www.amazon.com" + form['action'], urlencode(postdata))
    soup2 = BeautifulSoup.BeautifulSoup(page)
    fname = "bought-it.html"
    open(fname, 'w').write(str(soup2))
    print "Appear to have put it in your cart, check '%s' to make sure" % (fname)
    sys.exit(0)
    
if __name__ == "__main__":
  random.seed()
  ca = CheckAmazon()
  bucket = []
  # Put in urls that I want to check more, more often.
  for url in ca.URLS:
    for x in range(url['percent']):
      bucket.append(url)
  
  while 1:
    randomUrl = random.choice(bucket)
    sys.stdout.write("Trying %-20s " % randomUrl['title'])
    ca.checkPage(randomUrl['url'])
    nSleepTime = 5 + random.uniform(-2, 2)  
    time.sleep(nSleepTime)
