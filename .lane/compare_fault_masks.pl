#!/usr/bin/env perl
use strict;
use warnings;

my ($eval_path, $pred_path) = @ARGV;
die "usage: $0 evaluator.tsv predictor.tsv\n" unless defined $pred_path;

sub read_evaluator {
    my ($path) = @_;
    open my $fh, '<', $path or die "open $path: $!\n";
    my %rows;
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        my ($nonce, $declared, $shots_csv) = split /\t/, $line, 3;
        die "bad evaluator row\n"
            unless defined($shots_csv) && $nonce =~ /^\d+$/ && $declared =~ /^\d+$/;
        die "duplicate evaluator nonce $nonce\n" if exists $rows{$nonce};

        my @nibbles = (0) x (141 * 16);
        my $observed = 0;
        if ($shots_csv ne '') {
            for my $shot (split /,/, $shots_csv) {
                die "bad shot $shot for nonce $nonce\n"
                    unless $shot =~ /^\d+$/ && $shot < 9024;
                my $word = int($shot / 64);
                my $bit = $shot % 64;
                my $nibble = int($bit / 4);
                my $digit = $word * 16 + (15 - $nibble);
                my $mask = 1 << ($bit % 4);
                die "duplicate shot $shot for nonce $nonce\n"
                    if $nibbles[$digit] & $mask;
                $nibbles[$digit] |= $mask;
                ++$observed;
            }
        }
        die "evaluator count mismatch for nonce $nonce\n" unless $observed == $declared;
        my $mask = join '', map { sprintf '%x', $_ } @nibbles;
        $rows{$nonce} = [$declared + 0, $mask];
    }
    close $fh or die "close $path: $!\n";
    return \%rows;
}

sub read_predictor {
    my ($path) = @_;
    open my $fh, '<', $path or die "open $path: $!\n";
    my %rows;
    my @pop = (0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4);
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        my ($nonce, $declared, $mask, @extra) = split /\s+/, $line;
        die "bad predictor row\n"
            unless !@extra && defined($mask) && $nonce =~ /^\d+$/ &&
                   $declared =~ /^\d+$/ && $mask =~ /^[0-9a-f]{2256}$/;
        die "duplicate predictor nonce $nonce\n" if exists $rows{$nonce};
        my $observed = 0;
        $observed += $pop[hex($_)] for split //, $mask;
        die "predictor count mismatch for nonce $nonce\n" unless $observed == $declared;
        # Word 140 has only shots 8960..9023; all 64 bits are live because 9024 = 141*64.
        $rows{$nonce} = [$declared + 0, $mask];
    }
    close $fh or die "close $path: $!\n";
    return \%rows;
}

my $eval = read_evaluator($eval_path);
my $pred = read_predictor($pred_path);
die "row-count mismatch\n" unless keys(%$eval) == keys(%$pred);

my ($eval_faults, $pred_faults, $exact, $mismatches) = (0, 0, 0, 0);
for my $nonce (keys %$eval) {
    die "missing predictor nonce $nonce\n" unless exists $pred->{$nonce};
    $eval_faults += $eval->{$nonce}[0];
    $pred_faults += $pred->{$nonce}[0];
    if ($eval->{$nonce}[0] == $pred->{$nonce}[0] &&
        $eval->{$nonce}[1] eq $pred->{$nonce}[1]) {
        ++$exact;
    } else {
        ++$mismatches;
    }
}
for my $nonce (keys %$pred) {
    die "unexpected predictor nonce $nonce\n" unless exists $eval->{$nonce};
}

print "rows=", scalar(keys %$eval),
      " evaluator_faults=$eval_faults predictor_faults=$pred_faults",
      " exact=$exact mismatches=$mismatches\n";
exit($mismatches == 0 ? 0 : 1);
