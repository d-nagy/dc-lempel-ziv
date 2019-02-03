""" Digital Communication - Lempel-Ziv compression """


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
    index = 0
    n = len(message)
    W = L = n

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
        print((d, l, next_sym))

        index += l + 1

# Test case from lecture slides
compress('ABRACADABRA')
