#!/usr/bin/env python3

"""usage: ./gen-indic-table.py IndicSyllabicCategory.txt IndicPositionalCategory.txt Blocks.txt

Input files:
* https://unicode.org/Public/UCD/latest/ucd/IndicSyllabicCategory.txt
* https://unicode.org/Public/UCD/latest/ucd/IndicPositionalCategory.txt
* https://unicode.org/Public/UCD/latest/ucd/Blocks.txt
"""


import sys

if len (sys.argv) != 4:
	sys.exit (__doc__)

ALLOWED_SINGLES = [0x00A0, 0x25CC]
ALLOWED_BLOCKS = [
	'Basic Latin',
	'Latin-1 Supplement',
	'Devanagari',
	'Bengali',
	'Gurmukhi',
	'Gujarati',
	'Oriya',
	'Tamil',
	'Telugu',
	'Kannada',
	'Malayalam',
	'Sinhala',
	'Myanmar',
	'Khmer',
	'Vedic Extensions',
	'General Punctuation',
	'Superscripts and Subscripts',
	'Devanagari Extended',
	'Myanmar Extended-B',
	'Myanmar Extended-A',
]

files = [open (x, encoding='utf-8') for x in sys.argv[1:]]

headers = [[f.readline () for _ in range (2)] for f in files]

data = [{} for _ in files]
values = [{} for _ in files]
for i, f in enumerate (files):
	for line in f:

		j = line.find ('#')
		if j >= 0:
			line = line[:j]

		fields = [x.strip () for x in line.split (';')]
		if len (fields) == 1:
			continue

		uu = fields[0].split ('..')
		start = int (uu[0], 16)
		end = start if len (uu) == 1 else int (uu[1], 16)
		t = fields[1]

		for u in range (start, end + 1):
			data[i][u] = t
		values[i][t] = values[i].get (t, 0) + end - start + 1

# Merge data into one dict:
defaults = ('Other', 'Not_Applicable', 'No_Block')
for i,v in enumerate (defaults):
	values[i][v] = values[i].get (v, 0) + 1
combined = {}
for i,d in enumerate (data):
	for u,v in d.items ():
		if i == 2 and u not in combined:
			continue
		if u not in combined:
			combined[u] = list (defaults)
		combined[u][i] = v
combined = {k:v for k,v in combined.items() if k in ALLOWED_SINGLES or v[2] in ALLOWED_BLOCKS}
data = combined
del combined

# Move the outliers NO-BREAK SPACE and DOTTED CIRCLE out
singles = {}
for u in ALLOWED_SINGLES:
	singles[u] = data[u]
	del data[u]

print ("/* == Start of generated table == */")
print ("/*")
print (" * The following table is generated by running:")
print (" *")
print (" *   ./gen-indic-table.py IndicSyllabicCategory.txt IndicPositionalCategory.txt Blocks.txt")
print (" *")
print (" * on files with these headers:")
print (" *")
for h in headers:
	for l in h:
		print(f" * {l.strip()}")
print (" */")
print ()
print ('#include "hb.hh"')
print ()
print ('#ifndef HB_NO_OT_SHAPE')
print ()
print ('#include "hb-ot-shape-complex-indic.hh"')
print ()

# Shorten values
short = [{
	"Bindu":		'Bi',
	"Cantillation_Mark":	'Ca',
	"Joiner":		'ZWJ',
	"Non_Joiner":		'ZWNJ',
	"Number":		'Nd',
	"Visarga":		'Vs',
	"Vowel":		'Vo',
	"Vowel_Dependent":	'M',
	"Consonant_Prefixed":	'CPrf',
	"Other":		'x',
},{
	"Not_Applicable":	'x',
}]
all_shorts = [{},{}]

# Add some of the values, to make them more readable, and to avoid duplicates


for i in range (2):
	for v,s in short[i].items ():
		all_shorts[i][s] = v

what = ["INDIC_SYLLABIC_CATEGORY", "INDIC_MATRA_CATEGORY"]
what_short = ["ISC", "IMC"]
print ('#pragma GCC diagnostic push')
print ('#pragma GCC diagnostic ignored "-Wunused-macros"')
cat_defs = []
for i in range (2):
	vv = sorted (values[i].keys ())
	for v in vv:
		v_no_and = v.replace ('_And_', '_')
		if v in short[i]:
			s = short[i][v]
		else:
			s = ''.join ([c for c in v_no_and if ord ('A') <= ord (c) <= ord ('Z')])
			if s in all_shorts[i]:
				raise Exception ("Duplicate short value alias", v, all_shorts[i][s])
			all_shorts[i][s] = v
			short[i][v] = s
		cat_defs.append(
			(f'{what_short[i]}_{s}', f'{what[i]}_{v.upper()}', str(values[i][v]), v)
		)

maxlen_s = max(len (c[0]) for c in cat_defs)
maxlen_l = max(len (c[1]) for c in cat_defs)
maxlen_n = max(len (c[2]) for c in cat_defs)
for s in what_short:
	print ()
	for c in [c for c in cat_defs if s in c[0]]:
		print(
			f"#define {c[0].ljust(maxlen_s)} {c[1].ljust(maxlen_l)} /* {c[2].rjust(maxlen_n)} chars; {c[3]} */"
		)
print ()
print ('#pragma GCC diagnostic pop')
print ()
print ("#define _(S,M) INDIC_COMBINE_CATEGORIES (ISC_##S, IMC_##M)")
print ()
print ()

total = 0
used = 0
last_block = None
def print_block(block, start, end, data):
	global total, used, last_block
	if block and block != last_block:
		print ()
		print ()
		print(f"  /* {block} */")
	num = 0
	assert start % 8 == 0
	assert (end+1) % 8 == 0
	for u in range (start, end+1):
		if u % 8 == 0:
			print ()
			print ("  /* %04X */" % u, end="")
		if u in data:
			num += 1
		d = data.get (u, defaults)
		print("%9s" % f"_({short[0][d[0]]},{short[1][d[1]]}),", end="")

	total += end - start + 1
	used += num
	if block:
		last_block = block

uu = sorted (data.keys ())

last = -100000
num = 0
offset = 0
starts = []
ends = []
print ("static const uint16_t indic_table[] = {")
for u in uu:
	if u <= last:
		continue
	block = data[u][2]

	start = u//8*8
	end = start+1
	while end in uu and block == data[end][2]:
		end += 1
	end = (end-1)//8*8 + 7

	if start != last + 1:
		if start - last <= 1+16*3:
			print_block (None, last+1, start-1, data)
		else:
			if last >= 0:
				ends.append (last + 1)
				offset += ends[-1] - starts[-1]
			print ()
			print ()
			print ("#define indic_offset_0x%04xu %d" % (start, offset))
			starts.append (start)

	print_block (block, start, end, data)
	last = end
ends.append (last + 1)
offset += ends[-1] - starts[-1]
print ()
print ()
occupancy = used * 100. / total
page_bits = 12
print ("}; /* Table items: %d; occupancy: %d%% */" % (offset, occupancy))
print ()
print ("uint16_t")
print ("hb_indic_get_categories (hb_codepoint_t u)")
print ("{")
print ("  switch (u >> %d)" % page_bits)
print ("  {")
pages = {u>>page_bits for u in starts+ends+list (singles.keys ())}
for p in sorted(pages):
	print ("    case 0x%0Xu:" % p)
	for u,d in singles.items ():
		if p != u>>page_bits: continue
		print ("      if (unlikely (u == 0x%04Xu)) return _(%s,%s);" % (u, short[0][d[0]], short[1][d[1]]))
	for (start,end) in zip (starts, ends):
		if p not in [start>>page_bits, end>>page_bits]: continue
		offset = "indic_offset_0x%04xu" % start
		print ("      if (hb_in_range<hb_codepoint_t> (u, 0x%04Xu, 0x%04Xu)) return indic_table[u - 0x%04Xu + %s];" % (start, end-1, start, offset))
	print ("      break;")
	print ("")
print ("    default:")
print ("      break;")
print ("  }")
print ("  return _(x,x);")
print ("}")
print ()
print ("#undef _")
for i in range (2):
	print ()
	vv = sorted (values[i].keys ())
	for v in vv:
		print(f"#undef {what_short[i]}_{short[i][v]}")
print ()
print ('#endif')
print ()
print ("/* == End of generated table == */")

# Maintain at least 30% occupancy in the table */
if occupancy < 30:
	raise Exception ("Table too sparse, please investigate: ", occupancy)
