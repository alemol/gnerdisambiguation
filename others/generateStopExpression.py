import sys
import pymysql
import re
import simplejson as json

def searchExpressions(text):
	text = removesigns(text)
	list_entities = []
	list_changes = {}
	list_entities = re.findall(r'<START:location> (.+?) <END>',str(text))
	for entity in list_entities:
		newEntity = ""
		if (re.findall(r'(.*) \| El Gráfico',entity)):
			newEntity = re.findall(r'(.*) \| El Gráfico',entity)
		if(re.findall(r'esquina roja de (.+?) ', entity)):
			newEntity = re.findall(r'esquina roja de (.+?) ',entity)
		if(re.findall(r'localidad de (.*)', entity)):
			newEntity = re.findall(r'localidad de (.*)',entity)
		if(re.findall(r'hasta (.*)', entity)):
			newEntity = re.findall(r'hasta (.*)',entity)
		if(re.findall(r'poblado de (.*)', entity)):
			newEntity = re.findall(r'poblado de (.*)',entity)
		if(re.findall(r'pueblo de (.[^\|]*)', entity)):
			newEntity = re.findall(r'pueblo de (.[^\|]*)',entity)
		if(re.findall(r'colonias como (.*)', entity)):
			newEntity = re.findall(r'colonias como (.*)',entity)
		if(re.findall(r'municipio de (.*)', entity)):
			newEntity = re.findall(r'municipio de (.*)',entity)
		if(re.findall(r'municipio de # (.*)', entity)):
			newEntity = re.findall(r'municipio de # (.*)',entity)
		if(re.findall(r'carriles centrales de (.+?)',entity)):
			newEntity = re.findall(r'carriles centrales de (.+? .+?) ',entity)
		if(re.findall(r'vecindad de (.+?)', entity)):
			newEntity = re.findall(r'vecindad de (.+?) ',entity)
		if(re.findall(r'barrio (.*)', entity)): ##Barrio de
			newEntity = re.findall(r'barrio (.*)',entity)
		if(re.findall(r'Barrio (.*)', entity)): ##Barrio de
			newEntity = re.findall(r'Barrio (.*)',entity)
		if(re.findall(r'barrio de (.*)', entity)):
			newEntity = re.findall(r'barrio de (.*)',entity)
		if(re.findall(r'barrio de (.*) , ubicada en las calles .*', entity)):
			newEntity = re.findall(r'barrio de (.*) , ubicada en las calles .*',entity)
		if(re.findall(r'zócalo de (.+?)', entity)):
			newEntity = re.findall(r'zócalo de (.*)',entity)
		if(re.findall(r'pileta de panteón de la (.+?)', entity)):
			newEntity = re.findall(r'pileta de panteón de la (.+? .+?) ',entity)
		if(re.findall(r'comunidad de (.*) ', entity)):
			newEntity = re.findall(r' comunidad de (.*) ',entity)
		if(re.findall(r'Cruz de San Juan Ixtayopan en (.+?) ', entity)):
			newEntity = re.findall(r'Cruz de San Juan Ixtayopan en (.+?) ',entity)
		if(re.findall(r'tramo (.* .*)', entity)):
			newEntity = re.findall(r'tramo (.* .*)',entity)
		if(re.findall(r'caudal de aguas negras en (.*) \|', entity)):
			newEntity = re.findall(r'caudal de aguas negras en (.*) \|',entity)
		if(re.findall(r'cadaver al (.+?) ', entity)):
			newEntity = re.findall(r'cadaver al (.+?) ',entity)
		if(re.findall(r'centro de la (.[^\|]*)', entity)):
			newEntity = re.findall(r'centro de la (.[^\|]*)',entity)
		if(re.findall(r'terreno de (.*)', entity)):
			newEntity = re.findall(r'terreno de (.*) ',entity)
		if(re.findall(r'ropero de departamento en (.+?) ', entity)):
			newEntity = re.findall(r'ropero de departamento en (.+?) ',entity)
		if(re.findall(r'penal de (.+?) ', entity)):
			newEntity = re.findall(r'penal de (.+?) ',entity)
		if(re.findall(r'Pobladores de (.*)', entity)):
			newEntity = re.findall(r'Pobladores de (.*)',entity)
		if(re.findall(r'trajinera de (.*)', entity)):
			newEntity = re.findall(r'trajinera de (.*)',entity)
		if(re.findall(r'aeropuerto de la (.*)', entity)):
			newEntity = re.findall(r'aeropuerto de la (.*)',entity)
		if(re.findall(r'cabecera municipal de (.*)', entity)):
			newEntity = re.findall(r'cabecera municipal de (.*)',entity)
		if(re.findall(r'cadáver al Centro de Justicia de (.*)', entity)):
			newEntity = re.findall(r'cadáver al Centro de Justicia de (.*)',entity)
		if(re.findall(r'Centro Femenil de Readaptación Social de (.*)', entity)):
			newEntity = re.findall(r'Centro Femenil de Readaptación Social de (.*)',entity)
		if(re.findall(r'Cerrada de Niños Héroes , (.*)', entity)):
			newEntity = re.findall(r'Cerrada de Niños Héroes , (.*)',entity)
		if(re.findall(r'chinampas de (.*)', entity)):
			newEntity = re.findall(r'chinampas de (.*)',entity)
		if(re.findall(r'Conalep de Tarango (.*)', entity)):
			newEntity = re.findall(r'Conalep de Tarango (.*)',entity)
		if(re.findall(r'Centro Histórico de la (.*)', entity)):
			newEntity = re.findall(r'Centro Histórico de la (.*)',entity)
		if(re.findall(r'del Servicio de Urgencias del (.*)', entity)):
			newEntity = re.findall(r'del Servicio de Urgencias del (.*)',entity)
		if(re.findall(r'deportivo Zarco , de la (.*)', entity)):
			newEntity = re.findall(r'deportivo Zarco , de la (.*)',entity)
		if(re.findall(r'Diócesis de (.*)', entity)):
			newEntity = re.findall(r'Diócesis de (.*)',entity)
		if(re.findall(r'dirección a (.*)', entity)):
			newEntity = re.findall(r'dirección a (.*)',entity)
		if(re.findall(r'Zona Metropolitana del (.*)', entity)):
			newEntity = re.findall(r'Zona Metropolitana del (.*)',entity)
		if(re.findall(r'pirotecnia de San Pablito , en (.*)', entity)):
			newEntity = re.findall(r'pirotecnia de San Pablito , en (.*)',entity)
		if(re.findall(r'las de (.+?) ', entity)):
			newEntity = re.findall(r'las de (.+?) ',entity)
		if(re.findall(r'zona de (.*)', entity)):
			newEntity = re.findall(r'zona de (.*)',entity)
		if(re.findall(r'trajinera de (.+?) ', entity)):
			newEntity = re.findall(r'trajinera de (.+?) ',entity)
		if(re.findall(r'terreno de (.[^\|]*)', entity)):
			newEntity = re.findall(r'terreno de (.[^\|]*)',entity)
		if(re.findall(r'chelería de (.+?) ', entity)):
			newEntity = re.findall(r'chelería de (.+?) ',entity)
		if(re.findall(r'puente de la carretera a (.*)', entity)):
			newEntity = re.findall(r'puente de la carretera a (.*)',entity)
		if(re.findall(r'deportivo Zarco, de la (.+?) ', entity)):
			newEntity = re.findall(r'deportivo Zarco, de la (.+?) ',entity)
		if(re.findall(r'del servicio de urgencias del (.+?) ', entity)):
			newEntity = re.findall(r'del servicio de urgencias del (.+?) ',entity)
		if(re.findall(r'caseta de cobro de (.*)', entity)):
			newEntity = re.findall(r'caseta de cobro de (.*)',entity)
		if(re.findall(r'el Paseo Bicentenario de (.+?) ', entity)):
			newEntity = re.findall(r'el Paseo Bicentenario de (.+?) ',entity)
		if(re.findall(r'cabecera municipal de (.+?) ', entity)):
			newEntity = re.findall(r'cabecera municipal de (.+?) ',entity)
		if(re.findall(r'choque sobre (.+?) ', entity)):
			newEntity = re.findall(r'choque sobre (.+?) ',entity)
		if(re.findall(r'construcción de (.[^\|]*)', entity)):
			newEntity = re.findall(r'construcción de (.[^\|]*)',entity)
		if(re.findall(r'anciano sobre (.*) ', entity)):
			newEntity = re.findall(r'anciano sobre (.[^\|]*)',entity)
		if(re.findall(r'intento de asalto en (.[^\|]*)', entity)):
			newEntity = re.findall(r'intento de asalto en (.+?) ',entity)
		if(newEntity):
			if(re.findall(r' con (.[^\|]*)', newEntity[0])):
				newEntity = re.findall(r' con (.[^\|]*) ',newEntity[0])
			if(re.findall(r'la (.*)',newEntity[0])):
				newEntity = re.findall(r'la (.*)',newEntity[0]) 
			if(re.findall(r' , (.*)',newEntity[0])):
				newEntity = re.findall(r' , (.*)',newEntity[0]) 
			fin_entity = '<START:location> ' + str(newEntity[0].strip()) + ' <END>'
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