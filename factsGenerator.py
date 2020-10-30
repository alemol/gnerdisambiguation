from opencage.geocoder import OpenCageGeocode
from shapely.geometry import Point
import simplejson as json
import hierarchical_level 
import scriptGetState as getAdmin1

def in_db(key, nameEntity, factList, replaceNameEntity, bounds):
	geocoder = OpenCageGeocode(key)
	query = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
	if(query):
		factList.append("(in_db {0} yes)".format(replaceNameEntity))
	else:
		factList.append("(in_db {0} no)".format(replaceNameEntity))

def predecessor(key, nameEntity, factList, stack, replaceNameEntity, bounds):
	geocoder = OpenCageGeocode(key)
	top_value = stack.top().getFeatureValue()
	query = geocoder.geocode(nameEntity, countrycode= 'MX', language='es', bounds = bounds, limit = 1, no_annotations = 1)
	fkey = query[0]["components"]["_type"]
	hlevel = hierarchical_level.dic_level()
	for key2, value in hlevel.items():
		if(fkey == key2):
			fvalue = value
	if(fvalue > top_value):
		factList.append("(predecessor {0} {1} yes)".format(replaceNameEntity, stack.top().getName()))
	else:
		factList.append("(predecessor {0} {1} no)".format(replaceNameEntity, stack.top().getName()))

def association_between(key, nameEntity, factList, stack, replaceNameEntity, bounds):
	geocoder = OpenCageGeocode(key)
	top_admin1Code = stack.top().getAdmin1code()
	top_featureValue = stack.top().getFeatureValue()
	query = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
	try:
		state_code = query[0]["components"]["state_code"]
	except Exception as e:
		coordinates = Point(query[0]["geometry"]["lng"], query[0]["geometry"]["lat"])
		state_code = getAdmin1.bridge(coordinates)
	if(state_code == top_admin1Code):
		factList.append("(association_between {0} {1} yes)".format(replaceNameEntity, stack.top().getName()))
	else:
		factList.append("(association_between {0} {1} no)".format(replaceNameEntity, stack.top().getName()))

def stackIsEmpty(factList, stack):
	if (stack.isEmpty()):
		factList.append("(stack is_empty yes)")
	else: 
		factList.append("(stack is_empty no)")

def conflictsStackIsEmpty(final_fact, conflicts_stack):
	if (conflicts_stack.isEmpty()):
		final_fact.append("(conflicts_stack is_empty yes)")
	else: 
		final_fact.append("(conflicts_stack is_empty no)")