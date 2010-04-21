#!/usr/bin/env python3
# encoding: utf8
"""Extracts Pokémon flavour (Pokédex) text from a ROM image of any of the
third-generation Pokémon games.
"""

from sys import argv

version = argv[2].lower()

if version in ('ruby', 'r'):
    offset = 0x3a0675
    pages = 2
elif version in ('sapphire', 's'):
    offset = 0x3a04bd
    pages = 2
elif version in ('emerald', 'e'):
    offset = 0x55d389
    pages = 1
elif version in ('firered', 'f', 'fr'):
    offset = 0x444cb2
    pages = 1
elif version in ('leafgreen', 'l', 'lg'):
    offset = 0x444aee
    pages = 1
else:
    print('Usage: rsefl_pokemon.py {ROM} {version}')
    exit(1)

table = {}
for line in open('rsefl.tbl'):
    line = line.rstrip('\n')
    byte, char = line.split('=', 1)

    byte = int(byte, 16)
    if char == '\\n':
        char = '\n'

    table[byte] = char

pokemon_names = open('pokemon.txt')
game = open(argv[1], 'rb')
game.seek(offset)

for pokemon in range(386):
    name = pokemon_names.readline().strip()
    print(name)            # Bulbasaur
    print('=' * len(name)) # =========

    for page in range(pages):
        while True:
            byte = game.read(1)
            if byte == b'\xff':
                break
 
            print(table.setdefault(
                ord(byte), '\\x{0:02x}'.format(ord(byte))
            ), end='')

        print('\n\n', end='')

        if version in ('firered', 'leafgreen', 'f', 'l', 'fr', 'lg'):
            # FR/LG texts are separated by either \xff\xff or \xff\x00\xff
            if game.read(1) == b'\x00':
                game.read(1)
