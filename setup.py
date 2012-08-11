# -*- coding: utf-8 -*-
import os, sys
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='disptrace',
    version='0.4',
    packages=['disptrace'],
    package_data={
        'disptrace':[
            'templates/beginstack.html',
            'templates/call.html',
            'templates/endstack.html',
            'templates/page.html']},
    description = 'Generate Python trace log in HTML',
    long_description = read('README.rst'),
    author = 'Atsuo Ishimoto',
    author_email = 'ishimoto@gembook.org',
    url = 'https://github.com/atsuoishimoto/disptrace',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Debuggers',
    ],
    license='MIT License',
    zip_safe=False,
    install_requires='jinja2', 
)
