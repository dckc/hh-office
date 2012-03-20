#!/home/connolly/projects/hh-office/claims/bin/python
#
# see also .htaccess and hh-office.conf
# http://pythonpaste.org/deploy/

import os
import wsgiref.handlers

from paste.deploy import loadapp

wsgi_app = loadapp('config:routing.ini',
                   relative_to=os.path.dirname(__file__))
wsgiref.handlers.CGIHandler().run(wsgi_app)
