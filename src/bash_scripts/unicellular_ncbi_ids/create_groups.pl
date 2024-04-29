#!/usr/bin/perl -w

# Author:
#   lab42open-team
#   https://github.com/lab42open-team/prego_data_internal/blob/master/dictionary/create_database.pl
# 
# Aim:
#   Periodically update unicellular list of NCBI Taxonomy Ids
# 
# Usage:
#   First, get the organisms_dictionary.tar.gz from JensenLab FTP (https://download.jensenlab.org) and unzip the 
#   * organism_entities.tsv and
#   * organism_groups.tsv 
#   Then, run:
#   ./create_groups.pl

use strict;
use POSIX;

my %serial_type_identifier = ();
open IN, "< organisms_entities.tsv";
open OUT, "> growthDB_identifiers.tsv";
while (<IN>) {
    s/\r?\n//;
    my ($serial, $type, $identifier) = split /\t/;
    $serial_type_identifier{$serial} = $type."\t".$identifier;
    print OUT $type, "\t", $identifier, "\n";
}
close IN;
close OUT;

open IN, "< organisms_groups.tsv";
open OUT, "> growthDB_groups.tsv";
while (<IN>) {
    s/\r?\n//;
    s/\\/\\\\/g;
    my ($serial1, $serial2) = split /\t/;
        next unless exists $serial_type_identifier{$serial1} and exists $serial_type_identifier{$serial2};
        print OUT $serial_type_identifier{$serial1}, "\t", $serial_type_identifier{$serial2}, "\n";
}
close IN;
close OUT;
