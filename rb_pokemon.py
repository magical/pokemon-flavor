from sys import argv

offset = 0xac000
table = {}
pokemon_names = []

for line in open('rb_pokemon.txt'):
    pokemon_names.append(line.rstrip('\n'))

for line in open('RBY.tbl'):
    line = line.rstrip('\n')
    byte, char = line.split('=', 1)

    byte = int(byte, 16)
    if char == '\\n':
        char = '\n'

    table[byte] = char

game = open(argv[1], 'rb')
game.seek(offset)

for pokemon in range(190):
    print(pokemon_names[pokemon])            # Rhydon
    print('=' * len(pokemon_names[pokemon])) # ======

    game.read(1) # \x00

    # flavour text, two pages
    for page in (1, 2):
        byte = game.read(1)
        while byte not in (b'\x49', b'\x50'):
            print(table.setdefault(ord(byte), '\\x{0}'.format(hex(ord(byte))[2:])), end='')
            byte = game.read(1)

        print('\n\n', end='')
