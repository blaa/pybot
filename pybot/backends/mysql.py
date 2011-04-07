from dbconnection import DBConnection
import MySQLdb as db

class MySQL:
    "Class supposed to wrap DB operation in a manner suitable for us"

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self, connection):
        "Connect to database"

        # print "Connecting to", connection

        if self.conn or self.cursor:
            raise Exception("Database connection already opened. Close previous first!")

        try:
            self.conn = db.connect(**connection.args())
            self.cursor = self.conn.cursor(db.cursors.DictCursor)
        except db.OperationalError, e:
            self.disconnect()
            return False
        
        return True

    def disconnect(self):
        "Disconnect from DB"
        # print "Disconnecting from database"
        if self.cursor:
            self.cursor.close()
            self.cursor = None
            
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def execute(self, sql, connection = None):
        # 1) Connect
        # 2) Execute query, prepare return value
        # 3) Disconnect
        if not self.conn and not connection:
            raise Exception("No connection and no connection parameters")
        if self.conn and connection:
            raise Exception("Connection already exists while calling select.")
        
        if connection:
            if self.connect(connection) == False:
                return "Unable to connect to database"

        # 2) Execute
        try:
            print "Executing SQL:", sql
            count = self.cursor.execute(sql)
            rows = self.cursor.fetchall()

            if sql.split()[0] != 'select':
                # Probably insert/update/delete
                return "%d rows modified." % count
            else:
                ret = "Results:\n"
                for entry in rows:
                    for key, val in entry.iteritems():
                            ret += "%s: %s\n" % (key, val)
                    ret += "\n"
                return ret

        except db.IntegrityError:
            # Nothing changed
            return "Integrity error - nothing changed."
        except db.OperationalError, e:
            code, desc = e
            return "Database operational error - try again: " + desc
        except:
            return "Database operation error. Please try again"
        finally:
            if connection:
                self.disconnect()

if __name__ == "__main__":
    m = MySQL()
    connection = DBConnection(username='otpasswd', password='otpasswd', db='otpasswd')
    print m.execute("insert into test values('a', 4)", connection)

# vim:tabstop=4:expandtab
