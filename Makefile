PYTHON=python
DIFF=diff
MYSQLDUMP=mysqldump
# see devtools target below
XSLTPROC=xsltproc
SQLAUTOCODE=sqlautocode

DABBLE_BAK=$(HOME)/Dropbox/hh-dabble-kaput/Dabble-2011-05-16-130809/
ZOHO_BAK=$(HOME)/Desktop/hh-zoho-bak/


BAK_FILE=$(HOME)/hh_office.sql.gz
restore:
	gunzip -c $(BAK_FILE) \
	| mysql --force --batch \
		-h mysql.hh-office.dreamhosters.com -u hopeharborkc -p \
		hopeharborkc


,balances: ,din attendance.sql
	$(PYTHON) mkimports.py --run attendance.sql >$@ \
		|| (mv -f $@ ,errs; exit 1)

,din: hh_from_dabble.sql ,dbak ,zin
	$(PYTHON) mkimports.py --run hh_from_dabble.sql >$@ \
		|| (mv -f $@ ,errs; exit 1)

,dbak:
	$(PYTHON) mkimports.py --dabble $(DABBLE_BAK) >$@ \
		|| (mv -f $@ ,errs; exit 1)

,zin: hh_from_zc.sql ,zbak ,hh_init
	$(PYTHON) mkimports.py --run hh_from_zc.sql && \
		touch $@

,hh_init: mkimports.py hh_data2.sql
	$(PYTHON) mkimports.py --make-tables

,zbak:
	$(PYTHON) mkimports.py --zoho $(ZOHO_BAK) >$@ \
		|| (mv -f $@ ,errs; exit 1)

hh_data_backup.sql:
	$(MYSQLDUMP) -u root -p --databases hh_office >$@


hh_data2.sql: hh_data2.py
	$(PYTHON) hh_data2.py >$@

# This was for bootstrapping; it's no longer used.
hh_data2.py:
	$(SQLAUTOCODE) `python mkimports.py --connurl` -o $@ \
		--generic-types

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
