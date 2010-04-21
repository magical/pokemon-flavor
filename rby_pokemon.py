#!/usr/bin/env python3
# encoding: utf8
"""Extracts Pokémon flavour (Pokédex) text from a ROM image of any of the
first-generation Pokémon games.
"""

from sys import argv

if len(argv) < 3:
    print("Usage: rby_pokemon.py {ROM} {version}")
    exit(1)

version = argv[2].lower()

if version in ('red', 'blue', 'r', 'b'):
    offset = 0xac000
    pokemon_names = open('rb_pokemon.txt') # R/B indices don't match the dex
elif version in ('yellow', 'y'):
    offset = 0xb8000
    pokemon_names = open('pokemon.txt')
else:
    print("Usage: rby_pokemon.py {ROM} {version}")
    exit(1)

table = {}

for line in open('rby.tbl'):
    line = line.rstrip('\n')
    byte, char = line.split('=', 1)

    byte = int(byte, 16)
    if char == '\\n':
        char = '\n'

    table[byte] = char

game = open(argv[1], 'rb')
game.seek(offset)

for pokemon in range(151):
    name = pokemon_names.readline().rstrip()
    print(name)            # Bulbasaur
    print('=' * len(name)) # =========

    game.read(1) # \x00

    # flavour text, two pages
    for page in (1, 2):
        while True:
            byte = game.read(1)
            if byte in (b'\x49', b'\x50'):
                break

            print(table.setdefault(
                ord(byte), '\\x{0:02x}'.format(ord(byte))
            ), end='')

        print('\n\n', end='')
