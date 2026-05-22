#used to generate a human readable and structured report from the analysis result
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
    lines.append("本报告由日志解析与规则诊断模块自动生成，后续可接入大语言模型 API 生成更自然的中文总结。")

    return "\n".join(lines)