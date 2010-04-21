from sys import argv

offsets = (0x181695, 0x1b8000, 0x1cc000, 0x1d0000)
table = {}
pokemon_names = []

for line in open('list of Pokémon.txt'):
    pokemon_names.append(line.rstrip('\n'))
    if len(pokemon_names) == 251:
        break

for line in open('GSC.tbl'):
    line = line.rstrip('\n')
    byte, char = line.split('=', 1)

    byte = int(byte, 16)
    if char == '\\n':
        char = '\n'

    table[byte] = char

game = open(argv[1], 'rb')
offset = 0
game.seek(offsets[offset])

for pokemon in range(251):
    print(pokemon_names[pokemon])            # Bulbasaur
    print('=' * len(pokemon_names[pokemon])) # =========

    # species name (e.g. Bulbasaur is the Seed Pokémon)
    while game.read(1) != b'\x50':
        pass

    game.read(4) # four mystery bytes

    # flavour text, two pages
    for page in (1, 2):
        byte = game.read(1)
        while byte != b'\x50':
            print(table.setdefault(ord(byte), '\\x{0}'.format(hex(ord(byte))[2:])), end='')
            byte = game.read(1)

        print('\n\n', end='')

    if pokemon % 64 == 63 and pokemon != 1:
        offset += 1
        game.seek(offsets[offset])
