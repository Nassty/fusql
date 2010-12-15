from functools import wraps

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def ok(self, message):
        return "%s %s %s" %( colors.OKGREEN, str(message),
                colors.ENDC )
    def warn(self, message):
        return "%s %s %s" %( colors.WARNING, str(message),
                colors.ENDC )
    
    def dump(self, message):
        return "%s %s %s" %( colors.HEADER, str(message),
                colors.ENDC )
    
def log(f):
    @wraps(f)
    def handler(*args, **kw):
        colorize = colors()
        if len(args) > 0 and "__class__" in dir(args[0]):
            header = "[MET] %s" % colorize.ok(args[0].__class__.__name__)
        else:
            header = "[FUN]"
        print "%s function %s called with (%s) " % (header, colorize.ok(f.__name__),
            colorize.warn(", ".join(map(str, args)) + " {" + ", ".join(["%s => %s"% (x,y) for x,y in
                kw.items() ] ) + "}"))
        return f(*args, **kw) 

    return handler

def dump(msg):
    colorize = colors()
    print "[SQL] dumped : %s" % colorize.dump(msg) 
if __name__ == "__main__":
    @log
    def asd(*args, **kw):
        dump(" ".join(map(str, args)))

    asd(1,2,3,4,5,6,7, asd=1, bsd=2, csd=3)
