import sqlite3

db = sqlite3.connect('id.db')
cursor = db.cursor()
cursor.execute(f"INSERT INTO ids VALUES ('312','32133')")
db.commit()
for i in cursor.execute("SELECT id,class FROM ids").fetchall():
    print(i)
db.close()