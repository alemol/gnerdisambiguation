class Entity:
	def __init__(self):
		self.name = ''
		self.featureCode = ''
		self.longitude = ''
		self.latitude = ''
		self.admin1_code = ''
		self.admin2_code = ''
		self.featureValue = ''
		self.alternateLongitude = []
		self.alternateLatitude = []

	def setName(self, name):
		self.name = name.replace(" ","_")

	def getName(self):
		return self.name

	def setCanonicalName(self, canonicalname):
		self.canonicalname = canonicalname

	def getCanonicalName(self):
		return self.canonicalname

	def setFeatureCode(self, code):
		self.featureCode = code

	def getFeatureCode(self):
		return self.featureCode

	def setFeatureValue(self, value):
		self.featureValue = value

	def getFeatureValue(self):
		return self.featureValue

	def setAdmin1code(self,admin):
		self.admin1_code = admin

	def getAdmin1code(self):
		return self.admin1_code

	def setAdmin2code(self,admin2):
		self.admin2_code = admin2

	def getAdmin2code(self):
		return self.admin2_code

	def setLatitude(self,latitude):
		self.latitude = latitude

	def getLatitude(self):
		return self.latitude

	def setLongitude(self,longitude):
		self.longitude = longitude

	def getLongitude(self):
		return self.longitude

	def setAlternateLatitude(self,alternateLatitude):
		self.alternateLatitude.append(alternateLatitude)

	def getAlternateLatitude(self):
		return self.alternateLatitude

	def setAlternateLongitude(self,alternatelongitude):
		self.alternateLongitude.append(alternatelongitude)

	def getAlternateLongitude(self):
		return self.alternateLongitude