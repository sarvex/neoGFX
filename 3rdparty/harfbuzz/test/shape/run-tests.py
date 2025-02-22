#!/usr/bin/env python3

import sys, os, subprocess, hashlib

def shape_cmd(command):
	global hb_shape, process
	print(f'{hb_shape} ' + " ".join(command))
	process.stdin.write ((';'.join (command) + '\n').encode ("utf-8"))
	process.stdin.flush ()
	return process.stdout.readline().decode ("utf-8").strip ()

args = sys.argv[1:]

have_freetype = int(os.getenv ('HAVE_FREETYPE', 1))
have_coretext = int(os.getenv ('HAVE_CORETEXT', 0))
have_directwrite = int(os.getenv ('HAVE_DIRECTWRITE', 0))
have_uniscribe = int(os.getenv ('HAVE_UNISCRIBE', 0))

if not args or args[0].find('hb-shape') == -1 or not os.path.exists (args[0]):
	sys.exit ("""First argument does not seem to point to usable hb-shape.""")
hb_shape, args = args[0], args[1:]

process = subprocess.Popen ([hb_shape, '--batch'],
			    stdin=subprocess.PIPE,
			    stdout=subprocess.PIPE,
			    stderr=sys.stdout)

passes = 0
fails = 0
skips = 0

if not len (args):
	args = ['-']

for filename in args:
	if filename == '-':
		print ("Running tests from standard input")
	else:
		print(f"Running tests in {filename}")

	f = sys.stdin if filename == '-' else open (filename, encoding='utf8')
	for line in f:
		comment = False
		if line.startswith ("#"):
			comment = True
			line = line[1:]

			if line.startswith (' '):
				print(f"#{line}")
				continue

		line = line.strip ()
		if not line:
			continue

		fontfile, options, unicodes, glyphs_expected = line.split (';')
		options = options.split ()
		if fontfile.startswith ('/') or fontfile.startswith ('"/'):
			if os.name == 'nt': # Skip on Windows
				continue

			fontfile, expected_hash = (fontfile.split('@') + [''])[:2]

			try:
				with open (fontfile, 'rb') as ff:
					if expected_hash:
						actual_hash = hashlib.sha1 (ff.read()).hexdigest ().strip ()
						if actual_hash != expected_hash:
							print(
								f'different version of {fontfile} found; Expected hash {expected_hash}, got {actual_hash}; skipping.'
							)
							skips += 1
							continue
			except IOError:
				print(f'{fontfile} not found, skip.')
				skips += 1
				continue
		else:
			cwd = os.path.dirname(filename)
			fontfile = os.path.normpath (os.path.join (cwd, fontfile))

		extra_options = ["--shaper=ot"]
		if glyphs_expected != '*':
			extra_options.append("--verify")

		if comment:
			print(f'# {hb_shape} "{fontfile}" --unicodes {unicodes}')
			continue

		if "--font-funcs=ft" in options and not have_freetype:
			skips += 1
			continue

		if "--shaper=coretext" in options and not have_coretext:
			skips += 1
			continue

		if "--shaper=directwrite" in options and not have_directwrite:
			skips += 1
			continue

		if "--shaper=uniscribe" in options and not have_uniscribe:
			skips += 1
			continue

		if "--font-funcs=ot" in options or not have_freetype:
			glyphs1 = shape_cmd ([fontfile, "--font-funcs=ot"] + extra_options + ["--unicodes", unicodes] + options)
		else:
			glyphs1 = shape_cmd ([fontfile, "--font-funcs=ft"] + extra_options + ["--unicodes", unicodes] + options)
			glyphs2 = shape_cmd ([fontfile, "--font-funcs=ot"] + extra_options + ["--unicodes", unicodes] + options)

			if glyphs1 != glyphs2 and glyphs_expected != '*':
				print(f"FT funcs: {glyphs1}", file=sys.stderr)
				print(f"OT funcs: {glyphs2}", file=sys.stderr)
				fails += 1
			else:
				passes += 1

		if glyphs1.strip() != glyphs_expected != '*':
			print(f"Actual:   {glyphs1}", file=sys.stderr)
			print(f"Expected: {glyphs_expected}", file=sys.stderr)
			fails += 1
		else:
			passes += 1

print ("%d tests passed; %d failed; %d skipped." % (passes, fails, skips), file=sys.stderr)
if not (fails + passes):
	print ("No tests ran.")
elif not (fails + skips):
	print ("All tests passed.")

if fails:
	sys.exit (1)
elif passes:
	sys.exit (0)
else:
	sys.exit (77)
