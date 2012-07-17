import disptrace


def browse_disptrace(dt):
    import tempfile, webbrowser, urllib, os

    html = dt.render()
    tempfiledes, temppath = tempfile.mkstemp(suffix='.html')
    tempfile = os.fdopen(tempfiledes, "w")
    tempfile.write(html)
    tempfile.close()
    tempurl = "file://{}".format(urllib.pathname2url(temppath))
    webbrowser.get(None).open_new(tempurl)


def if_test(a, b, c):
    if a > 10:
        print "this"
    elif b > 10:
        print "that"
    else:
        print "result is", b*c

t = disptrace.DispTrace()
t.runfunc(if_test, 1, 2, 3)
browse_disptrace(t)


