
# preparation block 
# calling the needed libraries and setting the constants values and path.
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import datetime as dt


path = 'C:/Users/Here/DAND/'

mongoPath = 'C:/Program Files/MongoDB/'

mongoBinPath = 'C:/Program Files/MongoDB/Server/3.2/bin/'

osmFileName = 'riyadh_saudi-arabia.osm'

finalJsonFile = 'riyadh_.json'



"""
Parts of the following code is taken from the Udacity course excercises.
https://www.udacity.com/course/viewer#!/c-ud032-nd/l-768058569/e-865240067/m-863660253
"""


# the following are regEx compilations to validate the nodes
lower = re.compile(r'^([a-z]|_)*$')
addr_street = re.compile(r'^addr:([a-z]|_)+')
addr_street_type = re.compile(r'^addr:([a-z]|_)+:([a-z]|_)+')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
pc = re.compile('^1\d{4}$')




# This dictionary is used to correct street naming in the nodes
mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Rd." : "Road"
          }

#The following list contains common namming words for streets and roads
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]


# this list will be used to shape the node by creating a dictionary key 
# named created containing keys for all the list elements if available
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]



def _count_tags(filename):
        '''Categorize every OSM Element name into groups using the other method : _key_type() '''

        keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
        for event, element in ET.iterparse(filename):
            if event == 'end':
                keys = _key_type(element, keys)
               

       
        return keys


def _key_type(element, keys):

	'''categorise the elements names into groups according to regEx to find the problematic keys'''
    if element.tag == "tag":

        att = element.attrib
        k = att['k']
        v = att['v']
        #print k, '--', v
        
        counter = 0
        result = lower.search(k)
        if not result == None:
            keys['lower'] += 1
            counter+=1
                    
        
        result = lower_colon.search(k)
        if not result == None:
            keys["lower_colon"] += 1
            counter+=1
            
        result = problemchars.search(k)
        if not result == None:
            keys["problemchars"] += 1
            counter+=1
            print 'problematic key/value' ,k, ' : ', v
            
        
        if counter == 0 :
            keys['other'] +=1
        
    return keys


	

#1st function to call	
def findTagsCount(osmFileName):
	'''Count tags and find problematic keys [Code is taken from the Udacity project excercises]
	'''
	print dt.datetime.now(), ' start time' 
	# to measure time because %time and %timeit didn't work as expected and 
	# to save time I resorted to this simple way

	keys = _count_tags(osmFileName)
	print dt.datetime.now(), ' END time'


	print "keys :"
	pprint.pprint(keys)

	print '-----------'



	
	
	
#2nd callable	
def findUniqueKeys(filename):
        
    ''' find unique keys in the tags elements and have a look at them '''
        
	tagKeys = set()# a set() so that only unique values are stored
	
	for event, element in ET.iterparse(filename):
		if event == 'end':
			if element.tag == 'tag':
				tagKeys.add(element.attrib['k'])
			   
					
						

	print " [", len(tagKeys),'] Unique keys :'
	pprint.pprint(tagKeys)
	return tagKeys



#3rd callable 	
def printValuesOfTheKey(filename, keyForValue):
    ''' print values of the suspected keys or problematic keys'''    
	for event, element in ET.iterparse(filename):
		if event == 'end':
						 
			if element.tag == 'tag' and element.attrib['k'] == keyForValue:
				print element.attrib['v']
         
       
  

  
# 4th callable
def extractParentElementsByKey(filename, key):
    '''  extract parent elements by keys so we can extract the userID and user name '''   
	elList =[]
	flag = False
	
	for event, element in ET.iterparse(filename):
		if event == 'end':
			if flag == True:
				if element.tag == 'node' or element.tag == 'way' or element.tag == 'relation':
					elList.append(element)
					flag=False
		   
			if element.tag == 'tag':
				if element.attrib['k'] == key:
					flag = True
					
						


	#debugging:
	#for e in  elList:
		#print 'user: ',e.attrib['user'], 'uid: ', e.attrib['uid']

		
		
	uids = []
	for el in elList:
		uids.append('uid: '+el.attrib['uid']+', user: '+ el.attrib['user'])


	# This is a neat library (collections.Counter) that change the List of element 
	# into a dictionary with count for each element repeated in the the list
	from collections import Counter
	countIds = Counter(uids)


	for k in countIds :
		print k, '... Count: ', countIds[k]
 
	return elList



		
		
		
		
		
#5th callable
def findPostalCodeErrors(filename, keyForValue = 'addr:postcode'):
    
	'''check if the postal codes are not valid; using the guidelines from the saudi post
	located here: http://www.address.gov.sa/en/address-format/zip-code
	notice that the postal code should be 5 digits starting with '1' '''
	pc = re.compile('^1\d{4}$')
	
	elList=[]
 
	flag = False
	for event, element in ET.iterparse(filename):
		if event == 'end':
			if flag == True:
				if element.tag == 'node' or element.tag == 'way' or element.tag == 'relation':
					elList.append(element)
					flag=False
			if element.tag == 'tag':
				if element.attrib['k'] == keyForValue :
					result = pc.match( element.attrib['v'])
					
					if not result:
						print element.attrib['v']
						flag = True
						
	for i in elList:
		print i.tag, 
		print 'uid = ',i.attrib['uid']
		for sub in list(i):
			try:
				
				print sub.attrib['k'],' : ', sub.attrib['v']
			except:
				pass
		print '\n.....\n'                
	return elList
    
 


 
# 6th callable
def findUserNodes(filename, userID, theChunk = 100, thePart = 0):
	''' find user nodes and inspect them to notice the input errors; if any
	Notice that this method uses the _giveMeChunkOfTheList() method go give only subList of the whole user list of nodes
	to prevent the browser from creating large DOM elements and crash'''
        
	uid = 0
	elList =[]
	
	for event, element in ET.iterparse(filename):
		if event == 'end':
			if 'uid' in element.attrib.keys() and  element.attrib['uid'] == userID:
				uid +=1
				elList.append(element)
			

			
	print 'total elements = ', uid
	
	theNewList, theRemainderList = _giveMeChunkOfTheList(elList, theChunk, thePart)
        
    


 

def _giveMeChunkOfTheList(theList, theChunk, thePart = 0):
    '''
    this method is used by the findUserNodes() method and it  takes a List and return a two sliced lists (The segment wanted , and the remaining after segmenting the input list).
    the size of the slice is decided by the parameter theChunk
    the location of the chunk taken from the origional list is decided by thePart parameter
	
	----
	if the user node list returned is so large then printing it would clog the browser by creating a very large DOM nodes
	bec I am using Ipython Notebook on the browser [jupyter]
    '''
    l = len(theList)
    partsCount = 0 
    remainder = 0
    
    #make sure the length of the list is larger than the chunk
    # and when that is confirmed then divide the list length by the chunk length
    if l >  theChunk:
        partsCount = l/ theChunk
        remainder = l% theChunk
    else:
        print "Error: The Max parameter(",  theChunk ,") is larger than the List : ", l
        
    
    # make sure the part the user want to view is within the limit (parsCount)
    if thePart > partsCount -1 :
        print "Error: The part parameter(", thePart ,") is larger than the List parts : ",\
        partsCount-1, " (zero-based count)"
        thePart = 0
    
    
    firstLimit = thePart * theChunk
    secondLimit = thePart * theChunk +  theChunk
    theNewList = theList[firstLimit:secondLimit]
    theRemainderList = theList[partsCount*theChunk:]
    
    #print notification so the user can adjust the size of the chunk or which part he wants from the list
    print "The List length = ", l, ", and it is divided into = ", partsCount,\
    " parts based on the chunk parameter you entered : ",\
    theChunk, " and the part that is returned to you is specified by the last parameter (i.e. [zero-based] thePart + 1 :",\
    thePart+1, "). The remainder of the list after dividing it into chunks = ", len(theRemainderList), " items"
    
    return theNewList,theRemainderList
   
    
    

  


# for each element in the file we will pass it to this metho
# this method utilizes other method to shape the nodes from the XML format to a dictionary object
# to be converted into Json object.
def _shape_element(element):
    node = {}
    node['created']={}
    node['pos']=[0.0,0.0]
    node['node_refs']=[]
    node["address"]={}
    
    # we are interested into two types of nodes [ node and way ]
    if element.tag == "node" or element.tag == "way" :
        
        node['type'] = element.tag
        for el in element:
            if el.tag == 'tag':
                k, v , addr = _processTag(el)
                if addr == 'addr':
                    node['address'][k] = v
                elif addr == 'other':
                    #it happens that some tag elements contains k="type" v="anyvalue"
                    #this would result into changing the main node['type'] key 
                    # so we end up with json object containig abnormal types keys
                    #this is why we have to check it up in the following line
                    if k == 'type':
                        node['type-userdefined']= v
                    else:
                        node[k] = v
                else:
                    return None
                    
                
            elif el.tag == 'nd':
                ref = _processNd(el)
                node['node_refs'].append(ref)
                
                
        # setting the node created keys and GPS location
        for a in element.attrib:
            if a in CREATED:
                node['created'][a]= element.attrib[a]
            elif a == 'lat':
                node['pos'][0]= float(element.attrib[a])
            elif a == 'lon':
                node['pos'][1]= float(element.attrib[a])
            
            elif a == 'type':
                node['type-userdefined']= element.attrib[a]
            
            else: 
                node[a]= element.attrib[a]
        
    
    
        # Cleaning
        if len(node['created']) == 0 :
            del node['created']
        if len(node['pos']) == 0 :
            del node['pos']
        if len(node['node_refs']) == 0 :
            del node['node_refs']
        if len(node["address"]) == 0 :
            del node["address"]
        
            
        return node    
            
    else:
        return None


    
    
# processing any tag element inside the nodes and converting the key value pair into dictionary keys with value
def _processTag(el):
        k = el.attrib['k']
        v = el.attrib['v']
        
       
        # problemchars is already a global variable.. it is mentioned as a comment here as a reminder
        # problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
        result = problemchars.search(k)
        if result :
           
            return None, None, None
            #print 'problematic  re....', result.group()

            
            
        # addr_street_type is already a global variable.. it is mentioned as a comment here as a reminder
        # addr_street_type = re.compile(r'^addr:([a-z]|_)+:([a-z]|_)+')

        result = addr_street_type.search(k)
        if  result :
            
            return None, None, None
       
        
        # pc and addr_street are already a global variables .. they are mentioned as comment here as a reminder
        # addr_street = re.compile(r'^addr:([a-z]|_)+$')
        # pc = re.compile('^1\d{4}$')  

        result = addr_street.search(k)
        if  result :
            if k.find('street') > -1:
                v = _update_name(v, mapping)
                
            if k.find('postcode') > -1:
                r = pc.match(v)
                if not r:
                    #try to clean the extra digits
                    v = _update_postalcode( v )
                    if not v:
                        return None, None, None
                
            return k[5:], v , 'addr'
            
            
        
        # lower is already a global variable.. it is mentioned as a comment here as a reminder
        #lower = re.compile(r'^([a-z]|_)*$')
    
        result = lower.search(k)
        if  result:
            
            return k, v , 'other'
            
 
  
      
  

        return None, None, None



# This is to correct street names if they are written in abbreviations
# this method utilzed the dictionary mapping declared in the beginning.
def _update_name(name, mapping):

    # street_type_re is already a global variable.. it is mentioned as a comment here as a reminder
    # street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    n = street_type_re.search(name)
    
    if n:
        wanted = n.group()
        if wanted in mapping:
            name = street_type_re.sub(mapping[wanted],name)
            
    
    return name


# This method will try to find a valid postal code and remove the suffix digits
def _update_postalcode( code ):
    pc = re.compile('^1\d{4}') 
    r = pc.match(code)
    
    if r:
        end = r.end()
        # remove the extra digits and return
        return code[:end]
    else:
        # The postal code value is not a valid one
        print 'This is a wrong postal code, not repairable'
        return None
    
    
def _processNd(el):
    ref = el.attrib['ref']
    
    return ref



# 7th callable
def process_map(file_in, pretty = False):
	'''This is the main method that takes the file and process it for auditing and cleaning and save it into a json file
	This method uses several other methods in this module'''
    counter = 0
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            counter += 1
            el = _shape_element(element)
            
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    
    # for debugging
    print 'Element found: ',counter, ' -- Dictionary items count: ', len(data)
    
	'''
	the resultant file 'riyadh_saudi-arabia.osm.json' is not a valid json object. It is rather a
	text file containing multiple lines, where each line is a valid json object.


	We have two options here:
	A- Using the mongodb shell to import this file. it works fine on this file.
	https://docs.mongodb.org/manual/reference/program/mongoimport/ 

	B- Convert these lines of json objects into a json object 
	 i.e. array of json objects 
	 the algorithm is easy to prefix it with '[' character and append it with ']' charachter and insert ',' 
	 charachter at the end of each line
	 
	 after this i checked the result object against: http://jsonlint.com/


	the reason i picked scenario B is that I would like to try pyMongo as much as I can
	'''
	with open(file_out, "r") as fi:
		with open(path + finalJsonFile, "w") as fo:
			fo.write('[')

			
			firstTime = True
			while True:
				if firstTime:
					line = fi.readline()
					nextLine = fi.readline()
					if nextLine:
						fo.write(line + ',')
					else:
						fo.write(line + ']' )
						break
					firstTime = False
				else:
					line=nextLine
					nextLine = fi.readline()

					if nextLine:
						fo.write(line + ',')
					else:
						fo.write(line + ']' )
						break


    return data




#8th Callable
def insertIntoMongoDB():
	''' After auditing the OSM file and exporting it to a Json file now we can insert it into MongoDB 
	Also some statistics regarding the DB will be shown'''
	from pymongo import MongoClient
	import pandas as pd
	import matplotlib.pyplot as plt
	client = MongoClient("mongodb://localhost:27017")

	db = client.riyadh_osm
	with open(path +  finalJsonFile, "r") as f:
		content = json.load(f)
		db.osm.insert_many(content)
    
	print 'Number of items inserted in the DB: ', db.osm.count()	
	print 'Collection osm size = ', db.command("collstats","osm")['storageSize']/1024, 'KB'
	# Is there a difference between the db and collection ( since the db has only one collection)?
	print 'Database storage size = ', db.command("dbstats")['storageSize']/1024, 'KB'
	# Count node types

	nodesCount = db.osm.find({'type':'node'}).count()
	waysCount = db.osm.find({'type':'way'}).count()
	print 'Nodes count = ', nodesCount 
	print 'Ways count = ', waysCount
	print 'Total = ' , nodesCount + waysCount

	# to confirm my calculations are correct
	print 'Total = ', db.osm.count()

	print 'nodes percentage = ', 100*(float(nodesCount)/(nodesCount + waysCount)),' %'
	
	# Count node types using the aggregate function
	print list(db.osm.aggregate([{"$group":{"_id": "$type", "count":{"$sum": 1}}}]))
	

	# We will draw a histogram but we should remove the outliers
	# and yet the curve is skewed.
	# Because most of the items are input by afew users.

	theLength = len(users)

	%matplotlib inline
	c = pd.Series([n['count'] for n in users])
	m =  c.mean()
	std =  c.std()

	std3 = 3* c.std()
	df = pd.DataFrame(users)

	newDf = df[abs(df['count']-m)< std3]
	newDf.hist(bins=50)
	plt.xlabel('Number of nodes')
	plt.ylabel('Number of users')
	plt.title('Histogram of users participation')
	plt.show()
	
	

	
	
#9th Callable
def listUsers():
	''' Count number of users '''
	users = list(db.osm.aggregate([{"$group":{"_id": "$created.user", "count":{"$sum": 1}}}, {"$sort": {"count": -1}}]))
	return users


#10th Callable
def investigateUser( userString):
	''' Find a user that starts with the 'userString' and count the user nodes '''
	users = listUsers()
	botre = re.compile(userString)

	for i in users:
		if botre.match(i['_id'].lower()):
			print i['_id'], ' with : ',i['count'], 'items input'
        
		

#11th Callable		
def findUserNodes(userString):
	''' list user nodes '''
	userNodes = list( db.osm.find({"created.user": userString}))
	return userNodes
	

#12th Callable
def groupByKey( key ):
	''' Count types of the key input 
	for example .. (amenities) or (type).. '''
	listOfGroups = list(db.osm.aggregate([{"$match":{key:{"$exists":1}}},{"$group":{"_id": "$"+key,\
				"count":{"$sum": 1}}}, {"$sort": {"count": -1}}]))
	print key,' total = ', len(listOfGroups)
	print listOfGroups
	print '-----------'
		
		
#13th callable
def findReligionPlaceOfWorship():
	''' Find types of religion for Places of worship '''
	religionTypesList = list(db.osm.aggregate([{"$match":{"amenity":{"$exists":1},"amenity":"place_of_worship"}},\
        {"$group":{"_id":"$religion", "count":{"$sum":1}}}]))
	return religionTypesList
