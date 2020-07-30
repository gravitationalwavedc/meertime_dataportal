#!/usr/bin/env python
import queries as q
import MySQLdb as sql

import proposals


def connect_to_DB(db_cfg):
    _host = db_cfg["MYSQL_HOST"]
    _db = db_cfg["MYSQL_DB"]
    _passwd = db_cfg["MYSQL_PWD"]
    _user = db_cfg["MYSQL_USER"]
    conn = sql.connect(host=_host, db=_db, passwd=_passwd, user=_user)
    return conn


def get_utc_id(utc, cur):
    row_count = cur.execute(q.get_utc_id_q, [utc,])
    if row_count == 1:
        utc_id = cur.fetchone()[0]
    else:
        cur.execute(q.insert_utc_q, [utc, utc,])
        cur.execute(q.get_utc_id_q, [utc,])
        utc_id = cur.fetchone()[0]
    return utc_id


def get_psr_id(psr, cur):
    row_count = cur.execute(q.get_psr_id_q, [psr,])
    if row_count == 1:
        psr_id = cur.fetchone()[0]
    else:
        cur.execute(q.insert_psr_q, [psr,])
        cur.execute(q.get_psr_id_q, [psr,])
        psr_id = cur.fetchone()[0]
    return psr_id


def get_proposal_id(proposal, cur):
    row_count = cur.execute(q.get_proposal_id_q, [proposal,])
    if row_count == 1:
        proposal_id = cur.fetchone()[0]
    else:
        if proposal in proposals.proposal_dict.keys():
            short_prop = proposals.proposal_dict[proposal]
        else:
            short_prop = "???"
        cur.execute(q.insert_proposal_q, [proposal, short_prop,])
        cur.execute(q.get_proposal_id_q, [proposal,])
        proposal_id = cur.fetchone()[0]
    return proposal_id
