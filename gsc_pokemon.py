#!/usr/bin/env python3
# encoding: utf8
"""Extracts Pokémon flavour (Pokédex) text from a ROM image of any of the
second-generation Pokémon games.
"""

from sys import argv

if len(argv) < 3:
    print("Usage: gsc_pokemon.py {ROM} {version}")
    exit(1)

version = argv[2].lower()

if version in ('gold', 'silver', 'g', 's'):
    # Pokémon #1, #65, #129, #193 (Bulbasaur, Alakazam, Magikarp, Yanma)
    offsets = (0x1a0000, 0x1a4000, 0x1a8000, 0x1ac000)
elif version in ('crystal', 'c'):
    # same as GS
    offsets = (0x181695, 0x1b8000, 0x1cc000, 0x1d0000)
else:
    print("Usage: gsc_pokemon.py {ROM} {version}")
    exit(1)

table = {}

for line in open('gsc.tbl'):
    line = line.rstrip('\n')
    byte, char = line.split('=', 1)

    byte = int(byte, 16)
    if char == '\\n':
        char = '\n'

    table[byte] = char

pokemon_names = open('pokemon.txt')
game = open(argv[1], 'rb')

offset = 0
game.seek(offsets[offset])

for pokemon in range(251):
    name = pokemon_names.readline().strip()
    print(name)            # Bulbasaur
    print('=' * len(name)) # =========

    # species name (e.g. Bulbasaur is the "SEED" Pokémon)
    while game.read(1) != b'\x50':
        pass

    game.read(4) # four mystery bytes

    # flavour text, two pages
    for page in (1, 2):
        while True:
            byte = game.read(1)
            if byte == b'\x50':
                break

            print(table.setdefault(
                ord(byte), '\\x{0:02x}'.format(ord(byte))
            ), end='')

        print('\n\n', end='')

    if pokemon % 64 == 63: # remember, Zhorken, we're starting from zero
        offset += 1
        game.seek(offsets[offset])
