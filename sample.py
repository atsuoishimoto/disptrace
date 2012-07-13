import disptrace, urlparse

def test():
    urlparse.urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')

t = disptrace.DispTrace()
t.runfunc(test)
print t.render()
