# -*- coding: utf-8 -*-
## File originall autogenerated by SQLAutoCode
## see http://code.google.com/p/sqlautocode/

from sqlalchemy import *

metadata = MetaData()


Client =  Table('Client', metadata,
    Column(u'id', INTEGER(), primary_key=True, nullable=False),
            Column(u'name', VARCHAR(length=80), nullable=False),
            Column(u'insurance', VARCHAR(length=80)),
            Column(u'approval', TEXT()),
            Column(u'DX', VARCHAR(length=80)),
            Column(u'note', TEXT()),
            Column(u'address', VARCHAR(length=80)),
            Column(u'phone', VARCHAR(length=80)),
            Column(u'DOB', DATE()),
            Column(u'file', VARCHAR(length=80)),
            Column(u'file_site', VARCHAR(length=80)),
            Column(u'file_opened', DATE()),
            Column(u'Officer_id', INTEGER()),
            Column(u'id_zoho', VARCHAR(length=45)),
            Column(u'id_dabble', VARCHAR(length=45)),
    
    
    )
Index(u'id_UNIQUE', Client.c.id, unique=True)
Index(u'fk_Client_Officer1', Client.c.Officer_id, unique=False)
Index(u'client_id_zoho', Client.c.id_zoho, unique=False)
Index(u'dab', Client.c.id_dabble, unique=False)


Group =  Table('Group', metadata,
    Column(u'evaluation', Integer(), nullable=False),
            Column(u'id', INTEGER(), primary_key=True, nullable=False),
            Column(u'name', VARCHAR(length=80), nullable=False),
            Column(u'rate', DECIMAL(precision=6, scale=2), nullable=False),
            Column(u'id_zoho', VARCHAR(length=45)),
            Column(u'id_dabble', VARCHAR(length=45)),
    
    
    )
Index(u'id_UNIQUE', Group.c.id, unique=True)


Officer =  Table('Officer', metadata,
    Column(u'id', INTEGER(), primary_key=True, nullable=False),
            Column(u'name', VARCHAR(length=80), nullable=False),
            Column(u'email', VARCHAR(length=80)),
            Column(u'id_zoho', VARCHAR(length=45)),
            Column(u'id_dabble', VARCHAR(length=45)),
    
    
    )
Index(u'id_UNIQUE', Officer.c.id, unique=True)


Session =  Table('Session', metadata,
    Column(u'id', INTEGER(), primary_key=True, nullable=False),
            Column(u'session_date', DATE(), nullable=False),
            Column(u'time', VARCHAR(length=20)),
            Column(u'Group_id', INTEGER(), nullable=False),
            Column(u'Therapist_id', INTEGER()),
            Column(u'id_zoho', VARCHAR(length=45)),
            Column(u'id_dabble', VARCHAR(length=45)),
    
    
    )
Index(u'fk_Session_Group1', Session.c.Group_id, unique=False)
Index(u'session_id_zoho', Session.c.id_zoho, unique=False)
Index(u'session_dabble', Session.c.id_dabble, unique=False)
Index(u'id_UNIQUE', Session.c.id, unique=True)
Index(u'dab', Session.c.id_dabble, unique=False)
Index(u'fk_Session_Therapist1', Session.c.Therapist_id, unique=False)


Therapist =  Table('Therapist', metadata,
    Column(u'id', INTEGER(), primary_key=True, nullable=False),
            Column(u'name', VARCHAR(length=80), nullable=False),
    
    
    )
Index(u'id_UNIQUE', Therapist.c.id, unique=True)
Index(u'Therapist_name', Therapist.c.name, unique=False)


Visit =  Table('Visit', metadata,
    Column(u'id', INTEGER(), primary_key=True, nullable=False),
            Column(u'attend_n', Integer(), nullable=False),
            Column(u'charge', INTEGER(), nullable=False),
            Column(u'client_paid', DECIMAL(precision=6, scale=2)),
            Column(u'insurance_paid', DECIMAL(precision=6, scale=2)),
            Column(u'due', DECIMAL(precision=6, scale=2), nullable=False),
            Column(u'note', TEXT()),
            Column(u'bill_date', DATE()),
            Column(u'check_date', DATE()),
            Column(u'Client_id', INTEGER(), nullable=False),
            Column(u'Session_id', INTEGER(), nullable=False),
            Column(u'id_zoho', VARCHAR(length=45)),
            Column(u'id_dabble', VARCHAR(length=45)),
    
    
    )
Index(u'id_UNIQUE', Visit.c.id, unique=True)
Index(u'fk_Visit_Client1', Visit.c.Client_id, unique=False)
Index(u'fk_Visit_Session1', Visit.c.Session_id, unique=False)
Index(u'visit_dabble', Visit.c.id_dabble, unique=False)
Index(u'visit_match', Visit.c.Session_id, Visit.c.Client_id, unique=False)


dataface__failed_logins =  Table('dataface__failed_logins', metadata,
    Column(u'attempt_id', INTEGER(), primary_key=True, nullable=False),
            Column(u'ip_address', VARCHAR(length=32), nullable=False),
            Column(u'username', VARCHAR(length=32), nullable=False),
            Column(u'time_of_attempt', INTEGER(), nullable=False),
    
    
    )


dataface__mtimes =  Table('dataface__mtimes', metadata,
    Column(u'name', VARCHAR(length=255), primary_key=True, nullable=False),
            Column(u'mtime', INTEGER()),
    
    
    )


dataface__preferences =  Table('dataface__preferences', metadata,
    Column(u'pref_id', INTEGER(), primary_key=True, nullable=False),
            Column(u'username', VARCHAR(length=64), nullable=False),
            Column(u'table', VARCHAR(length=128), nullable=False),
            Column(u'record_id', VARCHAR(length=255), nullable=False),
            Column(u'key', VARCHAR(length=128), nullable=False),
            Column(u'value', VARCHAR(length=255), nullable=False),
    
    
    )
Index(u'username', dataface__preferences.c.username, unique=False)
Index(u'table', dataface__preferences.c.table, unique=False)
Index(u'record_id', dataface__preferences.c.record_id, unique=False)


dataface__version =  Table('dataface__version', metadata,
    Column(u'version', INTEGER(), nullable=False, default=text(u"'0'")),
    
    
    )


users =  Table('users', metadata,
    Column(u'username', VARCHAR(length=80), primary_key=True, nullable=False),
    
    
    )
