from sys import argv

table = {}

for line in open('RBY.tbl'):
    line = line.rstrip('\n')
    byte, char = line.split('=', 1)

    byte = int(byte, 16)
    if char == '\\n':
        char = '\n'

    table[byte] = char

game = open(argv[1], 'rb')

while True:
    byte = game.read(1)

    if byte == b'':
        break

    print(table.setdefault(ord(byte), '\\x{0}'.format(hex(ord(byte))[2:])), end='')
