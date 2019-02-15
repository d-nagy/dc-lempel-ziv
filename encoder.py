""" Digital Communication - Lempel-Ziv Encoder """

import os
from bitarray import bitarray


class Lz77Encoder():
    """ LZ77 Encoder """

    def __init__(self, window_size, buffer_size):
        self.window_size = window_size
        self.buffer_size = buffer_size
        self.distance_bits = window_size.bit_length()
        self.length_bits = buffer_size.bit_length()
        self.compression = []
        self.file_ext = '.LZ77'


    def set_window_size(self, window_size):
        """ Setter method for window size """
        self.window_size = window_size
        self.distance_bits = (window_size - 1).bit_length()


    def set_buffer_size(self, buffer_size):
        """ Setter method for buffer size """
        self.buffer_size = buffer_size
        self.length_bits = (buffer_size - 1).bit_length()


    def compress(self, filename):
        """
        Compress a file using LZ77 coding.

        Params:
            filename: name of file to compress
        """

        self.compression = []

        with open(filename + self.file_ext, 'x') as output:
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

                distance, length, next_sym = self.encode_at_pos(window, buffer)
                code = self.code_to_bits(distance, length, next_sym)
                code_to_write += code

                self.compression.append((distance, length, next_sym))

                next_bytes = bitarray()
                try:
                    next_bytes.fromfile(input_file, length + 1)
                except EOFError:
                    pass

                window += buffer[:(length + 1) * 8]

                if window.length() > self.window_size * 8:
                    del window[:window.length() - self.window_size * 8]

                del buffer[:(length + 1) * 8]
                buffer += next_bytes

        with open(filename + self.file_ext, 'ab') as output:
            output.write(code_to_write.tobytes())

        os.remove(filename)


    def code_to_bits(self, distance, length, next_sym):
        """
        Encode a distance-length pair and the next character from the
        LZ77 algorithm as binary.

        Params:
            distance: how many bytes backwards the match was found
            length: the length of the found match
            next_sym: the character following the matched substring

        Returns:
            Bitarray encoding the LZ77 code.
        """

        distance_bin = bin(distance)[2:].rjust(self.distance_bits, '0')
        length_bin = bin(length)[2:].rjust(self.length_bits, '0')

        next_sym_bin = bitarray()
        next_sym_bin.frombytes(next_sym)

        code = bitarray(distance_bin + length_bin) + next_sym_bin

        return code


    @staticmethod
    def encode_at_pos(window, buffer):
        """
        Perform LZ77 coding at the current position in the input message,
        characterized by the given sliding window and lookahead buffer.

        Params:
            window: the sliding window
            buffer: the lookahead buffer

        Returns:
            A triple (distance, length, next_sym) where "distance" is the number
            of bytes backwards in the message that a match was found for the
            first "length" number of characters in the lookahead buffer, and
            "next_sym" is the next character in the lookahead buffer after the
            matched substring.
        """

        window_bytes = window.tobytes()
        buffer_bytes = buffer.tobytes()
        buffer_len = len(buffer_bytes)

        length = 0
        substring = b''
        next_sym = buffer_bytes[length:length + 1]

        while substring + next_sym in window_bytes:
            substring += next_sym
            length += 1
            next_sym = buffer_bytes[length:length + 1]
            if length == buffer_len - 1 or buffer_len <= 1:
                break

        if length > 0:
            distance = window_bytes[::-1].index(substring[::-1]) + length
        else:
            distance = 0

        return (distance, length, next_sym)


class LzssEncoder(Lz77Encoder):
    """ LZSS Encoder """

    def __init__(self, window_size, buffer_size):
        super().__init__(window_size, buffer_size)
        self.file_ext = '.LZSS'


    def compress(self, filename):
        """
        Compress a file using LZSS coding.

        Params:
            filename: name of file to compress
        """

        self.compression = []

        with open(filename + self.file_ext, 'x') as output:
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

                distance, length, next_sym = self.encode_at_pos(window, buffer)
                code = self.code_to_bits(distance, length, next_sym)
                code_to_write += code

                self.compression.append((distance, length, next_sym))

                if not code_to_write.length() % 8:
                    with open(filename + self.file_ext, 'ab') as output:
                        output.write(code_to_write.tobytes())
                    code_to_write = bitarray()

                next_bytes = bitarray()
                try:
                    next_bytes.fromfile(input_file, length + 1)
                except EOFError:
                    pass

                window += buffer[:(length + 1) * 8]

                if window.length() > self.window_size * 8:
                    del window[:window.length() - self.window_size * 8]

                buffer = buffer[(length + 1) * 8:] + next_bytes

        with open(filename + self.file_ext, 'ab') as output:
            output.write(code_to_write.tobytes())

        os.remove(filename)


    def code_to_bits(self, distance, length, next_sym):
        next_sym_bin = bitarray()
        next_sym_bin.frombytes(next_sym)

        if distance == 0 and length == 0:
            code = bitarray('0') + next_sym_bin
        else:
            distance_bin = bin(distance)[2:].rjust(self.distance_bits, '0')
            length_bin = bin(length)[2:].rjust(self.length_bits, '0')

            code = bitarray('1' + distance_bin + length_bin) + next_sym_bin

        return code


if __name__ == '__main__':
    import sys
    import time

    # FILE = sys.argv[1]
    FILE = 'misc/alice29.txt'
    # W = int(sys.argv[2])
    # L = int(sys.argv[3])

    encoder = Lz77Encoder(10000, 600)
    # encoder = LzssEncoder(W, L)

    uncompressed_size = os.path.getsize(FILE)

    start = time.time()
    encoder.compress(FILE)
    end = time.time()

    runtime = end - start

    compressed_size = os.path.getsize(FILE + encoder.file_ext)
    ratio = uncompressed_size / compressed_size

    print('-----------------------------------------')
    print('LZ77 Encoder')
    print('-----------------------------------------')
    print(f'Sliding window size = {10000} bytes')
    print(f'Lookahead buffer size = {600} bytes')
    print('-----------------------------------------')
    print(f'File:              {FILE}')
    print(f'Original size:     {uncompressed_size} bytes')
    print(f'Compressed size:   {compressed_size} bytes')
    print(f'Compression ratio: {round(ratio, 2)}')
    print(f'Running time:      {round(runtime, 2)} seconds')
    print('-----------------------------------------')


    print(max(encoder.compression, key=lambda x: x[1]))
