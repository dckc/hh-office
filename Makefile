# Convert database schema from HTML to SQL via OWL
#
# 1. make
#    to load unlinked data
# 2. log in and run fixup.link_officers etc.
#

MKDIR=mkdir

XSLTPROC=xsltproc
PYTHON=python
SQLITE3=sqlite3
DIFF=diff
PAGER=less

DB=/tmp/dz.db
BAK=../hh-dabble-kaput/Dabble-2011-05-16-130809
U=dconnolly@hopeharborkc.com

check: att_cur_norm.csv att_zoho_norm.csv
	$(DIFF) -u att_cur_norm.csv att_zoho_norm.csv | $(PAGER)

att_cur_norm.csv: $(DB) flatten_attendance_current.sql csv_norm.py
	$(SQLITE3) -csv $(DB) '.read flatten_attendance_current.sql' \
		| $(PYTHON) csv_norm.py /dev/stdin > $@

att_zoho_norm.csv: csv_norm.py att_flat_zoho.csv
	$(PYTHON) csv_norm.py  att_flat_zoho.csv >$@

attendance_flat_dabble.csv: $(DB) flatten_attendance_dabble.sql
	(echo ".output $@"; echo ".read flatten_attendance_dabble.sql") \
	  | $(SQLITE3) -csv $(DB) 

start: load-basics load-visits

load-visits: $(DB) zoho-api-key
	$(PYTHON) migrate_hh.py --load-visits $(DB) $(U)

load-basics: $(DB) zoho-api-key
	$(PYTHON) migrate_hh.py --load-basics $(DB) $(U)

$(DB): $(BAK)/Visit.csv hh_data.sql
	$(PYTHON) migrate_hh.py --prepare-db $(DB) $(BAK)


hh_data.sql: hh_data.owl owl2sql.xsl
	$(XSLTPROC) --novalid -o $@ owl2sql.xsl hh_data.owl

hh_data.owl: hh_data.html grokDBSchema.xsl
	$(XSLTPROC) --novalid -o $@ grokDBSchema.xsl hh_data.html

clean:
	$(RM) *~ *.pyc testchiro-db hh_data.owl hh_data.sql $(DB)

