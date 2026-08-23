#!/usr/bin/env ruby
# Freeze a private deterministic D32 corpus without printing nonce values.

require "digest"
require "fileutils"
require "openssl"
require "securerandom"
require "set"

abort "usage: freeze_corpora.rb PRIVATE_ROOT H64_FILE EXCLUSION..." if ARGV.length < 3

private_root = File.expand_path(ARGV.shift)
h64_path = File.expand_path(ARGV.shift)
exclusion_paths = ARGV.map { |path| File.expand_path(path) }
FileUtils.mkdir_p(private_root, mode: 0o700)

parse = lambda do |path|
  lines = File.binread(path).lines(chomp: true)
  abort "#{path}: blank or noncanonical row" unless lines.all? { |line| line.match?(/\A(?:0|[1-9][0-9]*)\z/) }
  values = lines.map(&:to_i)
  abort "#{path}: value outside [0,2^48)" unless values.all? { |value| value >= 0 && value < (1 << 48) }
  abort "#{path}: duplicate value" unless values.uniq.length == values.length
  values
end

h64 = parse.call(h64_path)
abort "H64 must contain exactly 64 rows" unless h64.length == 64
excluded = exclusion_paths.flat_map { |path| parse.call(path) }.to_set
abort "H64 overlaps a prior corpus" unless (h64.to_set & excluded).empty?

seed_path = File.join(private_root, "D32.seed")
unless File.exist?(seed_path)
  File.binwrite(seed_path, SecureRandom.random_bytes(32))
  File.chmod(0o600, seed_path)
end
seed = File.binread(seed_path)
abort "private seed must be exactly 32 bytes" unless seed.bytesize == 32

blocked = excluded | h64.to_set
values = []
counter = 0
while values.length < 32
  message = "ecdsa.fail/q1270/routed-combined/D32/v1\0".b + [counter].pack("Q>")
  digest = OpenSSL::HMAC.digest("SHA256", seed, message)
  value = digest.byteslice(0, 6).unpack1("H*").to_i(16)
  values << value unless blocked.include?(value) || values.include?(value)
  counter += 1
end
body = values.sort.map { |value| "#{value}\n" }.join
d32_path = File.join(private_root, "D32.nonces")
if File.exist?(d32_path) && File.binread(d32_path) != body
  abort "existing D32 corpus differs; refusing overwrite"
end
File.binwrite(d32_path, body)
File.chmod(0o600, d32_path)

d32 = parse.call(d32_path)
abort "D32 must contain exactly 32 rows" unless d32.length == 32
abort "D32 overlaps H64 or a prior corpus" unless (d32.to_set & blocked).empty?

puts "FREEZE_CORPORA_PASS"
puts "h64_rows=#{h64.length}"
puts "h64_sha256=#{Digest::SHA256.file(h64_path).hexdigest}"
puts "d32_rows=#{d32.length}"
puts "d32_sha256=#{Digest::SHA256.file(d32_path).hexdigest}"
puts "seed_sha256=#{Digest::SHA256.file(seed_path).hexdigest}"
puts "prior_values=#{excluded.length}"
puts "overlap=0"

