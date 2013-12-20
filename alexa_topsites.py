#!/usr/bin/env python

import hmac
import argparse
import httplib2

from lxml import etree
from hashlib import sha1
from urllib import quote_plus
from base64 import b64encode
from datetime import datetime

def gen_url(access_key_id, secret_access_key, country, start, count):
    service_host   = 'ats.amazonaws.com'    
    query = {
          "Action"             :     'TopSites'
        , "AWSAccessKeyId"     :     access_key_id
        , "Timestamp"          :     datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        , "ResponseGroup"      :     'Country'
        , "Start"              :     start
        , "Count"              :     count
        , "CountryCode"        :     country_code
        , "SignatureVersion"   :     '2'
        , "SignatureMethod"    :     'HmacSHA1'
             }
    join = lambda x: '='.join(     [  x[0], quote_plus(str(x[1]))  ]     )
    
    query_str = '&'.join(     sorted( map(join, query.iteritems()) )     )
    
    sign_str  = 'GET\n%s\n/\n%s' % (service_host,query_str)
    signature = hmac.new(secret_access_key, sign_str, sha1).digest()
    
    query_str += '&Signature=' + quote_plus( b64encode(signature).strip() )
    
    url = 'http://%s/?%s' % (service_host, query_str)
    return url

def get_alexa_sites(url):
#    http = httplib2.Http()
    resp, content = http.request(url, 'GET')
    xml = etree.fromstring(content)
    namespace_map = {'aws' : 'http://ats.amazonaws.com/doc/2005-11-21'}
    entries = xml.xpath('//aws:DataUrl', namespaces = namespace_map)
    entries = [entry.text for entry in entries]
    return entries

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Get a range of Alexa Top sites for a specific country')

    parser.add_argument('-k', action='store', dest='access_key_id')
    parser.add_argument('-s', action='store', dest='secret_access_key')
    parser.add_argument('-c', action='store', dest='country_code')
    parser.add_argument('-a', action='store', dest='start', type=int)
    parser.add_argument('-z', action='store', dest='count', type=int)
    
    args = parser.parse_args()

    if not args.count:
        parser.print_help()
        exit(2)
    access_key_id = args.access_key_id
    secret_access_key = args.secret_access_key
    country_code = args.country_code
    start = args.start
    count = args.count
    
    http = httplib2.Http()
                
    step  = 100 if count > 100 else count

    for i in xrange(start, count, step):
        url = gen_url(access_key_id, secret_access_key, country_code, i, step)
        print '\n'.join(get_alexa_sites(url))
