disptrace - trace Python statement execution HTML
=================================================

Disptrace traces Python code execution, generating HTML file to display
execused line of codes. The resulting HTML has navigation menu to
collapse function calls or hide paticuler modules and functions.

-----
Usage
-----

Create disptrace.Disptrace object as trace module in Python standard
library, and invoke target function to be traced as follow::

    import disptrace
    t = disptrace.DispTrace()
    t.runfunc(myfunc)
    with open("trace.html", "w") as f:
        f.write(t.render())

DispTrace.render() method generates HTML string of the information.

~/.disptrace file
-----------------

You can create ~/.disptrace file to specify default value of ignoremods
and ignoredirs in ConfigParser style ini file::

    [disptrace]
    ignorepath=/usr/local/lib/python2.6/dist-packages/:/usr/lib/python2.6/plat-linux2
    ignoremodule=sys, os

ignorepath is a list of directories whose modules or packages should be
ignored. Each path should deilmited by os.path.pathsep character (':' in
Unixes, ';' in Windows).

ignoremodule list of modules or packages to ignore. Each modules should
be delimited by ',' character.
