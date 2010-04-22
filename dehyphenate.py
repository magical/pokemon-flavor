#!/usr/bin/env python3.1
import sys
import re
from collections import OrderedDict as odict

# I'm too lazy to parse the command-line, so you get a module-level constant.
# This controls the how the flavor text it outputted.
# raw     - preserve form breaks and soft hyphens
# cat     - concatenate lines and strip soft hyphens
# changes - don't show the full flavor text; just the hyphenated words
#           and how each interpreted by the script
FORMAT = 'changes'

f = open(sys.argv[1], encoding="utf-8")

# First things first: parse the flavor text file.
flavor_texts = odict()
state = 'pokemon'
for line in f:
    line = line.strip()
    if state == 'pokemon':
        if line == '':
            continue
        pokemon = line
        state = 'underline'
    elif state == 'underline':
        assert line.replace('=', '') == ''
        assert len(line) == len(pokemon)
        state = 'page1'
        flavor = ""
    elif state in ('page1', 'page2'):
        if line == '':
            if state == 'page1':
                # This is the break between two pages, so add a form feed
                flavor = flavor + '\f'
                state = 'page2'
            elif state == 'page2':
                flavor_texts[pokemon] = flavor
                state = 'pokemon'
            continue
        flavor += line + '\n'
    else:
        raise ValueError(state)
if state != 'pokemon':
    flavor_texts[pokemon] = flavor


# Load words from the system dictionary
words = set(x.strip() for x in open('/usr/share/dict/words', encoding='latin-1'))
# My dictionary is missing a few words
words.add('pok\xe9mon')
words.add('telekinetic')
words.add('unprogrammed')
words.remove('')

def isword(word):
    # A little normalization.
    word = word.lower()
    if word.endswith("\u2019s") or word.endswith("'s"):
        word = word[:-2]

    # If the word is in the dictionary, it's a word!
    if word in words:
        return True
    # If this is a hyphenated word, we should check whether all
    # the components are words.
    if "-" in word:
        if all(component in words for component in word.split("-")):
            return True
    # Guess it's not a word after all.
    return False

def analyze_word(changes, first_half, sep, second_half):
    word = first_half + "-" + second_half
    without_hyphen = first_half + second_half
    # If we can remove the hyphen and get a real word, then it's
    # probably a soft hyphen
    if isword(without_hyphen):
        changes[word] = without_hyphen
        return first_half + "\N{soft hyphen}" + sep + second_half
    else:
        changes[word] = word
        return first_half + "-" + sep + second_half

hyphen_pattern = r"""
(?P<first_half>   # Grab the first half of a word
 (?:
  [A-Za-z\xe9]    # Which consists of alphabetic characters
 |
  -(?!-)          # or a solitary hyphens
 )+
) 
(?<!-)-           # Separated by a hyphen
(?P<sep>
 \n               # which occurs at the end of a line
 \f?              # optionally followed by a form feed
)
(?P<second_half>  # And grab the word which follows it
 (?:
  [A-Za-z]
 |
  -(?!-)
 )+
)
"""
hyphen_re = re.compile(hyphen_pattern, re.VERBOSE)

for pokemon, flavor in flavor_texts.items():
    changes = odict()

    def callback(m):
        return analyze_word(changes, *m.groups())
    flavor_texts[pokemon] = hyphen_re.sub(callback, flavor)

    if FORMAT == 'changes' and changes:
        print(pokemon, ":", sep="")
        for from_, to in changes.items():
            print(from_, "->", to)
        print()

if FORMAT == 'raw':
    for pokemon, flavor in flavor_texts.items():
        print(pokemon)
        print("=" * len(pokemon))
        print(flavor)
        print()
elif FORMAT == 'cat':
    def fix_flavor(flavor):
        flavor = (flavor.replace("\f", "")
                        .replace("\N{soft hyphen}\n", "")
                        .replace("-\n", "-")
                        .replace("\n", " "))
        return flavor

    for pokemon, flavor in flavor_texts.items():
        print("{:10s} {}".format(pokemon, fix_flavor(flavor)))
