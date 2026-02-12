import sys
import resource
import signal

# --- HARD LIMITS ---
resource.setrlimit(resource.RLIMIT_CPU, (2, 2))        # 2 seconds CPU
resource.setrlimit(resource.RLIMIT_AS, (128 * 1024**2, 128 * 1024**2))  # 128MB RAM
resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))      # no child processes
resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))  # 1MB output

def timeout_handler(signum, frame):
    raise TimeoutError("Execution time exceeded")

signal.signal(signal.SIGXCPU, timeout_handler)

# --- EXECUTION ---
code = sys.stdin.read()
exec(code, {"__builtins__": {}})