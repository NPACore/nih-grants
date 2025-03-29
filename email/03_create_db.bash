#!/usr/bin/env bash
#
# create sqlite3 db that can be modified by
#  collect_nih_email.pl from voilentmonkey browser requests specified by nih_userscript.js
#
# 20250329WF - init

DB=nih_emails.db 
WEBIDS_TXT=webid_missing_contacts.txt

[ -r  "$DB" ] && echo "already have DB. 'rm $DB' to reinit" && exit 1
[ ! -s "$WEBIDS_TXT" ] && echo "missing project web id file $WEBIDS_TXT" && exit 1

sqlite3 $DB 'create table pids(id number primary key, email text, json text, address text);'
sqlite3 $DB ".import $WEBIDS_TXT pids"
