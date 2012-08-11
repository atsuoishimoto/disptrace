import disptrace, mock, StringIO, os

def func1():
    a = 1+2
    func2()
    b = 4+5
    return

def func2():
    c = 1
    func3()

def func3():
    pass

def func4():
    try:
        func5()
    except:
        pass

def func5():
    raise Exception()

def func_if(f):
    if f:
        a = 1
    else:
        b = 1

class TestTrace:
    def test_trace(self):
        t = disptrace.DispTrace()
        t.runfunc(func1)

        assert len(disptrace.TraceCall.roots) == 1
        calls = iter(disptrace.TraceCall.roots[0])

        # func1
        why, (obj,) = calls.next()
        assert why == 'call'
        assert (__file__, __name__, 'func1') == (obj.filename, obj.modulename, obj.funcname)

        assert ('line', (__file__, func1.func_code.co_firstlineno+1)) == calls.next()
        assert ('line', (__file__, func1.func_code.co_firstlineno+2)) == calls.next()

        # func2
        why, (obj,) = calls.next()
        assert why == 'call'
        assert (__file__, __name__, 'func2') == (obj.filename, obj.modulename, obj.funcname)

        assert ('line', (__file__, func2.func_code.co_firstlineno+1)) == calls.next()
        assert ('line', (__file__, func2.func_code.co_firstlineno+2)) == calls.next()

        # func3
        why, (obj,) = calls.next()
        assert why == 'call'
        assert (__file__, __name__, 'func3') == (obj.filename, obj.modulename, obj.funcname)
        assert ('line', (__file__, func3.func_code.co_firstlineno+1)) == calls.next()
        assert ('return', (__file__, func3.func_code.co_firstlineno+1)) == calls.next()

    def testExc(self):
        t = disptrace.DispTrace()
        t.runfunc(func4)

        calls = iter(disptrace.TraceCall.roots[0])

        why, (obj,) = calls.next()
        assert why == 'call'
        assert (__file__, __name__, 'func4') == (obj.filename, obj.modulename, obj.funcname)

        assert ('line', (__file__, func4.func_code.co_firstlineno+1)) == calls.next()
        assert ('line', (__file__, func4.func_code.co_firstlineno+2)) == calls.next()
        (why, (obj,)) = calls.next()
        assert why == 'call'
        assert (__file__, __name__, 'func5') == (obj.filename, obj.modulename, obj.funcname)
        assert ('line', (__file__, func5.func_code.co_firstlineno+1)) == calls.next()
        assert ('exception', (__file__, func5.func_code.co_firstlineno+1)) == calls.next()
        assert ('return', (__file__, func5.func_code.co_firstlineno+1)) == calls.next()
        assert ('exception', (__file__, func4.func_code.co_firstlineno+2)) == calls.next()
        assert ('line', (__file__, func4.func_code.co_firstlineno+3)) == calls.next()
        assert ('line', (__file__, func4.func_code.co_firstlineno+4)) == calls.next()
        assert ('return', (__file__, func4.func_code.co_firstlineno+4)) == calls.next()

    def testIf(self):
        t = disptrace.DispTrace()
        t.runfunc(func_if, False)

        calls = iter(disptrace.TraceCall.roots[0])
        (why, (obj,)) = calls.next()
        assert why == 'call'
        assert ('line', (__file__, func_if.func_code.co_firstlineno+1)) == calls.next()
        assert ('line', (__file__, func_if.func_code.co_firstlineno+3)) == calls.next()
        assert ('line', (__file__, func_if.func_code.co_firstlineno+4)) == calls.next()
        assert ('return', (__file__, func_if.func_code.co_firstlineno+4)) == calls.next()

    def testRender(self):
        t = disptrace.DispTrace()
        t.runfunc(func1)
        t.render()

    def testConfPath(self):
        conf = StringIO.StringIO("""
[disptrace]
ignorepath=%s
ignoremodule=
""" % (os.path.split(__file__)[0]))

        with mock.patch.object(disptrace.DispTrace, '_getcfgfile', return_value=conf):
            t = disptrace.DispTrace()
            t.runfunc(func1)

            assert len(disptrace.TraceCall.roots) == 1
            calls = iter(disptrace.TraceCall.roots[0])

            assert not list(calls) # calls should be empty
                
    def testConfModule(self):
        conf = StringIO.StringIO("""
[disptrace]
ignorepath=
ignoremodule=%s
""" % (__name__))

        with mock.patch.object(disptrace.DispTrace, '_getcfgfile', return_value=conf):
            t = disptrace.DispTrace()
            t.runfunc(func1)

            assert len(disptrace.TraceCall.roots) == 1
            calls = iter(disptrace.TraceCall.roots[0])

            assert not list(calls) # calls should be empty
                
if __name__ == '__main__':
    t = disptrace.DispTrace()
    t.runfunc(func3)
    print t.render()
