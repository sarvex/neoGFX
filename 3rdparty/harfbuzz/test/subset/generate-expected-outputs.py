#!/usr/bin/env python3

# Pre-generates the expected output subset files (via fonttools) for
# specified subset test suite(s).

import os
import sys
import shutil
import io
import re
import tempfile

from difflib import unified_diff
from fontTools.ttLib import TTFont

from subprocess import check_call
from subset_test_suite import SubsetTestSuite


def usage():
	print("Usage: generate-expected-outputs.py hb-subset <test suite file> ...")


def strip_check_sum (ttx_string):
	return re.sub ('checkSumAdjustment value=["]0x([0-9a-fA-F])+["]',
		       'checkSumAdjustment value="0x00000000"',
		       ttx_string, count=1)


def generate_expected_output(input_file, unicodes, profile_flags, output_directory, font_name):
	fonttools_path = os.path.join(tempfile.mkdtemp (), font_name)
	args = [
		"fonttools",
		"subset",
		input_file,
		*[
			"--drop-tables+=DSIG",
			"--drop-tables-=sbix",
			f"--unicodes={unicodes}",
			f"--output-file={fonttools_path}",
		],
	]
	args.extend(profile_flags)
	check_call(args)
	with io.StringIO () as fp:
		with TTFont (fonttools_path) as font:
			font.saveXML (fp)
		fonttools_ttx = strip_check_sum (fp.getvalue ())

	harfbuzz_path = os.path.join(tempfile.mkdtemp (), font_name)
	args = [
		hb_subset,
		f"--font-file={input_file}",
		f"--output-file={harfbuzz_path}",
		f"--unicodes={unicodes}",
		"--drop-tables+=DSIG",
		"--drop-tables-=sbix",
	]
	args.extend(profile_flags)
	check_call(args)
	with io.StringIO () as fp:
		with TTFont (harfbuzz_path) as font:
			font.saveXML (fp)
		harfbuzz_ttx = strip_check_sum (fp.getvalue ())

	if harfbuzz_ttx != fonttools_ttx:
		for line in unified_diff (fonttools_ttx.splitlines (1), harfbuzz_ttx.splitlines (1), fonttools_path, harfbuzz_path):
			sys.stdout.write (line)
		sys.stdout.flush ()
		raise Exception ('ttx for fonttools and harfbuzz does not match.')

	output_path = os.path.join(output_directory, font_name)
	shutil.copy(harfbuzz_path, output_path)


args = sys.argv[1:]
if not args:
	usage()
hb_subset, args = args[0], args[1:]
if not args:
	usage()

for path in args:
	with open(path, mode="r", encoding="utf-8") as f:
		test_suite = SubsetTestSuite(path, f.read())
		output_directory = test_suite.get_output_directory()

		print(f"Generating output files for {output_directory}")
		for test in test_suite.tests():
			unicodes = test.unicodes()
			font_name = test.get_font_name()
			print(f"Creating subset {output_directory}/{font_name}")
			generate_expected_output(test.font_path, unicodes, test.get_profile_flags(),
						 output_directory, font_name)
