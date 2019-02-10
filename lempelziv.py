""" Digital Communication - Lempel-Ziv compression """

import os
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import numpy as np

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
        """
        Perform a running time analysis on the encoder and decoder, plot and
        save results.

        Params:
            input_dir: directory containing files to benchmark with
            rounds: number of times to run benchmark on each file to get average
                    times
        """

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


    def analyse_compression_ratio(self, filename):
        file_size = os.path.getsize(filename)

        upper_lim = round(float(file_size) / 1000) * 1000
        step = int(upper_lim / 10)

        window_sizes = buffer_sizes = [size for size in range(step, upper_lim + step, step)]

        benchmarks = self.benchmark_ratio(filename, window_sizes, buffer_sizes)

        x_values, y_values = np.meshgrid(window_sizes, buffer_sizes)
        z_values = []

        for ratios in benchmarks.values():
            row = []
            for ratio in ratios:
                row.append(ratio)
            z_values.append(row)



    def benchmark_time(self, filename, rounds):
        """
        Benchmark running time of compression and decompression on given file,
        obtaining the following data:

            Max. running time
            Min. running time
            Average running time

        Params:
            filename: name of file to compress/decompress
            rounds: number of times to repeat benchmark
        """

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


    def benchmark_ratio(self, filename, window_sizes, buffer_sizes):
        """
        Benchmark compression ratio on given file, using given window and
        lookahead buffer sizes.
        """

        uncompressed_size = os.path.getsize(filename)

        benchmarks = {}

        for w_size in window_sizes:
            self.encoder.set_window_size(w_size)
            self.decoder.set_window_size(w_size)

            benchmarks[w_size] = []

            for b_size in buffer_sizes:
                self.encoder.set_buffer_size(b_size)
                self.decoder.set_buffer_size(b_size)

                self.compress(filename)
                compressed_size = os.path.getsize(filename + '.LZIV')
                self.decompress(filename + '.LZIV')
                ratio = uncompressed_size / compressed_size
                benchmarks[w_size].append(ratio)

        return benchmarks



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
