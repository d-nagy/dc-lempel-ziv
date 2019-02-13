""" Digital Communication - Lempel-Ziv Decoder """

import os
from bitarray import bitarray


class Lz77Decoder():
    """ LZ77 Decoder """

    def __init__(self, window_size, buffer_size):
        self.window_size = window_size
        self.buffer_size = buffer_size
        self.distance_bits = (window_size - 1).bit_length()
        self.length_bits = (buffer_size - 1).bit_length()
        self.step = self.distance_bits + self.length_bits + 8
        self.decompression = []
        self.file_ext = '.LZ77'

    def set_window_size(self, window_size):
        """ Setter method for window size """
        self.window_size = window_size
        self.distance_bits = (window_size - 1).bit_length()
        self.step = self.distance_bits + self.length_bits + 8


    def set_buffer_size(self, buffer_size):
        """ Setter method for buffer size """
        self.buffer_size = buffer_size
        self.length_bits = (buffer_size - 1).bit_length()
        self.step = self.distance_bits + self.length_bits + 8


    def decompress(self, filename):
        """
        Decompress a file that was compressed using LZ77 coding.

        Params:
            filename: name of file to decompress
        """

        self.decompression = []

        message = b''
        index = 0

        with open(filename, 'rb') as input_file:
            while True:
                chunk = bitarray()

                try:
                    chunk.fromfile(input_file, self.step)
                except EOFError:
                    chunk.fromfile(input_file)

                code_len = chunk.length()

                if code_len == 0:
                    break

                for c_index in range(0, code_len, self.step):
                    code_bin = chunk[c_index:c_index + self.step]

                    if code_bin.length() < self.step - 8:
                        break

                    distance, length, next_sym = self._parse_bin_code(code_bin)

                    self.decompression.append((distance, length, next_sym))

                    substring = message[index - distance:index - distance + length] + next_sym
                    message += substring

                    index += length + 1

        with open(filename.replace(self.file_ext, ''), 'wb') as output_file:
            output_file.write(message)

        os.remove(filename)


    def _parse_bin_code(self, code_bin):
        length_index = self.distance_bits + self.length_bits

        distance_bin = code_bin[:self.distance_bits]
        length_bin = code_bin[self.distance_bits:length_index]
        next_sym_bin = code_bin[length_index:length_index + 8]

        distance = self._bitarray_to_int(distance_bin)
        length = self._bitarray_to_int(length_bin)

        if next_sym_bin.length() < 8:
            next_sym = b''
        else:
            next_sym = next_sym_bin.tobytes()

        return distance, length, next_sym


    @staticmethod
    def _bitarray_to_int(bits):
        return int('0b' + bits.to01(), 2)


class LzssDecoder(Lz77Decoder):
    """ LZSS Decoder """

    def __init__(self, window_size, buffer_size):
        super().__init__(window_size, buffer_size)
        self.file_ext = '.LZSS'


    def decompress(self, filename):
        """
        Decompress a file that was compressed using LZ77 coding.

        Params:
            filename: name of file to decompress
        """

        self.decompression = []

        message = b''
        index = 0

        compressed = bitarray()

        with open(filename, 'rb') as input_file:
            compressed.fromfile(input_file)

            while True:
                code_bin = compressed[:self.step + 1]

                if code_bin.length() < 8:
                    break

                if not code_bin.pop(0):
                    next_sym = code_bin[:8].tobytes()
                    distance = length = 0
                    substring = b''
                    del compressed[:9]
                else:
                    if code_bin.length() < self.step - 8:
                        break
                    distance, length, next_sym = self._parse_bin_code(code_bin)
                    substring = message[index - distance:index - distance + length]
                    del compressed[:self.step + 1]

                self.decompression.append((distance, length, next_sym))

                message += substring + next_sym

                index += length + 1

        with open(filename.replace(self.file_ext, ''), 'wb') as output_file:
            output_file.write(message)

        os.remove(filename)


if __name__ == '__main__':
    import sys

    FILE = sys.argv[1]
    W = int(sys.argv[2])
    L = int(sys.argv[3])

    # decoder = Lz77Decoder(W, L)
    # decoder.decompress(f'{FILE}.LZ77')

    decoder = LzssDecoder(W, L)
    decoder.decompress(f'{FILE}.LZSS')
    # [print(code) for code in decoder.decompression]
