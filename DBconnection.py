import pymysql

def db_conect():
	conn = pymysql.connect(	
	host = "localhost",
	user = "root",
	passwd = "sreyes",
	db = "geoparse")
	return conn