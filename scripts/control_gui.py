#!/usr/bin/env python3
import tkinter as tk
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class App(Node):
    def __init__(self):
        super().__init__('robot_control_panel')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
    def send(self, x=0.0, z=0.0):
        m = Twist(); m.linear.x = x; m.angular.z = z; self.pub.publish(m)

rclpy.init()
node = App()
root = tk.Tk(); root.title('Serving Robot Control')
root.geometry('360x300')

def button(text, x, z):
    return tk.Button(root, text=text, width=10, height=2, command=lambda: node.send(x, z))

button('Forward', 0.20, 0).grid(row=0, column=1, padx=5, pady=5)
button('Left', 0, 0.50).grid(row=1, column=0, padx=5, pady=5)
button('STOP', 0, 0).grid(row=1, column=1, padx=5, pady=5)
button('Right', 0, -0.50).grid(row=1, column=2, padx=5, pady=5)
button('Reverse', -0.20, 0).grid(row=2, column=1, padx=5, pady=5)

root.protocol('WM_DELETE_WINDOW', lambda: (node.send(), node.destroy_node(), rclpy.shutdown(), root.destroy()))

def spin():
    rclpy.spin_once(node, timeout_sec=0.0)
    root.after(20, spin)
spin(); root.mainloop()
