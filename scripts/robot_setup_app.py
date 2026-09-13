#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import ttk
from pathlib import Path

WS = Path.home() / 'autonomous_serving_robot_ws'

class RobotSetupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Autonomous Serving Robot - Setup & Test')
        self.geometry('900x620')
        self.status = {}
        self.build()

    def build(self):
        ttk.Label(self, text='Autonomous Serving Robot', font=('TkDefaultFont', 18, 'bold')).pack(anchor='w', padx=18, pady=(18, 2))
        ttk.Label(self, text='Setup, diagnostics and commissioning').pack(anchor='w', padx=18, pady=(0, 12))
        tabs = ttk.Notebook(self)
        tabs.pack(fill='both', expand=True, padx=12, pady=8)
        for title, checks in [('System Setup', self.system_checks()), ('Hardware', self.hardware_checks()), ('ROS 2 / Robot', self.ros_checks())]:
            tab = ttk.Frame(tabs, padding=14)
            tabs.add(tab, text=title)
            for name, fn in checks:
                row = ttk.Frame(tab); row.pack(fill='x', pady=5)
                ttk.Label(row, text=name, width=30).pack(side='left')
                result = ttk.Label(row, text='Not checked', width=18)
                result.pack(side='left')
                detail = ttk.Label(row, text=''); detail.pack(side='left', padx=8, fill='x', expand=True)
                self.status[name] = (result, detail, fn)
                ttk.Button(row, text='Check', command=lambda n=name: self.check(n)).pack(side='right')
            ttk.Button(tab, text='Run all checks', command=lambda: self.run_tab(checks)).pack(anchor='w', pady=14)
        logtab = ttk.Frame(tabs, padding=12); tabs.add(logtab, text='Log')
        self.log = tk.Text(logtab, state='disabled'); self.log.pack(fill='both', expand=True)
        ttk.Label(self, text='SAFE MODE: software diagnostics only. Do not enable motors until wiring and Hall/tach signals are verified.', wraplength=850).pack(anchor='w', padx=18, pady=10)

    def system_checks(self):
        return [('Ubuntu', lambda: self.command("grep PRETTY_NAME /etc/os-release")), ('Python 3', lambda: self.command('python3 --version')), ('ROS 2', lambda: self.command('ros2 --version')), ('Workspace', lambda: (0, str(WS)) if (WS / 'src' / 'serving_robot' / 'package.xml').exists() else (1, 'Workspace not installed'))]

    def hardware_checks(self):
        return [('Serial devices', lambda: self.command("ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null")), ('USB permissions', lambda: self.command('groups')),
                ('ESP32 telemetry', lambda: self.topic('/motor/status')), ('LiDAR /scan', lambda: self.topic('/scan')), ('IMU /imu/data', lambda: self.topic('/imu/data'))]

    def ros_checks(self):
        return [('ROS graph', lambda: self.command('ros2 node list')), ('/cmd_vel', lambda: self.topic('/cmd_vel')), ('/odom', lambda: self.topic('/odom')), ('Serving command', lambda: self.topic('/serving/command')), ('Nav2', lambda: self.command("ros2 node list | grep -E 'planner_server|controller_server|bt_navigator|amcl|slam_toolbox'"))]

    def command(self, text):
        try:
            p = subprocess.run(text, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=8)
            return p.returncode, p.stdout.strip()
        except Exception as e:
            return 1, str(e)

    def topic(self, name):
        return self.command(f'ros2 topic info {name}')

    def check(self, name):
        label, detail, fn = self.status[name]
        code, out = fn()
        label.config(text='PASS' if code == 0 else 'CHECK')
        detail.config(text=(out or 'No output').replace('\n', ' ')[:130])
        self.write(f'[{name}] {"PASS" if code == 0 else "CHECK"}\n{out}\n')

    def run_tab(self, checks):
        for name, _ in checks: self.check(name)

    def write(self, text):
        self.log.config(state='normal'); self.log.insert('end', text + '\n'); self.log.see('end'); self.log.config(state='disabled')

if __name__ == '__main__':
    RobotSetupApp().mainloop()
