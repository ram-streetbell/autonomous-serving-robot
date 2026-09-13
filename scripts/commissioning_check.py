#!/usr/bin/env python3
"""Headless commissioning preflight for fresh Ubuntu systems."""
import os
import shutil
import subprocess
from pathlib import Path

WS = Path.home() / 'autonomous_serving_robot_ws'

def check(label, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, str(e)
    print(f"{'PASS' if ok else 'CHECK'}  {label}: {detail}")
    return ok

def cmd(c):
    p = subprocess.run(c, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=8)
    return p.returncode == 0, p.stdout.strip().splitlines()[0][:120] if p.stdout.strip() else 'no output'

def main():
    results = []
    results.append(check('Ubuntu', lambda: (Path('/etc/os-release').exists() and 'ubuntu' in Path('/etc/os-release').read_text().lower(), 'Ubuntu detected')))
    results.append(check('Python 3', lambda: cmd('python3 --version')))
    results.append(check('ROS 2', lambda: cmd('ros2 --version')))
    results.append(check('Workspace', lambda: ((WS/'src'/'serving_robot'/'package.xml').exists(), str(WS))))
    results.append(check('colcon', lambda: (shutil.which('colcon') is not None, shutil.which('colcon') or 'not installed')))
    devices = list(Path('/dev').glob('ttyUSB*')) + list(Path('/dev').glob('ttyACM*'))
    results.append(check('Serial device', lambda: (bool(devices), ', '.join(map(str, devices)) or 'none detected')))
    results.append(check('Git', lambda: cmd('git --version')))
    print('\nPreflight:', f'{sum(results)}/{len(results)} checks passed')
    print('Motor activation is intentionally NOT performed by this tool.')
    return 0 if all(results[:5]) else 1

if __name__ == '__main__':
    raise SystemExit(main())
