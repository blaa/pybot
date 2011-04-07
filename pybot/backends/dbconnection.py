class DBConnection:
    "Hold database connection information"

    def __init__(self, db, username, password='', host='localhost'):
        self.host = host
        self.db = db
        self.username = username
        self.password = password

    def args(self):
        "Return configuration in a way suitable for db.connect function"
        return {
            'host': self.host,
            'user': self.username,
            'passwd': self.password,
            'db': self.db,
        }

    def __repr__(self):
        return "%s@%s db:%s pass:%s" % (self.username, self.host, self.db, self.password)     
            
            
            
            
