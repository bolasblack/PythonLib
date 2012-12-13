#!/usr/bin/env python
#coding=utf-8

"""
    taobaoapi.py
    ~~~~~~~~~~~~~

    Taobao API simple class
    
    :copyright: (c) 2012 by c4605.
    :fork from https://github.com/laoqiu/sinaapp/blob/master/webapp/scripts/taobao_func.py
    :license: BSD, see LICENSE for more details.

    Usage: 

        from taobaoapi import TaobaoAPI, TaobaoRequest

        appkey = ""
        secret = ""
        client = TaobaoAPI(appkey, secret, widget=True)
        method = "taobao.taobaoke.widget.items.convert"
        fields = "click_url"

        req = TaobaoRequest(method,
                            fields=fields,
                            num_iids="16160683075",
                            is_mobile="true")

        source = client.execute(req)

        print source
"""

import json
import hmac
import re
import urllib, urllib2
from datetime import datetime
import time

class TaobaoAPI(object):
    """
    client = TaobaoAPI(appkey, appsecret)
    req = TaobaoRequest(method)
    req.setParams(fields,product_id)
    product = client.execute(req)
    """

    def __init__(self, appkey, secret, debug=False, widget=False):
        self.appkey = appkey
        self.secret = secret
        self.timestamp = self._timestamp()
        if debug:
            self.apiurl = "http://gw.api.tbsandbox.com/router/rest"
        elif widget:
            self.apiurl = "http://gw.api.taobao.com/widget/rest"
        else:
            self.apiurl = "http://gw.api.taobao.com/router/rest"

    def _timestamp(self):
        return str(int(time.time() * 1000))

    def _calcMd5(self, message, secret):
        hmacObj = hmac.new(secret)
        hmacObj.update(message)
        return hmacObj.hexdigest()

    def _sign(self):
        appkey = self.appkey
        secret = self.secret
        timestamp = self.timestamp
        message = secret + "app_key" + appkey + "timestamp" + timestamp + secret
        sign = self._calcMd5(message, secret).upper()
        return sign

    def _get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv: 1.9.2.13) Gecko/20101203 Firefox/3.6.13", 
            # "User-Agent":  "Mozilla/5.0 (X11; U; Linux i686; en-US; rv: 1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13"
            "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8", 
            "Accept-Language": "zh-cn, zh;q=0.5", 
            # "Accept-Encoding": "gzip, deflate", 
            "Accept-Charset": "GB2312, utf-8;q=0.7, *;q=0.7", 
            "Keep-Alive": "115", 
            "Connection": "keep-alive", 
            # "Host": "", 
            "Cache-Control": "no-cache",
            "Referer": "http: //localhost/taobaojssdk/test.html"
        }

    def getParams(self, params):
        params['v'] = '2.0'
        #params['format'] = 'json'
        params['partner_id'] = 'top-apitools'
        #params['partner_id'] = 'top-sdk-js-20120801'
        params['sign_method'] = "hmac"
        params['app_key'] = self.appkey
        params['timestamp'] = self.timestamp
        params['sign'] = self._sign()
        return urllib.urlencode(params)

    def execute(self, request):
        try:
            params = self.getParams(request.params)
        except BadParamsError:
            return
        
        while True:
            print params
            request = urllib2.Request(
                url = self.apiurl,
                data = params,
                headers = self._get_headers()
            )
            source = urllib2.urlopen(request).read()
            data = json.loads(source)
            if data.get('code',0)==7:
                time.sleep(10)
                print 'error 7: api get times overflow'
            else:
                break
        return data


class BadParamsError(Exception): pass


class TaobaoRequest(object):
    """
    make a request
    req = TaobaoRequest(method, fileds='num_iid,title,price', product_id=1)
    """

    def __init__(self, *args, **kwargs):
        self.params = {'method':args[0]}
        self.setParams(**kwargs)
    
    def setParams(self, *args, **kwargs):
        for key in kwargs.keys():
            self.params[key] = kwargs[key]


