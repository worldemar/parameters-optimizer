#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import multiprocessing
import multiprocessing.managers
import signal
import subprocess
import tempfile
import threading
import time
import psutil

from process_performance.context import InvokeContextInterface, InvokeResult
from process_performance.parameters import Parameters
from process_performance.shape import ParameterSpaceShape


def _spawn_process(context: InvokeContextInterface, params: dict):
    def stream_data_to_buffer(descriptor, buffer):
        buffer.append(descriptor.read())

    with tempfile.TemporaryDirectory() as tmpdir:
        # lists for mutability
        stdout = []
        stderr = []

        context.pre(workdir=tmpdir)

        process =  psutil.Popen(
            args=context.argv(args=params),
            cwd=tmpdir,
            bufsize=-1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout_thread = threading.Thread(
            target=stream_data_to_buffer,
            args=(process.stdout, stdout))
        stderr_thread = threading.Thread(
            target=stream_data_to_buffer,
            args=(process.stderr, stderr))
        stdout_thread.start()
        stderr_thread.start()

        while process.is_running():
            try:
                context.status(process.pid)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f'InvokeContextInterface.status exception: {exc}')
            # poll() required on linux/darwin, otherwise
            # is_running() will always return True
            # and NoSuchProcess is never thrown
            process.poll()
            time.sleep(0.001)

        process.wait()
        stdout_thread.join()
        stderr_thread.join()

        context.post()

        return InvokeResult(
            exit_code=process.returncode,
            stdout=stdout[0],
            stderr=stderr[0],
        )


def _disable_sigint():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class CustomManager(multiprocessing.managers.BaseManager):
    pass


def run(
        processes: int,
        context_class: type,
        parameters_space: Parameters,
        shape: ParameterSpaceShape):
    CustomManager.register('context_class', context_class)
    with CustomManager() as manager:
        contexts = []
        with multiprocessing.Pool(
                processes=processes,
                initializer=_disable_sigint) as pool:
            tasks = []
            for params in parameters_space.gen(shape=shape)():
                context = manager.context_class()
                tasks.append(pool.apply_async(
                    func=_spawn_process,
                    args=(context, params),
                    callback=context.success,
                    error_callback=context.error,
                ))
                contexts.append(context)
            for task in tasks:
                task.wait()
        return [context.data() for context in contexts]
