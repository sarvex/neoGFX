#!/usr/bin/env python3
# flake8: noqa: F821

"""usage: ./gen-use-table.py IndicSyllabicCategory.txt IndicPositionalCategory.txt ArabicShaping.txt DerivedCoreProperties.txt UnicodeData.txt Blocks.txt Scripts.txt IndicSyllabicCategory-Additional.txt IndicPositionalCategory-Additional.txt

Input files:
* https://unicode.org/Public/UCD/latest/ucd/IndicSyllabicCategory.txt
* https://unicode.org/Public/UCD/latest/ucd/IndicPositionalCategory.txt
* https://unicode.org/Public/UCD/latest/ucd/ArabicShaping.txt
* https://unicode.org/Public/UCD/latest/ucd/DerivedCoreProperties.txt
* https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
* https://unicode.org/Public/UCD/latest/ucd/Blocks.txt
* https://unicode.org/Public/UCD/latest/ucd/Scripts.txt
* ms-use/IndicSyllabicCategory-Additional.txt
* ms-use/IndicPositionalCategory-Additional.txt
"""


import sys

if len (sys.argv) != 10:
	sys.exit (__doc__)

DISABLED_SCRIPTS = {
	'Arabic',
	'Lao',
	'Samaritan',
	'Syriac',
	'Thai',
}

files = [open (x, encoding='utf-8') for x in sys.argv[1:]]

headers = [
	[f.readline() for _ in range(2)] for j, f in enumerate(files) if j != 4
]
for j in range(7, 9):
	for line in files[j]:
		if line := line.rstrip():
			headers[j - 1].append(line)
		else:
			break
headers.append (["UnicodeData.txt does not have a header."])

unicode_data = [{} for _ in files]
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
		t = fields[1 if i not in [2, 4] else 2]

		if i == 2:
			t = f'jt_{t}'
		elif i == 3 and t != 'Default_Ignorable_Code_Point':
			continue
		elif i == 7 and t == 'Consonant_Final_Modifier':
			# TODO: https://github.com/MicrosoftDocs/typography-issues/issues/336
			t = 'Syllable_Modifier'
		elif i == 8 and t == 'NA':
			t = 'Not_Applicable'

		i0 = i if i < 7 else i - 7
		for u in range (start, end + 1):
			unicode_data[i0][u] = t
		values[i0][t] = values[i0].get (t, 0) + end - start + 1

defaults = ('Other', 'Not_Applicable', 'jt_X', '', 'Cn', 'No_Block', 'Unknown')

# Merge data into one dict:
for i,v in enumerate (defaults):
	values[i][v] = values[i].get (v, 0) + 1
combined = {}
for i,d in enumerate (unicode_data):
	for u,v in d.items ():
		if u not in combined:
			if i >= 4:
				continue
			combined[u] = list (defaults)
		combined[u][i] = v
combined = {k: v for k, v in combined.items() if v[6] not in DISABLED_SCRIPTS}


property_names = [
	# General_Category
	'Cc', 'Cf', 'Cn', 'Co', 'Cs', 'Ll', 'Lm', 'Lo', 'Lt', 'Lu', 'Mc',
	'Me', 'Mn', 'Nd', 'Nl', 'No', 'Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po',
	'Ps', 'Sc', 'Sk', 'Sm', 'So', 'Zl', 'Zp', 'Zs',
	# Indic_Syllabic_Category
	'Other',
	'Bindu',
	'Visarga',
	'Avagraha',
	'Nukta',
	'Virama',
	'Pure_Killer',
	'Invisible_Stacker',
	'Vowel_Independent',
	'Vowel_Dependent',
	'Vowel',
	'Consonant_Placeholder',
	'Consonant',
	'Consonant_Dead',
	'Consonant_With_Stacker',
	'Consonant_Prefixed',
	'Consonant_Preceding_Repha',
	'Consonant_Succeeding_Repha',
	'Consonant_Subjoined',
	'Consonant_Medial',
	'Consonant_Final',
	'Consonant_Head_Letter',
	'Consonant_Initial_Postfixed',
	'Modifying_Letter',
	'Tone_Letter',
	'Tone_Mark',
	'Gemination_Mark',
	'Cantillation_Mark',
	'Register_Shifter',
	'Syllable_Modifier',
	'Consonant_Killer',
	'Non_Joiner',
	'Joiner',
	'Number_Joiner',
	'Number',
	'Brahmi_Joining_Number',
	'Hieroglyph',
	'Hieroglyph_Joiner',
	'Hieroglyph_Segment_Begin',
	'Hieroglyph_Segment_End',
	# Indic_Positional_Category
	'Not_Applicable',
	'Right',
	'Left',
	'Visual_Order_Left',
	'Left_And_Right',
	'Top',
	'Bottom',
	'Top_And_Bottom',
	'Top_And_Bottom_And_Left',
	'Top_And_Right',
	'Top_And_Left',
	'Top_And_Left_And_Right',
	'Bottom_And_Left',
	'Bottom_And_Right',
	'Top_And_Bottom_And_Right',
	'Overstruck',
	# Joining_Type
	'jt_C',
	'jt_D',
	'jt_L',
	'jt_R',
	'jt_T',
	'jt_U',
	'jt_X',
]

class PropertyValue(object):
	def __init__(self, name_):
		self.name = name_
	def __str__(self):
		return self.name
	def __eq__(self, other):
		return self.name == (other if isinstance(other, str) else other.name)
	def __ne__(self, other):
		return not (self == other)
	def __hash__(self):
		return hash(str(self))

property_values = {}

for name in property_names:
	value = PropertyValue(name)
	assert value not in property_values
	assert value not in globals()
	property_values[name] = value
globals().update(property_values)


def is_BASE(U, UISC, UDI, UGC, AJT):
	return (UISC in [Number, Consonant, Consonant_Head_Letter,
			Tone_Letter,
			Vowel_Independent,
			] or
		# TODO: https://github.com/MicrosoftDocs/typography-issues/issues/484
		AJT in [jt_C, jt_D, jt_L, jt_R] and UISC != Joiner or
		(UGC == Lo and UISC in [Avagraha, Bindu, Consonant_Final, Consonant_Medial,
					Consonant_Subjoined, Vowel, Vowel_Dependent]))
def is_BASE_NUM(U, UISC, UDI, UGC, AJT):
	return UISC == Brahmi_Joining_Number
def is_BASE_OTHER(U, UISC, UDI, UGC, AJT):
	if UISC == Consonant_Placeholder: return True
	return U in [0x2015, 0x2022, 0x25FB, 0x25FC, 0x25FD, 0x25FE]
def is_CGJ(U, UISC, UDI, UGC, AJT):
	# Also includes VARIATION_SELECTOR and ZWJ
	return UISC == Joiner or UDI and UGC in [Mc, Me, Mn]
def is_CONS_FINAL(U, UISC, UDI, UGC, AJT):
	return ((UISC == Consonant_Final and UGC != Lo) or
		UISC == Consonant_Succeeding_Repha)
def is_CONS_FINAL_MOD(U, UISC, UDI, UGC, AJT):
	return UISC == Syllable_Modifier
def is_CONS_MED(U, UISC, UDI, UGC, AJT):
	# Consonant_Initial_Postfixed is new in Unicode 11; not in the spec.
	return (UISC == Consonant_Medial and UGC != Lo or
		UISC == Consonant_Initial_Postfixed)
def is_CONS_MOD(U, UISC, UDI, UGC, AJT):
	return (UISC in [Nukta, Gemination_Mark, Consonant_Killer] and
		not is_SYM_MOD(U, UISC, UDI, UGC, AJT))
def is_CONS_SUB(U, UISC, UDI, UGC, AJT):
	return UISC == Consonant_Subjoined and UGC != Lo
def is_CONS_WITH_STACKER(U, UISC, UDI, UGC, AJT):
	return UISC == Consonant_With_Stacker
def is_HALANT(U, UISC, UDI, UGC, AJT):
	return UISC == Virama
def is_HALANT_NUM(U, UISC, UDI, UGC, AJT):
	return UISC == Number_Joiner
def is_HIEROGLYPH(U, UISC, UDI, UGC, AJT):
	return UISC == Hieroglyph
def is_HIEROGLYPH_JOINER(U, UISC, UDI, UGC, AJT):
	return UISC == Hieroglyph_Joiner
def is_HIEROGLYPH_SEGMENT_BEGIN(U, UISC, UDI, UGC, AJT):
	return UISC == Hieroglyph_Segment_Begin
def is_HIEROGLYPH_SEGMENT_END(U, UISC, UDI, UGC, AJT):
	return UISC == Hieroglyph_Segment_End
def is_INVISIBLE_STACKER(U, UISC, UDI, UGC, AJT):
	# Split off of HALANT
	return (UISC == Invisible_Stacker
		and not is_SAKOT(U, UISC, UDI, UGC, AJT)
	)
def is_ZWNJ(U, UISC, UDI, UGC, AJT):
	return UISC == Non_Joiner
def is_OTHER(U, UISC, UDI, UGC, AJT):
	# Also includes BASE_IND and SYM
	return ((UGC == Po or UISC in [Consonant_Dead, Joiner, Modifying_Letter, Other])
		and not is_BASE(U, UISC, UDI, UGC, AJT)
		and not is_BASE_OTHER(U, UISC, UDI, UGC, AJT)
		and not is_CGJ(U, UISC, UDI, UGC, AJT)
		and not is_SYM_MOD(U, UISC, UDI, UGC, AJT)
		and not is_Word_Joiner(U, UISC, UDI, UGC, AJT)
	)
def is_REPHA(U, UISC, UDI, UGC, AJT):
	return UISC in [Consonant_Preceding_Repha, Consonant_Prefixed]
def is_SAKOT(U, UISC, UDI, UGC, AJT):
	# Split off of HALANT
	return U == 0x1A60
def is_SYM_MOD(U, UISC, UDI, UGC, AJT):
	return U in [0x1B6B, 0x1B6C, 0x1B6D, 0x1B6E, 0x1B6F, 0x1B70, 0x1B71, 0x1B72, 0x1B73]
def is_VOWEL(U, UISC, UDI, UGC, AJT):
	return (UISC == Pure_Killer or
		UGC != Lo and UISC in [Vowel, Vowel_Dependent])
def is_VOWEL_MOD(U, UISC, UDI, UGC, AJT):
	return (UISC in [Tone_Mark, Cantillation_Mark, Register_Shifter, Visarga] or
		UGC != Lo and UISC == Bindu)
def is_Word_Joiner(U, UISC, UDI, UGC, AJT):
	# Also includes Rsv
	return (UDI and U not in [0x115F, 0x1160, 0x3164, 0xFFA0, 0x1BCA0, 0x1BCA1, 0x1BCA2, 0x1BCA3]
		and UISC == Other
		and not is_CGJ(U, UISC, UDI, UGC, AJT)
	) or UGC == Cn

use_mapping = {
	'B':	is_BASE,
	'N':	is_BASE_NUM,
	'GB':	is_BASE_OTHER,
	'CGJ':	is_CGJ,
	'F':	is_CONS_FINAL,
	'FM':	is_CONS_FINAL_MOD,
	'M':	is_CONS_MED,
	'CM':	is_CONS_MOD,
	'SUB':	is_CONS_SUB,
	'CS':	is_CONS_WITH_STACKER,
	'H':	is_HALANT,
	'HN':	is_HALANT_NUM,
	'IS':	is_INVISIBLE_STACKER,
	'G':	is_HIEROGLYPH,
	'J':	is_HIEROGLYPH_JOINER,
	'SB':	is_HIEROGLYPH_SEGMENT_BEGIN,
	'SE':	is_HIEROGLYPH_SEGMENT_END,
	'ZWNJ':	is_ZWNJ,
	'O':	is_OTHER,
	'R':	is_REPHA,
	'Sk':	is_SAKOT,
	'SM':	is_SYM_MOD,
	'V':	is_VOWEL,
	'VM':	is_VOWEL_MOD,
	'WJ':	is_Word_Joiner,
}

use_positions = {
	'F': {
		'Abv': [Top],
		'Blw': [Bottom],
		'Pst': [Right],
	},
	'M': {
		'Abv': [Top],
		'Blw': [Bottom, Bottom_And_Left, Bottom_And_Right],
		'Pst': [Right],
		'Pre': [Left, Top_And_Bottom_And_Left],
	},
	'CM': {
		'Abv': [Top],
		'Blw': [Bottom, Overstruck],
	},
	'V': {
		'Abv': [Top, Top_And_Bottom, Top_And_Bottom_And_Right, Top_And_Right],
		'Blw': [Bottom, Overstruck, Bottom_And_Right],
		'Pst': [Right],
		'Pre': [Left, Top_And_Left, Top_And_Left_And_Right, Left_And_Right],
	},
	'VM': {
		'Abv': [Top],
		'Blw': [Bottom, Overstruck],
		'Pst': [Right],
		'Pre': [Left],
	},
	'SM': {
		'Abv': [Top],
		'Blw': [Bottom],
	},
	'H': None,
	'IS': None,
	'B': None,
	'FM': {
		'Abv': [Top],
		'Blw': [Bottom],
		'Pst': [Not_Applicable],
	},
	'R': None,
	'SUB': None,
}

def map_to_use(data):
	out = {}
	items = use_mapping.items()
	for U, (UISC, UIPC, AJT, UDI, UGC, UBlock, _) in data.items():

		# Resolve Indic_Syllabic_Category

		# TODO: These don't have UISC assigned in Unicode 13.0.0, but have UIPC
		if 0x1CE2 <= U <= 0x1CE8: UISC = Cantillation_Mark

		# Tibetan:
		# TODO: These don't have UISC assigned in Unicode 13.0.0, but have UIPC
		if 0x0F18 <= U <= 0x0F19 or 0x0F3E <= U <= 0x0F3F: UISC = Vowel_Dependent

		# TODO: https://github.com/harfbuzz/harfbuzz/pull/627
		if 0x1BF2 <= U <= 0x1BF3: UISC = Nukta; UIPC = Bottom

		# TODO: U+1CED should only be allowed after some of
		# the nasalization marks, maybe only for U+1CE9..U+1CF1.
		if U == 0x1CED: UISC = Tone_Mark

		values = [k for k,v in items if v(U, UISC, UDI, UGC, AJT)]
		assert len(values) == 1, f"{hex(U)} {UISC} {UDI} {UGC} {AJT} {values}"
		USE = values[0]

		# Resolve Indic_Positional_Category

		# TODO: These should die, but have UIPC in Unicode 13.0.0
		if U in [0x953, 0x954]: UIPC = Not_Applicable

		# TODO: These are not in USE's override list that we have, nor are they in Unicode 13.0.0
		if 0xA926 <= U <= 0xA92A: UIPC = Top
		# TODO: https://github.com/harfbuzz/harfbuzz/pull/1037
		#  and https://github.com/harfbuzz/harfbuzz/issues/1631
		if U in [0x11302, 0x11303, 0x114C1]: UIPC = Top
		if 0x1CF8 <= U <= 0x1CF9: UIPC = Top

		# TODO: https://github.com/harfbuzz/harfbuzz/pull/982
		# also  https://github.com/harfbuzz/harfbuzz/issues/1012
		if 0x1112A <= U <= 0x1112B: UIPC = Top
		if 0x11131 <= U <= 0x11132: UIPC = Top

		assert (
			UIPC in [Not_Applicable, Visual_Order_Left]
			or U == 0x0F7F
			or USE in use_positions
		), f"{hex(U)} {UIPC} {USE} {UISC} {UDI} {UGC} {AJT}"

		if pos_mapping := use_positions.get(USE, None):
			values = [k for k,v in pos_mapping.items() if v and UIPC in v]
			assert (
				len(values) == 1
			), f"{hex(U)} {UIPC} {USE} {UISC} {UDI} {UGC} {AJT} {values}"
			USE = USE + values[0]

		out[U] = (USE, UBlock)
	return out

use_data = map_to_use(combined)

print ("/* == Start of generated table == */")
print ("/*")
print (" * The following table is generated by running:")
print (" *")
print(
	f" *   {sys.argv[0]} IndicSyllabicCategory.txt IndicPositionalCategory.txt ArabicShaping.txt DerivedCoreProperties.txt UnicodeData.txt Blocks.txt Scripts.txt IndicSyllabicCategory-Additional.txt IndicPositionalCategory-Additional.txt"
)
print (" *")
print (" * on files with these headers:")
print (" *")
for h in headers:
	for l in h:
		print(f" * {l.strip()}")
print (" */")
print ()
print ("#ifndef HB_OT_SHAPE_COMPLEX_USE_TABLE_HH")
print ("#define HB_OT_SHAPE_COMPLEX_USE_TABLE_HH")
print ()
print ('#include "hb.hh"')
print ()
print ('#include "hb-ot-shape-complex-use-machine.hh"')
print ()

total = 0
used = 0
last_block = None
def print_block(block, start, end, use_data):
	global total, used, last_block
	if block and block != last_block:
		print ()
		print ()
		print(f"  /* {block} */")
		if start % 16:
			print (' ' * (20 + (start % 16 * 6)), end='')
	num = 0
	assert start % 8 == 0
	assert (end+1) % 8 == 0
	for u in range (start, end+1):
		if u % 16 == 0:
			print ()
			print ("  /* %04X */" % u, end='')
		if u in use_data:
			num += 1
		d = use_data.get (u)
		if d is not None:
			d = d[0]
		elif u in unicode_data[4]:
			d = 'O'
		else:
			d = 'WJ'
		print ("%6s," % d, end='')

	total += end - start + 1
	used += num
	if block:
		last_block = block

uu = sorted (use_data.keys ())

last = -100000
num = 0
offset = 0
starts = []
ends = []
print ('#pragma GCC diagnostic push')
print ('#pragma GCC diagnostic ignored "-Wunused-macros"')
for k,v in sorted(use_mapping.items()):
	if k in use_positions and use_positions[k]: continue
	print ("#define %s	USE(%s)	/* %s */" % (k, k, v.__name__[3:]))
for k,v in sorted(use_positions.items()):
	if not v: continue
	for suf in v.keys():
		tag = k + suf
		print ("#define %s	USE(%s)" % (tag, tag))
print ('#pragma GCC diagnostic pop')
print ("")
print ("static const uint8_t use_table[] = {")
for u in uu:
	if u <= last:
		continue
	if use_data[u][0] == 'O':
		continue
	block = use_data[u][1]

	start = u//8*8
	end = start+1
	while end in uu and block == use_data[end][1]:
		end += 1
	end = (end-1)//8*8 + 7

	if start != last + 1:
		if start - last <= 1+16*3:
			print_block (None, last+1, start-1, use_data)
		else:
			if last >= 0:
				ends.append (last + 1)
				offset += ends[-1] - starts[-1]
			print ()
			print ()
			print ("#define use_offset_0x%04xu %d" % (start, offset))
			starts.append (start)

	print_block (block, start, end, use_data)
	last = end
ends.append (last + 1)
offset += ends[-1] - starts[-1]
print ()
print ()
occupancy = used * 100. / total
page_bits = 12
print ("}; /* Table items: %d; occupancy: %d%% */" % (offset, occupancy))
print ()
print ("static inline uint8_t")
print ("hb_use_get_category (hb_glyph_info_t info)")
print ("{")
print ("  hb_codepoint_t u = info.codepoint;")
print ("  switch (u >> %d)" % page_bits)
print ("  {")
pages = {u>>page_bits for u in starts+ends}
for p in sorted(pages):
	print ("    case 0x%0Xu:" % p)
	for (start,end) in zip (starts, ends):
		if p not in [start>>page_bits, end>>page_bits]: continue
		offset = "use_offset_0x%04xu" % start
		print ("      if (hb_in_range<hb_codepoint_t> (u, 0x%04Xu, 0x%04Xu)) return use_table[u - 0x%04Xu + %s];" % (start, end-1, start, offset))
	print ("      break;")
	print ("")
print ("    default:")
print ("      break;")
print ("  }")
print ("  if (_hb_glyph_info_get_general_category (&info) == HB_UNICODE_GENERAL_CATEGORY_UNASSIGNED)")
print ("    return WJ;")
print ("  return O;")
print ("}")
print ()
for k in sorted(use_mapping.keys()):
	if k in use_positions and use_positions[k]: continue
	print(f"#undef {k}")
for k,v in sorted(use_positions.items()):
	if not v: continue
	for suf in v.keys():
		tag = k + suf
		print(f"#undef {tag}")
print ()
print ()
print ("#endif /* HB_OT_SHAPE_COMPLEX_USE_TABLE_HH */")
print ("/* == End of generated table == */")

# Maintain at least 50% occupancy in the table */
if occupancy < 50:
	raise Exception ("Table too sparse, please investigate: ", occupancy)
