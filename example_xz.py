#!/usr/bin/env python
"""
    Usage example.
    Edit parameters to suit your need and run!
"""

import os
import shutil
import time
import csv
import matplotlib.pyplot as plt
import random

from process_performance.parameters import Parameters
from process_performance.runner import InvokeContextInterface, run
from process_performance.shape import ParameterSpaceShape


class InvokeContext(InvokeContextInterface):
    '''
        A class responsible for preparing, formatting command,
        cleaning up and data collection for subprocess.
    '''
    workdir: str
    file_path: str
    file_size_raw: int
    file_size_compressed: int
    time_start: float
    time_stop: float
    exit_code: int
    arg_string: str

    def pre(self, workdir) -> None:
        '''
            Called right before process spawns,
            receives directory process will start in
        '''
        self.workdir = workdir

        filename = 'example.file'
        filepath = os.path.join(workdir, filename)
        with open(filepath, 'wb') as f:
            for n in range(200):
                f.write(random.randbytes(n)*n)

        self.file_path = os.path.abspath(filepath)
        self.file_size_raw = os.stat(self.file_path).st_size
        self.time_start = time.time()


    def post(self) -> None:
        '''
            Called right after process exits.
            working directory is erased after this call
        '''
        self.time_stop = time.time()
        self.file_size_compressed = os.stat(self.file_path + '.xz').st_size


    def success(self, result) -> None:
        '''
            Called once subprocess exited,
            receives result object containing return code, stdout and stderr
        '''
        self.exit_code = result.returncode


    def error(self, exception) -> None:
        '''
            Called on process spawning error,
            receives exception that ocurred during process spawning
        '''
        print(exception)


    def argv(self, args) -> list:
        '''
            Receives dictionary of { parameter_name : parameter_value }
            Must return list of formatted command line args to run as subprocess
        '''
        args = [arg for arg in args.values() if arg != '']
        self.arg_string = ' '.join(args)
        return ['xz.exe',
                '--compress',  # force compression
                '--keep',  # keep source files
                ] + args + [self.file_path]

    def data(self) -> dict:
        return {
            'exit': self.exit_code,
            'dt': self.time_stop - self.time_start,
            'ratio': float(self.file_size_raw) / self.file_size_compressed,
            'args': self.arg_string,
            'size_raw': self.file_size_raw,
            'size_compressed': self.file_size_compressed,
        }


def main():
    # define possible parameter values
    param_space = Parameters.from_dict({
        'preset': [f'-{x}' for x in range(0, 10)],
        'extreme': ['', '-e'],
        'threads': [f'--threads={x}' for x in range(1, 5)],
    })

    # run process with all possible parameters
    data = run(
        processes=1,
        context_class=InvokeContext,
        parameters_space=param_space,
        shape=ParameterSpaceShape.CUBE
    )

    # write data to csv for later analysis
    headers = ['exit', 'size_raw', 'size_compressed', 'dt', 'ratio', 'args']
    with open('example_xz.csv', 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    # plot dt/ratio graph
    plt.plot(
        [d['dt'] for d in data],
        [d['ratio'] for d in data],
        'o')
    plt.xlabel('Time (sec)')
    plt.ylabel('Compression ratio')
    plt.title('XZ compression ratio')
    plt.show()


if __name__ == '__main__':
    main()
