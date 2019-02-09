""" Digital Communication - Lempel-Ziv compression """

import decoder
import encoder


class LempelZiv():
    """ Class implementing LZ77 coding """

    def __init__(self, window_size, buffer_size):
        self.window_size = window_size
        self.buffer_size = buffer_size
        self.encoder = encoder.LzEncoder(window_size, buffer_size)
        self.decoder = decoder.LzDecoder(window_size, buffer_size)


    def compress(self, filename):
        """ Compress data """
        self.encoder.compress(filename)


    def decompress(self, filename):
        """ Decompress data """
        self.decoder.decompress(filename)


if __name__ == '__main__':
    FILE = 'lorem.txt'
    W = 10000
    L = 1000

    lz = LempelZiv(W, L)

    lz.compress(f'test_files/{FILE}')
    lz.decompress(f'test_files/{FILE}.LZIV')

    assert len(lz.encoder.compression) == len(lz.decoder.decompression)

    # print(len(lz.decoder.decompression))

    # [print(f'{x}    {y}') for (x, y) in zip(lz.encoder.compression, lz.decoder.decompression)]
