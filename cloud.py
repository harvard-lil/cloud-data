import dns.resolver
import time, json
import requests

# loop through lines in top_2000_alexa_sites.txt
# for line, get the IP of the name contained in the line
# from the IP hit the ARIN API and get the org name and handle
# if org is a cloud provider, set flag to true
# write line out to TSV file
#
# line in TSV should look like:
# Alexa rank, name, address, org name, org handle, cloud flag
# 1, google.com, 1.1.1.1, google inc, goog, 0

f = open('top_2000_alexa_sites.txt', 'r')

rank = 1

for line in f:
    print rank
    name = line.rstrip()
    
    try:
        answers = dns.resolver.query(name, 'A')
        ip_address = answers[0].address

        print name, ip_address
        # get org from IP from ARIN API
        url = 'http://whois.arin.net/rest/ip/' + ip_address
        headers = {'Accept': 'application/json'}
        r = requests.get(url, headers=headers)
        jr = json.loads(r.text)

        if 'net' in jr and 'orgRef' in jr['net'] and '@name' in jr['net']['orgRef']:
            print jr['net']['orgRef']['@name']
            print jr['net']['orgRef']['@handle']
        else:
            print "no org found"
            
    except:
        pass

    print ""

    if rank == 5:
        break    
    
    rank += 1
    time.sleep(1)
    
