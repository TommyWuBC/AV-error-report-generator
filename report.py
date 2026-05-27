import json
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

def build_llm_prompt(analysis_result):
    compact_input = {
        "time_range": analysis_result["time_range"],
        "severity_counts": analysis_result["severity_counts"],
        "top_fault_events": analysis_result["top_fault_events"],
    }

    analysis_json = json.dumps(
        compact_input,
        ensure_ascii=False,
        indent=2
    )

    return f"""
            你不是故障诊断引擎，而是故障报告生成器。

            请根据下面的结构化 report_input_json 生成中文“一页纸故障诊断报告”。

            必须遵守：
            1. report_input_json 是唯一事实来源。
            2. 只能把 observed_log_event / observed_fact 字段写成客观事实。
            3. possible_cause、suggested_action、needs_algorithm_team 是规则引擎给出的诊断建议，不是已验证事实。
            4. 如果 confirmed_root_cause_available 为 false, 不得使用“根因确定为”“根因定位为”“已确认由于”等表达。
            5. 如果 causal_chain_available 为 false，不得把多个异常写成确定因果链；只能写“同时出现”“可能相关”“需进一步验证”。
            6. 建议可以保留，但必须放在“建议/排查方向”中，不得写成已经发生的事实。
            7. 缺失字段写“未提供”或“日志中未体现”。
            8. 不要编造设备编号、作业场景、用户现象、车辆行为、硬件损坏、软重启、自恢复、系统机制缺陷。
            9. 输出 Markdown。
            10. 表格中的事件次数不得使用 “x/y”(例如“91/14”) 这类缩写格式。若多个异常需要同时展示，必须分别写明对应事件名称与次数。

            报告结构：
            一、基础信息
            二、核心故障结论（区分客观事实与规则判断）
            三、各功能节点异常明细
            四、客观事实 / 可能原因 / 建议动作
            五、分级处理建议
            六、故障复盘结论
            七、优化建议

            写作要求：
            - 简洁，面向现场交付、运维、售后技术人员。
            - 不要逐条复述所有日志，只保留主要异常。
            - 所有建议前必须写“建议”。
            - 所有推测前必须写“可能”或“需验证”。
            - 不得使用“导致、引发、造成、证明、说明系统缺乏、数据链路雪崩”等确定性因果词，除非输入中明确允许。

            report_input_json 如下：
        ```json
        {analysis_json}
        """