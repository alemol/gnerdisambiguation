import clips, re, sys, json, factsGenerator, hierarchical_level
import scriptGetState as getAdmin1
import DBconnection
from shapely.geometry import Point
from opencage.geocoder import OpenCageGeocode
from stack import Stack
from entity import Entity

key = 'd8c768d5f902425ea0ee628c9984ee4c'
bounds='-117.07031,14.82841,-86.92383,32.43044'

class Disambiguation:
	success = False
	resultados = []
	method = "opencage"

	def __init__(self, method):
		self.stack = Stack()
		self.conflicts_stack = Stack()
		self.support_stack = Stack()
		self.method = method
	
	def __del__(self):
		self.stack.removeAll()
		self.conflicts_stack.removeAll()
		self.support_stack.removeAll()

	def getResultados(self):
		return self.resultados

	#############################################################################################
	def load_entities(self, text):
		list_entity = re.findall(r'<START:location>[\s]+(.+?)[\s]+<END>',text)
		if (self.method == "opencage"):
			for entity in list_entity:
				factList=self.facts_generator_oc(entity, self.stack)
				self.clip_s(factList)
		elif (self.method == "geonames"):
			self.conn = DBconnection.db_conect() 
			for entity in list_entity:
				factList=self.facts_generator_gn(entity, self.conn, self.stack)
				self.clip_s(factList)
		else:
			print("Ingrese un metodo valido")
		self.success = True
		return self.success
		
	def facts_generator_oc(self, nameEntity, stack):
		print("opencage")
		factList = []
		replaceNameEntity = nameEntity.replace(" ", "_")
		if (stack.isEmpty()):
			factsGenerator.in_db_oc(key, nameEntity, factList, replaceNameEntity, bounds)
			factsGenerator.stackIsEmpty(factList, stack)
		else:
			factsGenerator.in_db_oc(key, nameEntity, factList, replaceNameEntity, bounds)
			factsGenerator.predecessor_oc(key, nameEntity, factList, stack, replaceNameEntity, bounds)
			factsGenerator.association_between_oc(key, nameEntity, factList, stack, replaceNameEntity, bounds)
			factsGenerator.stackIsEmpty(factList, stack)
		return factList

	def facts_generator_gn(self, nameEntity, conn, stack):
		print("geonames")
		cursor = conn.cursor()
		factList = []
		replaceNameEntity = nameEntity.replace(" ", "_")
		if (stack.isEmpty()):
			factsGenerator.in_db_gn(nameEntity, cursor, factList, replaceNameEntity)
			factsGenerator.stackIsEmpty(factList, stack)
		else:
			factsGenerator.in_db_gn(nameEntity, cursor, factList, replaceNameEntity)
			factsGenerator.predecessor_gn(nameEntity, cursor, factList, stack, replaceNameEntity)
			factsGenerator.association_between_gn(nameEntity, cursor, factList, stack, replaceNameEntity)
			factsGenerator.stackIsEmpty(factList, stack)
		cursor.close()
		return factList

	def clip_s(self, factList):
		env = clips.Environment()
		env.define_function(self.addLocation)
		env.define_function(self.stackExchange)
		env.define_function(self.associateConflictTop)
		env.define_function(self.addConflictsStack)
		env.define_function(self.conflictAddStack)
		env.define_function(self.addLocationWithAssociation)
		env.define_function(self.addLocationWithoutAssociation)
		env.load('rules.clp')
		aux = ''
		for a in factList:
			aux += a + '\n'

		env.load_facts(aux)
		env.run()
		env.reset()

	def addLocation(self, nameEntity):
		if (self.method == "opencage"):
			e = self.getEntity_oc(nameEntity)
		elif(self.method == "geonames"):
			e = self.getEntity_gn(nameEntity)
		self.stack.push(e)
		self.success = False

	def addLocationWithAssociation(self, nameEntity):
		if (self.method == "opencage"):
			e = self.getEntityWithAssociation_oc(nameEntity)
		elif(self.method == "geonames"):
			e = self.getEntityWithAssociation_gn(nameEntity)
		self.stack.push(e)

	def addLocationWithoutAssociation(self, nameEntity):
		if (self.method == "opencage"):
			e = self.getEntityWithoutAssociation_oc(nameEntity)
		elif(self.method == "geonames"):
			e = self.getEntityWithoutAssociation_gn(nameEntity)
		self.stack.push(e)

	def stackExchange(self, nameEntity):
		replaceNameEntity = nameEntity.replace("_", " ")
		t = self.stack.top()
		self.stack.pop()
		if (self.method == "opencage"):
			e = self.getEntity_oc(replaceNameEntity)
		elif(self.method == "geonames"):
			e = self.getEntity_gn(replaceNameEntity)
			self.stack.push(e)

		if(t.getFeatureValue() == 10):
			n = self.associateConflictTop(t.getName())
		else:
			if (self.method == "opencage"):
				n = self.getEntityWithAssociation_oc(t.getName())
				self.stack.push(n)
			elif(self.method == "geonames"):
				n = self.getEntityWithAssociation_gn(t.getName())
				self.stack.push(n)
		self.getAlternate(t,n)

	def getAlternate(self, t,n):
		t_alternateLongitude = t.getAlternateLongitude()
		t_alternateLatitude = t.getAlternateLatitude()
		if (len(t_alternateLatitude)==0):
			pass
		else:
			for element in range(len(t_alternateLatitude)):
				self.stack.top().setAlternateLongitude(t_alternateLongitude[element])
				self.stack.top().setAlternateLatitude(t_alternateLatitude[element])
		self.stack.top().setAlternateLongitude(t.getLongitude())
		self.stack.top().setAlternateLatitude(t.getLatitude())

	def associateConflictTop(self, nameEntity):
		e = Entity()
		e.setName(nameEntity)
		e.setCanonicalName(nameEntity)
		e.setFeatureCode("other")
		e.setFeatureValue("10")
		e.setAdmin1code(self.stack.top().getAdmin1code())
		e.setLatitude(self.stack.top().getLatitude())
		e.setLongitude(self.stack.top().getLongitude())
		self.stack.push(e)

	def addConflictsStack(self, nameEntity):
		e = Entity()
		e.setName(nameEntity)
		e.setFeatureCode("Other")
		e.setFeatureValue("9")
		self.conflicts_stack.push(e)

	def conflictAddStack(self):
		self.stack_to_support_stack()
		top = self.support_stack.top()
		self.support_stack.pop()
		newTop = self.support_stack.top()
		while (top.getAdmin1code() == newTop.getAdmin1code()):
			if (self.support_stack.isEmpty()):
				break
			else:
				self.stack.push(top)
				top = self.support_stack.top()
				self.support_stack.pop()
		if (self.support_stack.isEmpty()):
			self.stack.push(top)
			self.conflicts_stack_to_stack()
		else:
			self.conflicts_stack_to_stack()
			self.stack.push(top)
		try:
			self.support_stack_to_stack()
		except Exception as e:
				pass

	def stack_to_support_stack(self):
		for i in range(self.stack.getSize()):
			if (self.stack.isEmpty()):
				pass
			else:
				top = self.stack.top()
				self.stack.pop()
				self.support_stack.push(top)

	def support_stack_to_stack(self):
		for i in range(self.support_stack.getSize()):
			if (self.support_stack.isEmpty()):
				pass
			else:
				top = self.support_stack.top()
				self.support_stack.pop()
				self.stack.push(top)

	def conflicts_stack_to_stack(self):
		for conflicts in conflicts_stack.entities():
			e = Entity()
			e.setName(conflicts.getName())
			e.setCanonicalName(conflicts.getName())
			e.setFeatureCode(self.stack.top().getFeatureCode())
			e.setFeatureValue(conflicts.getFeatureValue())
			e.setAdmin1code(self.stack.top().getAdmin1code())
			e.setLatitude(self.stack.top().getLatitude())
			e.setLongitude(self.stack.top().getLongitude())
			self.stack.push(e)
		self.conflicts_stack.removeAll()

	def getEntity_oc(self, nameEntity):
		geocoder = OpenCageGeocode(key)
		response = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
		e = self.addEntityObject(response,nameEntity)
		return e

	def getEntity_gn(self, nameEntity):
		conn = self.conn
		cursor = conn.cursor()
		query = ("SELECT name, d.feature_code,admin1_code,latitude,longitude,feature_value,admin2_code "
			"FROM geoparse.locations d INNER JOIN fc_view ON (d.feature_code = fc_view.feature_code) "
			"WHERE (name LIKE '%{0}' OR alternatenames LIKE '%{0},%') "
			"ORDER BY feature_value asc, population desc  LIMIT 2;")
		cursor.execute(query.format(nameEntity))
		ent = cursor.fetchall()
		e = self.addEntityObject(ent,nameEntity)
		cursor.close()
		return e

	def getEntityWithAssociation_oc(self, nameEntity):
		top_FeatureValue = self.stack.top().getFeatureValue()
		top_admin1Code = self.stack.top().getAdmin1code()
		boundsLocal = '{0},{1}'.format(self.stack.top().getLatitude(),self.stack.top().getLongitude())
		geocoder = OpenCageGeocode(key)
		query = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = boundsLocal, limit = 5, no_annotations = 1)
		if (query):
			e = self.addEntityObject(query,nameEntity)
		else:
			query2 = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1, proximity = boundsLocal)
			e = self.addEntityObject(query2,nameEntity)
		return e

	def getEntityWithAssociation_gn(self, nameEntity):
		top_FeatureValue = self.stack.top().getFeatureValue()
		top_admin1Code = self.stack.top().getAdmin1code()
		conn = self.conn
		cursor = conn.cursor()

		query=("SELECT name, d.feature_code as feature_code,"
	    	"admin1_code, latitude, longitude, feature_value, admin2_code,"
			"SQRT(POW((CAST(latitude AS DECIMAL(10,4)) - ({0})),2) + "
	    	"POW((CAST(longitude AS DECIMAL(10,4)) - ({1})),2)) AS distance_to_top "
			"FROM geoparse.locations d INNER JOIN fc_view ON(d.feature_code = fc_view.feature_code) "
				"WHERE (name LIKE '%{2}' OR alternatenames LIKE '%{2},%') "
					"AND feature_value >={3} AND admin1_code = {4} "
			"ORDER BY feature_value, distance_to_top LIMIT 2;")
		query2=("SELECT name, d.feature_code as feature_code,"
	    	"admin1_code, latitude, longitude, feature_value, admin2_code "
			"FROM geoparse.locations d INNER JOIN fc_view ON(d.feature_code = fc_view.feature_code) "
				"WHERE (name LIKE '%{0}' OR alternatenames LIKE '%{0},%') "
					"AND feature_value >={1} "
			"ORDER BY feature_value LIMIT 2;")
		query3 =  ("SELECT name, d.feature_code AS feature_code, admin1_code, "
			"latitude, longitude, feature_value,admin2_code "
			"FROM geoparse.locations d INNER JOIN fc_view ON (d.feature_code = fc_view.feature_code) " 
			"WHERE (name LIKE '%{0}' OR alternatenames LIKE '%{0},%') " 
			"ORDER BY feature_value LIMIT 2;")	
		
		if(cursor.execute(query.format(self.stack.top().getLatitude(), self.stack.top().getLongitude(), nameEntity, top_FeatureValue, top_admin1Code))):
			ent = cursor.fetchall()
			e = self.addEntityObject(ent,nameEntity)
		elif(cursor.execute(query2.format(nameEntity, top_FeatureValue))):
			ent = cursor.fetchall()
			e = self.addEntityObject(ent,nameEntity)	
		else:
			cursor.execute(query3.format(nameEntity))
			ent = cursor.fetchall()
			e = self.addEntityObject(ent,nameEntity)
		cursor.close()
		return e

	def getEntityWithoutAssociation_oc(self, nameEntity):
		geocoder = OpenCageGeocode(key)
		query = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
		e = self.addEntityObject(query,nameEntity)
		return e

	def getEntityWithoutAssociation_gn(self, nameEntity):
		conn = self.conn
		cursor = conn.cursor()
		top_FeatureValue = self.stack.top().getFeatureValue()
		query = ("SELECT name,d.feature_code,admin1_code,latitude,longitude,feature_value,admin2_code "
			"FROM locations d INNER JOIN fc_view ON (d.feature_code = fc_view.feature_code) "
			"WHERE (name LIKE '%{0}' OR alternatenames LIKE '%{0},%') "
			"AND feature_value>={1} ORDER BY feature_value LIMIT 2;")
		cursor.execute(query.format(nameEntity, top_FeatureValue))
		ent = cursor.fetchall()
		cursor.close()
		e = self.addEntityObject(ent,nameEntity)
		return e

	def addEntityObject(self, response,nameEntity):
		e = Entity()
		e.setCanonicalName(nameEntity)
		if (self.method == "opencage"):
			try:
				e.setAdmin1code(response[0]["components"]["state_code"])
			except Exception:
				coordinates = Point(response[0]["geometry"]["lng"], response[0]["geometry"]["lat"])
				state_code = getAdmin1.bridge(coordinates)
				e.setAdmin1code(state_code)
			e.setLatitude(response[0]["geometry"]["lat"])
			e.setLongitude(response[0]["geometry"]["lng"])
			e.setName(nameEntity)
			feature_code, feature_value = self.fvalue(response[0]["components"]["_type"])
			e.setFeatureValue(feature_value)
			e.setFeatureCode(feature_code)
			return e
		else:
			try:
				e.setAdmin1code(response[0][6])
			except Exception:
				coordinates = Point(response[0][4],response[0][3])
				state_code = getAdmin1.bridge(coordinates)
				e.setAdmin1code(state_code)
			
			e.setFeatureCode(response[0][1])
			e.setAdmin1code(response[0][2])
			e.setLatitude(response[0][3])
			e.setLongitude(response[0][4])
			e.setFeatureValue(response[0][5])
			e.setAdmin2code(response[0][6])
			e.setName(nameEntity)
			if len(response)==2:
				e.setAlternateLongitude(response[1][4])
				e.setAlternateLatitude(response[1][3])

			return e	

	def fvalue(self, featureV):
		hlevel = hierarchical_level.dic_level()
		for key, value in hlevel.items():
			if(featureV == key):
				return key, value

	def getStack(self):
		dic_entities = {}
		dic_entity = {}
		for ee in self.stack.entities():
			dic_entities = {'name': ee.getName(), 'feature_code':ee.getFeatureCode(),'longitude':ee.getLongitude(),'latitude':ee.getLatitude(),
			'admin1_code':ee.getAdmin1code(), 'feature_value': ee.getFeatureValue()}
			name_key = ee.getCanonicalName().replace("_", " ")
			dic_entity[name_key] = dic_entities
		return dic_entity

def main():
	text = "Los <START:location> Tacos de doña Lupe <END>, la  <START:location> Panaderia el Rosal <END> y la <START:location> Ferreteria el clavo <END> están registrados en el municipio de <START:location> Guerrero <END> , <START:location> Tamaulipas <END>"
	val = "geonames" # 1 opencage 2 geonames
	initObject = Disambiguation(val)
	resultados = initObject.load_entities(text)
	print("GOOD?",resultados)
	finalStack = initObject.getStack()
	print("Stack Complete: ",finalStack)
	del initObject

if __name__ == '__main__':
	main()