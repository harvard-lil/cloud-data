import sys, json, time
import dns.resolver
import requests

def main(argv):

    # get ip for domain        
    arin_domains_100 = ['google.com', 'facebook.com', 'youtube.com', 'yahoo.com', 
        'amazon.com', 'ebay.com', 'wikipedia.org', 'linkedin.com', 'twitter.com', 
        'bing.com', 'craigslist.org', 'pinterest.com', 'blogspot.com', 'go.com',
        'live.com', 'espn.go.com', 'paypal.com', 'huffingtonpost.com', 'tumblr.com', 
        'cnn.com', 'wordpress.com', 'walmart.com', 'instagram.com', 'msn.com', 
        'netflix.com', 'weather.com', 'apple.com', 'imgur.com', 'imdb.com', 
        'aol.com', 'reddit.com', 'microsoft.com', 'yelp.com', 'bankofamerica.com', 
        'bestbuy.com', 'ask.com', 'chase.com', 'nytimes.com', 'etsy.com', 
        'foxnews.com', 'about.com', 'target.com', 'adobe.com', 'xvideos.com', 
        'cnet.com', 'godaddy.com', 'wellsfargo.com', 'xhamster.com', 
        'secureserver.net', 'pandora.com', 't.co', 'pornhub.com', 'flickr.com', 
        'comcast.net', 'ups.com', 'blogger.com', 'buzzfeed.com', 'nbcnews.com', 
        'usps.com', 'zillow.com', 'conduit.com', 'wordpress.org', 'zedo.com', 
        'salesforce.com', 'stackoverflow.com', 'hulu.com', 'dailymail.co.uk', 
        'hootsuite.com', 'nfl.com', 'vimeo.com', 'outbrain.com', 'aweber.com', 
        'fiverr.com', 'kohls.com', 'usatoday.com', 'forbes.com', 'fedex.com', 
        'googleusercontent.com', 'indeed.com', 'groupon.com', 'macys.com', 
        'bbc.co.uk', 'dropbox.com', 'amazonaws.com', 'livejasmin.com', 
        'thepiratebay.sx', 'avg.com', 'newegg.com', 'wikia.com', 'homedepot.com', 
        'drudgereport.com', 'constantcontact.com', 'washingtonpost.com', 
        'bleacherreport.com', 'reference.com', 'tmz.com', 'baidu.com', 
        'capitalone.com', 'optmd.com', 'att.com']
        
    arin_domains_250 = ['google.com', 'facebook.com', 'youtube.com', 'yahoo.com', 'amazon.com', 'ebay.com', 'wikipedia.org', 'linkedin.com', 'twitter.com', 'bing.com', 'craigslist.org', 'pinterest.com', 'blogspot.com', 'go.com', 'live.com', 'paypal.com', 'espn.go.com', 'huffingtonpost.com', 'tumblr.com', 'cnn.com', 'wordpress.com', 'walmart.com', 'instagram.com', 'msn.com', 'netflix.com', 'weather.com', 'apple.com', 'imgur.com', 'imdb.com', 'aol.com', 'reddit.com', 'microsoft.com', 'yelp.com', 'bankofamerica.com', 'bestbuy.com', 'ask.com', 'nytimes.com', 'chase.com', 'etsy.com', 'foxnews.com', 'about.com', 'target.com', 'adobe.com', 'cnet.com', 'xvideos.com', 'godaddy.com', 'wellsfargo.com', 'secureserver.net', 'xhamster.com', 'pandora.com', 't.co', 'flickr.com', 'pornhub.com', 'comcast.net', 'ups.com', 'usps.com', 'buzzfeed.com', 'nbcnews.com', 'blogger.com', 'zillow.com', 'conduit.com', 'zedo.com', 'wordpress.org', 'salesforce.com', 'stackoverflow.com', 'nfl.com', 'hulu.com', 'dailymail.co.uk', 'hootsuite.com', 'vimeo.com', 'outbrain.com', 'aweber.com', 'fiverr.com', 'forbes.com', 'kohls.com', 'usatoday.com', 'fedex.com', 'indeed.com', 'googleusercontent.com', 'groupon.com', 'macys.com', 'dropbox.com', 'amazonaws.com', 'bbc.co.uk', 'livejasmin.com', 'avg.com', 'wikia.com', 'newegg.com', 'constantcontact.com', 'homedepot.com', 'bleacherreport.com', 'drudgereport.com', 'washingtonpost.com', 'thepiratebay.sx', 'reference.com', 'tmz.com', 'baidu.com', 'optmd.com', 'att.com', 'capitalone.com', 'wsj.com', 'americanexpress.com', 'retailmenot.com', 'upworthy.com', 'sears.com', 'slickdeals.net', 'pch.com', 'swagbucks.com', 'answers.com', 'deviantart.com', 'wikihow.com', 'cbssports.com', 'cj.com', 'toysrus.com', 'hostgator.com', 'youporn.com', 'nydailynews.com', 'verizonwireless.com', 'vube.com', 'xnxx.com', 'pof.com', 'businessinsider.com', 'redtube.com', 'goodreads.com', 'gap.com', 'infusionsoft.com', 'warriorforum.com', 'mailchimp.com', 'tripadvisor.com', 'okcupid.com', 'photobucket.com', 'latimes.com', 'statcounter.com', 'coupons.com', 'ehow.com', 'abcnews.go.com', 'overstock.com', 'stumbleupon.com', 'bp.blogspot.com', 'match.com', 'webmd.com', 'mashable.com', 'soundcloud.com', 'foodnetwork.com', 'kickass.to', 'theblaze.com', 'mozilla.org', 'force.com', 'alibaba.com', 'citibank.com', 'allrecipes.com', 'trulia.com', 'zappos.com', 'cbslocal.com', 'staples.com', 'foxsports.com', 'shareasale.com', 'themeforest.net', 'nordstrom.com', 'costco.com', 'directrev.com', 'backpage.com', 'time.com', 'meetup.com', 'lowes.com', 'intuit.com', 'empowernetwork.com', 'qq.com', 'ca.gov', 'addthis.com', 'files.wordpress.com', 'wikimedia.org', 'dailymotion.com', 'yellowpages.com', 'theguardian.com', 'slideshare.net', 'archive.org', 'accuweather.com', 'linksynergy.com', 'examiner.com', 'expedia.com', 'media.tumblr.com', 'nba.com', 'thefreedictionary.com', 'shopathome.com', 'wunderground.com', 'monster.com', 'southwest.com', 'bloomberg.com', 'tube8.com', 'jcpenney.com', 'motherless.com', 'nih.gov', 'akamaihd.net', 'viralnova.com', 'barnesandnoble.com', 'gawker.com', 'ign.com', 'weebly.com', 'verizon.com', 'shutterfly.com', 'dell.com', 'w3schools.com', 'surveymonkey.com', 'today.com', 'citrixonline.com', 'weather.gov', 'npr.org', 'bluehost.com', 'ancestry.com', 'typepad.com', 'priceline.com', 'worldstarhiphop.com', 'taboola.com', 'whitepages.com', 'cnbc.com', 'tigerdirect.com', 'people.com', 'kmart.com', 'woot.com', 'disqus.com', 'stackexchange.com', 'realtor.com', 'comcast.com', 'careerbuilder.com', 'nypost.com', 'gotomeeting.com', 'list-manage.com', 'slate.com', 'taleo.net', 'walgreens.com', 'twitch.tv', 'bitly.com', 'mapquest.com', 'marketwatch.com', 'microsoftonline.com', 'usbank.com', 'reuters.com', 'zulily.com', 'clickbank.com', 'sina.com.cn', 'eonline.com', 'bhphotovideo.com', 'ticketmaster.com', 'sfgate.com', 'fandango.com', '4dsply.com', 'taobao.com', 'cbs.com', 'hp.com']
    
    handles = []
    names = []
    
    rank = 1
    for domain in arin_domains_250:
        
        print "<tr>"
        print '<td><a href="http://www.alexa.com/siteinfo/' + domain + '">' + str(rank) + '</a></td>'
        print '<td><a href="http://' + domain + '">' + domain + '</a></td>'
        try:
            answers = dns.resolver.query(domain, 'A')
            
            # get org from IP from ARIN API
            url = 'http://whois.arin.net/rest/ip/' + answers[0].address
            headers = {'Accept': 'application/json'}
            r = requests.get(url, headers=headers)
            jr = json.loads(r.text)

            ip_address = answers[0].address
            
            print "<td>" + ip_address + "</td>"

            if 'net' in jr and 'orgRef' in jr['net'] and '@name' in jr['net']['orgRef']:
                handles.append(jr['net']['orgRef']['@handle'])
                names.append({jr['net']['orgRef']['@handle']: jr['net']['orgRef']['@name']})
                print '<td><a href="' + jr['net']['orgRef']['$'] + ' " target="_blank">' + jr['net']['orgRef']['@name'] + "</a></td>"
            else:
                print "<td></td>"
                
        except:
            print '<td></td><td></td>'
        
        
        print "</tr>"
        
        rank += 1
        time.sleep(1)

    print handles
    print names
if __name__ == "__main__":
    main(sys.argv)