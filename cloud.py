import dns.resolver
import time, json, re, csv
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



def get_arin_data():

    # Some common cloud hosts
    cloud_providers = ['amazon', 'rackspace', 'softlayer', 'microsoft', 'google']


    rows = []

    f = open('top_2000_alexa_sites.txt', 'r')

    rank = 1

    for line in f:
        row = []
        row.append(rank)
        name = line.rstrip()
    
        try:
            answers = dns.resolver.query(name, 'A')
            ip_address = answers[0].address

            # get org from IP from ARIN API
            url = 'http://whois.arin.net/rest/ip/' + ip_address
            headers = {'Accept': 'application/json'}
            r = requests.get(url, headers=headers)
            jr = json.loads(r.text)
        
            org_name = ""
            org_handle = ""
            cloud_based = 0

            if 'net' in jr and 'orgRef' in jr['net'] and '@name' in jr['net']['orgRef']:
                org_name = jr['net']['orgRef']['@name']
                org_handle = jr['net']['orgRef']['@handle']


                for cloud_provider in cloud_providers:
                    if bool(re.search(cloud_provider, org_name.lower())):

                        cloud_based = cloud_providers.index(cloud_provider) + 1
                        break
        except:
            pass

        row.append(name)
        row.append(ip_address)
        row.append(cloud_based)
        row.append(org_name)
        row.append(org_handle)
        rows.append(row)
    
        if not rank % 100:
            print "indexed %s" % rank   
    
        rank += 1
        time.sleep(1)
        print row
    
    
    with open('top_2000.csv', 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(rows)
        
        
def convert_to_table():
    """
    Read rank, name, address, etc data from csv and write it out to 
    an HTML table
    """
    
    print "converting to table"
    
    with open('top_2000.csv', 'rb') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        for row in rows:
            print "<tr>"
            for item in row:
                print "<td>%s</td>" % item
            print "</tr>"

def get_aggregate_table():
    """
    Get aggregate numbers
    """
    
    with open('top_2000.csv', 'rb') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        for row in rows:
            print row

if __name__ == "__main__":
    get_arin_data()
    #convert_to_table()