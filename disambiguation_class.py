import pymysql, clips, re, sys, json, factsGenerator, hierarchical_level
import scriptGetState as getAdmin1
from shapely.geometry import Point
from opencage.geocoder import OpenCageGeocode
from stack import Stack
from entity import Entity

key = 'd8c768d5f902425ea0ee628c9984ee4c'
bounds='-117.07031,14.82841,-86.92383,32.43044'
class Disambiguation:
	stack
	conflicts_stack
	support_stack	
	success = True
	resultados = []

	def __init__(self):
		stack=Stack()
		conflicts_stack=Stack()
		support_stack=Stack()
	
	def __delete__(self, instance):
		es = extractStack()
		stack.removeAll()
		conflicts_stack.removeAll()
		support_stack.removeAll()

	def getResultados(self):
		return resultados

	#############################################################################################
	def load_entities(list_entity):
		# file = read_file_as_json(filename)
		# list_entity = []
		# text = file["data"][0]["labeled"]
		# position = 0
		# list_entity = re.findall(r'<START:location>[\s]+(.+?)[\s]+<END>',text)
		# print(list_entity)
		for entity in list_entity:
			factList=facts_generator(entity, self.stack)
			#print("factList",factList)
			#print("entity",entity)
			clip_s(factList)
		
		return self.success
		
	def facts_generator(nameEntity, stack):
		factList = []
		replaceNameEntity = nameEntity.replace(" ", "_")
		if (stack.isEmpty()):
			factsGenerator.in_db(key, nameEntity, factList, replaceNameEntity, bounds)
			factsGenerator.stackIsEmpty(factList, stack)
		else:
			factsGenerator.in_db(key, nameEntity, factList, replaceNameEntity, bounds)
			factsGenerator.predecessor(key, nameEntity, factList, stack, replaceNameEntity, bounds)
			factsGenerator.association_between(key, nameEntity, factList, stack, replaceNameEntity, bounds)
			factsGenerator.stackIsEmpty(factList, stack)
		return factList

	def clip_s(factList):
		env = clips.Environment()
		env.define_function(addLocation)
		env.define_function(stackExchange)
		env.define_function(associateConflictTop)
		env.define_function(addConflictsStack)
		env.define_function(conflictAddStack)
		env.define_function(addLocationWithAssociation)
		env.define_function(addLocationWithoutAssociation)
		env.load('rules.clp')
		
		aux = ''
		for a in factList:
			aux += a + '\n'

		env.load_facts(aux)
		
		for fact in env.facts():
			print(fact)
		for act in env.activations():
			print(act)
		print("##########################")
		env.run()
		#print(x)
		env.reset()

	def addLocation(nameEntity):
		e = getEntity(nameEntity)
		self.stack.push(e)
		print("Top de la pila: {0}".format(stack.top().getName()))
		for ee in stack.entities():
			print(ee.getName())
		self.success = False

	def addLocationWithAssociation(nameEntity):
		e = getEntityWithAssociation(nameEntity)
		stack.push(e)
		print("Top de la pila: {0}".format(stack.top().getName()))
		for ee in stack.entities():
			print(ee.getName())

	def addLocationWithoutAssociation(nameEntity):
		e = getEntityWithoutAssociation(nameEntity)
		stack.push(e)
		print("Top de la pila: {0}".format(stack.top().getName()))
		for ee in stack.entities():
			print(ee.getName())

	def stackExchange(nameEntity):
		replaceNameEntity = nameEntity.replace("_", " ")
		t = stack.top()
		stack.pop()
		e = getEntity(replaceNameEntity)
		stack.push(e)
		if(t.getFeatureValue() == 10):
			n = associateConflictTop(t.getName())
		else:
			n = getEntityWithAssociation(t.getName())
			stack.push(n)
		getAlternate(t,n)
		print("Top de la pila: {0}".format(stack.top().getName()))
		for ee in stack.entities():
			print(ee.getName())

	def getAlternate(t,n):
		t_alternateLongitude = t.getAlternateLongitude()
		t_alternateLatitude = t.getAlternateLatitude()
		if (len(t_alternateLatitude)==0):
			pass
		else:
			for element in range(len(t_alternateLatitude)):
				stack.top().setAlternateLongitude(t_alternateLongitude[element])
				stack.top().setAlternateLatitude(t_alternateLatitude[element])
		stack.top().setAlternateLongitude(t.getLongitude())
		stack.top().setAlternateLatitude(t.getLatitude())
		#print(stack.top().getName(), stack.top().getAlternateLatitude(), stack.top().getAlternateLongitude())

	def associateConflictTop(nameEntity):
		e = Entity()
		e.setName(nameEntity)
		e.setCanonicalName(nameEntity)
		e.setFeatureCode("other")
		e.setFeatureValue("10")
		e.setAdmin1code(stack.top().getAdmin1code())
		#e.setAdmin2code(stack.top().getAdmin2code())
		e.setLatitude(stack.top().getLatitude())
		e.setLongitude(stack.top().getLongitude())
		stack.push(e)
		print("Top de la pila: {0}".format(stack.top().getName()))
		#print("ot")
		#print(stack.top())
		for ee in stack.entities():
			print("associateConflictTop " + ee.getName(), ee.getAdmin1code())

	def addConflictsStack(nameEntity):
		e = Entity()
		e.setName(nameEntity)
		e.setFeatureCode("Other")
		e.setFeatureValue("9")
		conflicts_stack.push(e)
		#print("Pila de Conflictos")
		#print(conflicts_stack.entities().getName())

	def conflictAddStack():
		stack_to_support_stack()
		top = support_stack.top()
		support_stack.pop()
		newTop = support_stack.top()
		while (top.getAdmin1code() == newTop.getAdmin1code()):
			if (support_stack.isEmpty()):
				break
			else:
				stack.push(top)
				top = support_stack.top()
				support_stack.pop()
		if (support_stack.isEmpty()):
			stack.push(top)
			conflicts_stack_to_stack()
		else:
			conflicts_stack_to_stack()
			stack.push(top)
		try:
			support_stack_to_stack()
		except Exception as e:
				pass
		#for entities in stack.entities():
		#	print("stack",entities.getName())

	def stack_to_support_stack():
		for i in range(stack.getSize()):
			if (stack.isEmpty()):
				pass
			else:
				top = stack.top()
				stack.pop()
				support_stack.push(top)

	def support_stack_to_stack():
		for i in range(support_stack.getSize()):
			if (support_stack.isEmpty()):
				pass
			else:
				top = support_stack.top()
				support_stack.pop()
				stack.push(top)

	def conflicts_stack_to_stack():
		for conflicts in conflicts_stack.entities():
			e = Entity()
			e.setName(conflicts.getName())
			e.setCanonicalName(conflicts.getName())
			e.setFeatureCode(stack.top().getFeatureCode())
			e.setFeatureValue(conflicts.getFeatureValue())
			e.setAdmin1code(stack.top().getAdmin1code())
			e.setLatitude(stack.top().getLatitude())
			e.setLongitude(stack.top().getLongitude())
			stack.push(e)
		conflicts_stack.removeAll()

	def getEntity(nameEntity):
		geocoder = OpenCageGeocode(key)
		response = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
		e = addEntityObject(response,nameEntity)
		return e

	def getEntityWithAssociation(nameEntity):
		top_FeatureValue = stack.top().getFeatureValue()
		top_admin1Code = stack.top().getAdmin1code()
		boundsLocal = '{0},{1}'.format(stack.top().getLatitude(),stack.top().getLongitude())
		geocoder = OpenCageGeocode(key)
		query = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = boundsLocal, limit = 5, no_annotations = 1)
		if (query):
			e = addEntityObject(query,nameEntity)
		else:
			query2 = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1, proximity = boundsLocal)
			e = addEntityObject(query2,nameEntity)
		return e

	def getEntityWithoutAssociation(nameEntity):
		geocoder = OpenCageGeocode(key)
		query = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
		e = addEntityObject(query,nameEntity)
		return e

	def addEntityObject(response,nameEntity):
		#print("addEntityObject")
		e = Entity()
	#	print("uno")
		e.setCanonicalName(nameEntity)
	#	print(nameEntity)
	#	print("dos")
		try:
			e.setAdmin1code(response[0]["components"]["state_code"])
	#		print("tres")
		except Exception:
			coordinates = Point(response[0]["geometry"]["lng"], response[0]["geometry"]["lat"])
			state_code = getAdmin1.bridge(coordinates)
			e.setAdmin1code(state_code)
		e.setLatitude(response[0]["geometry"]["lat"])
		e.setLongitude(response[0]["geometry"]["lng"])
		e.setName(nameEntity)
		feature_code, feature_value = fvalue(response[0]["components"]["_type"])
		e.setFeatureValue(feature_value)
		e.setFeatureCode(feature_code)
		return e

	def fvalue(featureV):
		hlevel = hierarchical_level.dic_level()
		for key, value in hlevel.items():
			if(featureV == key):
				return key, value

def main():
	initObject = Disambiguation()
	resultados = initObject.load_entities(listEntity)
	remove(initObject)