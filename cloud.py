import dns.resolver
import time, json, re, csv, ConfigParser, re, subprocess
import requests
import tldextract
from tempfile import NamedTemporaryFile
import shutil

# loop through lines in top_2000_alexa_sites.txt
# for line, get the IP of the name contained in the line
# from the IP hit the ARIN API and get the org name and handle
# if org is a cloud provider, set flag to true
# write line out to TSV file
#
# line in TSV should look like:
# Alexa rank, name, address, org name, org handle, cloud flag
# 1, google.com, 1.1.1.1, google inc, goog, 0



def get_arin_data(domain_list, result_file):
    """
    Read in file containing contain containing domain names and using the ARIN
    API, get the owner of the IP. If the owner matches a string in our list of
    cloud owners, mark it
    
    domain_list = file containing list of domains. We'll get details from ARIN
    for each domain in this list
    
    result_file = file we'll write the details we get from ARIN, for each 
    domain
    """

    print "gettings arin data"

    # Some common cloud hosts
    cloud_providers = ['amazon', 'rackspace', 'softlayer', 'microsoft', 'google']

    rows = []

    f = open(domain_list, 'r')

    rank = 1

    for line in f:
        row = []
        row.append(rank)
        name = line.rstrip()
        name_parts = tldextract.extract(name)
        name = name_parts.domain + '.' + name_parts.suffix
        org_name = ""
        org_handle = ""
        cloud_based = 0
    
        try:
            answers = dns.resolver.query(name, 'A')
            ip_address = answers[0].address

            # get org from IP from ARIN API
            url = 'http://whois.arin.net/rest/ip/' + ip_address
            headers = {'Accept': 'application/json'}
            r = requests.get(url, headers=headers)
            jr = json.loads(r.text)    

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
    
        #print row
    
        rank += 1
        time.sleep(.5)
        
    
    with open(result_file, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(rows)
        

def get_ripe_data(result_file):
    # Sometimes the IP isn't owned by ARIN.
    #
    # This function operates on the result file produced by our ARIN-related
    # function. We'll loop through the CSV and if the row pointes to RIPE,
    # we'll operate on it.

    cloud_providers = ['amazon', 'rackspace', 'softlayer', 'microsoft', 'google']

    tempfile = NamedTemporaryFile(delete=False)

    org_pattern = re.compile('([^\s]+)')

    count = 0

    with open(result_file, 'rb') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        writer = csv.writer(tempfile, delimiter=',', quotechar='"')
        
        for row in rows:
            new_row = row
            
            if row[5] and row[5] == 'RIPE' or row[5] == '':
                # Let's hit the RIPE WHOIS server
                
                whois_output = subprocess.check_output(['whois', '-h', 'riswhois.ripe.net', row[2]])
                
                tokenized = whois_output.split('\n')
                
                for token in tokenized:
                    if token.startswith('descr:'):
                        descr_tokens = token.split(':')
                        for cloud_provider in cloud_providers:
                            descr_value = descr_tokens[1].strip()
                            if bool(re.search(cloud_provider, descr_value.lower())):
                                new_row[3] = cloud_providers.index(cloud_provider) + 1
                                break
                            else:
                                new_row[3] = 0
                                
                        new_row[4] = descr_value

                        # try to get an org handle by grabbing
                        # the first chunk before the space
                        org_handle = descr_value
                        matches = org_pattern.match(descr_value)

                        if matches:
                            org_handle = matches.group(1)

                        new_row[5] = org_handle

                count += 1
                    
            # write the row out to our temp file
            writer.writerow(new_row)
            time.sleep(1)
                
    # all done rewriting.
    shutil.move(tempfile.name, result_file)
    print "Updated %s rows" % count
        
def get_crunchbase_data(crunchbase_key, raw_companies_file):
    """
    given a year, get the domain names for all startups using the cruncbase api
    """
    
    # load in all crunchbase companies (many MBs)
    json_data = open(raw_companies_file)
    companies = json.load(json_data)
    json_data.close()
    
    print "processing %s companies" % len(companies)
    
    count = 1
    
    for company in companies[197700:]:
        
        payload = {'api_key': crunchbase_key}
    
        url = 'http://api.crunchbase.com/v/1/company/' + company['permalink'] + '.js'
        r = requests.get(url, params=payload)
        r_text = r.text
        # somteimes we don't get a json object
        if not r_text:
            next
        
        try:
            jr = json.loads(r_text.replace('\r\n', ''))
        except:
            print "cloudn't load %s " % r.url
            next
        
        #print json.dumps(jr, sort_keys=True, indent=4, separators=(',', ': '))
        
        
        if 'deadpooled_url' in jr and 'deadpooled_year' in jr and 'total_money_raised' in jr:
            if jr['deadpooled_url'] or jr['deadpooled_year'] or not jr['total_money_raised']:
                next

        try:
            money_raised = re.sub(r"\D", "", jr['total_money_raised'])
        
            if float(money_raised) <= 0:
                next
        except:
            next
        
        if 'founded_year' in jr and 'homepage_url' in jr and jr['homepage_url']:

            # todo: wrap this up in a function
            if jr['founded_year'] == 2006:
                with open("data/crunchbase_details_2006.csv", "a") as myfile:
                    myfile.write(jr['homepage_url'] + '\n')

            if jr['founded_year'] == 2007:
                with open("data/crunchbase_details_2007.csv", "a") as myfile:
                    myfile.write(jr['homepage_url'] + '\n')
                
            if jr['founded_year'] == 2008:
                with open("data/crunchbase_details_2008.csv", "a") as myfile:
                    myfile.write(jr['homepage_url'] + '\n')

            if jr['founded_year'] == 2009:
                with open("data/crunchbase_details_2009.csv", "a") as myfile:
                    myfile.write(jr['homepage_url'] + '\n')
                
            if jr['founded_year'] == 2010:
                with open("data/crunchbase_details_2010.csv", "a") as myfile:
                    myfile.write(jr['homepage_url'] + '\n')

            if jr['founded_year'] == 2011:
                with open("data/crunchbase_details_2011.csv", "a") as myfile:
                    myfile.write(jr['homepage_url'] + '\n')
                
            if jr['founded_year'] == 2012:
                with open("data/crunchbase_details_2012.csv", "a") as myfile:
                    myfile.write(jr['homepage_url'] + '\n')

            if jr['founded_year'] == 2013:
                with open("data/crunchbase_details_2013.csv", "a") as myfile:
                    myfile.write(jr['homepage_url'] + '\n')

        if not count % 100:
            print "processed %s " % count


        count += 1

def convert_to_table(result_file):
    """
    Read rank, name, address, etc data from csv and write it out to 
    an HTML table
    
    result_file = file with ARIN details. 
    """

    ignore_list = ['RIPE', 'APNIC', 'AFRINIC', 'LACNIC']
    cloud_providers = ['Other', 'Amazon', 'Rackspace', 'Softlayer', 'Microsoft', 'Google']
    
    print "converting to table"
    
    total = 0
    with open(result_file, 'rb') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        for row in rows:
            if row[5] and row[5] not in ignore_list:
                total += 1
                print "<tr>"
            
                # rank 
                #print '<td>%s</td>' % row[0]
                # cloud provider
                print '<td class="%s">%s</td>' % (cloud_providers[int(row[3])], cloud_providers[int(row[3])])
                # ip
                print '<td>%s</td>' % row[1]
                # ip
                print '<td>%s</td>' % row[2]
                # ip owner
                print '<td><a href="http://whois.arin.net/rest/org/%s">%s</a></td>' % (row[5], row[4])
            
                print "</tr>"

    print "total is %s" % total
    
def get_aggregate_table(result_file, cloud_providers):
    """
    Get aggregate numbers. Count up names in cloud. Get percent of names and
    dump them out in order.
    """
    print "Aggregating results"
    
    # Some common cloud hosts
    cloud_providers = ['amazon', 'rackspace', 'softlayer', 'microsoft', 'google']
    
    with open(result_file, 'rb') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        for row in rows:
            if row[3] > 0:
                print row
                
def sum_cloud_providers(result_file):
    """
    A helper to sum cloud providers
    """
    
    ignore_list = ['RIPE', 'APNIC', 'AFRINIC', 'LACNIC']
    
    total = 0
    sums = [0,0,0,0,0,0]
    
    with open(result_file, 'rb') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        for row in rows:
                if row[5] and row[5] not in ignore_list:
                    total += 1
                    sums[int(row[3])] += 1
                    
    print "total %s names" % total
    
    for sum in sums:
        perc = "{0:.2f}%".format(float(sum)/total * 100)
        print "<td>%s or %s</td>" % (sum, perc)

if __name__ == "__main__":
    """
    get alexa names, get the top 2000 sites from alex and dump them in a file
    
    get arin data, given a csv file of domain names, create a csv file
    of name, ip, ownership, cloud hosted, and other detals
    
    get crunchbase data, get the domain names of startups created in the last year
    
    create html table of names, given a csv of arin data, create an html table
    
    create html table of aggregate, given a csv file of arin data, aggregate cloud
    usage and print html table
    
    """
    
    # Config file for things we don't want git to track
    config = ConfigParser.RawConfigParser()
    config.read('etc/settings.cfg')
    crunchbase_key = config.get('general', 'crunchbase_key')
    
    
    #get_crunchbase_data(crunchbase_key, 'crunchbase_companies.json')
    #get_arin_data('data/crunchbase_details_2010.txt', 'data/results/crunchbase_2010.csv')
    result_files = ['data/results/crunchbase_2008.csv',
        'data/results/crunchbase_2009.csv', 'data/results/crunchbase_2010.csv',
        'data/results/crunchbase_2011.csv', 'data/results/crunchbase_2012.csv',
        'data/results/top_2000.csv']
    
    for result_file in result_files:
        get_ripe_data(result_file)
    #sum_cloud_providers('data/results/crunchbase_2009.csv')
    #convert_to_table('data/results/crunchbase_2009.csv')
    #get_aggregate_table('top_2000.csv')
