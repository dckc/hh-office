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

It also uses PyFPDF__, a reporting library, for PDF reports.

__ http://xataface.com/
__ https://code.google.com/p/pyfpdf/wiki/Tutorialo

TODO
====

Near term goals:

 * optimize entering sign-in sheets
   * save and add another
   * reduce mouse work
       * choosing clients
       * how to Save the sign-in sheet with the keyboard?
       * tabbing between fields in general

data cleanup:
  - be more rigorous about time? time interval? start/end time?

In progress:

 * integrate insurance billing
