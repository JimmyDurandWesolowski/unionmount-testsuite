#
# Tools for test scripts
#
import os

class ArgumentError(Exception):
    def __init__(self, msg):
        self.__msg = msg
    def __str__(self):
        return self.__msg

class TestError(Exception):
    def __init__(self, msg):
        self.__msg = msg
    def __str__(self):
        return self.__msg

def system(command):
    ret = os.system(command)
    if ret != 0:
        raise RuntimeError("Command failed: " + command)
    return True

def read_file(path):
    fd = open(path, "r")
    data = fd.read()
    del fd
    return data

#
# Check for taint (kernel warnings and oopses)
#
current_taint = read_file("/proc/sys/kernel/tainted")
def check_not_tainted():
    taint = read_file("/proc/sys/kernel/tainted")
    if taint != current_taint:
        raise RuntimeError("TAINTED " + current_taint + " -> ", taint)
