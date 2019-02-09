""" Digital Communication - Lempel-Ziv Encoder """

import os
from bitarray import bitarray


class LzEncoder():
    """ LZ77 Encoder """

    def __init__(self, window_size, buffer_size):
        self.window_size = window_size
        self.buffer_size = buffer_size
        self.distance_bits = (window_size - 1).bit_length()
        self.length_bits = (buffer_size - 1).bit_length()
        self.compression = []


    def compress(self, filename):
        """
        Compress a file using LZ77 coding.

        Params:
            filename: name of file to compress
        """

        self.compression = []

        with open(filename + '.LZIV', 'x') as output:
            pass

        code_to_write = bitarray()

        with open(filename, 'rb') as input_file:
            buffer = bitarray()
            window = bitarray()

            try:
                buffer.fromfile(input_file, self.buffer_size)
            except EOFError:
                buffer.fromfile(input_file)

            while buffer.length() > 0:
                code = bitarray()

                distance, length, next_sym = self._encode_at_pos(window, buffer)
                code = self._code_to_bits(distance, length, next_sym)
                code_to_write += code

                self.compression.append((distance, length, next_sym))

                if not code_to_write.length() % 8:
                    with open(filename + '.LZIV', 'ab') as output:
                        output.write(code_to_write.tobytes())
                    code_to_write = bitarray()

                next_bytes = bitarray()
                try:
                    next_bytes.fromfile(input_file, length + 1)
                except EOFError:
                    pass

                window += buffer[:(length + 1) * 8]

                if window.length() > self.window_size * 8:
                    window = window[window.length() - self.window_size * 8:]

                buffer = buffer[(length + 1) * 8:] + next_bytes

        with open(filename + '.LZIV', 'ab') as output:
            output.write(code_to_write.tobytes())

        os.remove(filename)


    def _code_to_bits(self, distance, length, next_sym):
        distance_bin = bin(distance)[2:].rjust(self.distance_bits, '0')
        length_bin = bin(length)[2:].rjust(self.length_bits, '0')

        next_sym_bin = bitarray()
        next_sym_bin.frombytes(next_sym)

        code = bitarray(distance_bin + length_bin) + next_sym_bin

        return code


    @staticmethod
    def _encode_at_pos(window, buffer):
        window_bytes = window.tobytes()
        buffer_bytes = buffer.tobytes()
        buffer_len = len(buffer_bytes)

        length = 0
        substring = b''
        next_sym = buffer_bytes[length:length + 1]

        while substring + next_sym in window_bytes:
            substring += next_sym
            length += 1
            if length >= buffer_len:
                next_sym = b''
                break
            next_sym = buffer_bytes[length:length + 1]

        if length > 0:
            distance = window_bytes[::-1].index(substring[::-1]) + length
        else:
            distance = 0

        return (distance, length, next_sym)


if __name__ == '__main__':
    import sys

    FILE = sys.argv[1]

    encoder = LzEncoder(10000, 1000)
    encoder.compress('test_files/' + FILE)
