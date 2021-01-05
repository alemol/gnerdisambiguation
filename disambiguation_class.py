import pymysql, clips, re, sys, json, factsGenerator, hierarchical_level
import scriptGetState as getAdmin1
from shapely.geometry import Point
from opencage.geocoder import OpenCageGeocode
from stack import Stack
from entity import Entity

key = 'd8c768d5f902425ea0ee628c9984ee4c'
bounds='-117.07031,14.82841,-86.92383,32.43044'

class Disambiguation:
	success = False
	resultados = []

	def __init__(self):
		self.stack = Stack()
		self.conflicts_stack = Stack()
		self.support_stack = Stack()
	
	def __del__(self):
		self.stack.removeAll()
		self.conflicts_stack.removeAll()
		self.support_stack.removeAll()

	def getResultados(self):
		return self.resultados

	#############################################################################################
	def load_entities(self, text):
		list_entity = re.findall(r'<START:location>[\s]+(.+?)[\s]+<END>',text)
		for entity in list_entity:
			factList=self.facts_generator(entity, self.stack)
			print("factList",factList)
			print("entity",entity)
			self.clip_s(factList)
		
		self.success = True
		return self.success
		
	def facts_generator(self, nameEntity, stack):
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
		
		for fact in env.facts():
			print(fact)
		for act in env.activations():
			print(act)
		print("##########################")
		env.run()
		#print(x)
		env.reset()

	def addLocation(self, nameEntity):
		e = self.getEntity(nameEntity)
		self.stack.push(e)
		print("Top de la pila: {0}".format(stack.top().getName()))
		for ee in stack.entities():
			print(ee.getName())
		self.success = False

	def addLocationWithAssociation(self, nameEntity):
		e = self.getEntityWithAssociation(nameEntity)
		self.stack.push(e)
		print("Top de la pila: {0}".format(stack.top().getName()))
		for ee in stack.entities():
			print(ee.getName())

	def addLocationWithoutAssociation(self, nameEntity):
		e = self.getEntityWithoutAssociation(nameEntity)
		self.stack.push(e)
		print("Top de la pila: {0}".format(stack.top().getName()))
		for ee in stack.entities():
			print(ee.getName())

	def stackExchange(self, nameEntity):
		replaceNameEntity = nameEntity.replace("_", " ")
		t = self.stack.top()
		self.stack.pop()
		e = self.getEntity(replaceNameEntity)
		self.getEntityWithAssociationstack.push(e)
		if(t.getFeatureValue() == 10):
			n = self.associateConflictTop(t.getName())
		else:
			n = self.getEntityWithAssociation(t.getName())
			self.stack.push(n)
		getAlternate(t,n)
		print("Top de la pila: {0}".format(self.stack.top().getName()))
		for ee in self.stack.entities():
			print(ee.getName())

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
		#print(stack.top().getName(), stack.top().getAlternateLatitude(), stack.top().getAlternateLongitude())

	def associateConflictTop(self, nameEntity):
		e = Entity()
		e.setName(nameEntity)
		e.setCanonicalName(nameEntity)
		e.setFeatureCode("other")
		e.setFeatureValue("10")
		e.setAdmin1code(stack.top().getAdmin1code())
		#e.setAdmin2code(stack.top().getAdmin2code())
		e.setLatitude(stack.top().getLatitude())
		e.setLongitude(stack.top().getLongitude())
		self.stack.push(e)
		print("Top de la pila: {0}".format(stack.top().getName()))
		#print("ot")
		#print(stack.top())
		for ee in stack.entities():
			print("associateConflictTop " + ee.getName(), ee.getAdmin1code())

	def addConflictsStack(self, nameEntity):
		e = Entity()
		e.setName(nameEntity)
		e.setFeatureCode("Other")
		e.setFeatureValue("9")
		self.conflicts_stack.push(e)
		#print("Pila de Conflictos")
		#print(conflicts_stack.entities().getName())

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
		#for entities in stack.entities():
		#	print("stack",entities.getName())

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

	def getEntity(self, nameEntity):
		geocoder = OpenCageGeocode(key)
		response = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
		e = self.addEntityObject(response,nameEntity)
		return e

	def getEntityWithAssociation(self, nameEntity):
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

	def getEntityWithoutAssociation(self, nameEntity):
		geocoder = OpenCageGeocode(key)
		query = geocoder.geocode(nameEntity, countrycode= 'mx', language='es', bounds = bounds, limit = 1, no_annotations = 1)
		e = self.addEntityObject(query,nameEntity)
		return e

	def addEntityObject(self, response,nameEntity):
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
		feature_code, feature_value = self.fvalue(response[0]["components"]["_type"])
		e.setFeatureValue(feature_value)
		e.setFeatureCode(feature_code)
		return e

	def fvalue(self, featureV):
		hlevel = hierarchical_level.dic_level()
		for key, value in hlevel.items():
			if(featureV == key):
				return key, value

def main():
	text = "Los <START:location> Tacos de doña Lupe <END>, la  <START:location> Panaderia el Rosal <END> y la <START:location> Ferreteria el clavo <END> están registrados en el municipio de <START:location> Guerrero <END> , <START:location> Tamaulipas <END>"
	initObject = Disambiguation()
	resultados = initObject.load_entities(text)
	print("GOOD?",resultados)
	del initObject

if __name__ == '__main__':
	main()