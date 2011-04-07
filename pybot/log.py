import time

class Log:
    NOTICE = 1
    ERROR = 2
    WARN = 3
    INTERNAL = 4
    SILENT = 10

    def __init__(self, logfile="bot.log", verbose=SILENT, level=WARN):
        "Open log file"
        if Log.__instance:
            raise Exception("Log is a singleton, use .create method")
        self.level = level
        self.verbose = verbose
        self.f = open(logfile, "a")

    __instance = None
    @classmethod
    def create(cls, logfile="bot.log", verbose=SILENT, level=WARN):
        if not cls.__instance:
            cls.__instance = Log(logfile, verbose, level)
        
        return cls.__instance

    def __del__(self):
        "Close log file and cleanup"
        self.f.close()

    def msg(self, message, level):
        "Universal message adder"
        txt = self.__prompt_(level) + message;
        if level >= self.level:
            self.f.write(txt + "\n")
            self.f.flush()
        if level >= self.verbose:
            print(txt)
                

    def notice(self, message, *args):
        "Add notice"
        self.msg(message % args, self.NOTICE)
    
    def warn(self, message, *args):
        "Add warning"
        self.msg(message % args, self.WARN)

    def error(self, message, *args):
        "Add error"
        self.msg(message % args, self.ERROR)

    def __timestamp_(self):
        "Create timestamp for log"
        return time.strftime("%y/%m/%d %T")

    def __type_(self, level):
        "Return level name"
        if level == self.ERROR:
            return "ERROR "
        elif level == self.NOTICE:
            return "NOTICE"
        elif level == self.WARN:
            return "WARN  "
        else:
            return "UNKNOW"

    def __prompt_(self, level):
        "Create whole prompt"
        if level == self.INTERNAL:
            return ("%s: ") % (self.__timestamp_()) 
        else:
            return ("%s %s: ") % (self.__timestamp_(), self.__type_(level)) 


