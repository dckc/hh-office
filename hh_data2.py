# -*- coding: utf-8 -*-
## File originall autogenerated by SQLAutoCode
## see http://code.google.com/p/sqlautocode/

from sqlalchemy import *
from sqlalchemy.schema import CreateTable, CreateIndex

metadata = MetaData()

TextLine=VARCHAR(length=120)
TextCode=VARCHAR(length=40)
Money=DECIMAL(precision=8, scale=2)

Client =  Table('Client', metadata,
                Column(u'id', INTEGER(), primary_key=True, nullable=False),
                Column(u'name', TextLine, nullable=False),
                Column(u'insurance', TextLine),
                Column(u'approval', TEXT()),
                Column(u'DX', TextLine),
                Column(u'note', TEXT()),
                Column(u'address', TextLine),
                Column(u'phone', TextLine),
                Column(u'DOB', DATE()),
                Column(u'Officer_id',
                       ForeignKey('Officer.id', ondelete="SET NULL")
                       ),
                Column(u'file', TextCode),
                Column(u'file_site', Enum('op', 'kck')),
                Column(u'file_opened', DATE()),
                Column('billing_cutoff', DATE()),
                Column('recent', DATE()),
                Column('charges', Money),
                Column('client_paid', Money),
                Column('insurance_paid', Money),
                Column('balance', Money),
                Column('balance_cached', TIMESTAMP()),
                Column(u'id_zoho', TextCode),
                Column(u'id_dabble', TextCode),

                Column('added_time', TIMESTAMP()),
                Column('added_user', TextCode),
                Column('modified_time', TIMESTAMP()),
                Column('modified_user', TextCode),
                mysql_engine='InnoDB'
                )

# Indexes for restoring from backup
Index(u'client_id_zoho', Client.c.id_zoho, unique=False)
Index(u'dab', Client.c.id_dabble, unique=False)


Group =  Table('Group', metadata,
               Column(u'id', INTEGER(), primary_key=True, nullable=False),
               Column(u'name', TextLine, nullable=False),
               Column(u'rate', Money, nullable=False),
               Column(u'evaluation', BOOLEAN(), server_default=text('0')),
               Column(u'id_zoho', TextCode),
               Column(u'id_dabble', TextCode),
               Column('added_time', TIMESTAMP()),
               Column('added_user', TextCode),
               Column('modified_time', TIMESTAMP()),
               Column('modified_user', TextCode),
               mysql_engine='InnoDB'
               )


Office = Table('Office', metadata,
               Column(u'id', INTEGER(), primary_key=True, nullable=False),
               Column(u'name', TextLine, nullable=False),
               Column(u'address', TextLine),
               Column(u'fax', TextLine),
               Column(u'notes', TEXT()),
               Column(u'id_zoho', TextCode),
               Column(u'id_dabble', TextCode),
               Column('added_time', TIMESTAMP()),
               Column('added_user', TextCode),
               Column('modified_time', TIMESTAMP()),
               Column('modified_user', TextCode),
               mysql_engine='InnoDB'
               )


Officer = Table('Officer', metadata,
                Column(u'id', INTEGER(), primary_key=True, nullable=False),
                Column(u'name', TextLine, nullable=False),
                Column(u'email', TextLine),
                Column(u'Office_id', INTEGER(),
                       ForeignKey('Office.id', ondelete="SET NULL")),
                Column(u'id_zoho', TextCode),
                Column(u'id_dabble', TextCode),
                Column('added_time', TIMESTAMP()),
                Column('added_user', TextCode),
                Column('modified_time', TIMESTAMP()),
                Column('modified_user', TextCode),
                mysql_engine='InnoDB'
                )


Session =  Table('Session', metadata,
                 Column(u'id', INTEGER(), primary_key=True, nullable=False),
                 Column(u'session_date', DATE(), nullable=False),
                 Column(u'time', TextCode),
                 Column(u'Group_id', INTEGER(),
                        ForeignKey('Group.id', ondelete="CASCADE"),
                        nullable=False),
                 Column(u'Therapist_id', INTEGER(),
                        ForeignKey('Therapist.id', ondelete="SET NULL")),
                 Column(u'id_zoho', TextCode),
                 Column(u'id_dabble', TextCode),
                 Column('added_time', TIMESTAMP()),
                 Column('added_user', TextCode),
                 Column('modified_time', TIMESTAMP()),
                 Column('modified_user', TextCode),
                 mysql_engine='InnoDB'
                 )

Index(u'session_id_zoho', Session.c.id_zoho, unique=False)
Index(u'session_dabble', Session.c.id_dabble, unique=False)

Therapist =  Table('Therapist', metadata,
                   Column(u'id', INTEGER(), primary_key=True, nullable=False),
                   Column(u'name', TextLine, nullable=False),
                   Column('weight', INTEGER()),
                   Column('added_time', TIMESTAMP()),
                   Column('added_user', TextCode),
                   Column('modified_time', TIMESTAMP()),
                   Column('modified_user', TextCode),
                   mysql_engine='InnoDB'
                   )

Index(u'Therapist_name', Therapist.c.name, unique=True)

Visit =  Table('Visit', metadata,
               Column(u'id', INTEGER(), primary_key=True, nullable=False),
               Column(u'attend_n', BOOLEAN(), server_default=text('0')),
               Column(u'charge', Money, nullable=False),
               Column(u'client_paid', Money, nullable=False),
               Column(u'insurance_paid', Money, nullable=False,
                      server_default=text('0.00')),
               Column(u'note', TEXT()),
               Column(u'bill_date', DATE()),
               Column(u'check_date', DATE()),
               Column(u'Client_id', INTEGER(),
                      ForeignKey('Client.id', ondelete="CASCADE"),
                      nullable=False),
               Column(u'Session_id', INTEGER(),
                      ForeignKey('Session.id', ondelete="CASCADE"),
                      nullable=False),
               Column(u'id_zoho', TextCode),
               Column(u'id_dabble', TextCode),
               Column('added_time', TIMESTAMP()),
               Column('added_user', TextCode),
               Column('modified_time', TIMESTAMP()),
               Column('modified_user', TextCode),
               mysql_engine='InnoDB'
               )

Index(u'visit_dabble', Visit.c.id_dabble, unique=False)
Index(u'visit_match', Visit.c.Session_id, Visit.c.Client_id, unique=False)

Batch = Table('Batch', metadata,
              Column('name', TextLine, primary_key=True),
              Column('cutoff', DATE()),
              Column('added_time', TIMESTAMP()),
              Column('added_user', TextCode),
              Column('modified_time', TIMESTAMP()),
              Column('modified_user', TextCode),
              )

users =  Table('users', metadata,
               Column(u'username', TextLine, primary_key=True, nullable=False),
               Column(u'role', Enum('READ ONLY', 'EDIT', 'DELETE',
                                    'OWNER', 'REVIEWER',
                                    'USER', 'ADMIN', 'MANAGER')),
               Column('added_time', TIMESTAMP()),
               Column('added_user', TextCode),
               Column('modified_time', TIMESTAMP()),
               Column('modified_user', TextCode),
               mysql_engine='InnoDB'
               )

def print_sql(m, schema='hh_office'):
    e = create_engine('mysql+mysqldb:///')
    print 'use %s;' % schema;
    for t in m.sorted_tables:
        print CreateTable(t, bind=e), ';'


if __name__ == '__main__':
    print_sql(metadata)

