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
CLAIMS=../hh-dabble-kaput/claim-spreadsheets
U=dconnolly@hopeharborkc.com

check: att_cur_norm.csv att_zoho_norm.csv
	$(DIFF) -u att_cur_norm.csv att_zoho_norm.csv | $(PAGER)

att_cur_norm.csv: $(DB) flatten_attendance_current.sql
	$(SQLITE3) -csv $(DB) '.read flatten_attendance_current.sql' >$@

att_zoho_norm.csv: create_flat_zoho.sql att_flat_zoho.csv
	$(SQLITE3) $(DB) '.read create_flat_zoho.sql'
	$(PYTHON) migrate_hh.py --load-csv \
		$(DB) att_flat_zoho.csv attendance_zoho
	(echo 'update attendance_zoho '; \
	 echo 'set client_pd = 1.0 * client_pd, ins_paid = 1.0 * ins_paid;'; \
	 echo 'select * from attendance_zoho;') \
	| $(SQLITE3) -csv $(DB)  > $@


attendance_flat_dabble.csv: $(DB) flatten_attendance_dabble.sql
	(echo ".output $@"; echo ".read flatten_attendance_dabble.sql") \
	  | $(SQLITE3) -csv $(DB) 

claims_scrape: claim_grok.py
	$(PYTHON) claim_grok.py $(CLAIMS)

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

