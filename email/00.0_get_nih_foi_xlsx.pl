#!/usr/bin/env perl
use strict; use warnings;

# overkill scripting to get email lists.
# initially a shell script but years 2014 to 2017 are not formated like the others
# would have been clear to just enumerate the 8 years listed
# as of 20250413, emails are listed for FYs 2014 to 2022

# where is the freedom on information email list index?
my $idx_site = "https://www.nih.gov/institutes-nih/nih-office-director/office-communications-public-liaison/freedom-information-act-office/contact-information-nih-supported-pis";

# make sure we have directory to save into
`mkdir -p xlsx`;

# pipe open the html index
open my $idx, "curl -sL '$idx_site' |";

while($_=<$idx>){
  # grab xlsx and year
  next unless m/a href="(.*xlsx).*FY (\d{4})/;
  my ($h,$y) = ($1, $2);
  my $out = "xlsx/$y.xlsx";

  # one of the year urls starts with '/' instead of full https:// address
  my $root_address = "https://www.nih.gov/";
  $h=~s|^/|$root_address|;

  # expect MBs of data but if 404, size will be very small
  -s $out > 100000 and next;
  print "# making '$out' from '$h'";
 `curl -sL "$h" -o "$out" >&2`;
}
