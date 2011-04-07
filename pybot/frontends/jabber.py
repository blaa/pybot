import time
import xmpp

from frontend import Frontend
from ..log import Log

##
# Jabber connect / init
##
class Jabber(Frontend):

    def __init__(self, jid, password, commands):
        self.jid = jid
        self.password = password
        self.log = Log.create()
        self.commands = commands
        self.conn = None


    def mainloop(self):
        self.log.notice("Jabber taking control")
        while True:
            self.log.notice("Connecting...")
            self.__connect()

            while True: 
                try:
                    # Process actions
                    ret = self.conn.Process(1)
                    if ret == None:
                        # Disconnected -> reconnect
                        del self.conn
                        break
                except KeyboardInterrupt:
                    # User interrupted -> quit
                    return


    
    def __connect(self):
        jid = xmpp.JID(self.jid)
        user, server = jid.getNode(), jid.getDomain()
    
        conn = xmpp.client.Client(server, debug=[])
        conres = None
        while True:
            conres = conn.connect()
            if not conres:
                time.sleep(10)
                log.warn("Unable to connect to server %s, retrying...", server)
            else:   
                break

        if conres == None:
            raise FrontendException("Connection error.")
    
        if conres <> 'tls':
            self.log.warn("Warning: unable to estabilish secure connection - TLS failed!")
    
        authres = conn.auth(user, self.password, sasl=0)
        if not authres:
            self.log.error("Unable to authorize on %s - check login/password.", server)
            del conn
            raise FrontendException("Authorization error.")
    
        if authres <> 'sasl':
            self.log.warn("Warning: unable to perform SASL auth with %s. Old authentication method used!", server)
    
        conn.RegisterHandler('message', self.__message_receiver)
        conn.RegisterDisconnectHandler(self.__disconnect_handler)
        conn.sendInitPresence()
        self.log.notice("Bot started.")
        self.conn = conn
        return True
    

    def __message_send(self, conn, jid, msg):
        conn.send(xmpp.Message(jid,msg))


    def __disconnect_handler(self):
        print "Disconnect handler called"
        return


    def __message_receiver(self, conn, mess):
        text = mess.getBody()
        user = mess.getFrom().getStripped()
        domain = mess.getFrom().getDomain()

        # 1) Validate user rights to do anything.
        # 2) Parse command
        # 3) Handle errors during parsing
        # 4) Execute command
        # 5) Reply user with answer
        if text == None:
            return

        ret = self.commands.execute_command(text, user)

        reply = ret
        if reply:
            self.__message_send(conn, mess.getFrom(), reply)

        return ret


# vim:tabstop=4:expandtab
