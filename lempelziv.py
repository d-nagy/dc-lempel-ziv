""" Digital Communication - Lempel-Ziv compression """

import bz2
import gzip
import os
import shutil
import time
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

import decoder
import encoder


class LempelZiv():
    """ Class implementing LZ77 coding """

    def __init__(self, window_size, buffer_size):
        self.window_size = window_size
        self.buffer_size = buffer_size
        self.lz77_encoder = encoder.Lz77Encoder(window_size, buffer_size)
        self.lz77_decoder = decoder.Lz77Decoder(window_size, buffer_size)


    def get_time_complexity_results(self, files, rounds, alg=None):
        benchmarks = {filename: self.benchmark_time(filename, rounds, alg)
                      for filename in files}

        avg_encoding_times = {key: value[0]['avg']
                              for key, value in benchmarks.items()}

        avg_decoding_times = {key: value[1]['avg']
                              for key, value in benchmarks.items()}

        max_encoding_times = {key: value[0]['max']
                              for key, value in benchmarks.items()}

        max_decoding_times = {key: value[1]['max']
                              for key, value in benchmarks.items()}

        min_encoding_times = {key: value[0]['min']
                              for key, value in benchmarks.items()}

        min_decoding_times = {key: value[1]['min']
                              for key, value in benchmarks.items()}

        encoding_times = [avg_encoding_times, max_encoding_times, min_encoding_times]
        decoding_times = [avg_decoding_times, max_decoding_times, min_decoding_times]

        return encoding_times, decoding_times


    def plot_encoder_time_complexity(self, encoding_times, files, file_sizes, gzip_times, bzip2_times):
        labels = ['Average (LZ77)', 'Maximum (LZ77)', 'Minimum (LZ77)']

        colors = ['b', 'r', 'g']

        plot_title = f'Encoder running time (window size = {self.window_size} bytes, buffer size = {self.buffer_size} bytes)'
        plot_filename = 'plots/encoder_running_time.png'

        plt.cla()

        for times, label, color in zip(encoding_times, labels, colors):
            x_values = []
            encoding_y_values = []

            for filename in files:
                x_values.append(file_sizes[filename])
                encoding_y_values.append(times[filename])

            plt.plot(x_values, encoding_y_values, color + 'x-', label=label)

        if gzip_times or bzip2_times:
            plot_title = 'Encoding running time comparison'
            plot_filename = 'plots/compare_encoding_running_time.png'

        if gzip_times:
            x_values = []
            encoding_y_values = []

            for filename in files:
                x_values.append(file_sizes[filename])
                encoding_y_values.append(gzip_times[0][filename])

            plt.plot(x_values, encoding_y_values, 'yx-', label='Average (gzip)')

        if bzip2_times:
            x_values = []
            encoding_y_values = []

            for filename in files:
                x_values.append(file_sizes[filename])
                encoding_y_values.append(bzip2_times[0][filename])

            plt.plot(x_values, encoding_y_values, 'cx-', label='Average (bzip2)')

        plt.title(plot_title)
        plt.xlabel('File size (KB)')
        plt.ylabel('Running time (s)')
        plt.legend()
        plt.savefig(plot_filename)
        plt.cla()


    def plot_decoder_time_complexity(self, decoding_times, files, file_sizes, gzip_times, bzip2_times):
        labels = ['Average (LZ77)', 'Maximum (LZ77)', 'Minimum (LZ77)']

        colors = ['b', 'r', 'g']

        plot_title = f'Decoder running time (window size = {self.window_size} bytes, buffer size = {self.buffer_size} bytes)'
        plot_filename = 'plots/decoder_running_time.png'

        plt.cla()

        for times, label, color in zip(decoding_times, labels, colors):
            x_values = []
            decoding_y_values = []

            for filename in files:
                x_values.append(file_sizes[filename])
                decoding_y_values.append(times[filename])

            plt.plot(x_values, decoding_y_values, color + 'x-', label=label)

        if gzip_times or bzip2_times:
            plot_title = 'Decoding running time comparison'
            plot_filename = 'plots/compare_decoding_running_time.png'

        if gzip_times:
            x_values = []
            encoding_y_values = []

            for filename in files:
                x_values.append(file_sizes[filename])
                encoding_y_values.append(gzip_times[0][filename])

            plt.plot(x_values, encoding_y_values, 'yx-', label='Average (gzip)')

        if bzip2_times:
            x_values = []
            encoding_y_values = []

            for filename in files:
                x_values.append(file_sizes[filename])
                encoding_y_values.append(bzip2_times[0][filename])

            plt.plot(x_values, encoding_y_values, 'cx-', label='Average (bzip2)')

        plt.title(plot_title)
        plt.xlabel('File size (KB)')
        plt.ylabel('Running time (s)')
        plt.legend()
        plt.savefig(plot_filename)
        plt.cla()


    def analyse_time_complexity(self, input_dir, rounds, compare=False):
        """
        Perform a running time analysis on the encoder and decoder, plot and
        save results.

        Params:
            input_dir: directory containing files to benchmark with
            rounds: number of times to run benchmark on each file to get average
                    times
        """

        files = [f'{input_dir}/{filename}' for filename in os.listdir(input_dir)]
        files.sort(key=os.path.getsize)

        file_sizes = {filename: os.path.getsize(filename) / 1000
                      for filename in files}

        encoding_times, decoding_times = self.get_time_complexity_results(files, rounds)
        gzip_encoding_times = gzip_decoding_times = []
        bzip2_encoding_times = bzip2_decoding_times = []

        self.plot_encoder_time_complexity(encoding_times, files, file_sizes, gzip_encoding_times, bzip2_encoding_times)
        self.plot_decoder_time_complexity(decoding_times, files, file_sizes, gzip_decoding_times, bzip2_decoding_times)

        if compare:
            gzip_encoding_times, gzip_decoding_times = self.get_time_complexity_results(files, rounds, alg='gzip')
            bzip2_encoding_times, bzip2_decoding_times = self.get_time_complexity_results(files, rounds, alg='bzip2')

        self.plot_encoder_time_complexity(encoding_times, files, file_sizes, gzip_encoding_times, bzip2_encoding_times)
        self.plot_decoder_time_complexity(decoding_times, files, file_sizes, gzip_decoding_times, bzip2_decoding_times)


    def analyse_time_params(self, filename, rounds):
        window_sizes = self._calc_window_sizes(filename)
        # buffer_sizes = self._calc_buffer_sizes(filename)
        buffer_sizes = [50, 100, 200, 300, 600, 900, 1200]

        original_window_size = self.lz77_encoder.window_size
        original_buffer_size = self.lz77_encoder.buffer_size

        avg_encoding_times = []
        max_encoding_times = []
        min_encoding_times = []

        avg_decoding_times = []
        max_decoding_times = []
        min_decoding_times = []

        x_values = np.array(window_sizes) / 1000

        for w_size in window_sizes:
            self.lz77_encoder.set_window_size(w_size)
            self.lz77_decoder.set_window_size(w_size)

            encoding_benchmark, decoding_benchmark = self.benchmark_time(filename, rounds)

            avg_encoding_times.append(encoding_benchmark['avg'])
            min_encoding_times.append(encoding_benchmark['min'])
            max_encoding_times.append(encoding_benchmark['max'])

            avg_decoding_times.append(decoding_benchmark['avg'])
            min_decoding_times.append(decoding_benchmark['min'])
            max_decoding_times.append(decoding_benchmark['max'])

        plt.cla()

        plt.plot(x_values, avg_encoding_times, color='b', label='Average')
        plt.plot(x_values, max_encoding_times, color='r', label='Maximum')
        plt.plot(x_values, min_encoding_times, color='g', label='Minimum')

        plt.title(f'Encoder running time (buffer size = {self.lz77_encoder.buffer_size} bytes, input size = {os.path.getsize(filename)} bytes)')
        plt.xlabel('Window size (KB)')
        plt.ylabel('Running time (s)')
        plt.legend()
        plt.savefig('plots/encoder_time_window_sizes.png')
        plt.cla()

        plt.plot(x_values, avg_decoding_times, color='b', label='Average')
        plt.plot(x_values, max_decoding_times, color='r', label='Maximum')
        plt.plot(x_values, min_decoding_times, color='g', label='Minimum')

        plt.title(f'Decoder running time (buffer size = {self.lz77_encoder.buffer_size} bytes, input size = {os.path.getsize(filename)} bytes)')
        plt.xlabel('Window size (KB)')
        plt.ylabel('Running time (s)')
        plt.legend()
        plt.savefig('plots/decoder_time_window_sizes.png')
        plt.cla()

        self.lz77_encoder.set_window_size(original_window_size)
        self.lz77_decoder.set_window_size(original_window_size)

        avg_encoding_times = []
        max_encoding_times = []
        min_encoding_times = []

        avg_decoding_times = []
        max_decoding_times = []
        min_decoding_times = []

        x_values = np.array(buffer_sizes)

        for b_size in buffer_sizes:
            self.lz77_encoder.set_buffer_size(b_size)
            self.lz77_decoder.set_buffer_size(b_size)

            encoding_benchmark, decoding_benchmark = self.benchmark_time(filename, rounds)

            avg_encoding_times.append(encoding_benchmark['avg'])
            min_encoding_times.append(encoding_benchmark['min'])
            max_encoding_times.append(encoding_benchmark['max'])

            avg_decoding_times.append(decoding_benchmark['avg'])
            min_decoding_times.append(decoding_benchmark['min'])
            max_decoding_times.append(decoding_benchmark['max'])

        plt.cla()

        plt.plot(x_values, avg_encoding_times, color='b', label='Average')
        plt.plot(x_values, max_encoding_times, color='r', label='Maximum')
        plt.plot(x_values, min_encoding_times, color='g', label='Minimum')

        plt.title(f'Encoder running time (W = {self.lz77_encoder.window_size}, Input size = {os.path.getsize(filename)}B)')
        plt.xlabel('Lookahead buffer size (KB)')
        plt.ylabel('Running time (s)')
        plt.legend()
        plt.savefig('plots/encoder_time_buffer_sizes.png')
        plt.cla()

        plt.plot(x_values, avg_decoding_times, color='b', label='Average')
        plt.plot(x_values, max_decoding_times, color='r', label='Maximum')
        plt.plot(x_values, min_decoding_times, color='g', label='Minimum')

        plt.title(f'Decoder running time (window size = {self.lz77_encoder.window_size} bytes, input size = {os.path.getsize(filename)} bytes)')
        plt.xlabel('Buffer size (B)')
        plt.ylabel('Running time (s)')
        plt.legend()
        plt.savefig('plots/decoder_time_buffer_sizes.png')

        self.lz77_encoder.set_buffer_size(original_buffer_size)
        self.lz77_decoder.set_buffer_size(original_buffer_size)


    def analyse_compression_ratio(self, filename):
        """
        Perform a compression ratio analysis on the encoder with varying window
        and lookahead buffer sizes, plot and save results.

        Params:
            filename: file to perform benchmark on
        """

        window_sizes = self._calc_window_sizes(filename)
        # buffer_sizes = self._calc_buffer_sizes(filename)
        buffer_sizes = [50, 100, 200, 300, 600, 900, 1200]

        benchmarks = self.benchmark_ratio(filename, window_sizes, buffer_sizes)

        x_values, y_values = np.meshgrid(np.array(window_sizes) / 1000,
                                         np.array(buffer_sizes))
        z_values = np.array(benchmarks).transpose()

        plt.cla()

        fig = plt.figure()
        axes = fig.gca(projection='3d')

        surf = axes.plot_surface(x_values, y_values, z_values, cmap=cm.coolwarm,
                                 linewidth=0)

        axes.zaxis.set_major_locator(LinearLocator(10))
        axes.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
        axes.set_title(f'Compression Ratio (input = {os.path.getsize(filename)} bytes)')
        axes.set_xlabel('Window size (KB)')
        axes.set_ylabel('Lookahead buffer size (B)')
        axes.set_zlabel('Compression ratio')

        fig.colorbar(surf, shrink=0.5, aspect=5)

        axes.view_init(30, 50)

        plt.savefig('plots/compression_ratio.png')

        axes.clear()


    def analyse_file_types(self, compare=False):
        original_window_size = self.lz77_encoder.window_size

        main_dir = 'file_types'

        x_values = []
        ratios = []
        gzip_ratios = []
        bzip2_ratios = []
        mpl_colors = ['lightsalmon', 'red', 'darkred', 'pink', 'deeppink', 'orange',
                      'gold', 'lemonchiffon', 'darkkhaki', 'plum', 'magenta',
                      'mediumpurple', 'purple', 'indigo', 'lime', 'seagreen',
                      'aqua', 'black']
        colors = []

        i = 0
        for ext in os.listdir(main_dir):
            files = [f'{main_dir}/{ext}/{filename}'
                     for filename in os.listdir(f'{main_dir}/{ext}')]
            files.sort(key=os.path.getsize)

            for filename in files:
                uncompressed_size = os.path.getsize(filename)
                window_size = min(150 * (uncompressed_size // 1000), 15000)

                x_values.append(f'{round(uncompressed_size / 1000, 1)} KB {ext}')
                colors.append(mpl_colors[i % len(mpl_colors)])

                print(f'{filename}: window size = {window_size}')

                self.lz77_encoder.set_window_size(window_size)
                self.lz77_decoder.set_window_size(window_size)

                self.compress_lz77(filename)

                compressed_size = os.path.getsize(filename + self.lz77_encoder.file_ext)
                ratio = uncompressed_size / compressed_size
                print('Ratio: ', round(ratio, 2))

                self.decompress_lz77(filename + self.lz77_encoder.file_ext)

                ratios.append(ratio)

                if compare:
                    self.compress_gzip(filename)

                    compressed_size = os.path.getsize(filename + '.gz')
                    ratio = uncompressed_size / compressed_size
                    print('Ratio (gzip): ', round(ratio, 2))

                    self.decompress_gzip(filename + '.gz')

                    gzip_ratios.append(ratio)

                    self.compress_bzip2(filename)

                    compressed_size = os.path.getsize(filename + '.bz2')
                    ratio = uncompressed_size / compressed_size
                    print('Ratio (bzip2): ', round(ratio, 2))

                    self.decompress_bzip2(filename + '.bz2')

                    bzip2_ratios.append(ratio)

            i += 1

        self.lz77_encoder.set_window_size(original_window_size)
        self.lz77_decoder.set_window_size(original_window_size)

        x_pos = [i for i in range(len(x_values))]

        plt.cla()
        fig = plt.figure(figsize=(12, 7))
        fig.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.bar(x_pos, ratios, color=colors)
        plt.xlabel('File')
        plt.ylabel('Compression ratio')
        plt.title('Compression ratio for various file types')
        plt.xticks(x_pos, x_values, rotation=90, fontsize='small')
        plt.savefig('plots/file_types.png')
        plt.cla()

        if compare:
            plt.bar(x_pos, ratios, 0.3, color='b', label='LZ77')
            plt.bar(np.array(x_pos) + 0.3, gzip_ratios, 0.3, color='r', label='gzip')
            plt.bar(np.array(x_pos) + 0.6, bzip2_ratios, 0.3, color='g', label='bzip2')
            plt.xlabel('File')
            plt.ylabel('Compression ratio')
            plt.title('Compression ratio for various file types by compression algorithm')
            plt.xticks(np.array(x_pos) + 0.45, x_values, rotation=90, fontsize='small')
            plt.legend(loc='best')
            plt.savefig('plots/ratio_comparison.png')


    def benchmark_time(self, filename, rounds, alg=None):
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

        if not alg:
            print(f'W = {self.lz77_encoder.window_size}, L = {self.lz77_encoder.buffer_size}')
            _compress = self.compress_lz77
            _decompress = self.decompress_lz77
            ext = self.lz77_encoder.file_ext
        elif alg == 'gzip':
            print('GZIP')
            _compress = self.compress_gzip
            _decompress = self.decompress_gzip
            ext = '.gz'
        elif alg == 'bzip2':
            print('BZIP2')
            _compress = self.compress_bzip2
            _decompress = self.decompress_bzip2
            ext = '.bz2'

        encoding_times = []
        decoding_times = []

        print(os.path.getsize(filename))

        for _ in range(rounds):
            encode_start = time.time()
            _compress(filename)
            encode_stop = time.time()
            encoding_times.append(encode_stop - encode_start)

            decode_start = time.time()
            _decompress(filename + ext)
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

        original_window_size = self.lz77_encoder.window_size
        original_buffer_size = self.lz77_encoder.buffer_size

        uncompressed_size = os.path.getsize(filename)

        benchmarks = []

        for w_size in window_sizes:
            self.lz77_encoder.set_window_size(w_size)
            self.lz77_decoder.set_window_size(w_size)

            row = []

            for b_size in buffer_sizes:
                self.lz77_encoder.set_buffer_size(b_size)
                self.lz77_decoder.set_buffer_size(b_size)

                self.compress_lz77(filename)
                compressed_size = os.path.getsize(filename + self.lz77_encoder.file_ext)
                self.decompress_lz77(filename + self.lz77_encoder.file_ext)
                ratio = uncompressed_size / compressed_size
                print(w_size, b_size, uncompressed_size, compressed_size, ratio)

                row.append(ratio)

            benchmarks.append(row)

        self.lz77_encoder.set_window_size(original_window_size)
        self.lz77_decoder.set_window_size(original_window_size)
        self.lz77_encoder.set_buffer_size(original_buffer_size)
        self.lz77_decoder.set_buffer_size(original_buffer_size)

        return benchmarks


    def compress_lz77(self, filename):
        """ Compress data using LZ77 """
        self.lz77_encoder.compress(filename)


    def decompress_lz77(self, filename):
        """ Decompress data using LZ77 """
        self.lz77_decoder.decompress(filename)


    def compress_gzip(self, filename):
        """ Compress data with gzip """
        with open(filename, 'rb') as input_file:
            with gzip.open(filename + '.gz', 'wb') as output_file:
                shutil.copyfileobj(input_file, output_file)


    def decompress_gzip(self, filename):
        """ Decompress data with gzip """
        with gzip.open(filename, 'rb') as input_file:
            with open(filename.replace('.gz', ''), 'wb') as output_file:
                shutil.copyfileobj(input_file, output_file)

        os.remove(filename)


    def compress_bzip2(self, filename):
        """ Compress data with bzip2 """
        with open(filename, 'rb') as input_file:
            data = input_file.read()
            compressed = bz2.compress(data)
            with open(filename + '.bz2', 'wb') as output_file:
                output_file.write(compressed)


    def decompress_bzip2(self, filename):
        """ Decompress data with bzip2 """
        with open(filename, 'rb') as input_file:
            data = input_file.read()
            decompressed = bz2.decompress(data)
            with open(filename.replace('.bz2', ''), 'wb') as output_file:
                output_file.write(decompressed)

        os.remove(filename)


    @staticmethod
    def _calc_window_sizes(filename):
        file_size = os.path.getsize(filename)

        upper_lim = round(float(file_size) / 1000) * 1000
        step = int(upper_lim / 10)

        return [size for size in range(step, upper_lim + step, step)]


    @staticmethod
    def _calc_buffer_sizes(filename):
        file_size = os.path.getsize(filename)

        upper_lim = round(float(file_size / 10) / 1000) * 1000
        step = int(upper_lim / 10)

        return [size for size in range(step, upper_lim + step, step)]


if __name__ == '__main__':
    INPUT_DIR = 'lorem'
    FILE = 'misc/alice29.txt'
    W = 10000
    L = 100

    lz = LempelZiv(W, L)

    lz.analyse_time_complexity(INPUT_DIR, 10, compare=True)
    lz.analyse_time_params('misc/alice29.txt', 10)
    lz.analyse_file_types(compare=True)
    lz.analyse_compression_ratio(FILE)