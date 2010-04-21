from sys import argv

version = argv[2].lower()
if version in ('ruby', 'r'):
    offset = 0x3a0675
    pages = 2
elif version in('sapphire', 's'):
    offset = 0x3a04bd
    pages = 2
elif version in('emerald', 'e'):
    offset = 0x55d389
    pages = 1

table = {}
for line in open('rse.tbl'):
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
