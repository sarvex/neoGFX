#!/usr/bin/env python3

# Runs a subsetting test suite. Compares the results of subsetting via harfbuzz
# to subsetting via fonttools.

from difflib import unified_diff
import os
import re
import subprocess
import sys
import tempfile
import shutil
import io

from subset_test_suite import SubsetTestSuite

try:
	from fontTools.ttLib import TTFont
except ImportError:
    TTFont = None

ots_sanitize = shutil.which ("ots-sanitize")

def subset_cmd(command):
	global hb_subset, process
	print(f'{hb_subset} ' + " ".join(command))
	process.stdin.write ((';'.join (command) + '\n').encode ("utf-8"))
	process.stdin.flush ()
	return process.stdout.readline().decode ("utf-8").strip ()

def cmd (command):
	p = subprocess.Popen (
		command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		universal_newlines=True)
	(stdoutdata, stderrdata) = p.communicate ()
	print (stderrdata, end="", file=sys.stderr)
	return stdoutdata, p.returncode

def fail_test(test, cli_args, message):
	print(f'ERROR: {message}')
	print ('Test State:')
	print(f'  test.font_path    {os.path.abspath(test.font_path)}')
	print(f'  test.profile_path {os.path.abspath(test.profile_path)}')
	print ('  test.unicodes	    %s' % test.unicodes ())
	expected_file = os.path.join (test_suite.get_output_directory (),
				      test.get_font_name ())
	print ('  expected_file	    %s' % os.path.abspath (expected_file))
	return 1

def run_test(test, should_check_ots):
	out_file = os.path.join(
		tempfile.mkdtemp(),
		f'{test.get_font_name()}-subset{test.get_font_extension()}',
	)
	cli_args = [
		f"--font-file={test.font_path}",
		f"--output-file={out_file}",
		f"--unicodes={test.unicodes()}",
		"--drop-tables+=DSIG",
		"--drop-tables-=sbix",
	]
	cli_args.extend (test.get_profile_flags ())
	ret = subset_cmd (cli_args)

	if ret != "success":
		return fail_test(test, cli_args, f"{' '.join(cli_args)} failed")

	expected_file = os.path.join (test_suite.get_output_directory (), test.get_font_name ())
	with open (expected_file, "rb") as fp:
		expected_contents = fp.read()
	with open (out_file, "rb") as fp:
		actual_contents = fp.read()

	if expected_contents == actual_contents:
		if should_check_ots:
			print ("Checking output with ots-sanitize.")
			if not check_ots (out_file):
				return fail_test (test, cli_args, 'ots for subsetted file fails.')
		return 0

	if TTFont is None:
		print ("fonttools is not present, skipping TTX diff.")
		return fail_test (test, cli_args, "hash for expected and actual does not match.")

	with io.StringIO () as fp:
		try:
			with TTFont (expected_file) as font:
				font.saveXML (fp)
		except Exception as e:
			print (e)
			return fail_test (test, cli_args, "ttx failed to parse the expected result")
		expected_ttx = fp.getvalue ()

	with io.StringIO () as fp:
		try:
			with TTFont (out_file) as font:
				font.saveXML (fp)
		except Exception as e:
			print (e)
			return fail_test (test, cli_args, "ttx failed to parse the actual result")
		actual_ttx = fp.getvalue ()

	if actual_ttx != expected_ttx:
		for line in unified_diff (expected_ttx.splitlines (1), actual_ttx.splitlines (1)):
			sys.stdout.write (line)
		sys.stdout.flush ()
		return fail_test (test, cli_args, 'ttx for expected and actual does not match.')

	return fail_test (test, cli_args, 'hash for expected and actual does not match, '
	                                  'but the ttx matches. Expected file needs to be updated?')


def has_ots ():
	if not ots_sanitize:
		print ("OTS is not present, skipping all ots checks.")
		return False
	return True

def check_ots(path):
	ots_report, returncode = cmd ([ots_sanitize, path])
	if returncode:
		print(f"OTS Failure: {ots_report}")
		return False
	return True

args = sys.argv[1:]
if not args or sys.argv[1].find ('hb-subset') == -1 or not os.path.exists (sys.argv[1]):
	sys.exit ("First argument does not seem to point to usable hb-subset.")
hb_subset, args = args[0], args[1:]

if not len (args):
	sys.exit ("No tests supplied.")

has_ots = has_ots()

process = subprocess.Popen ([hb_subset, '--batch'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=sys.stdout)

fails = 0
for path in args:
	with open (path, mode="r", encoding="utf-8") as f:
		print(f"Running tests in {path}")
		test_suite = SubsetTestSuite (path, f.read ())
		for test in test_suite.tests ():
			fails += run_test (test, has_ots)

if fails != 0:
	sys.exit ("%d test(s) failed." % fails)
else:
	print ("All tests passed.")
