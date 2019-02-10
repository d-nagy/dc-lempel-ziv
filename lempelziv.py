""" Digital Communication - Lempel-Ziv compression """

import os
import time
import numpy as np
import matplotlib.pyplot as plt

import decoder
import encoder


class LempelZiv():
    """ Class implementing LZ77 coding """

    def __init__(self, window_size, buffer_size):
        self.window_size = window_size
        self.buffer_size = buffer_size
        self.encoder = encoder.LzEncoder(window_size, buffer_size)
        self.decoder = decoder.LzDecoder(window_size, buffer_size)


    def analyse_time_complexity(self, input_dir, rounds):
        files = [f'{input_dir}/{filename}' for filename in os.listdir(input_dir)]

        file_sizes = {filename: os.path.getsize(filename) / 1000
                      for filename in files}

        benchmarks = {filename: self.benchmark_time(filename, rounds)
                      for filename in files}

        avg_encoding_times = {key: value[0]['avg']
                              for key, value in benchmarks.items()}

        avg_decoding_times = {key: value[1]['avg']
                              for key, value in benchmarks.items()}

        x_values = []
        encoding_y_values = []
        decoding_y_values = []

        for filename in files:
            x_values.append(file_sizes[filename])
            encoding_y_values.append(avg_encoding_times[filename])
            decoding_y_values.append(avg_decoding_times[filename])

        plt.plot(x_values, encoding_y_values, 'o')
        plt.title('Encoder running time')
        plt.xlabel('File size (KB)')
        plt.ylabel('Average running time (s)')
        plt.savefig('plots/encoder_running_time.png')
        plt.cla()

        plt.plot(x_values, decoding_y_values, 'o')
        plt.title('Decoder running time')
        plt.xlabel('File size (KB)')
        plt.ylabel('Average running time (s)')
        plt.savefig('plots/decoder_running_time.png')


    def benchmark_time(self, filename, rounds):
        print(f'{filename}: {rounds} rounds')

        encoding_times = []
        decoding_times = []

        for _ in range(rounds):
            encode_start = time.time()
            self.compress(filename)
            encode_stop = time.time()
            encoding_times.append(encode_stop - encode_start)

            decode_start = time.time()
            self.decompress(filename + '.LZIV')
            decode_stop = time.time()
            decoding_times.append(decode_stop - decode_start)

        encoding_benchmark = {'max': max(encoding_times),
                              'min': min(encoding_times),
                              'avg': sum(encoding_times)/rounds}

        decoding_benchmark = {'max': max(decoding_times),
                              'min': min(decoding_times),
                              'avg': sum(decoding_times)/rounds}

        print(f'\tAverage encoding time: {encoding_benchmark["avg"]}')
        print(f'\tAverage decoding time: {decoding_benchmark["avg"]}')
        print()

        return (encoding_benchmark, decoding_benchmark)


    def compress(self, filename):
        """ Compress data """
        self.encoder.compress(filename)


    def decompress(self, filename):
        """ Decompress data """
        self.decoder.decompress(filename)


if __name__ == '__main__':
    INPUT_DIR = 'lorem'
    W = 10000
    L = 250

    lz = LempelZiv(W, L)

    lz.analyse_time_complexity(INPUT_DIR, 1)

    # print(len(lz.decoder.decompression))

    # [print(f'{x}    {y}') for (x, y) in zip(lz.encoder.compression, lz.decoder.decompression)]
