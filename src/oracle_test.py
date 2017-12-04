import cx_Oracle

def oracle_test(table_name, row_count = 10):
	myDsn = cx_Oracle.makedsn('80.65.65.66', '1521', 'ETFLAB')
	conn = cx_Oracle.connect(user='BP09', password='o7uwfSxI', dsn=myDsn)
	cursor = conn.cursor()
	statement = 'SELECT * FROM {0} SAMPLE(2) WHERE ROWNUM <= {1}'.format('BP07.' + table_name, row_count)
	cursor.execute(statement)
	user_data = cursor.fetchall()
	cursor.close()
	conn.close()
	return '<html><body>' + '<br>'.join([str(user) for user in user_data]) + '</body></html>'

if __name__ == '__main__':
	oracle_test('USERS')
