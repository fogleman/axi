from math import modf
from serial import Serial
from serial.tools.list_ports import comports
import time

STEPS_PER_INCH = 2032
STEPS_PER_MM = 80

VID_PID = '04D8:FD92'

def find_port():
    for port in comports():
        if VID_PID in port[2]:
            return port[0]
    return None

class Device(object):
    def __init__(self, steps_per_unit=STEPS_PER_INCH):
        port = find_port()
        if port is None:
            raise Exception('cannot find axidraw device')
        self.serial = Serial(port, timeout=1)
        self.steps_per_unit = steps_per_unit

    def readline(self):
        return self.serial.readline().strip()

    def command(self, *args):
        line = ','.join(map(str, args))
        self.serial.write(line + '\r')
        return self.readline()

    def version(self):
        return self.command('V')

    # motor functions
    def enable_motors(self):
        return self.command('EM', 1, 1)

    def disable_motors(self):
        return self.command('EM', 0, 0)

    def motor_status(self):
        return self.command('QM')

    def move(self, duration, a, b):
        return self.command('XM', duration, a, b)

    def wait(self):
        while '1' in self.motor_status():
            time.sleep(0.1)

    def run_plan(self, plan):
        step_ms = 30
        step_s = step_ms / 1000.0
        t = 0
        ex = 0
        ey = 0
        while t < plan.t:
            i1 = plan.instant(t)
            i2 = plan.instant(t + step_s)
            d = i2.p.sub(i1.p)
            ex, sx = modf(d.x * self.steps_per_unit + ex)
            ey, sy = modf(d.y * self.steps_per_unit + ey)
            self.move(step_ms, int(sx), int(sy))
            t += step_s
        self.wait()

    # pen functions
    def pen_up(self, delay=0):
        return self.command('SP', 1, delay)

    def pen_down(self, delay=0):
        return self.command('SP', 0, delay)
