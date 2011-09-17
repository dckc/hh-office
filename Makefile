DIFF=diff
# see devtools target below
XSLTPROC=xsltproc
SQLAUTOCODE=sqlautocode

DABBLE_RESTORE_DB=/tmp/dz.db

hh_data1.py: $(DABBLE_RESTORE_DB)
	$(SQLAUTOCODE) sqlite:///$(DABBLE_RESTORE_DB) --noindex -o $@ \
		--noindex --generic-types

# obsolete: this is done at run-time by print_report
amt_due_skel.xml: amt_due_skel.html reportspec.xsl
	$(XSLTPROC) --novalid --output $@ reportspec.xsl amt_due_skel.html

devtools: ubuntu-packages python-packages

ubuntu-packages:
	apt-get install python-pip xsltproc python-mysqldb python-lxml

python-packages:
	pip install sqlautocode

# http://chatlogs.planetrdf.com/swig/2011-09-17#T20-15-25
# * DanC_ hunts for a way to bootstrap SQLAlchemy from an existing DB
# <gsnedders> DanC_: http://code.google.com/p/sqlautocode/
# <gsnedders> DanC_: Seemed to mostly work alright on large MySQL DB at work, though using declarative mode it didn't inc. indexes.
# sqlautocode http://pypi.python.org/pypi/sqlautocode/0.7
# eb991930cd502d826cf0f4109fedcd5d
