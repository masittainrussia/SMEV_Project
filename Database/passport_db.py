import sqlite3

connection = sqlite3.connect('passport_requests_database.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Requests (
id INTEGER PRIMARY KEY,
message_id TEXT NOT NULL,
json_received BLOB NOT NULL, 
response_message_id TEXT,
xml_result BLOB,
document_status_code INT,
invalidity_reason INT
)
''')

connection.commit()
