from opencage.geocoder import OpenCageGeocode
from shapely.geometry import Point
import simplejson as json
import hierarchical_level 
import scriptGetState as getAdmin1

################################### OPEN CAGE #################################
def in_db_oc(key, nameEntity, factList, replaceNameEntity, bounds):
	geocoder = OpenCageGeocode(key)
	query = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
	if(query):
		factList.append("(in_db {0} yes)".format(replaceNameEntity))
	else:
		factList.append("(in_db {0} no)".format(replaceNameEntity))

def predecessor_oc(key, nameEntity, factList, stack, replaceNameEntity, bounds):
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

def association_between_oc(key, nameEntity, factList, stack, replaceNameEntity, bounds):
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

################################### GeoNames #################################
def in_db_gn(nameEntity, cursor, factList, replaceNameEntity):
	if(cursor.execute("SELECT name FROM locations WHERE (name LIKE '%{0}' OR alternatenames LIKE '%{0},%');".format(nameEntity))):
		factList.append("(in_db {0} yes)".format(replaceNameEntity))
	else:
		factList.append("(in_db {0} no)".format(replaceNameEntity))

def predecessor_gn(nameEntity, cursor, factList, stack, replaceNameEntity):
	top_admin1Code = stack.top().getAdmin1code()
	top_admin2Code = stack.top().getAdmin2code()
	top_name = stack.top().getName()
	query=("SELECT name,feature_value FROM locations " 
	"INNER JOIN fc_view ON (locations.feature_code = fc_view.feature_code) "
	"WHERE admin1_code={0} AND admin2_code={1} AND (name LIKE '%{2}' " 
	"OR alternatenames LIKE '%{2},%') AND feature_value<"
	"(SELECT feature_value FROM locations "
	"	INNER JOIN fc_view ON (locations.feature_code = fc_view.feature_code) "
	"   WHERE (name LIKE '%{3}' OR alternatenames LIKE '%{3},%') "
	"ORDER BY feature_value LIMIT 1);")
	#cursor.execute(query.format(top_admin1Code, top_admin2Code, top_name,nameEntity))
	cursor.execute(query.format(top_admin1Code, top_admin2Code, top_name,nameEntity))
	ent = cursor.fetchall()
	if(ent):
		factList.append("(predecessor {0} {1} yes)".format(replaceNameEntity, stack.top().getName()))
	else:
		factList.append("(predecessor {0} {1} no)".format(replaceNameEntity, stack.top().getName()))

def association_between_gn(nameEntity, cursor, factList, stack, replaceNameEntity):
	top_admin1Code = stack.top().getAdmin1code()
	top_featureValue = stack.top().getFeatureValue()
	top_name = stack.top().getName()
	query = ("SELECT name,feature_code,admin1_code FROM locations "
			"WHERE admin1_code ={0} AND (name LIKE '%{1}' "
			"OR alternatenames LIKE '%{1},%') LIMIT 1;")
	query2 =("SELECT name, feature_code, admin1_code FROM locations "
			"WHERE admin1_code = "
			"(SELECT admin1_code FROM locations "
				"INNER JOIN fc_view ON (locations.feature_code = fc_view.feature_code)"
				"WHERE (name LIKE '%{0}' OR alternatenames LIKE '%{0},%') LIMIT 1) " 
			"AND (name LIKE '%{1}' OR alternatenames LIKE '%{1},%') LIMIT 1;")
	if(cursor.execute(query.format(top_admin1Code,nameEntity))):
		factList.append("(association_between {0} {1} yes)".format(replaceNameEntity, stack.top().getName()))
	elif(cursor.execute(query2.format(nameEntity,top_name))):
		factList.append("(association_between {0} {1} yes)".format(replaceNameEntity, stack.top().getName()))
	else:
		factList.append("(association_between {0} {1} no)".format(replaceNameEntity, stack.top().getName()))

################################### Stack  #################################
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