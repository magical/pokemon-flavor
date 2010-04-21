from sys import argv

offset = 0x1a0000
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
game.read(offset)

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

    # There's a big block of zeroes every sixty-four Pokémon.
    if pokemon % 64 == 63:
        # This will also eat the first letter of the next Pokémon's species
        # name, but that shouldn't cause any problems.
        while game.read(1) == 0x0:
            pass
