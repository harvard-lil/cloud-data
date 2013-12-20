#!/usr/bin/python

"""
    PyWhoisAPI is a library for Python that wraps the ARIN WhoisRWS API.
    https://www.arin.net/resources/whoisrws/whois_api.html

	Questions, comments? rambasnet@gmail.com
"""

import urllib2

from urllib2 import HTTPError

__author__ = "Ram Basnet <rambasnet@gmail.com>"
__version__ = "1"

"""PyARINWhoisAPI - Easy ARIN Whois utilities in Python"""

try:
	import simplejson
except ImportError:
	try:
		import json as simplejson
	except:
		raise Exception("PyWhoisAPI requires the simplejson library (or Python 2.6) to work. http://www.undefined.org/python/")

class APIError(Exception):
	def __init__(self, msg, error_code=None):
		self.msg = msg
		#if error_code == 400:
		#	raise APILimit(msg)
	def __str__(self):
		return repr(self.msg)


class Whois:
    def __init__(self, headers=None):
        #the base URL is where ARIN is hosting the whois service
        self.baseURL = 'http://whois.arin.net/rest'

        self.opener = urllib2.build_opener()
        if headers is not None:
            self.opener.addheaders = [('User-agent', headers)]

        self.DataType = {'xml':'xml', 'json':'json', 'text':'txt', 'html':'html'}
        
        #ARIN's data model has the following five types of addressable resources
        #Point of Contacts, Organization, a network, autonomous system number(s), a customer of roganization
        self.ResourceType = ['poc', 'org', 'net', 'asn', 'customer']
               
    def constructApiURL(self, baseUrl, params):
        return baseUrl + ";" + ";".join(["%s=%s" %(key, value) for (key, value) in params.iteritems()])
    
     
    def getWhoisData(self, url, format):
        if not self.DataType.has_key(format):
            #enforce the default format returned by the service as json
            format = 'json'
        extension = self.DataType[format]
        url += "." + extension
        try:
            if format == 'json':
                return simplejson.load(self.opener.open(url))
            else:
                return self.opener.open(url).read()
        except HTTPError, e:
            raise APIError("getWhoisData() failed with a %s error code." % `e.code`)
        
        
    def getPointOfContact(self, handle, format='json'):
        resourceUrl = "/poc/%s"%(handle)
        return self.getWhoisData(self.baseURL + resourceUrl, format)
        
    def getPointOfContactsAssociatedWith(self, resourceType, resourceHandle, format='json'):
        """
        In the ARIN Whois data model, resources have relationship to other resources. Getting references
        to thes resources can be accomplished by addressing the resource in question and applying a resource type
        qualifier. For ease of use, the methods are broken to return individual resource type.
        This method fetches list of Point of Contacts related to given resource type and the resource handle.
        For example, getPointOfcontactsAssociatedWith('org', 'ARIN', 'xml') returns all the point of contacs of the organization
        with the handle ARIN in xml format.
        """
   
        RelatedResourceType = ['org', 'asn', 'net']
        
        if resourceType not in RelatedResourceType:
            raise APIError("getPointOfContactsAssociatedWith() failed due to unrecognized resource type. Resource type most be any one of %s."%str(RelatedResourceType))
        
        resourceUrl = '/%s/%s/pocs'%(resourceType, resourceHandle)
        
        return self.getWhoisData(self.baseURL + resourceUrl, format)
        
    
    def getOrganization(self, handle, fromat='json'):
        resourceUrl = "/org/%s"%(handle)
        return self.getWhoisData(self.baseURL + resourceUrl, format)
    
    
    def getOrganizationsAssociatedWithPOC(self, resourceHandle, format='json'):
        """
        In the ARIN Whois data model, resources have relationship to other resources. Getting references
        to thes resources can be accomplished by addressing the resource in question and applying a resource type
        qualifier. For ease of use, the methods are broken to return individual resource type.
        This method fetches list of organizations related to given resource type and the resource handle.
        For example, getOrganizationsAssociatedWith('poc', 'KOSTE-ARIN', 'xml') returns all the organizations of the POC
        with the handle KOSTE-ARIN in xml format.
        """
        
        #RelatedResourceType = ['poc']
        
        #if resourceType not in RelatedResourceType:
        #    raise APIError("getOrganizationsAssociatedWith() failed due to unrecognized resource type. Resource type most be any one of %s."%str(RelatedResourceType))
        
        resourceUrl = '/poc/%s/orgs'%(resourceHandle)
        
        return self.getWhoisData(self.baseURL + resourceUrl, format)   
    
    def getNetwork(self, handle, fromat='json'):
        resourceUrl = "/net/%s"%(handle)
        return self.getWhoisData(self.baseURL + resourceUrl, format)
    
    
    def getNetworksAssociatedWith(self, resourceType, resourceHandle, format='json'):
        """
        In the ARIN Whois data model, resources have relationship to other resources. Getting references
        to thes resources can be accomplished by addressing the resource in question and applying a resource type
        qualifier. For ease of use, the methods are broken to return individual resource type.
        This method fetches list of networks related to given resource type and the resource handle.
        For example, getNetworksAssociatedWith('poc', 'KOSTE-ARIN', 'xml') returns all the networks associated
        with the handle KOSTE-ARIN in xml format.
        """
   
        RelatedResourceType = ['poc', 'org']
        
        if resourceType not in RelatedResourceType:
            raise APIError("getNetworksAssociatedWith() failed due to unrecognized resource type. Resource type most be any one of %s."%str(RelatedResourceType))
        
        resourceUrl = '/%s/%s/nets'%(resourceType, resourceHandle)
        
        return self.getWhoisData(self.baseURL + resourceUrl, format)
    
    def getAutonomousSystemNumbers(self, handle, fromat='json'):
        resourceUrl = "/asn/%s"%(handle)
        return self.getWhoisData(self.baseURL + resourceUrl, format)
    
    
    def getAutonomousSystemNumbersAssociatedWith(self, resourceType, resourceHandle, format='json'):
        """
        In the ARIN Whois data model, resources have relationship to other resources. Getting references
        to thes resources can be accomplished by addressing the resource in question and applying a resource type
        qualifier. For ease of use, the methods are broken to return individual resource type.
        This method fetches list of networks related to given resource type and the resource handle.
        For example, getAutonomousSystemNumbersAssociatedWith('poc', 'KOSTE-ARIN', 'xml') returns all the ASNs associated
        with the handle KOSTE-ARIN in xml format.
        """
        RelatedResourceType = ['poc', 'org']
        if resourceType not in AllowedResourceType:
            raise APIError("getAutonomousSystemNumbersAssociatedWith() failed due to unrecognized resource type. Resource type most be any one of %s."%str(RelatedResourceType))
        
        resourceUrl = '/%s/%s/asns'%(resourceType, resourceHandle)
        
        return self.getWhoisData(self.baseURL + resourceUrl, format)
      

    def getParentNetwork(self, networkHandle, format='json'):
        """
        In the ARIN Whois data model, resources have relationship to other resources. Getting references
        to thes resources can be accomplished by addressing the resource in question and applying a resource type
        qualifier. For ease of use, the methods are broken to return individual resource type.
        This method fetches list of parent networks of the given resource handle.
        For example, getParentNetwork('NET192', 'xml') returns the list of parent networks associated
        with the handle KOSTE-ARIN in xml format.
        """
        
        resourceUrl = '/net/%s/parent'%(resourceHandle)
        
        return self.getWhoisData(self.baseURL + resourceUrl, format)
    
    def getChildNetworks(self, networkHandle, format='json'):
        """
        In the ARIN Whois data model, resources have relationship to other resources. Getting references
        to thes resources can be accomplished by addressing the resource in question and applying a resource type
        qualifier. For ease of use, the methods are broken to return individual resource type.
        This method fetches list of parent networks of the given resource handle.
        For example, getChildNetworks('NET192', 'xml') returns the list of parent networks associated
        with the handle KOSTE-ARIN in xml format.
        """
        
        resourceUrl = '/net/%s/children'%(resourceHandle)
        
        return self.getWhoisData(self.baseURL + resourceUrl, format)
    
    
    def getUnrelatedListOfOrgs(self, **kwargs):
        """
            Serach and Return a list of organizations in xml format.
            supported parameters: 
            handle - the handle of the organization
            name - the name of organization
            dba - the name of the organization does business with
        """

        url = self.constructApiURL(self.baseURL+"/orgs", kwargs)

        try:
            return self.opener.open(url).read()
        except HTTPError, e:
            raise APIError("getUnrelatedListOfOrgs() failed with a %s error code." % `e.code`)
        
    def getUnrelatedListOfCustomers(self, **kwargs):
        """
        Search and Return a list of Customers in xml format.
        supported parameters:
            handle - the handle of the customer
            name - the name of the customer
        """
        
        url = self.constructApiURL(self.baseURL+"/customers", kwargs)
        try:
            return self.opener.open(url).read()
        except HTTPError, e:
            raise APIError("getUnrelatedListOfCustomers() failed with a %s error code." % `e.code`)
        
    def getUnrelatedPointOfContacts(self, **kwargs):
        """
        Search and Return a list of POCs in xml format.
        supported parameters:
            handle - the handle of the POC
            domain - the domain of the email address for the POC
            first - the first name of the POC
            middle - the middle name of the POC
            last - the last name of the POC
            company - the company name registered by the POC
            city - the city registered by the POC
        """
        
        url = self.constructApiURL(self.baseURL+"/customers", kwargs)
        try:
            return self.opener.open(url).read()
        except HTTPError, e:
            raise APIError("getUnrelatedPointOfContacts() failed with a %s error code." % `e.code`)
        
        
    def getUnrelatedListOfAutonomousSystemNumbers(self, **kwargs):
        """
        Search and Return a list of ASNs in xml format.
        supported parameters:
            handle - the handle of the ASN
            name - the name of the ASN
        """
        
        url = self.constructApiURL(self.baseURL+"/asns", kwargs)
        try:
            return self.opener.open(url).read()
        except HTTPError, e:
            raise APIError("getUnrelatedListOfAutonomousSystemNumbers() failed with a %s error code." % `e.code`)   
        
        
    def getNetworkRegistrationRelatedToIP(self, IP, format='json'):
        """
            Gets the networks that a given particular IP address may fall within.
        """
        resourceUrl = '/ip/%s'%(IP)
        
        return self.getWhoisData(self.baseURL + resourceUrl, format)
        
        
    def getNetworkRegistrationRelatedToCIDR(self, CIDR, prefix=None, format='json'):
        """
            Gets the networks that a given the full CIDR notation of range.
        """
        if prefix is not None:
            resourceUrl = '/cidr/%s/%s'%(CIDR, prefix)
        else:
            resourceUrl = '/cidr/%s'%(CIDR)
        
        return self.getWhoisData(self.baseURL + resourceUrl, format)
    
if __name__ == "__main__":
    whois = Whois()
    #print whois.getPointOfContact('KOSTE-ARINasdfsdf', format='json')
    #print whois.getPointOfContactsAssociatedWith('org', 'ARIN', 'xml')
    #whois.getNetworksAssociatedWith('poc', 'KOSTE-ARIN', 'xml')
    
    #print whois.getUnrelatedListOfOrgs(name='ARIN*')
    #print whois.getNetworkRegistrationRelatedToIP('192.149.252.75', format='json')
    print whois.getNetworkRegistrationRelatedToCIDR('192.149.252.0/24', prefix='more')