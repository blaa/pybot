import re
from xml.dom import minidom
from backends.dbconnection import DBConnection

def smartsplit(s):
    def wordsplit():
        res = re.finditer(r'"([^"]+)"|(\S+)', s)
        for match in res:
            if match.group(1):
                yield match.group(1)
            else:
                yield match.group(2)
    res = [str(s1).translate(None, "'\"'") for s1 in wordsplit()]
    return res

class Executor:
    "Class which builds up a 'command' to be executed in backend."
    TYPE_SQL, TYPE_CLI, TYPE_NONE = range(3)
    
    def __init__(self, sql, system, databases, users):
        "Initialize stuff; saves databases for later use"

        # Store object for doing SQL queries and command line actions
        self.sql = sql
        self.system = system
        
        # Holds information how to connect to any database
        self.databases = databases
        # Holds information about users and their access level
        self.users = users
        # Parameters we parse and use to generate sql/command
        self.parameters = []
        # SQL/CLI/NONE at the moment
        self.action_type = None
        # List of SQLs or command line commands to perform.
        self.actions = []
        # DBConnection class used for connecting to server.
        self.database = None
        self.level=None
        
    def parse_parameters(self, cur):
        for param in cur.getElementsByTagName("parameter"):
            name = param.getAttribute("name")
            self.parameters.append(name)
        
    def parse_action(self, cur):
        act = cur.getElementsByTagName("action")
        if not act:
            self.action_type = self.TYPE_NONE 
            return
        act = act[0]
        type = act.getAttribute("type")
        self.level = int(act.getAttribute("level"))
        if type == "sql":
            self.action_type = self.TYPE_SQL
            database_number = int(act.getAttribute("database"))
            self.database = self.databases[database_number]
            for sql in act.getElementsByTagName("sql"):
                self.actions.append(sql.firstChild.nodeValue.strip())
        else:
            self.action_type = self.TYPE_CLI
            for cmd in act.getElementsByTagName("command"):
                self.actions.append(cmd.firstChild.nodeValue.strip())        

    def execute(self, parameters, user):
        # Read parameters
        # Create SQL/CLI commands to run
        # run them.
        actions = list(self.actions)
        if (len(parameters)!=0):
            if parameters[0]=="help":
                if len(self.parameters)!=0:
                    ret="Parameters needed:\n"
                    for i in self.parameters:
                        ret+=i+"\n"
                else:
                        ret="No parameters needed"
                return ret
        if (len(parameters)%2):
            return "Wrong number of parameters"

        pairs = len(parameters)/2
        par = []
        for i in range(0,pairs):
            par = par + [ [parameters[2*i], parameters[2*i+1]] ]
        for k in self.parameters:
            find = 0
            for l in range(0,pairs):
                if k == par[l][0]:
                    find = 1
                    for i in range(0, len(actions)):
                        pom = '~' + k + '~'
                        actions[i] = actions[i].replace(pom, par[l][1])
            if find == 0:
                return "'" + k + "' parameter missing"

        reply = ""

        if user not in self.users:
            return "No permission to execute this command"
        if self.level < self.users[user]:
            return "No permission to execute this command"

        for i in actions:
            if self.action_type == self.TYPE_SQL:
                a = self.sql.execute(i, connection = self.database)
                reply += a
                reply += "\n"
            else:
                for i in actions:
                    reply += self.system.execute(i)
                    reply += "\n"
        return reply


class Commands:
    def __init__(self, file, sql, system):
        "Parse commands description from the file"

        # SQL backend
        self.sql = sql

        # System application backend
        self.system = system

        # Commands tree
        self.commands = {}

        # Read XML file describing commands
        tree = minidom.parse(file)

        # Parse database part
        self.databases = self.parse_databases(tree)
		
		# Parse users part
        self.users = self.parse_users(tree)

        # Parse command part
        tmp = tree.getElementsByTagName("commands")[0]
        self.parse_tree(tmp, self.commands)


    def parse_databases(self, tree):
        "Parse database definitions from XML file"
        nodes = tree.childNodes
        dbs=nodes[0].getElementsByTagName("databases")[0]
        d={}

        for i in dbs.getElementsByTagName("db"):
            db_id = int(i.getAttribute("id"))
            if db_id in d:
                raise Exception("Duplicate database ID")
            db_name = i.getAttribute("db")
            db_user = i.getAttribute("user")
            db_pass = i.getAttribute("pass")
            db_host = i.getAttribute("host")
            conn = DBConnection(db_name, db_user, db_pass, db_host)
            d[db_id] = conn
        return d
    def parse_users(self, tree):
        "Parse database definitions from XML file"
        nodes = tree.childNodes
        dbs=nodes[0].getElementsByTagName("users")[0]
        d={}

        for i in dbs.getElementsByTagName("user"):
            jid = i.getAttribute("jid")
            if jid in d:
                raise Exception("Duplicate user ID")
            user_level = int(i.getAttribute("level"))
            d[jid] = user_level
        return d

    def parse_tree(self, cur, pos):
        # Eventual new position in "keyword" tree
        newpos = None

        if isinstance(cur, minidom.Element) and len(cur.getElementsByTagName("keyword")) == 0:
            # If true, then we are at the end of tree and we need to
            # parse command definition
            attr = cur.getAttribute("name")
            pos[attr] = Executor(self.sql, self.system, self.databases, self.users)
            pos[attr].parse_parameters(cur)
            pos[attr].parse_action(cur)
        else:
            # Ok, there's something more to traverse!
            if isinstance(cur, minidom.Element) and cur.tagName == "keyword":
                attr = cur.getAttribute("name")
                newpos = {}
                pos[attr] = newpos
            if cur.firstChild:
                # Jesli bylo slowo kluczowe to 
                # analizuj wglab zaczynajac od jego
                # poziomu
                if newpos != None:
                    self.parse_tree(cur.firstChild, newpos)
                else:
                    self.parse_tree(cur.firstChild, pos)

        # Whatever happens - dig further.
        if cur.nextSibling:
            self.parse_tree(cur.nextSibling, pos)


    def execute_command(self, input, user):
        """Parse command according to the built tree.
        If it's correct - execute it. Otherwise
        raise exception describing kind of the error.
        """

        def match_recur(pos, command):
            "Helper recursive function"
            def get_error(pos,command):
                ret=""
                if len(command) == 0:
                    ret+="Command too short. You can try:\n"
                else:
                    for i in command:
                        ret+=i+" "
                    ret+="is unrecognised. Perhaps you meant:\n"
                for key in pos:
                    ret+=key+"\n"
                return ret
            def get_help(pos):
                ret="You can try:\n"
                for key in pos:
                    ret+=key+"\n"
                return ret
            if len(command) == 0:
                return (None, get_error(pos,command))
            key = command[0]
            if key in pos:
                if isinstance(pos[key], Executor):
                    return (pos[key], command[1:])
                else:
                    return match_recur(pos[key], command[1:])
            elif key=="help":
                return (None, get_help(pos))
            return (None, get_error(pos,command))

        input = smartsplit(input.strip())
        executor, parameters = match_recur(self.commands, input)
        if executor == None:
            return parameters

        return executor.execute(parameters, user)

# vim:tabstop=4:expandtab
