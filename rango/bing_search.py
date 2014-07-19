import json
import urllib, urllib2

def run_query(serach_terms):
	# Specify the base
	root_url = 'https://api.datamarket.azure.com/Bing/Search/'
	version = 'v1/'
	source = 'Web'

	# Specify how many results we wish to be returned per page.
    # Offset specifies where in the results list to start from.
    # With results_per_page = 10 and offset = 11, this would start from page 2.
	results_per_page = 10
	offset = 0

    # Wrap quotes around our query terms as required by the Bing API.
    # The query we will then use is stored within variable query.
	query = "'{0}'".format(serach_terms)
	query = urllib.quote(query)

    # Construct the latter part of our request's URL.
    # Sets the format of the response to JSON and sets other properties.
	search_url = "{0}{1}{2}?$format=json&$top={3}&$skip={4}&Query={5}".format(
		root_url,
		version,
		source,
		results_per_page,
		offset,
		query)

    # Setup authentication with the Bing servers.
    # The username MUST be a blank string, and put in your API key!
	username = ''
	bing_api_key = 'QDiIOl3QUZw5GUu5aOcxiAE5lvMrYLCqYi5hAkiV2/o'

    # Create a 'password manager' which handles authentication for us.
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, search_url, username, bing_api_key)

    # Create our resluts list which we'll populate.
	results = []

	try:
    	# Prepare for connecting to Bing's servers.
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)

    	# connect to the server and read the response generated.
		response = urllib2.urlopen(search_url).read()

    	# convert the string response to a pyhon dict object
		json_response = json.loads(response)

    	# Loop through each page returned, populaing out results list
		for result in json_response['d']['results']:
			results.append({
				'title': result['Title'],
				'link': result['Url'],
				'summary': result['Description'],
				'rank': result['ID']})

    # Catch a URLError exception - something went wrong when connecting
	except urllib2.URLError, e:
		print "Error when querying the Bing API ",e

	return results

if __name__ == '__main__':
	query =  raw_input("Please enter search key word: ")
	# Take user input

	result_list = run_query(query)
	for result in result_list:
		print 'Rank: {0}'.format(result['rank'])
		print u'Title: {0}'.format(result['title'])
		print 'Link: {0}'.format(result['link'])
		print ''
