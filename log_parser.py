import re

#Example: [    8892] 0520-10:17:44 [INFO]main: ROS Init Succ.
LOG_PATTERN = re.compile(r"\[\s*(\d+)\]\s+(\d{4}-\d{2}:\d{2}:\d{2})\s+\[(\w+)\](.*)")

def parse_line(line):
    match = LOG_PATTERN.match(line)

    if match is None:
        return None
    
    pid = match.group(1)
    timestamp = match.group(2)
    severity = match.group(3)
    rest = match.group(4).strip()
    #print("DEBUG rest =", repr(rest))

    if ": " in rest:
        module, message = rest.split(": ", 1)
        module = module.strip()
        message = message.strip()
    else:
        module = rest.strip().rstrip(":")
        message = ""

    return {
        "pid": pid,
        "timestamp": timestamp,
        "severity": severity,
        "module": module,
        "message": message,
    }

def classify_unparsed_line(line):
    cleaned = line.strip()
    lower = cleaned.lower()

    if not cleaned:
        return "blank"

    if lower.startswith("arena") or lower.startswith("total") or "system bytes" in lower or "in use bytes" in lower or "max mmap" in lower:
        return "memory_info"

    if lower.startswith("pid") or "pcpt_node" in lower or "pcpt_main" in lower:
        return "thread_info"

    if " r--p " in lower or " r-xp " in lower or " rw-p " in lower or " ---p " in lower or "[heap]" in lower:
        return "process_map"
    
    if "日志库" in lower:
        return "logging_system"

    danger_keywords = [
        "segmentation fault",
        "exception",
        "traceback",
        "backtrace",
        "fatal",
        "error",
        "failed",
        "fail",
        "timeout",
        "abnormal",
        "崩溃",
        "异常",
        "失败",
        "错误",
        "超时",
    ]

    if any(keyword in lower for keyword in danger_keywords):
        return "possibly_important"

    return "unknown"

def parse_interval_marker(message):
    if message.endswith(". Begin."):
        base_message = message[:-len(". Begin.")]
        base_message = base_message.rstrip(".")
        return base_message, "begin"

    if message.endswith(". End."):
        base_message = message[:-len(". End.")]
        base_message = base_message.rstrip(".")
        return base_message, "end"

    return message.rstrip("."), None