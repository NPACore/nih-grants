#!/usr/bin/env perl
#
# expect data to be json from nih PiPoEmail.
# that data is behind recaptcha so using nih_userscript.js w/violentmonkey to capture and forward to
# cgi-server hosting this file
# 
# 20250329WF - init
use strict; use warnings;
use v5.40; use feature qw/say signatures/;
use Data::Dumper qw/Dumper/;
use JSON 'decode_json';
use CGI::Carp qw(fatalsToBrowser);
use DBI;

say "Content-type: text/plain\n";

# read POST data
my @req=<STDIN>;
my $req="@req";
chomp($req);
# $req like
# '{"PI":{"profile_id":11932348,"first_name":null,"middle_name":null,"last_name":null,"is_contact_pi":true,"full_name":"MAREK, SCOTT ","title":null,"email":"smarek@wustl.edu"},"PO":{"first_name":null,"middle_name":null,"last_name":null,"full_name":"T, L A","email":"...@nih.gov"}}'

# check data is good
my $json = decode_json($req) or die "bad json: $!";
my $pi = $json->{'PI'} or die "bad request, no PI: $!";
if(not $pi->{email} or not $pi->{profile_id}){ die "missing either profile_id or email!: $!"; }

# see Makefile for DB schema
# upsert based on primary key='id', considering safe b/c will have already exited if email is missing
my $dbh = DBI->connect('DBI:SQLite:nih_emails.db', { RaiseError => 1, AutoCommit => 1 }) or die $DBI::errstr;
my $ins = $dbh->prepare("INSERT or replace into pids (id, email, json, address) values (?,?,?,?)");
$ins->execute($pi->{profile_id}, $pi->{email}, $req, $ENV{REMOTE_ADDR}||"");

# send url next profile id, will be consumed by nih_userscript.js
my ($next) = $dbh->selectrow_array("select id from pids where email is null limit 1");
if($next) { say "https://reporter.nih.gov/project-details/$next"; }
exit 0;
