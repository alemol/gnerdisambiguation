# tarea Shanel
# hacer script que haga peticiones POST a
# http://geoparsing.geoint.mx/ws/

import requests, sys
import simplejson as json

__author__ = 'Shanel Reyes-Palacios'

def read_file(rawText):
	try:
		input_file = open(rawText, 'r', encoding="utf8")
		text = input_file.read()
		input_file.close()
	except IOError:
		sys.exit('problem reading: ' + rawText)
	return text

def save_file(labeledText, processedText):
	try:
		output_file = open (labeledText,'w', encoding="utf8")
		output_file.write(processedText)
		output_file.close()
	except IOError:
		sys.exit('problem writting: ' + labeledText)

def request(rawText, labeledText):
	text = read_file(rawText)
	url = "http://geoparsing.geoint.mx/ws/"
	data = dict({"text" : text})
	response = requests.post(url, json = data, headers={"Content-Type":"application/json"})
	txt = json.dumps(response.json(), encoding="utf8", indent=2, ensure_ascii=False)
	save_file(labeledText, txt)
	print(response)

def main():
	rawText = sys.argv[1]
	labeledText = sys.argv[2]
	request(rawText, labeledText)	

if __name__ == '__main__':
	main()