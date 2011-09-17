# -*- coding: utf-8 -*-

from sqlalchemy import *

# grabbing cdecimal per note in
# http://www.sqlalchemy.org/docs/core/types.html#sqlalchemy.types.Numeric
import sys
try:
    import cdecimal  # http://pypi.python.org/pypi/cdecimal/2.2
    # 2.2 515625c5c5830b109c57af93d49ae2c57ec3f230d46a3e0583840ff73d7963be
    sys.modules["decimal"] = cdecimal
except ImportError:
    pass  # perhaps warn about performance hit?

meta = MetaData()

T_NAME = VARCHAR(80)
T_PHONE = VARCHAR(20)
T_CODE = VARCHAR(20)
T_MONEY = DECIMAL(6, 2)

offices = Table('offices', meta,
                Column('id', INTEGER(), primary_key=True),
                Column('name', T_NAME),
                Column('fax', T_PHONE),
                Column('address', TEXT()),
                Column('notes', TEXT())
                )

officers = Table('officers', meta,
                 Column('id', INTEGER(), primary_key=True),
                 Column('name', T_NAME),
                 Column('email', T_NAME),
                 Column('office', INTEGER(), ForeignKey('offices.id'))
                 )

batches = Table('batches', meta,
                Column('id', INTEGER(), primary_key=True),
                Column('name', T_NAME),
 );

clients = Table('clients', meta,
                Column('id', INTEGER(), primary_key=True),
                Column('name', T_NAME),
                Column('ins', TEXT()),
                Column('approval', T_NAME),
                Column('DX', T_CODE),
                Column('note', TEXT()),
                Column('officer', INTEGER(), ForeignKey('officers.id')),
                Column('DOB', DATE()),
                Column('address', TEXT()),
                Column('phone', T_PHONE),
                Column('batch', INTEGER(), ForeignKey('batches.id'))
                )

groups = Table('groups', meta,
               Column('id', INTEGER(), primary_key=True),
               Column('name', T_NAME),
               Column('rate', T_MONEY),
               Column('Eval', BOOLEAN())
               )

sessions = Table('sessions', meta,
                 Column('id', INTEGER(), primary_key=True),
                 Column('date', DATE()),
                 Column('group_id', INTEGER(), ForeignKey('groups.id'),
                        nullable=False),
                 Column('time', T_CODE),
                 Column('therapist', T_NAME)
                 )

visits = Table('visits', meta,
               Column('id', INTEGER(), primary_key=True),
               Column('session', INTEGER(), ForeignKey('sessions.id'),
                      nullable=False),
               Column('client', INTEGER(), ForeignKey('clients.id'),
                      nullable=False),
               Column('attend', BOOLEAN()),
               Column('client_pd', T_MONEY),
               Column('note', TEXT()),
               Column('bill_date', DATE()),
               Column('check_date', DATE()),
               Column('ins_paid', T_MONEY)
               )


Progressnote =  Table('Progressnote', meta,
    Column(u'ID', VARCHAR(length=500), primary_key=False),
            Column(u'CLIENT', VARCHAR(length=500), primary_key=False),
            Column(u'SESSION_DATE', VARCHAR(length=500), primary_key=False),
            Column(u'SESSION_DURATION', VARCHAR(length=500), primary_key=False),
            Column(u'NOTES', VARCHAR(length=500), primary_key=False),
            Column(u'SIGNED_BY', VARCHAR(length=500), primary_key=False),
            Column(u'SIGNED_ON', VARCHAR(length=500), primary_key=False),
    
    
    )

