#!/usr/bin/env python

import urllib
import urllib2
import re

class Currency:
  def __init__(self):
    self.site = 'xe'
    self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    if self.site == 'oanda':
      self.siteurl = 'http://www.oanda.com/convert/classic?'
      self.args = { 'value': 1, 'expr' : '', 'exch': ''}
      self.keys = ['value', 'expr', 'exch']
      self.re_exch = re.compile(r'<span\s+class=["]result_val["]>\s*.*?\s*([0-9.]+\.[0-9]+)\s*</span>', re.DOTALL|re.MULTILINE)
    elif self.site == 'xe':
      self.siteurl = 'http://www.xe.com/ucc/convert.cgi'
      self.args = {'Amount': '1.0', 'From':'', 'To':''}
      self.keys = ['Amount', 'From', 'To']
      self.re_exch = re.compile(r'([0-9]+\.[0-9]+) %s', re.DOTALL|re.MULTILINE)
    else:
      self.siteurl = 'http://fxtop.com/en/'

  def Exchange(self, cur_from, cur_to):
    cur_from = cur_from.upper()
    cur_to = cur_to.upper()
    self.args[self.keys[0]] = 1
    self.args[self.keys[1]] = cur_from
    self.args[self.keys[2]] = cur_to
    if self.site == 'xe':
      self.re_exch = re.compile(self.re_exch.pattern % cur_to, re.DOTALL|re.MULTILINE)
    query = self.siteurl
    req = urllib2.Request(query, urllib.urlencode(self.args), {'User-Agent' : self.user_agent})
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    grps = self.re_exch.search(data)
    if grps:
      return '1 %s = %s %s' % (cur_from, grps.group(1), cur_to)
    else:
      print data
      return 'Did not find search string'

  def testSearch(self):
    txt = '<span class="result_val"> 0.55882</span>'
    grps = self.re_exch.search(txt)
    if not grps:
      print 'Failed search test'
      assert(False)

  def siteTwo(self):
    return
    txt = '<FONT SIZE=-1>PTE Portuguese Esc.</FONT></TD><TD ALIGN=CENTER><FONT SIZE=-1>200.482</FONT>'
    self.re_exch = re.compile(r'<FONT SIZE=-1>[A-Z]{3}\s.*?<FONT SIZE=-1>([0-9]+\.[0-9]+)<', re.DOTALL|re.MULTILINE)
    grps = self.re_exch.search(txt)
    print grps

     
if __name__ == '__main__':
  currency = Currency()
  currency.siteTwo()
  print currency.Exchange('BRL', 'USD')
