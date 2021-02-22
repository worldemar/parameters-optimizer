#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import multiprocessing
import multiprocessing.managers
import signal
import subprocess
import tempfile

from process_performance.context import InvokeContextInterface, InvokeResult
from process_performance.parameters import Parameters
from process_performance.shape import ParameterSpaceShape


def _spawn_process(context: InvokeContextInterface, params: dict):
    with tempfile.TemporaryDirectory() as tmpdir:
        context.pre(tmpdir)
        result = subprocess.run(
            check=False,  # error must be handled in InvokeContextInterface
            args=context.argv(args=params),
            cwd=tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        context.post()
        return InvokeResult(
            returncode=result.returncode,
            stdout=result.stdout.decode(),
            stderr=result.stderr.decode()
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
        with multiprocessing.Pool(processes=processes, initializer=_disable_sigint) as pool:
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
