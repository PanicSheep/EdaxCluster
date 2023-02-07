import subprocess
import secrets
import numpy as np
import multiprocessing
from pathlib import Path
from typing import Iterable
from core import write_position_file
from .output import Line, parse


class Engine:
    def __init__(self, exe_path, level: int):
        self.level: int = level
        self.exe: Path = Path(exe_path)

    def name(self, separator: str = ' '):
        return separator.join(['Edax4.4', 'level', str(self.level)])

    def __solve(self, pos) -> Line:
        tmp_file = self.exe.parent / f'temp_{secrets.token_hex(16)}.script'
        write_position_file(pos, tmp_file) # create temp file
        cmd = [self.exe, '-n', '1', '-l', str(self.level), '-solve', tmp_file]
        if self.level < 2:
            cmd += ['-h', '10']
        result = subprocess.run(
            cmd,
            cwd = self.exe.parent,
            capture_output = True,
            text = True)
        tmp_file.unlink() # remove temp file
        return parse(result.stdout)
            
    def solve(self, pos) -> list[Line]:
        if not isinstance(pos, Iterable):
            return self.__solve(pos)
        
        with multiprocessing.Pool() as pool:
            results = pool.map(
                self.__solve, 
                np.array_split(pos, multiprocessing.cpu_count() * 4)
                )
        return [r for result in results for r in result]

    def choose_move(self, pos) -> list[int]:
        result = self.solve(pos)
        return [(r.pv[0] if r.pv else 64) for r in result]