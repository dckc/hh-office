hh-office
---------

hh-office is a record keeping app for a small counseling practice.

by Dan Connolly, madmode_

_ http://www.madmode.com/

It's the Nth generation of this app:

0. a spreadsheet and a great big table for sorting :)
1. a filemaker db
2. a web-hosted dabbledb app
3. a Zoho Creator app

This is the 1st generation to be all open source, though.

It's built using xataface_, a php/mysql framework::

  11ec0e67be67f14cd0c49d4820ba42d5  xataface-1.3rc6.tar.gz

It also uses rlib_, a reporting library, for large PDF reports::

  06b3e629c6f99a8b2fd1264f32db8f56  rlib-1.3.7.tar.gz

_ http://xataface.com/
_ http://rlib.sicompos.com/

TODO
====

Unmet requirements:

* link pdf report
  * set up cgi

Near term goals:

 * permissions: view-only vs. edit

Eventual goals:

 * integrate end-of-month reporting to officers
 * integrate insurance billing
