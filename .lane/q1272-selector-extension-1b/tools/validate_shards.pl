#!/usr/bin/env perl
use strict;
use warnings;
use Math::BigInt;

die "usage: $0 shards.tsv occupied.tsv h64.nonces d32.nonces wave_from wave_to pilot_from pilot_to\n"
    unless @ARGV == 8;
my ($map, $occupied, $h64, $d32, $wave_from_s, $wave_to_s,
    $pilot_from_s, $pilot_to_s) = @ARGV;
my $wave_from = Math::BigInt->new($wave_from_s);
my $wave_to = Math::BigInt->new($wave_to_s);
my $pilot_from = Math::BigInt->new($pilot_from_s);
my $pilot_to = Math::BigInt->new($pilot_to_s);
my $domain = Math::BigInt->new(2)->bpow(48);
die "bad wave interval\n" unless $wave_from < $wave_to && $wave_to <= $domain;
die "bad pilot interval\n" unless $pilot_from < $pilot_to;
die "wave is not immediate pilot successor\n" unless $wave_from == $pilot_to;
die "pilot overlap\n" if $pilot_from < $wave_to && $wave_from < $pilot_to;

open my $mf, '<', $map or die "$map: $!\n";
my (@shards, %ids);
while (my $line = <$mf>) {
    chomp $line;
    next if $line =~ /^\s*#/ || $line =~ /^\s*$/;
    my @f = split /\t/, $line, -1;
    die "bad shard row: $line\n" unless @f == 5;
    my ($id, $s_s, $e_s, $count_s, $state) = @f;
    die "bad shard id: $id\n" unless $id =~ /^slot\d{2}$/ && !$ids{$id}++;
    die "bad shard numeric fields: $line\n"
        unless $s_s =~ /^\d+$/ && $e_s =~ /^\d+$/ && $count_s =~ /^\d+$/;
    die "range was declared prematurely\n" unless $state eq 'planned_not_declared';
    my ($s, $e, $count) = map { Math::BigInt->new($_) } ($s_s, $e_s, $count_s);
    die "bad shard interval: $line\n"
        unless $s < $e && ($e - $s) == $count && $count == 50_000_000;
    push @shards, [$id, $s, $e, $count];
}
close $mf or die "$map: $!\n";
die "shard count mismatch\n" unless @shards == 20;
die "wave start mismatch\n" unless $shards[0][1] == $wave_from;
die "wave end mismatch\n" unless $shards[-1][2] == $wave_to;
for my $i (0 .. $#shards) {
    die "shard id sequence mismatch\n" unless $shards[$i][0] eq sprintf('slot%02d', $i + 1);
    die "shard discontinuity\n" if $i && $shards[$i-1][2] != $shards[$i][1];
}
die "wave count mismatch\n" unless ($wave_to - $wave_from) == 1_000_000_000;

open my $of, '<', $occupied or die "$occupied: $!\n";
my $occupied_rows = 0;
while (my $line = <$of>) {
    chomp $line;
    next if $line =~ /^\s*#/ || $line =~ /^\s*$/;
    my @f = split /\t/, $line, -1;
    die "bad occupied row: $line\n" unless @f == 6;
    my ($s, $e) = map { Math::BigInt->new($_) } @f[1,2];
    die "occupied overlap: $f[0]\n" if $s < $wave_to && $wave_from < $e;
    $occupied_rows++;
}
close $of or die "$occupied: $!\n";
die "occupied ledger row count mismatch\n" unless $occupied_rows == 40;

my %fixtures;
for my $path ($h64, $d32) {
    open my $nf, '<', $path or die "$path: $!\n";
    while (my $line = <$nf>) {
        chomp $line;
        die "bad fixture nonce\n" unless $line =~ /^\d+$/;
        die "duplicate fixture nonce\n" if $fixtures{$line}++;
        my $n = Math::BigInt->new($line);
        die "wave overlaps fixture nonce $line\n" if $wave_from <= $n && $n < $wave_to;
    }
    close $nf or die "$path: $!\n";
}
die "fixture count mismatch\n" unless keys(%fixtures) == 96;

print "Q1272_EXTENSION_RANGE_OK occupied=40 fixtures=96 prior=[$pilot_from_s,$pilot_to_s) wave=[$wave_from_s,$wave_to_s) shards=20 count=1000000000 declared=no\n";
