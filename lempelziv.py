""" Digital Communication - Lempel-Ziv compression """

import bitarray

class LempelZiv():
    """ Class implementing LZ77 coding """

    def __init__(self, window_size, lookahead_buffer_size):
        self.window_size = window_size
        self.lookahead_buffer_size = lookahead_buffer_size

    def compress(self, data):
        """ Compress data """
        pass

    def decompress(self, data):
        """ Decompress data """
        pass


# Function just for getting the algorithm right, will move to class once done
def compress(message):
    result = bitarray.bitarray()

    index = 0
    n = len(message)
    W = L = n

    d_len = (W - 1).bit_length()
    l_len = (L - 1).bit_length()

    while index < n:
        window = message[max(index - W, 0):index]
        buffer = message[index:index + L]

        l = 0
        substring = ''
        next_sym = buffer[l]
        while substring + next_sym in window:
            substring += next_sym
            l += 1
            if index + l == n:
                next_sym = None
                break
            next_sym = buffer[l]

        d = window[::-1].index(substring[::-1]) + l if l > 0 else 0

        # Just print the encoding info
        # print((d, l, next_sym))

        bin_d = bin(d)[2:]
        bin_l = bin(l)[2:]

        result += '0' * (d_len - len(bin_d)) + bin_d
        result += '0' * (l_len - len(bin_l)) + bin_l

        bin_next_sym = bitarray.bitarray()

        if next_sym:
            bin_next_sym.fromstring(next_sym)
            result += bin_next_sym
        else:
            result += '11111111'

        index += l + 1

    return result


if __name__ == '__main__':
    # Test case from lecture slides
    test = "Peter Piper picked a peck of pickled peppers; A peck of pickled peppers Peter Piper picked;If Peter Piper picked a peck of pickled peppers,Where's the peck of pickled peppers Peter Piper picked?"

    uncompressed = bitarray.bitarray()
    uncompressed.fromstring(test)

    compressed = compress(test)

    print(f'Uncompressed length: {uncompressed.length()}')
    print(f'Compressed length:   {compressed.length()}')
