#!/usr/bin/env python
"""
    Usage example.
    Edit parameters to suit your need and run!
"""

import os
import csv
import matplotlib.pyplot as plt

from process_performance.parameters import Parameters
from process_performance.runner import InvokeContextInterface, run
from process_performance.shape import ParameterSpaceShape


# pylint: disable=too-many-instance-attributes
class InvokeContext(InvokeContextInterface):
    '''
        A class responsible for preparing, formatting command,
        cleaning up and data collection for subprocess.
    '''
    file_path: str
    file_size_raw: int
    file_size_compressed: int
    exit_code: int
    arg_string: str
    user_time: float
    system_time: float
    extreme: bool

    def pre(self, workdir) -> None:
        '''
            Called right before process spawns,
            receives directory process will start in
        '''
        filename = 'example.file'
        filepath = os.path.join(workdir, filename)
        with open(filepath, 'wb') as example_file:
            with open(__file__, 'rb') as _self_file:
                _self_file_data = _self_file.read()
                for _ in range(10):
                    for chunk_length in range(len(_self_file_data)):
                        example_file.write(
                            _self_file_data[-chunk_length:chunk_length])

        self.file_path = os.path.abspath(filepath)
        self.file_size_raw = os.stat(self.file_path).st_size

    def post(self) -> None:
        '''
            Called right after process exits.
            working directory is erased after this call
        '''
        self.file_size_compressed = os.stat(self.file_path + '.xz').st_size

    def success(self, result) -> None:
        '''
            Called once subprocess exited,
            receives result object containing return code, stdout and stderr
        '''
        self.exit_code = result.exit_code
        self.user_time = result.time_user
        self.system_time = result.time_system

    def error(self, exception) -> None:
        '''
            Called on process spawning error,
            receives exception that ocurred during process spawning
        '''
        print(exception)

    def argv(self, args) -> list:
        '''
            Receives dictionary of { parameter_name : parameter_value }
            must return list of command line args to run as subprocess
        '''
        self.extreme = args['extreme'] != ''
        arg_list = [arg for arg in args.values() if arg != '']
        self.arg_string = ' '.join(arg_list)
        return ['xz.exe',
                '--compress',  # force compression
                '--keep',  # keep source files
                ] + arg_list + [self.file_path]

    def data(self) -> dict:
        return {
            'exit': self.exit_code,
            'usertime': f'{self.user_time:.3f}',
            'systemtime': f'{self.system_time:.3f}',
            'extreme': self.extreme,
            'ratio':
                f'{float(self.file_size_raw) / self.file_size_compressed:.1f}',
            'args': self.arg_string,
            'size_raw': self.file_size_raw,
            'size_compressed': self.file_size_compressed,
        }


def main():
    # define possible parameter values
    param_space = Parameters.from_dict({
        'preset': [f'-{x}' for x in range(0, 10)],
        'extreme': ['', '-e'],
    })

    # run process with all possible parameters
    data = run(
        processes=1,
        context_class=InvokeContext,
        parameters_space=param_space,
        shape=ParameterSpaceShape.CUBE
    )

    # write data to csv for later analysis
    headers = [
        'exit',
        'size_raw', 'size_compressed',
        'usertime', 'systemtime',
        'ratio', 'extreme',
        'args']
    with open('example_xz.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    plt.grid(visible=True)
    for extreme in [False, True]:
        plot_data = []
        for datapoint in data:
            if datapoint['extreme'] == extreme:
                plot_data.append(datapoint)
        plt.plot(
            [(d['usertime'] + d['systemtime']) for d in plot_data],
            [d['ratio'] for d in plot_data],
            'o')
    plt.xlabel('Time (sec, lower is better)')
    plt.ylabel('Compression ratio (bigger is better)')
    plt.title('XZ compression ratio')
    plt.show()


if __name__ == '__main__':
    main()
