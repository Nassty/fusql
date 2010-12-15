from functools import wraps

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def ok(self, message):
        return "%s%s%s" %( colors.OKGREEN, str(message),
                colors.ENDC )
    def warn(self, message):
        return "%s%s%s" %( colors.WARNING, str(message),
                colors.ENDC )
    
    def dump(self, message):
        return "%s%s%s" %( colors.HEADER, str(message),
                colors.ENDC )

def log(skip=False, showReturn=False):
    def _log(f):
        @wraps(f)
        def handler(*args, **kw):
            colorize = colors()

            if len(args) > 0 and "__class__" in dir(args[0]):
                header = "[MET] %s." % colorize.ok(args[0].__class__.__name__)
            else:
                header = "[FUN] "

            fun_name = colorize.ok(f.__name__)

            fun_args = colorize.warn(", ".join(map(str, args[1:])))
            if len(kw.items()) != 0:
                fun_args += colorize.warn(" {" + ", ".join(["%s => %s"% (x,y) for x,y in
                    kw.items() ] ) + "}")

            retValue = f(*args, **kw)

            retstr = ""
            if showReturn:
                retstr = " returned " + colorize.ok(str(retValue))

            if not skip:
                print "%s%s(%s)%s" % (header, fun_name, fun_args, str(retstr))

            return retValue

        return handler
    return _log

def dump(msg):
    colorize = colors()
    print "[SQL] dumped : %s" % colorize.dump(msg) 
if __name__ == "__main__":
    @log()
    def asd(*args, **kw):
        if args:
            dump(" ".join(map(str, args)))

    asd(1,2,3,4,5,6,7, asd=1, bsd=2, csd=3)
    asd(asd=1, bsd=2, csd=3)
    asd()
