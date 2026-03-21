#!/usr/bin/env python3
"""
简单可视化 - 无需OpenCV，展示算法工作流
"""

import json
from pathlib import Path

def create_workflow_diagram():
    """创建工作流程图"""
    
    diagram = """
# 🔥 隐患检测算法工作流程

## 📊 可视化流程图

```
输入图片
    │
    ▼
┌─────────────────┐
│  步骤1: 目标检测  │
│  YOLOv8识别灭火器  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  步骤2: 区域定位  │
│ 霍夫圆检测压力表  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  步骤3: 特征提取  │
│ 霍夫直线检测指针  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  步骤4: 规则判断  │
│ 绿区/黄区/红区判断 │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  步骤5: 结果输出  │
│ JSON结构化数据   │
└─────────────────┘
```

## 🎨 检测过程可视化说明

### 1. 目标检测 (YOLOv8)
- **输入**: 原始图片
- **处理**: YOLO神经网络识别物体
- **输出**: 灭火器边界框 [x1, y1, x2, y2]
- **可视化**: 红色矩形框标注

### 2. 压力表定位 (霍夫圆检测)
- **输入**: 灭火器区域ROI
- **处理**: 霍夫变换检测圆形
- **输出**: 圆心坐标 (cx, cy), 半径 r
- **可视化**: 蓝色圆形标注

### 3. 指针检测 (霍夫直线检测)
- **输入**: 压力表区域
- **处理**: 霍夫变换检测最长直线
- **输出**: 指针角度 (0-360°)
- **可视化**: 绿色直线标注

### 4. 区域判断 (规则引擎)
- **输入**: 指针角度
- **处理**: 
  - 绿区: 0-120° (正常)
  - 黄区: 120-240° (警告)  
  - 红区: 240-360° (隐患)
- **输出**: 隐患判断结果
- **可视化**: 彩色扇形区域

### 5. 结果输出 (结构化JSON)
```json
{
  "success": true,
  "hazard_detected": false,
  "confidence": 0.92,
  "hazard_name": "灭火器压力表正常",
  "reasoning": [
    "检测到灭火器 (置信度: 0.95)",
    "定位压力表区域 (半径: 45px)",
    "检测到指针 (角度: 45.0°)",
    "指针位于绿区"
  ],
  "evidence": {
    "fire_extinguisher_bbox": [100, 150, 300, 400],
    "gauge_center": [200, 250],
    "gauge_radius": 45,
    "pointer_angle": 45.0,
    "zone": "green"
  }
}
```

## 🖼️ 可视化示例

```
┌─────────────────────────────────────┐
│        原始输入图片                   │
│                                     │
│    [图片显示区域]                    │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│  步骤1: YOLO检测灭火器 (红色框)        │
│  ┌─────────────────────┐           │
│  │                     │           │
│  │     灭火器区域       │           │
│  │                     │           │
│  └─────────────────────┘           │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│  步骤2: 定位压力表 (蓝色圆)            │
│        ○───── 压力表                │
│       / \\                          │
│      /   \\                         │
│     /     \\                        │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│  步骤3: 检测指针方向 (绿色线)          │
│        ○──→ 指针方向: 45°           │
│       / \\                          │
│      /   \\                         │
│     /     \\                        │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│  步骤4: 判断区域 (彩色扇形)            │
│   绿区(0-120°)  黄区(120-240°)       │
│      ███           ███              │
│   红区(240-360°)                     │
│      ███                            │
│  指针在绿区 → 正常 ✅                │
└─────────────────────────────────────┘
```

## 🔧 技术实现细节

### YOLOv8配置
```yaml
模型: yolov8n.pt
输入尺寸: 640x640
置信度阈值: 0.5
类别: fire_extinguisher (COCO数据集)
```

### 霍夫变换参数
```python
# 圆检测
dp=1, minDist=50, param1=50, param2=30
minRadius=10, maxRadius=100

# 直线检测  
rho=1, theta=np.pi/180, threshold=20
minLineLength=半径/2, maxLineGap=10
```

### 区域判断逻辑
```python
def judge_zone(angle):
    if 0 <= angle < 120:
        return "green", "正常"
    elif 120 <= angle < 240:
        return "yellow", "警告"
    else:
        return "red", "隐患"
```

## 📈 性能指标

| 步骤 | 处理时间 | 内存占用 | 准确率目标 |
|------|----------|----------|------------|
| YOLO检测 | 100-200ms | ~500MB | 95%+ |
| 霍夫圆检测 | 10-50ms | 低 | 90%+ |
| 指针检测 | 5-20ms | 低 | 85%+ |
| 总流程 | < 300ms | ~500MB | >80% |

## 🎯 验证状态

### ✅ 已完成验证
- [x] API接口格式
- [x] Web上传界面
- [x] JSON输出结构
- [x] Docker容器化
- [x] 技术链路通畅

### 🔄 待验证
- [ ] 真实图片准确率
- [ ] 不同光照条件
- [ ] 各种角度适应性
- [ ] OpenClaw集成测试

## 📁 项目文件说明

```
hazard-detection-mvp/
├── app.py              # FastAPI主应用
├── detector.py         # 核心检测算法
├── visual_detector.py  # 可视化工具
├── requirements.txt    # 依赖列表
├── Dockerfile         # 容器化配置
└── README.md          # 完整文档
```

## 🚀 下一步测试建议

1. **环境准备**: 在本地安装Python 3.8+和依赖
2. **数据收集**: 准备20-30张测试图片
3. **准确率测试**: 运行完整算法验证
4. **性能优化**: 根据测试结果调整参数
5. **生产部署**: Docker容器化部署

---

**生成时间**: 2026-03-21  
**版本**: 可视化报告 v1.0  
**状态**: 技术链路验证完成，待真实数据测试
"""
    
    return diagram

def save_visualization_files():
    """保存可视化文件"""
    
    # 创建工作流程图
    workflow_diagram = create_workflow_diagram()
    
    # 保存为Markdown
    with open("workflow_visualization.md", "w", encoding="utf-8") as f:
        f.write(workflow_diagram)
    
    # 创建JSON格式的流程说明
    workflow_json = {
        "algorithm_name": "Fire Extinguisher Pressure Gauge Detection",
        "version": "1.0.0",
        "workflow_steps": [
            {
                "step": 1,
                "name": "Object Detection",
                "algorithm": "YOLOv8",
                "input": "Raw image",
                "output": "Fire extinguisher bounding box",
                "visualization": "Red rectangle",
                "parameters": {
                    "model": "yolov8n.pt",
                    "confidence_threshold": 0.5,
                    "input_size": [640, 640]
                }
            },
            {
                "step": 2,
                "name": "Gauge Localization",
                "algorithm": "Hough Circle Transform",
                "input": "Fire extinguisher ROI",
                "output": "Gauge center and radius",
                "visualization": "Blue circle",
                "parameters": {
                    "dp": 1,
                    "minDist": 50,
                    "param1": 50,
                    "param2": 30,
                    "minRadius": 10,
                    "maxRadius": 100
                }
            },
            {
                "step": 3,
                "name": "Pointer Detection",
                "algorithm": "Hough Line Transform",
                "input": "Gauge region",
                "output": "Pointer angle (0-360°)",
                "visualization": "Green line",
                "parameters": {
                    "rho": 1,
                    "theta": "np.pi/180",
                    "threshold": 20,
                    "minLineLength": "radius/2",
                    "maxLineGap": 10
                }
            },
            {
                "step": 4,
                "name": "Zone Judgment",
                "algorithm": "Rule-based classification",
                "input": "Pointer angle",
                "output": "Hazard detection result",
                "visualization": "Colored zones (green/yellow/red)",
                "rules": [
                    {"zone": "green", "range": [0, 120], "status": "正常"},
                    {"zone": "yellow", "range": [120, 240], "status": "警告"},
                    {"zone": "red", "range": [240, 360], "status": "隐患"}
                ]
            },
            {
                "step": 5,
                "name": "Result Output",
                "algorithm": "JSON serialization",
                "input": "All detection results",
                "output": "Structured JSON response",
                "visualization": "Formatted JSON display",
                "fields": [
                    "success",
                    "hazard_detected", 
                    "confidence",
                    "hazard_name",
                    "reasoning",
                    "evidence"
                ]
            }
        ],
        "performance_targets": {
            "accuracy": ">80%",
            "processing_time": "<300ms",
            "memory_usage": "~500MB",
            "concurrent_requests": "1 (可扩展)"
        },
        "verification_status": {
            "completed": [
                "API interface format",
                "Web upload interface", 
                "JSON output structure",
                "Docker containerization",
                "Technical workflow"
            ],
            "pending": [
                "Real image accuracy",
                "Lighting condition adaptation",
                "Angle variation handling",
                "OpenClaw integration"
            ]
        }
    }
    
    # 保存JSON
    with open("workflow_details.json", "w", encoding="utf-8") as f:
        json.dump(workflow_json, f, ensure_ascii=False, indent=2)
    
    # 创建简单的HTML可视化
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>隐患检测算法工作流程可视化</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .step {{ border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        .step-header {{ display: flex; align-items: center; margin-bottom: 10px; }}
        .step-number {{ background: #4CAF50; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; }}
        .visualization {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; font-family: monospace; }}
        .status-completed {{ color: #4CAF50; font-weight: bold; }}
        .status-pending {{ color: #ff9800; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 隐患检测算法工作流程可视化</h1>
        
        <div class="step">
            <div class="step-header">
                <div class="step-number">1</div>
                <h3>目标检测 (YOLOv8)</h3>
            </div>
            <p><strong>输入:</strong> 原始图片</p>
            <p><strong>输出:</strong> 灭火器边界框 [x1, y1, x2, y2]</p>
            <div class="visualization">
                ┌─────────────────────┐<br>
                │     灭火器区域       │<br>
                │    [红色矩形框]      │<br>
                └─────────────────────┘
            </div>
        </div>
        
        <div class="step">
            <div class="step-header">
                <div class="step-number">2</div>
                <h3>压力表定位 (霍夫圆检测)</h3>
            </div>
            <p><strong>输入:</strong> 灭火器区域</p>
            <p><strong>输出:</strong> 圆心坐标, 半径</p>
            <div class="visualization">
                &nbsp;&nbsp;&nbsp;○───── 压力表<br>
                &nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;\\<br>
                &nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\\<br>
                /&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\\<br>
                [蓝色圆形]
            </div>
        </div>
        
        <div class="step">
            <div class="step-header">
                <div class="step-number">3</div>
                <h3>指针检测 (霍夫直线检测)</h3>
            </div>
            <p><strong>输入:</strong> 压力表区域</p>
            <p><strong>输出:</strong> 指针角度 (0-360°)</p>
            <div class="visualization">
                &nbsp;&nbsp;&nbsp;○──→ 指针方向<br>
                &nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;\\<br>
                &nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\\<br>
                /&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\\<br>
                [绿色直线]
            </div>
        </div>
        
        <div class="step">
            <div class="step-header">
                <div class="step-number">4</div>
                <h3>区域判断 (规则引擎)</h3>
            </div>
            <p><strong>规则:</strong></p>
            <ul>
                <li>绿区(0-120°): 正常 ✅</li>
                <li>黄区(120-240°): 警告 ⚠️</li>
                <li>红区(240-360°): 隐患 ❌</li>
            </ul>
            <div class="visualization">
                绿区 ███ 黄区 ███ 红区 ███
            </div>
        </div>
        
        <div class="step">
            <div class="step-header">
                <div class="step-number">5</div>
                <h3>结果输出 (JSON格式)</h3>
            </div>
            <p><strong>输出示例:</strong></p>
            <div class="visualization">
                {{<br>
                &nbsp;&nbsp;"success": true,<br>
                &nbsp;&nbsp;"hazard_detected": false,<br>
                &nbsp;&nbsp;"confidence": 0.92,<br>
                &nbsp;&nbsp;"hazard_name": "灭火器压力表正常"<br>
                }}
            </div>
        </div>
        
        <h2>📊 验证状态</h2>
        <p><span class="status-completed">✅ 已完成:</span> API接口、Web界面、Docker配置、技术链路</p>
        <p><span class="status-pending">⏳ 待验证:</span> 真实算法准确率、性能测试、OpenClaw集成</p>
        
        <h2>🚀 下一步</h2>
        <p>1. 在本地环境安装依赖并运行完整版本</p>
        <p>2. 收集真实测试图片验证准确率</p>
        <p>3. 根据测试结果优化算法参数</p>
    </div>
</body>
</html>"""
    
    with open("workflow_visualization.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ 可视化文件已生成:")
    print("   📄 workflow_visualization.md - Markdown格式")
    print("   📊 workflow_details.json - JSON详细说明")
    print("   🌐 workflow_visualization.html - HTML可视化")
    
    return [
        "workflow_visualization.md",
        "workflow_details.json", 
        "workflow_visualization.html"
    ]

def main():
    """主函数"""
    print("🎨 生成隐患检测算法可视化...")
    files = save_visualization_files()
    print(f"\n📁 生成 {len(files)} 个可视化文件")
    print("🎯 可视化完成！")

if __name__ == "__main__":
    main()