#Find the number of cpu cores available, fork and create that number of processes, run the do_bad_guy_work.py script in each process

import os
import multiprocessing
import sys
import logging
import signal


pids = []


logger = logging.getLogger(__name__)
num_cores = multiprocessing.cpu_count() - 3
print("Starting a worker on each of the " + str(num_cores) + " cores")
for i in range(num_cores):
  pid = os.fork()
  logger.info("started new process with pid: " + str(pid))
  if pid == 0:
    os.system("python -m src.password_breaking_agent.do_bad_guy_work")
    sys.exit()
for pid in pids:
    os.kill(pid, signal.SIGTERM)
try:
    # Wait for any child process to terminate
    os.wait()
except KeyboardInterrupt:
    # This will be raised when a SIGINT (ctrl+C) is received
    # Kill all processes in the current process group
    os.killpg(os.getpgrp(), signal.SIGTERM)