
#this is used for sorting the order of event entries 
SEVERITY_PRIORITY = {
    "FATAL": 4,
    "ERR": 3,
    "WARN": 2,
    "INFO": 1,
}

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