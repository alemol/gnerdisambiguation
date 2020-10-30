def dic_level():
	hierarchical_level = {}
	hierarchical_level = {
		'continent' : 0,
		'country' : 1,
		'state' : 2, 'state_district':2, 'providence':2,
		'city':3, 'town':3,
		'county' : 4,
		'region' : 5,
		'village' : 6, 'hamlet' : 6, 'locality' : 6, 'croft' : 6,
		'neighbourhood' : 7, 'shop' : 7, 'suburb' : 7, 'city_disctict' : 7, 'disctrict' : 7, 'quarter' : 7, 'city_block' : 7, 'residential' : 7,'commercial' : 7,'industrial' : 7 , 'houses' : 7, 'subdivision' : 7,'allotments' : 7,'house' : 7,'building' : 7,'public building' : 7,'isolated_dwelling' : 7,
		'building' : 8, 'railway':8, 'road' : 8, 'footway' : 8, 'street_name' : 8, 'residential' : 8, 'path' : 8, 'pedestrian' : 8,'road_reference' : 8,'square' : 8, 'place' : 8,'island' : 8,'body_of_water' : 8,'fictitious' : 8,
		'unknown' : 9
	}
	return hierarchical_level