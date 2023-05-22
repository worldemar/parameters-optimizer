#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class InvokeResult:
    exit_code: int
    stdout: str
    stderr: str


class InvokeContextInterface(ABC):
    '''
        A class responsible for preparing, formatting command,
        cleaning up and data collection for subprocess.
    '''
    @abstractmethod
    def pre(self, workdir: str) -> None:
        '''
            Called right before process spawns,
            receives directory process will start in
        '''

    @abstractmethod
    def post(self) -> None:
        '''
            Called right after process exits,
            working directory is cleaned after this call
        '''

    @abstractmethod
    def success(self, result: InvokeResult) -> None:
        '''
            Called once subprocess return code is collected,
            receives result object containing return code, stdout and stderr
        '''

    @abstractmethod
    def error(self, exception: Exception) -> None:
        '''
            Called on process spawning error,
            receives exception that ocurred during process spawning
        '''

    @abstractmethod
    def argv(self, args: dict[str:any]) -> list:
        '''
            Called on process spawn.
            Receives dictionary of { parameter_name : parameter_value }
            must return list of command line args to run as subprocess
        '''

    @abstractmethod
    def status(self, pid: int) -> None:
        '''
            Called repeatedly during process monitoring.
            Receives process pid as a parameter.
            Use this to gather process data, to monitor
            its status and send signals if needed.

            Note that his method might never be called
            if process exits faster than monitoring starts.
        '''

    @abstractmethod
    def data(self) -> dict:
        '''
            called last to collect data.
            must return all interesting data as dictionary
        '''
