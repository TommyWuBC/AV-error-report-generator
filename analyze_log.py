import re
from collections import Counter
from pathlib import Path
from pprint import pprint
import json

#Example: [    8892] 0520-10:17:44 [INFO]main: ROS Init Succ.
LOG_PATTERN = re.compile(r"\[\s*(\d+)\]\s+(\d{4}-\d{2}:\d{2}:\d{2})\s+\[(\w+)\](.*)")

#this is used for sorting the order of event entries 
SEVERITY_PRIORITY = {
    "FATAL": 4,
    "ERR": 3,
    "WARN": 2,
    "INFO": 1,
}

def main():
    log_path = Path("nav_node.log")
    
    #counters
    #this handles number of occurence of each severity type in parsed lines
    severity_counts = Counter()
    #this is for handling unparsed lines logic
    unparsed_type_counts = Counter()
    #this is for handling timer logic
    first_timestamp = None
    last_timestamp = None
    
    with open(log_path, "r", encoding="utf-8", errors="ignore") as file:
        parsed_count = 0
        unparsed_count = 0
        unparsed_examples = []
        unparsed_examples_by_type = {}
        event_groups = {}

        for line in file:
            parsed = parse_line(line)

            if parsed is None:
                category = classify_unparsed_line(line)
                unparsed_count += 1
                unparsed_type_counts[category] += 1
                if category not in unparsed_examples_by_type:
                    unparsed_examples_by_type[category] = []

                if len(unparsed_examples_by_type[category]) < 5:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        unparsed_examples_by_type[category].append(cleaned_line)
                        
                continue
            
            severity_counts[parsed["severity"]] += 1
            
            #this is for handling event groups logic of parsed lines
            if parsed["severity"] in ("WARN", "ERR", "FATAL"):
                base_message, marker = parse_interval_marker(parsed["message"])
                #create a tuple and make it the key
                key = (parsed["module"], base_message)
                if key not in event_groups:
                    #create new key value pair entry in dictionary
                    event_groups[key] = {
                        "module": parsed["module"],
                        "message": base_message,
                        "severity": parsed["severity"],
                        "count": 0,
                        "begin_count": 0,
                        "end_count": 0,
                        "first_seen": parsed["timestamp"],
                        "last_seen": parsed["timestamp"],
                    }
                event_groups[key]["count"] += 1
                event_groups[key]["last_seen"] = parsed["timestamp"]
                if marker == "begin":
                    event_groups[key]["begin_count"] += 1
                elif marker == "end":
                    event_groups[key]["end_count"] += 1
                
            parsed_count += 1
            if first_timestamp is None:
                first_timestamp = parsed["timestamp"]
            last_timestamp = parsed["timestamp"]
    
    sorted_events = sorted(
        #the dict is called event_groups, dict of <tuple, inner dict>
        event_groups.values(), #only return the values
        #this tells sorted() what to sort by, which is the count field of inner dict
        key=lambda event: (
            SEVERITY_PRIORITY.get(event["severity"], 0),
            event["count"]
        ),
        reverse=True #largest first
    )
    
    #attach diagnosis information into each event object
    for event in sorted_events[:10]:
        diagnosis = classify_fault_event(event)
        event["diagnosis"] = diagnosis
    
    #create entry (dict) of the results
    analysis_result = {
        "parsed_lines": parsed_count,
        "unparsed_lines": unparsed_count,
        "severity_counts": dict(severity_counts),
        "unparsed_categories": dict(unparsed_type_counts),
        "time_range": {
            "start": first_timestamp,
            "end": last_timestamp,
        },
        "top_fault_events": sorted_events[:10],
    }     
    
    pprint(analysis_result)
    #output
    output_path = log_path.stem + "_analysis.json"
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(
            analysis_result,
            output_file,
            ensure_ascii=False,
            indent=4
        )
    
    report_text = generate_markdown_report(analysis_result)
    report_path = log_path.stem + "_report.md"
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_text)
    print(f"Report saved to: {report_path}")
    """
    #then print for debugging purposes  
    print("Parsed lines:", parsed_count)
    print("Unparsed lines:", unparsed_count)
    print("Severity counts:", severity_counts)
    print("\nUnparsed line categories:")
    for category, count in unparsed_type_counts.most_common():
        print(f"{category}: {count}")

    print("\nUnparsed examples by category:")
    for category, examples in unparsed_examples_by_type.items():
        print(f"\n[{category}]")
        for example in examples:
            print("-", example)
        
    print("Time range:", first_timestamp, "to", last_timestamp)
    
    print("\nTop fault events:")
    
    for event in sorted_events[:10]: #print the top 10 events
        print(f"\nCount: {event['count']}")
        print(f"Severity: {event['severity']}")
        print(f"Module: {event['module']}")
        print(f"Message: {event['message']}")
        print(f"First seen: {event['first_seen']}")
        print(f"Last seen: {event['last_seen']}")
        #diagnose the type of fault
        diagnosis = classify_fault_event(event)
        print(f"Subsystem: {diagnosis['subsystem']}")
        print(f"Fault type: {diagnosis['fault_type']}")
        print(f"Severity level: {diagnosis['severity_level']}")
        print(f"Possible cause: {diagnosis['possible_cause']}")
        print(f"Suggestion: {diagnosis['suggestion']}")
        print(f"Needs algorithm team: {diagnosis['needs_algorithm_team']}")
    """


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
        base_message = message.removesuffix(". Begin.")
        base_message = base_message.rstrip(".")
        return base_message, "begin"

    if message.endswith(". End."):
        base_message = message.removesuffix(". End.")
        base_message = base_message.rstrip(".")
        return base_message, "end"

    return message.rstrip("."), None

#use this to classify the fault event
def classify_fault_event(event):
    message = event["message"].lower()
    module = event["module"].lower()
    original_message = event["message"]

    if "region map is invalid" in message:
        return {
            "subsystem": "感知模块",
            "fault_type": "区域地图无效",
            "severity_level": "P1",
            "possible_cause": "区域地图配置缺失、损坏或与当前任务地图不匹配。",
            "suggestion": "检查地图配置文件、区域地图文件和任务区域设置。",
            "needs_algorithm_team": True,
        }

    if "getlocationmsg" in message or "定位数据异常" in original_message:
        return {
            "subsystem": "定位模块",
            "fault_type": "定位数据异常或缺失",
            "severity_level": "P1",
            "possible_cause": "定位消息未正常发布，或 GNSS/IMU/SLAM 数据异常。",
            "suggestion": "检查定位节点状态、定位话题连接、GNSS/IMU/SLAM 输入。",
            "needs_algorithm_team": True,
        }

    if "timeout" in message or "超时" in original_message:
        return {
            "subsystem": "通信/数据链路",
            "fault_type": "数据超时",
            "severity_level": "P2",
            "possible_cause": "上游节点未正常发布数据，或通信链路延迟/中断。",
            "suggestion": "检查相关 ROS topic 是否正常发布，确认节点状态和网络延迟。",
            "needs_algorithm_team": False,
        }

    if "点云" in original_message:
        return {
            "subsystem": "感知模块",
            "fault_type": "点云数据异常",
            "severity_level": "P1",
            "possible_cause": "激光雷达、点云网络传输或点云检测链路异常。",
            "suggestion": "检查 LiDAR 连接、点云输入、网络状态和感知节点运行状态。",
            "needs_algorithm_team": True,
        }
    
    if "failed to obtain the matching pose" in message:
        return {
            "subsystem": "定位/坐标变换模块",
            "fault_type": "匹配位姿获取失败",
            "severity_level": "P2",
            "possible_cause": "定位数据、TF 坐标变换或时间戳匹配异常。",
            "suggestion": "检查定位数据时间戳、TF 发布状态以及感知节点与定位节点的时间同步。",
            "needs_algorithm_team": True,
        }

    if "det_dynamic_obst" in message:
        return {
            "subsystem": "感知模块",
            "fault_type": "动态障碍物检测异常",
            "severity_level": "P2",
            "possible_cause": "动态障碍物检测结果异常或残差异常。",
            "suggestion": "检查动态障碍物检测输入、点云/视觉数据质量和检测模块状态。",
            "needs_algorithm_team": True,
        }

    if "感知数据异常" in original_message:
        return {
            "subsystem": "感知模块",
            "fault_type": "感知数据异常",
            "severity_level": "P1",
            "possible_cause": "感知数据链路异常，可能与点云、检测结果或上游感知输入有关。",
            "suggestion": "检查 LiDAR/相机输入、感知节点状态和相关 ROS topic 是否正常。",
            "needs_algorithm_team": True,
        }
    
    if "camera data" in message and "fail" in message:
        return {
            "subsystem": "视觉感知模块",
            "fault_type": "相机数据获取失败",
            "severity_level": "P1",
            "possible_cause": "相机输入异常、视觉分割模块异常或图像数据未正常接收。",
            "suggestion": "检查相机设备连接、图像话题发布状态以及视觉分割模块运行状态。",
            "needs_algorithm_team": True,
        }
    
    if "state is abnormal" in message:
        return {
            "subsystem": "导航控制模块",
            "fault_type": "导航状态异常",
            "severity_level": "P1",
            "possible_cause": "导航状态机进入异常状态，可能由定位、感知或路径规划异常触发。",
            "suggestion": "检查导航状态机、路径规划结果以及上游定位/感知输入。",
            "needs_algorithm_team": True,
        }
    
    if "获取感知数据失败" in original_message:
        return {
            "subsystem": "导航-感知接口",
            "fault_type": "感知数据获取失败",
            "severity_level": "P1",
            "possible_cause": "导航模块无法获取感知结果，可能是感知节点异常或 ROS topic 中断。",
            "suggestion": "检查感知节点是否正常运行，确认相关 topic 是否正常发布。",
            "needs_algorithm_team": True,
        }
    
    if "not recv state rpt rsp" in message:
        return {
            "subsystem": "动态地图管理模块",
            "fault_type": "状态响应未接收",
            "severity_level": "P2",
            "possible_cause": "动态地图管理模块未收到状态响应，可能存在通信异常。",
            "suggestion": "检查动态地图服务状态、通信链路和相关 ROS 服务。",
            "needs_algorithm_team": False,
        }
        
    if "data invalid" in message:
        return {
            "subsystem": "数据接收模块",
            "fault_type": "数据无效",
            "severity_level": "P2",
            "possible_cause": "接收到的数据为空、格式错误或未正常更新。",
            "suggestion": "检查上游数据发布节点和数据格式。",
            "needs_algorithm_team": True,
        }

    return {
        "subsystem": "未知模块",
        "fault_type": "未分类故障",
        "severity_level": "P3",
        "possible_cause": "当前规则库未覆盖该故障模式。",
        "suggestion": "建议人工复核该日志事件，并根据实际原因补充规则。",
        "needs_algorithm_team": True,
    }
    
def generate_markdown_report(analysis_result):
    lines = []

    lines.append("# 自动驾驶清扫车故障诊断报告")
    lines.append("")

    lines.append("## 1. 日志概览")
    lines.append(f"- 日志时间范围：{analysis_result['time_range']['start']} 至 {analysis_result['time_range']['end']}")
    lines.append(f"- 已解析日志行数：{analysis_result['parsed_lines']}")
    lines.append(f"- 未解析日志行数：{analysis_result['unparsed_lines']}")
    lines.append("")

    lines.append("## 2. 严重等级统计")
    for severity, count in analysis_result["severity_counts"].items():
        lines.append(f"- {severity}: {count}")
    lines.append("")

    lines.append("## 3. 主要故障事件")
    for index, event in enumerate(analysis_result["top_fault_events"], start=1):
        diagnosis = event["diagnosis"]

        lines.append(f"### {index}. {diagnosis['fault_type']}")
        lines.append(f"- 子系统：{diagnosis['subsystem']}")
        lines.append(f"- 原始模块：`{event['module']}`")
        lines.append(f"- 原始信息：`{event['message']}`")
        lines.append(f"- 日志等级：{event['severity']}")
        lines.append(f"- 出现次数：{event['count']}")
        lines.append(f"- 首次出现：{event['first_seen']}")
        lines.append(f"- 最后出现：{event['last_seen']}")

        if event.get("begin_count") or event.get("end_count"):
            lines.append(f"- Begin 次数：{event.get('begin_count', 0)}")
            lines.append(f"- End 次数：{event.get('end_count', 0)}")

        lines.append(f"- 诊断等级：{diagnosis['severity_level']}")
        lines.append(f"- 可能原因：{diagnosis['possible_cause']}")
        lines.append(f"- 建议处理：{diagnosis['suggestion']}")
        lines.append(f"- 是否需要算法团队介入：{'是' if diagnosis['needs_algorithm_team'] else '否'}")
        lines.append("")

    lines.append("## 4. 初步结论")
    top_events = analysis_result["top_fault_events"]

    if top_events:
        classified_events = [
            event for event in top_events
            if event["diagnosis"]["fault_type"] != "未分类故障"
        ]

        if classified_events:
            main_event = classified_events[0]
        else:
            main_event = top_events[0]

        main_diag = main_event["diagnosis"]

        lines.append(
            f"本次日志中主要问题为【{main_diag['fault_type']}】，"
            f"涉及子系统为【{main_diag['subsystem']}】，"
            f"累计出现 {main_event['count']} 次。"
        )
    else:
        lines.append("未检测到明显 WARN/ERR/FATAL 故障事件。")

    lines.append("")
    lines.append("本报告由日志解析与规则诊断模块自动生成，后续可接入本地大模型生成更自然的中文总结。")

    return "\n".join(lines)
    

if __name__ == "__main__":
    main()