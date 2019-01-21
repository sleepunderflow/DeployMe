#!/usr/bin/python3
import struct
import sys

fileName = sys.argv[1]
contentLength = 24


def main():
    file = open(fileName, 'rb')
    buffer = file.read()

    # print(buffer)
    location = -1
    for pos in range(0, len(buffer) - 8):
        text = buffer[pos:pos+8]
        number = int.from_bytes(text, byteorder='little')
        if number == 0xdeadbeefdeadbeef:
            location = pos
            break
    if location == -1:
        raise ValueError('Byte sequence not found in the source file')
    print(location)

    content = list(buffer[location:location+contentLength])

    for c in content:
        print(hex(c)[2:], end=' ')

    print('\n')

    header = int.from_bytes(content[0:8], byteorder='little')
    print('Header: {0}'.format(hex(header)))

    flags = int.from_bytes(content[8:16], byteorder='little')
    print('Flags: {0}'.format(hex(flags)))

    injectedDataOffset = int.from_bytes(content[16:24], byteorder='little')
    print('injectedDataOffset: {0}'.format(hex(injectedDataOffset)))


main()
