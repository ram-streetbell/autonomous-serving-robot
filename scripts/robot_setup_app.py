#!/usr/bin/env python3
import os
import queue
import shlex
import signal
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parents[1]
WS = Path.home() / "autonomous_serving_robot_ws"


def ros_shell(command):
    return "bash -lc " + shlex.quote(
        "source /opt/ros/jazzy/setup.bash 2>/dev/null || source /opt/ros/humble/setup.bash 2>/dev/null; "
        "source ~/.robot_env 2>/dev/null || true; " + command
    )


class RobotSetupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Autonomous Serving Robot - Setup & Test")
        self.geometry("1040x760")
        self.minsize(940, 680)
        self.q = queue.Queue()
        self.proc = None
        self.rows = {}
        self.map_path = tk.StringVar()
        self._build()
        self.after(100, self._drain)
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build(self):
        head = ttk.Frame(self, padding=16)
        head.pack(fill="x")
        ttk.Label(head, text="Autonomous Serving Robot", font=("TkDefaultFont", 20, "bold")).pack(anchor="w")
        ttk.Label(head, text="New-system setup • hardware commissioning • ROS 2 diagnostics • safe testing").pack(anchor="w", pady=(2, 0))
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=12, pady=6)
        self._checks_tab(tabs, "System", self.system_checks())
        self._checks_tab(tabs, "Hardware", self.hardware_checks())
        self._checks_tab(tabs, "ROS 2", self.ros_checks())
        self._actions_tab(tabs)
        logtab = ttk.Frame(tabs, padding=10)
        tabs.add(logtab, text="Log")
        self.log = tk.Text(logtab, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)
        bottom = ttk.Frame(self, padding=(16, 4, 16, 12))
        bottom.pack(fill="x")
        ttk.Label(bottom, text="SAFE MODE: diagnostics and setup do not enable motor power. Verify wiring, E-stop, Hall order, tach/PPR and the 0–5 V interface before driving.", wraplength=950).pack(anchor="w")

    def _checks_tab(self, tabs, title, checks):
        tab = ttk.Frame(tabs, padding=14)
        tabs.add(tab, text=title)
        for name, fn in checks:
            row = ttk.Frame(tab)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=name, width=28).pack(side="left")
            result = ttk.Label(row, text="NOT CHECKED", width=15)
            result.pack(side="left")
            detail = ttk.Label(row, text="", anchor="w")
            detail.pack(side="left", fill="x", expand=True, padx=8)
            ttk.Button(row, text="Check", command=lambda n=name: self.check(n)).pack(side="right")
            self.rows[name] = (result, detail, fn)
        ttk.Button(tab, text="Run all checks", command=lambda c=checks: self.run_checks(c)).pack(anchor="w", pady=16)

    def _actions_tab(self, tabs):
        tab = ttk.Frame(tabs, padding=16)
        tabs.add(tab, text="Setup & Test")
        ttk.Label(tab, text="1. New-system setup", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        ttk.Label(tab, text="The installer supports Ubuntu 24.04 + ROS 2 Jazzy or Ubuntu 22.04 + ROS 2 Humble. It installs dependencies and builds the workspace.", wraplength=900).pack(anchor="w", pady=(3, 8))
        ttk.Button(tab, text="Install / Rebuild Robot Software", command=self.install).pack(anchor="w", pady=4)

        ttk.Separator(tab).pack(fill="x", pady=14)
        ttk.Label(tab, text="2. Runtime", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        buttons = ttk.Frame(tab)
        buttons.pack(anchor="w", pady=8)
        ttk.Button(buttons, text="Start Hardware", command=self.hardware).grid(row=0, column=0, padx=(0, 8), pady=4)
        ttk.Button(buttons, text="Start Software Bringup", command=self.bringup).grid(row=0, column=1, padx=8, pady=4)
        ttk.Button(buttons, text="Start Mapping", command=self.mapping).grid(row=0, column=2, padx=8, pady=4)
        ttk.Button(buttons, text="Stop Runtime", command=self.stop).grid(row=0, column=3, padx=8, pady=4)

        ttk.Separator(tab).pack(fill="x", pady=14)
        ttk.Label(tab, text="3. Autonomous navigation", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        ttk.Label(tab, text="Select a saved Nav2 map (.yaml). Navigation starts only after you choose a map; motor enable remains under the hardware safety design.", wraplength=900).pack(anchor="w", pady=(3, 8))
        maprow = ttk.Frame(tab)
        maprow.pack(fill="x", pady=4)
        ttk.Entry(maprow, textvariable=self.map_path).pack(side="left", fill="x", expand=True)
        ttk.Button(maprow, text="Browse…", command=self.choose_map).pack(side="left", padx=6)
        ttk.Button(maprow, text="Start Autonomous Navigation", command=self.autonomy).pack(anchor="w", pady=6)
        ttk.Button(maprow, text="Save Current SLAM Map", command=self.save_map).pack(anchor="w", pady=4)

        ttk.Separator(tab).pack(fill="x", pady=14)
        ttk.Label(tab, text="4. Testing tools", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        ttk.Label(tab, text="Manual control is for controlled bench testing only. Keep the drive wheels lifted until direction, Hall order, tach feedback and emergency stop are verified.", wraplength=900).pack(anchor="w", pady=(3, 8))
        ttk.Button(tab, text="Open Manual Control", command=self.manual).pack(anchor="w", pady=4)

    def system_checks(self):
        return [
            ("Ubuntu", lambda: self.command(". /etc/os-release; printf '%s %s' \"$ID\" \"$VERSION_ID\"")),
            ("Python 3", lambda: self.command("python3 --version")),
            ("Tkinter", lambda: self.command("python3 -c 'import tkinter'")),
            ("ROS 2", lambda: self.command(ros_shell("ros2 --version"))),
            ("Workspace", lambda: (0, str(WS)) if (WS / "src" / "serving_robot" / "package.xml").exists() else (1, "Workspace not installed")),
            ("Colcon", lambda: self.command("colcon --version")),
        ]

    def hardware_checks(self):
        return [
            ("Serial devices", lambda: self.command("ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null")),
            ("USB group", lambda: self.command("id -nG | grep -qw dialout")),
            ("ESP32 telemetry", lambda: self.topic("/motor/status")),
            ("LiDAR /scan", lambda: self.topic("/scan")),
            ("IMU /imu/data", lambda: self.topic("/imu/data")),
        ]

    def ros_checks(self):
        return [
            ("ROS graph", lambda: self.ros("node list")),
            ("/cmd_vel", lambda: self.topic("/cmd_vel")),
            ("/odom", lambda: self.topic("/odom")),
            ("Serving command", lambda: self.topic("/serving/command")),
            ("Nav2 nodes", lambda: self.command(ros_shell("ros2 node list | grep -E 'planner_server|controller_server|bt_navigator|amcl|slam_toolbox'"))),
        ]

    def command(self, text, timeout=10):
        try:
            p = subprocess.run(text, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
            return p.returncode, p.stdout.strip()
        except Exception as exc:
            return 1, str(exc)

    def ros(self, args):
        return self.command(ros_shell("ros2 " + args))

    def topic(self, name):
        return self.ros("topic info " + shlex.quote(name))

    def check(self, name):
        result, detail, fn = self.rows[name]
        code, out = fn()
        state = "PASS" if code == 0 else "CHECK"
        result.config(text=state)
        detail.config(text=(out or "No output").replace("\n", " ")[:180])
        self.write(f"[{state}] {name}: {out or 'No output'}")

    def run_checks(self, checks):
        for name, _ in checks:
            self.check(name)

    def run_async(self, title, command):
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning("Already running", "A runtime command is already running. Stop it first.")
            return
        self.write(f"[RUN] {title}: {command}")

        def worker():
            try:
                self.proc = subprocess.Popen(["bash", "-lc", command], cwd=str(ROOT), start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                for line in self.proc.stdout:
                    self.q.put(line.rstrip())
                rc = self.proc.wait()
                self.q.put(f"[EXIT {rc}] {title}")
            except Exception as exc:
                self.q.put(f"[ERROR] {exc}")

        threading.Thread(target=worker, daemon=True).start()

    def install(self):
        self.run_async("installer", "bash scripts/install.sh")

    def hardware(self):
        self.run_async("hardware", ros_shell("ros2 launch serving_robot hardware.launch.py"))

    def bringup(self):
        self.run_async("software bringup", ros_shell("ros2 launch serving_robot bringup.launch.py"))

    def mapping(self):
        self.run_async("mapping", ros_shell("ros2 launch serving_robot mapping.launch.py"))

    def choose_map(self):
        path = filedialog.askopenfilename(title="Select saved Nav2 map", filetypes=[("Map YAML", "*.yaml"), ("All files", "*")])
        if path:
            self.map_path.set(path)

    def autonomy(self):
        path = self.map_path.get().strip()
        if not path or not Path(path).is_file():
            messagebox.showwarning("Map required", "Select an existing saved Nav2 map YAML first.")
            return
        self.run_async("autonomous navigation", ros_shell("ros2 launch serving_robot autonomy.launch.py map=" + shlex.quote(path)))

    def save_map(self):
        path = filedialog.asksaveasfilename(title="Save SLAM map as", defaultextension=".yaml", filetypes=[("Map YAML", "*.yaml")])
        if not path:
            return
        prefix = os.path.splitext(path)[0]
        self.run_async("map save", ros_shell("ros2 run nav2_map_server map_saver_cli -f " + shlex.quote(prefix)))

    def stop(self):
        if self.proc and self.proc.poll() is None:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGINT)
            except ProcessLookupError:
                pass
            self.write("[STOP] Sent SIGINT to the complete runtime process group")
        else:
            self.write("[INFO] No runtime started by this app")

    def manual(self):
        subprocess.Popen(["bash", "-lc", ros_shell("python3 " + shlex.quote(str(ROOT / "scripts" / "control_gui.py")))])

    def write(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _drain(self):
        try:
            while True:
                self.write(self.q.get_nowait())
        except queue.Empty:
            pass
        self.after(100, self._drain)

    def _close(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno("Runtime running", "Stop the active runtime before closing?"):
                self.stop()
            else:
                return
        self.destroy()


if __name__ == "__main__":
    RobotSetupApp().mainloop()
