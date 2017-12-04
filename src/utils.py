import json

def valid_json(json_str):
	try:
		_ = json.loads(json_str)
		return True
	except ValueError:
		return False
