hh-office
---------

hh-office is a record keeping app for a small counseling practice.

by Dan Connolly, madmode__

__ http://www.madmode.com/

It's the Nth generation of this app:

0. a spreadsheet and a great big table for sorting :)
1. a filemaker db
2. a web-hosted dabbledb app
3. a Zoho Creator app

This is the 1st generation to be all open source, though.

It's built using xataface__, a php/mysql framework::

  11ec0e67be67f14cd0c49d4820ba42d5  xataface-1.3rc6.tar.gz

It also uses rlib__, a reporting library, for large PDF reports::

  06b3e629c6f99a8b2fd1264f32db8f56  rlib-1.3.7.tar.gz

__ http://xataface.com/
__ http://rlib.sicompos.com/

TODO
====

Unmet requirements:

 * restore from Zoho, DabbleDB backups
 * exclude inactive clients for performance?
   * move Account fields to Client table?
 * optimize entering sign-in sheets
   * reduce clutter; make it obvious how to make a new session
   * therapist order (Sep 17 testing)
   * clients case sensitive
   * pick client w keyboard
   * reduce mouse work
       * choosing clients
       * how to Save the sign-in sheet with the keyboard?
       * tabbing between fields in general
   * default Visit.client_paid to 0.00
   * default Visit.charge from Group.rate::

  class tables_individual {

  function Entity_ID__default(){

per http://xataface.com/forum/viewtopic.php?t=5236#25458

 * access control for printed reports

data cleanup:
  - be more rigorous about time? time interval? start/end time?

Near term goals:

 * permissions: view-only vs. edit
http://xataface.com/wiki/permissions.ini_file
 * format money fields better in the list view
http://stackoverflow.com/questions/4995979/php-currency-formatting-trailing-zeros

Eventual goals:

 * integrate end-of-month reporting to officers
   * merging PDF: pdftk__ 
 * integrate insurance billing

__ http://www.pdflabs.com/docs/build-pdftk/
