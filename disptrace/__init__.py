import trace, os, sys, threading, linecache, datetime, ConfigParser, StringIO
from jinja2 import Environment, PackageLoader

def traceiter(call):
    iters = [iter(call._lines)]
    while iters:
        for rec in iters[-1]:
            yield rec
            if rec[0] == 'call':
                iters.append(iter(rec[1][0]._lines))
                break
        else:
            iters.pop()

class TraceCall:
    tracelocal = threading.local()
    roots = []

    @classmethod
    def init(cls):
        cls.tracelocal.curfunc = None
        del cls.roots[:]
        return cls('', '', '', 0)

    def __iter__(self):
        return traceiter(self)

    def __repr__(self):
        return "<TraceCall at %x (%s.%s)>" % (id(self), self.modulename, self.funcname)

    def __init__(self, filename, modulename, funcname, lineno):
        self.parent = getattr(self.tracelocal, 'curfunc', None)
        self.filename = filename
        self.modulename = modulename
        self.funcname = funcname
        self.lineno = lineno
        self._lines = []
        TraceCall.tracelocal.curfunc = self
        if self.parent:
            self.parent.appendTrace('call', (self,))
        else:
            self.roots.append(self)

        self.localtrace = self._localtrace

    def _localtrace(self, frame, why, arg):
        if why in ("line", "exception", "c_exception", "return"):
            # record the file name and line number of every trace
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno

            self.appendTrace(why, (filename, lineno))

        if why == "return":
            self.tracelocal.curfunc = self.parent
            self.parent = None

        return self.localtrace

    def appendTrace(self, why, args):
        self._lines.append((why, args))


class DispTrace(trace.Trace):
    """
    Derived from trace.Trace class in Python standard library.

    .. method:: __init__(ignoremods=(), ignoredirs=())

      :param ignoremods: list of modules or packages to ignore.
      :param ignoredirs: list of directories whose modules or packages should 
                         be ignored.
    """

    env = Environment(
        loader=PackageLoader('disptrace', 'templates'),
        autoescape=True,
        extensions=['jinja2.ext.autoescape'])

    templ_beginstack = env.get_template('beginstack.html')
    templ_endstack = env.get_template('endstack.html')
    templ_call = env.get_template('call.html')
    templ_page = env.get_template('page.html')

    def __init__(self, ignoremods=(), ignoredirs=()):
        ignoremods, ignoredirs = map(list, (ignoremods, ignoredirs))
        mods, dirs = self._loadcfg()
        ignoremods += mods
        ignoredirs += dirs
        trace.Trace.__init__(
            self, trace=1, count=0,
            ignoremods=ignoremods, ignoredirs=ignoredirs)
        
        self._loadcfg()
        
    DEFAULT_CONF = """
[disptrace]
ignorepath=
ignoremodule=
"""
    
    def _getcfgfile(self):
        path = os.path.expanduser("~/.disptrace")
        if os.path.exists(path):
            return open(path)
        
    def _loadcfg(self):
        cfg = ConfigParser.SafeConfigParser()
        cfg.readfp(StringIO.StringIO(self.DEFAULT_CONF))
        
        f = self._getcfgfile()
        if f:
            cfg.readfp(f)
            
        ignorepath = cfg.get('disptrace', 'ignorepath')
        ignorepath = filter(None, 
            [p.strip() for p in ignorepath.split(os.path.pathsep)])
        
        ignoremodule = cfg.get('disptrace', 'ignoremodule')
        ignoremodule = filter(None, 
            [p.strip() for p in ignoremodule.split(',')])
        return ignoremodule, ignorepath

    def globaltrace_lt(self, frame, why, arg):
        """Handler for call events.

        If the code block being entered is to be ignored, returns `None',
        else returns self.localtrace.
        """
        if why == 'call':
            code = frame.f_code
            filename = code.co_filename#frame.f_globals.get('__file__', None)
            if filename:
                # XXX modname() doesn't work right for packages, so
                # the ignore support won't work right for packages
#                modulename = trace.modname(filename)
                modulename = frame.f_globals.get('__name__', None)
                if __name__ != modulename:
                    if modulename is not None:
                        ignore_it = self.ignore.names(filename, modulename)
                        if not ignore_it:
                            call = TraceCall(filename, modulename,
                                code.co_name, frame.f_lineno)
                            return call.localtrace

    def run(self, cmd):
        self.root = TraceCall.init()
        return trace.Trace.run(self, cmd)

    def runctx(self, cmd, globals=None, locals=None):
        self.root = TraceCall.init()
        return trace.Trace.runctx(self, cmd, globals, locals)

    def runfunc(self, func, *args, **kw):
        self.root = TraceCall.init()
        return trace.Trace.runfunc(self, func, *args, **kw)

    def render(self):
        """ return HTML format string of execused line of codes."""

        stack = []
        page = []
        lines = []
        modules = {}
        seq = 0
        for why, args in self.root:
            seq += 1
            if why == 'call':
                call, = args
                modules.setdefault(call.modulename, []).append(call.funcname)

                if lines:
                    page.append(self.templ_call.render(lines=lines, level=len(stack), call=stack[-1]))
                    del lines[:]
                stack.append(call)
                page.append(self.templ_beginstack.render(seq=seq, call=call, level=len(stack)))

                if call.filename and call.lineno:
                    line = unicode(linecache.getline(call.filename, call.lineno), 'utf-8', 'replace')
                else:
                    line = u''
                lines.append((call.lineno, line))
            elif why == 'line':
                filename, lineno = args
                if filename and lineno:
                    line = unicode(linecache.getline(filename, lineno), 'utf-8', 'replace')
                else:
                    line = u''
                lines.append((lineno, line))
            elif why == 'return':
                if lines:
                    page.append(self.templ_call.render(lines=lines, level=len(stack), call=stack[-1]))
                    del lines[:]

                page.append(self.templ_endstack.render())
                stack.pop()

        if lines:
            page.append(self.templ_call.render(lines=lines, level=len(stack), call=stack[-1]))


        modules = list(modules.items())
        modules.sort()
        modules = [(module, sorted(set(funcs))) for module, funcs in modules]
        return self.templ_page.render(created=datetime.datetime.now(), contents=u"".join(page), modules=modules)

