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


# --- WHITELISTS ---
SAFE_BUILTINS = {
    # ---- Basic Types ----
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,

    # ---- Constructors ----
    "range": range,
    "len": len,
    "enumerate": enumerate,
    "zip": zip,

    # ---- Math & Utility ----
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "round": round,

    # ---- Logic ----
    "all": all,
    "any": any,

    # ---- Functional ----
    "map": map,
    "filter": filter,

    # ---- Output ----
    "print": print,

    # ---- Exceptions ----
    "Exception": Exception,
    "ValueError": ValueError,
    "TypeError": TypeError,
}


# --- EXECUTION ---
code = sys.stdin.read()
exec(code, {"__builtins__": SAFE_BUILTINS})