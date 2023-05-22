#!/usr/bin/env python

import os
import sys
from collections import namedtuple

from psutil import Process, NoSuchProcess
from process_performance.parameters import Parameters
from process_performance.runner import \
    InvokeContextInterface, _spawn_process, run
from process_performance.shape import ParameterSpaceShape


class InvokeContextProcessTimes(InvokeContextInterface):
    cpu_times: namedtuple

    def pre(self, workdir) -> None:
        pass

    def post(self) -> None:
        pass

    def success(self, result) -> None:
        pass

    def error(self, exception) -> None:
        pass

    def argv(self, args) -> list:
        platforms = {
            'win32': [os.path.join(sys.base_prefix, 'python'),
                      '-c', args['cpu loader']],
            'linux': [os.path.join(sys.base_prefix, 'python'),
                      '-c', args['cpu loader']],
            'darwin': [os.path.join(sys.base_prefix, 'bin/python'),
                       '-c', args['cpu loader']],
        }
        if sys.platform in platforms:
            return platforms[sys.platform]
        raise RuntimeError(f'platform not supported: "{sys.platform}"')

    def status(self, pid: int) -> None:
        try:
            self.cpu_times = Process(pid).cpu_times()
        except NoSuchProcess:
            pass

    def data(self) -> dict:
        return {
            'times': self.cpu_times
        }


def test_spawn_cpu_times():
    _t = 1
    _times = '__import__(\'os\').times()'
    _time = '__import__(\'time\').time()'
    _psutil_ctime = '__import__(\'psutil\').Process().create_time()'
    _args = {
        'cpu loader':
            "while " +
            f"min({_times}.system, {_times}.user) <= {_t*2} " +
            " and " +
            f"{_time} - {_psutil_ctime} <= {_t*20}" +
            ": print(__import__('os').times())"
    }

    context = InvokeContextProcessTimes()
    result = _spawn_process(context, _args)

    assert result.exit_code == 0
    assert result.stderr == b''
    assert result.stdout != b''
    assert context.data()['times'].user >= _t
    assert context.data()['times'].system >= _t


class InvokeContextCallCount(InvokeContextInterface):
    calls_pre: int = 0
    calls_post: int = 0
    calls_success: int = 0
    calls_error: int = 0
    calls_argv: int = 0
    calls_data: int = 0
    calls_status: int = 0

    def pre(self, workdir) -> None:
        self.calls_pre += 1

    def post(self) -> None:
        self.calls_post += 1

    def success(self, result) -> None:
        self.calls_success += 1

    def error(self, exception) -> None:
        self.calls_error += 1

    def argv(self, args) -> list:
        self.calls_argv += 1
        if sys.platform == 'win32':
            return ['cmd.exe', '/c', 'echo']
        return ['sh', '-c', 'echo']

    def status(self, pid: int) -> None:
        self.calls_status += 1

    def data(self) -> dict:
        self.calls_data += 1
        return {
            'calls_pre': self.calls_pre,
            'calls_post': self.calls_post,
            'calls_success': self.calls_success,
            'calls_error': self.calls_error,
            'calls_argv': self.calls_argv,
            'calls_status': self.calls_status,
            'calls_data': self.calls_data,
        }


def test_run_call_count():
    param_space = Parameters.from_dict({})

    data = run(
        processes=1,
        context_class=InvokeContextCallCount,
        parameters_space=param_space,
        shape=ParameterSpaceShape.CUBE
    )

    assert data[0]['calls_error'] == 0
    assert data[0]['calls_pre'] == 1
    assert data[0]['calls_post'] == 1
    assert data[0]['calls_success'] == 1
    assert data[0]['calls_argv'] == 1
    assert data[0]['calls_status'] >= 1
    assert data[0]['calls_data'] == 1


class InvokeContextStdout(InvokeContextInterface):
    stdout: str = ''

    def pre(self, workdir) -> None:
        pass

    def post(self) -> None:
        pass

    def success(self, result) -> None:
        self.stdout = result.stdout.decode().strip()

    def error(self, exception) -> None:
        pass

    def argv(self, args) -> list:
        platforms = {
            'win32': ['cmd.exe', '/c', 'echo Hello World'],
            'linux': ['sh', '-c', 'echo Hello World'],
            'darwin': ['sh', '-c', 'echo Hello World'],
        }
        if sys.platform in platforms:
            return platforms[sys.platform]
        raise RuntimeError(f'platform not supported: "{sys.platform}"')

    def status(self, pid: int) -> None:
        pass

    def data(self) -> dict:
        return {
            'stdout': self.stdout,
        }


def test_run_stdout():
    param_space = Parameters.from_dict({})

    data = run(
        processes=1,
        context_class=InvokeContextStdout,
        parameters_space=param_space,
        shape=ParameterSpaceShape.CUBE
    )

    assert data[0]['stdout'] == 'Hello World'


class InvokeContextError(InvokeContextInterface):
    exception = None

    def pre(self, workdir) -> None:
        pass

    def post(self) -> None:
        pass

    def success(self, result) -> None:
        pass

    def error(self, exception) -> None:
        self.exception = exception

    def argv(self, args) -> list:
        return ['unknown_binary.exe']

    def status(self, pid: int) -> None:
        pass

    def data(self) -> dict:
        return {
            'exception': self.exception.strerror,
        }


def test_run_exception():
    param_space = Parameters.from_dict({})

    data = run(
        processes=1,
        context_class=InvokeContextError,
        parameters_space=param_space,
        shape=ParameterSpaceShape.CUBE
    )

    assert data[0]['exception'] != ''
