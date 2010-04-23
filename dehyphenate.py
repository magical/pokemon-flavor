#!/usr/bin/env python3.1
import sys
import re
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from collections import OrderedDict as odict

def myfile(mode='r', encoding=None):
    if 'b' in mode and encoding is not None:
        raise ValueError("binary mode can't take an encoding")
    def inner(path):
        if path == "-":
            if mode == 'r':
                return sys.stdin
            elif mode == 'w':
                return sys.stdout
            elif mode == 'rb':
                return sys.stdin.buffer
            elif mode == 'wb':
                return sys.stdout.buffer
        else:
            return open(path, mode=mode, encoding=encoding)
    return inner

arg_parser = ArgumentParser(
    formatter_class=RawDescriptionHelpFormatter,
    epilog="""\
Formats:
 oneline - collapse newlines, page breaks, and soft hyphens
 csv     - output a csv file with the "raw" flavor text
 orig    - should round-trip

 changes - don't show the full flavor text--just the hyphenated words
           and how they are interpreted by the script
""")
arg_parser.add_argument("file", type=myfile('r', encoding="utf-8"),
    help="The flavor text file you want to dehyphenate")
arg_parser.add_argument("-f", "--format",
    metavar='FORMAT',
    default='oneline',
    choices=['oneline', 'csv', 'orig', 'changes'],
    help="Output format")

args = arg_parser.parse_args()
FORMAT = args.format
f = args.file

# First things first: parse the flavor text file.
flavor_texts = odict()
state = 'pokemon'
flavor = []
next_line = f.readline()
end = False
while True:
    line = next_line
    if not line:
        state = 'endflavor'
        end = True
    line = line.strip()
    next_line = f.readline()
    peek = next_line.strip()

    if peek.startswith("=") and peek.replace("=", "") == "":
        assert len(peek) == len(line)
        state = 'endflavor'

    if state == 'endflavor':
        if flavor:
            flavor.pop() # form feed
            flavor_texts[pokemon] = ''.join(flavor)
            flavor[:] = []
        state = 'pokemon'
        pokemon = None
        if end:
            break

    if state == 'pokemon':
        pokemon = line
        state = 'underline'
    elif state == 'underline':
        state = 'flavor'
    elif state == 'flavor':
        flavor.append(line)
        if peek != "":
            flavor.append("\n")
        else:
            state = 'pagebreak'
    elif state == 'pagebreak':
        if peek == "":
            pass
        else:
            flavor.append("\f")
            state = 'flavor'
    else:
        raise ValueError(state)


# Load words from the system dictionary
words = set(x.strip() for x in open("/usr/share/dict/words", encoding='latin-1'))
# My dictionary is missing a few words
words.add("pok\xe9mon")
words.add("telekinetic")
words.add("unprogrammed")

words.discard("")

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
        changes.append((word, without_hyphen))
        return first_half + "\N{soft hyphen}" + sep + second_half
    else:
        changes.append((word, word))
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
 [\n\f]           # which occurs before a line break or form feed
)
(?P<second_half>  # And grab the word which follows it, too
 (?:
  [A-Za-z]
 |
  -(?!-)
 )+
)
"""
hyphen_re = re.compile(hyphen_pattern, re.VERBOSE)

changes = odict()
for pokemon, flavor in flavor_texts.items():
    changes[pokemon] = []

    def callback(m):
        return analyze_word(changes[pokemon], *m.groups())
    flavor_texts[pokemon] = hyphen_re.sub(callback, flavor)

if FORMAT == 'oneline':
    def fix_flavor(flavor):
        return (flavor.replace("\f", "\n")
                      .replace("\N{soft hyphen}\n", "")
                      .replace("-\n", "-")
                      .replace("\n", " "))

    for pokemon, flavor in flavor_texts.items():
        print("{:10s} {}".format(pokemon, fix_flavor(flavor)))
elif FORMAT == 'csv':
    import csv
    writer = csv.writer(sys.stdout)
    writer.writerow(["Pok\xe9mon", "Flavor"])
    writer.writerows(flavor_texts.items())
elif FORMAT == 'orig':
    def fix_flavor(flavor):
        return (flavor.replace("\f", "\n\n")
                      .replace("\N{soft hyphen}", "-"))

    for pokemon, flavor in flavor_texts.items():
        print(pokemon)
        print("=" * len(pokemon))
        print(fix_flavor(flavor))
        print()
elif FORMAT == 'changes':
    for pokemon, changed_words in changes.items():
        if not changed_words:
            continue
        print(pokemon, ":", sep="")
        for from_, to in changed_words:
            print(from_, "->", to)
        print()
else:
    print("Unknown format: {}".format(FORMAT), file=sys.stderr)
