import sys
import pymysql
import re
import simplejson as json

EXPRESSIONS = [
	r'(.*) \| El Gráfico',
	r'esquina roja de (.+?) ',
	r'localidad de (.*)',
	r'hasta (.*)',
	r'poblado de (.*)',
	r'pueblo de (.[^\|]*)',
	r'colonias como (.*)',
	r'municipio de (.*)',
	r'municipio de # (.*)',
	r'carriles centrales de (.+?)',
	r'vecindad de (.+?)',
	r'barrio (.*)', ##Barrio de
	r'Barrio (.*)', ##Barrio de
	r'barrio de (.*)',
	r'barrio de (.*) , ubicada en las calles .*',
	r'zócalo de (.+?)',
	r'pileta de panteón de la (.+?)',
	r'comunidad de (.*) ',
	r'Cruz de San Juan Ixtayopan en (.+?) ',
	r'tramo (.* .*)',
	r'caudal de aguas negras en (.*) \|',
	r'cadaver al (.+?) ',
	r'centro de la (.[^\|]*)',
	r'terreno de (.*)',
	r'ropero de departamento en (.+?) ',
	r'penal de (.+?) ',
	r'Pobladores de (.*)',
	r'trajinera de (.*)',
	r'aeropuerto de la (.*)',
	r'cabecera municipal de (.*)',
	r'cadáver al Centro de Justicia de (.*)',
	r'Centro Femenil de Readaptación Social de (.*)',
	r'Cerrada de Niños Héroes , (.*)',
	r'chinampas de (.*)',
	r'Conalep de Tarango (.*)',
	r'Centro Histórico de la (.*)',
	r'del Servicio de Urgencias del (.*)',
	r'deportivo Zarco , de la (.*)',
	r'Diócesis de (.*)',
	r'dirección a (.*)',
	r'Zona Metropolitana del (.*)',
	r'pirotecnia de San Pablito , en (.*)',
	r'las de (.+?) ',
	r'zona de (.*)',
	r'trajinera de (.+?) ',
	r'terreno de (.[^\|]*)',
	r'chelería de (.+?) ',
	r'puente de la carretera a (.*)',
	r'deportivo Zarco, de la (.+?) ',
	r'del servicio de urgencias del (.+?) ',
	r'caseta de cobro de (.*)',
	r'el Paseo Bicentenario de (.+?) ',
	r'cabecera municipal de (.+?) ',
	r'choque sobre (.+?) ',
	r'construcción de (.[^\|]*)',
	r'anciano sobre (.*) ',
	r'intento de asalto en (.[^\|]*)',
]

def searchExpressions(text):
	text = removesigns(text)
	list_entities = []
	list_changes = {}
	list_entities = re.findall(r'<START:location> (.+?) <END>',str(text))
	for entity in list_entities:
		newEntity = ""
		for expression in EXPRESSIONS:
			if (re.findall(expression,entity)):
				newEntity = re.findall(expression,entity)
		
		if(newEntity):
			if(re.findall(r' con (.[^\|]*)', newEntity[0])):
				newEntity = re.findall(r' con (.[^\|]*) ',newEntity[0])
			if(re.findall(r'la (.*)',newEntity[0])):
				newEntity = re.findall(r'la (.*)',newEntity[0]) 
			if(re.findall(r' , (.*)',newEntity[0])):
				newEntity = re.findall(r' , (.*)',newEntity[0]) 

			fin_entity = '<START:location> ' + str(newEntity[0].strip()) + ' <END>'

			#get initial information
			for match in re.finditer(str(newEntity[0].strip()), str(entity)):
				start = match.start()
				end = match.end()
				fin_entity = entity[:start] + fin_entity + entity[end:]
				
			entity = '<START:location> ' + str(entity) + ' <END>'
			list_changes.update({entity : fin_entity})
		else:
			pass
	finalText = removeExpressions(text, list_changes)
	return finalText
	
def removesigns(text):
	text = text.replace('\'','')
	text = text.replace('\"','')
	text = text.replace('\\\"','')
	text = text.replace(';','')
	return text

def removeExpressions(text, list_changes):
	finalText = text
	for key, value in list_changes.items():
		finalText = finalText.replace(key, value)
	return finalText