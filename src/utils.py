import json
import os

def valid_json(json_str):
	try:
		_ = json.loads(json_str)
		return True
	except ValueError:
		return False

def valid_question_answer_data(comp_type, question_data, answer_data):
	if comp_type == 'fill':
		return len(question_data) > 0 and len(answer_data) > 0
	elif comp_type == 'multiple_choice':
		try:
			question_data = json.loads(question_data)
			answer_data = int(json.loads(answer_data))
			question = question_data['question']
			answers = question_data['answers']
			return len(question) > 0 and len(answers) == 4 and \
		 	all(len(answer) > 0 for answer in answers)
		except:
			return False

def gitpull():
	os.system('./gitpull.sh')
