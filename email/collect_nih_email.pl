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
use HTML::Entities 'decode_entities';
use DBI;

# read POST data
my @req=<STDIN>;
my $req="@req";
chomp($req);
$req = decode_entities($req);
# $req like
# '{"page": "https://sdafdsf/123456", "PI":{"profile_id":11932348,"first_name":null,"middle_name":null,"last_name":null,"is_contact_pi":true,"full_name":"MAREK, SCOTT ","title":null,"email":"smarek@wustl.edu"},"PO":{"first_name":null,"middle_name":null,"last_name":null,"full_name":"T, L A","email":"...@nih.gov"}}'


# no real input
if(length($req) < 50){
   say "Status: 500";
   say "Content-type: text/plain\n";
   say "Input data too short: $req";
   exit;
}

# check data is good
my $json = decode_json($req) or die "bad json '$req': $!";
my $pi = $json->{'PI'} or die "bad request, no PI: $!";
my $page = $json->{'page'} or die "bad request, no page: $!";
my $page_id = $page =~ s/.*\/|#.*//gr;
if(not $pi->{email} or not $page_id){ die "missing either page_id or email!: $!"; }

# see Makefile for DB schema
# upsert based on primary key='id', considering safe b/c will have already exited if email is missing
my $dbh = DBI->connect('DBI:SQLite:emails/nih_emails.db', { RaiseError => 1, AutoCommit => 1 }) or die $DBI::errstr;
my $ins = $dbh->prepare("INSERT or replace into pids (id, email, json, address) values (?,?,?,?)") or die "cant create insert! ". $DBI::errstr;
$ins->execute($page_id, $pi->{email}, $req, $ENV{REMOTE_ADDR}||"");
$dbh->commit() or die "cannot commit/write to DB?! $!";
#open my $f, ">", "emails/$page_id";
#print $f "$page_id\t". $pi->{email}."\t$req\t$ENV{REMOTE_ADDR}\n";
#close $f;

# send url next profile id, will be consumed by nih_userscript.js
my ($next) = $dbh->selectrow_array("select id from pids where email is null ORDER BY RANDOM() limit 1");

say "Content-type: text/plain\n";
if($next) { say "https://reporter.nih.gov/project-details/$next"; }
$dbh->disconnect();
exit 0;
