#!/usr/bin/env python

import os
import sys
from process_performance.parameters import Parameters
from process_performance.runner import \
    InvokeContextInterface, _spawn_process, run
from process_performance.shape import ParameterSpaceShape


class InvokeContextDataCollector(InvokeContextInterface):
    calls_pre: int = 0
    calls_post: int = 0
    calls_success: int = 0
    calls_error: int = 0
    calls_argv: int = 0
    calls_data: int = 0
    exception = None

    def pre(self, workdir) -> None:
        for i in range(1000):
            filename = os.path.join(workdir, f'{i}-' + 'test_file_' * 10)
            with open(filename, 'wb') as file:
                file.write(b'123')
        self.calls_pre += 1

    def post(self) -> None:
        self.calls_post += 1

    def success(self, result) -> None:
        self.calls_success += 1

    def error(self, exception) -> None:
        self.exception = exception
        self.calls_error += 1

    def argv(self, args) -> list:
        self.calls_argv += 1
        if sys.platform == 'win32':
            return ['cmd.exe', '/c', '&&'.join(['dir'] * 10)]
        return ['bash', '-c', '&&'.join(['ls'] * 10)]

    def data(self) -> dict:
        self.calls_data += 1
        return {
            'exception': self.exception,
            'calls_pre': self.calls_pre,
            'calls_post': self.calls_post,
            'calls_success': self.calls_success,
            'calls_error': self.calls_error,
            'calls_argv': self.calls_argv,
            'calls_data': self.calls_data,
        }


def test_spawn_process():
    context = InvokeContextDataCollector()
    result = _spawn_process(context, {'p1': [1]})
    print(result.stdout)
    assert result.exit_code == 0
    assert result.stdout.count(b'test_file') == 100000
    assert result.stderr == b''
    assert result.time_system > 0
    assert result.time_user > 0
    # must be called by spawner
    assert context.calls_argv == 1
    assert context.calls_pre == 1
    assert context.calls_post == 1
    # called by run, not by spawner
    assert context.calls_data == 0
    assert context.calls_error == 0
    assert context.calls_success == 0


class InvokeContextSuccess(InvokeContextInterface):
    calls_pre: int = 0
    calls_post: int = 0
    calls_success: int = 0
    calls_error: int = 0
    calls_argv: int = 0
    calls_data: int = 0
    exception = None

    def pre(self, workdir) -> None:
        self.calls_pre += 1

    def post(self) -> None:
        self.calls_post += 1

    def success(self, result) -> None:
        self.calls_success += 1

    def error(self, exception) -> None:
        self.exception = exception
        self.calls_error += 1

    def argv(self, args) -> list:
        self.calls_argv += 1
        if sys.platform == 'win32':
            return ['cmd.exe', '/c', 'echo Hello World']
        return ['bash', '-c', 'echo Hello World']

    def data(self) -> dict:
        self.calls_data += 1
        return {
            'exception': self.exception,
            'calls_pre': self.calls_pre,
            'calls_post': self.calls_post,
            'calls_success': self.calls_success,
            'calls_error': self.calls_error,
            'calls_argv': self.calls_argv,
            'calls_data': self.calls_data,
        }


def test_run_success():
    param_space = Parameters.from_dict({
        'p1': [1],
    })

    data = run(
        processes=1,
        context_class=InvokeContextSuccess,
        parameters_space=param_space,
        shape=ParameterSpaceShape.CUBE
    )

    assert data[0]['exception'] is None
    assert data[0]['calls_error'] == 0
    assert data[0]['calls_pre'] == 1
    assert data[0]['calls_post'] == 1
    assert data[0]['calls_success'] == 1
    assert data[0]['calls_argv'] == 1
    assert data[0]['calls_data'] == 1


class InvokeContextError(InvokeContextInterface):
    calls_pre: int = 0
    calls_post: int = 0
    calls_success: int = 0
    calls_error: int = 0
    calls_argv: int = 0
    calls_data: int = 0
    exception = None

    def pre(self, workdir) -> None:
        self.calls_pre += 1

    def post(self) -> None:
        self.calls_post += 1

    def success(self, result) -> None:
        self.calls_success += 1

    def error(self, exception) -> None:
        self.exception = exception
        self.calls_error += 1

    def argv(self, args) -> list:
        self.calls_argv += 1
        return ['unknown_binary.exe']

    def data(self) -> dict:
        self.calls_data += 1
        return {
            'exception': self.exception.strerror,
            'calls_pre': self.calls_pre,
            'calls_post': self.calls_post,
            'calls_success': self.calls_success,
            'calls_error': self.calls_error,
            'calls_argv': self.calls_argv,
            'calls_data': self.calls_data,
        }


def test_run_error():
    param_space = Parameters.from_dict({
        'p1': [1],
    })

    data = run(
        processes=1,
        context_class=InvokeContextError,
        parameters_space=param_space,
        shape=ParameterSpaceShape.CUBE
    )

    assert data[0]['exception'] != ''
    assert data[0]['calls_error'] == 1
    assert data[0]['calls_pre'] == 1
    assert data[0]['calls_post'] == 0
    assert data[0]['calls_success'] == 0
    assert data[0]['calls_argv'] == 1
    assert data[0]['calls_data'] == 1
