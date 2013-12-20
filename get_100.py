import re

domains = []

f = open("html_junk.txt", "r")
 
for line in f:
    m = re.search('siteinfo/(.*)"', line)
    if m:
        domains.append(m.group(1))
        
        
print domains