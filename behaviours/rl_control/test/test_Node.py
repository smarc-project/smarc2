import os
import signal
import time
from multiprocessing import Process

import behaviours.rl_control.rl_control.Node


def test_node():
    process = Process(target=behaviours.rl_control.rl_control.Node.main)
    try:
        process.start()

        time.sleep(1)
        #TODO Need a way to actually verify the state
      #  assert behaviours.rl_control.rl_control.Node.node is not None
    finally:
        os.kill(process.pid, signal.SIGINT)
