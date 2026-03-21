#!/usr/bin/env python3
"""
可视化检测器 - 展示算法工作流程
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arrow
import matplotlib

# 使用非交互式后端（适合服务器）
matplotlib.use('Agg')

class VisualDetector:
    """可视化检测器，展示算法每一步"""
    
    def __init__(self):
        self.steps = []
        self.figures = []
        
    def add_step(self, image, title, description=None):
        """添加一个步骤的可视化"""
        self.steps.append({
            'image': image.copy(),
            'title': title,
            'description': description
        })
    
    def simulate_detection(self, image_path):
        """模拟检测过程并生成可视化"""
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            # 创建模拟图像
            image = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        # 步骤1：原始图像
        self.add_step(image, "1. 原始图像", "输入的安全隐患图片")
        
        # 步骤2：灭火器检测（模拟YOLO）
        img_with_bbox = image.copy()
        cv2.rectangle(img_with_bbox, (100, 80), (500, 350), (255, 0, 0), 3)
        cv2.putText(img_with_bbox, "灭火器检测", (120, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        self.add_step(img_with_bbox, "2. 目标检测", "YOLOv8检测灭火器边界框")
        
        # 步骤3：压力表定位
        img_with_gauge = image.copy()
        center = (300, 150)
        radius = 40
        cv2.circle(img_with_gauge, center, radius, (0, 0, 255), 3)
        cv2.putText(img_with_gauge, "压力表定位", (center[0]-60, center[1]-radius-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        self.add_step(img_with_gauge, "3. 压力表定位", "霍夫圆检测找到表盘")
        
        # 步骤4：指针检测
        img_with_pointer = image.copy()
        # 画指针
        angle = 45  # 模拟绿区
        length = 30
        end_x = int(center[0] + length * np.cos(np.radians(angle)))
        end_y = int(center[1] + length * np.sin(np.radians(angle)))
        cv2.line(img_with_pointer, center, (end_x, end_y), (0, 255, 0), 3)
        cv2.putText(img_with_pointer, f"指针角度: {angle}°", (center[0]+50, center[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        self.add_step(img_with_pointer, "4. 指针检测", "霍夫直线检测找到指针方向")
        
        # 步骤5：区域判断
        img_with_zones = image.copy()
        # 画区域弧线
        cv2.ellipse(img_with_zones, center, (35, 35), 0, 0, 120, (0, 255, 0), 3)  # 绿区
        cv2.ellipse(img_with_zones, center, (35, 35), 0, 120, 240, (0, 255, 255), 3)  # 黄区
        cv2.ellipse(img_with_zones, center, (35, 35), 0, 240, 360, (0, 0, 255), 3)  # 红区
        
        # 添加图例
        cv2.putText(img_with_zones, "绿区: 正常", (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(img_with_zones, "黄区: 警告", (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(img_with_zones, "红区: 隐患", (20, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # 判断结果
        if 0 <= angle < 120:
            result = "正常 (绿区)"
            color = (0, 255, 0)
        elif 120 <= angle < 240:
            result = "警告 (黄区)"
            color = (0, 255, 255)
        else:
            result = "隐患 (红区)"
            color = (0, 0, 255)
        
        cv2.putText(img_with_zones, f"判断: {result}", (center[0]-80, center[1]+100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        self.add_step(img_with_zones, "5. 区域判断", f"指针在{angle}°，判断为{result}")
        
        # 步骤6：最终结果
        img_final = image.copy()
        # 合并所有标注
        cv2.rectangle(img_final, (100, 80), (500, 350), (255, 0, 0), 2)
        cv2.circle(img_final, center, radius, (0, 0, 255), 2)
        cv2.line(img_final, center, (end_x, end_y), (0, 255, 0), 3)
        
        # 添加结果文本
        cv2.putText(img_final, "隐患检测结果:", (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(img_final, f"• 检测到灭火器", (40, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(img_final, f"• 定位压力表", (40, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(img_final, f"• 指针角度: {angle}°", (40, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(img_final, f"• 判断: {result}", (40, 160), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        self.add_step(img_final, "6. 最终结果", "完整的检测流程可视化")
        
        return self.steps
    
    def create_visualization_report(self, output_path="detection_visualization.png"):
        """创建可视化报告"""
        if not self.steps:
            return None
        
        # 创建子图
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for idx, step in enumerate(self.steps[:6]):  # 最多显示6个步骤
            ax = axes[idx]
            # 转换BGR到RGB
            img_rgb = cv2.cvtColor(step['image'], cv2.COLOR_BGR2RGB)
            ax.imshow(img_rgb)
            ax.set_title(f"{step['title']}", fontsize=12, fontweight='bold')
            if step['description']:
                ax.text(0.5, -0.15, step['description'], 
                       transform=ax.transAxes, ha='center', fontsize=9,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            ax.axis('off')
        
        plt.suptitle("🔥 隐患检测算法工作流程可视化", fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 可视化报告已保存: {output_path}")
        return output_path
    
    def create_html_report(self, output_path="visual_report.html"):
        """创建HTML可视化报告"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>隐患检测算法可视化报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 30px; }
        .step { margin: 20px 0; padding: 15px; border-left: 5px solid #4CAF50; background: #f9f9f9; }
        .step-title { font-weight: bold; color: #333; margin-bottom: 10px; }
        .step-desc { color: #666; margin-bottom: 10px; }
        .image-container { text-align: center; margin: 10px 0; }
        .image-container img { max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }
        .workflow { display: flex; flex-wrap: wrap; justify-content: space-between; }
        .workflow-step { width: 30%; margin: 10px 0; }
        .result-box { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .legend { display: flex; justify-content: center; margin: 20px 0; }
        .legend-item { margin: 0 15px; display: flex; align-items: center; }
        .legend-color { width: 20px; height: 20px; margin-right: 8px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 隐患检测算法工作流程可视化</h1>
            <p>灭火器压力表检测 - 算法步骤分解</p>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #ff0000;"></div>
                <span>灭火器检测 (YOLO)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #0000ff;"></div>
                <span>压力表定位 (霍夫圆)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #00ff00;"></div>
                <span>指针检测 (霍夫直线)</span>
            </div>
        </div>
        
        <h2>📊 检测流程</h2>
        <div class="workflow">
"""
        
        # 添加步骤
        for idx, step in enumerate(self.steps):
            # 保存步骤图片
            step_img_path = f"step_{idx+1}.png"
            cv2.imwrite(step_img_path, step['image'])
            
            html += f"""
            <div class="workflow-step">
                <div class="step">
                    <div class="step-title">步骤 {idx+1}: {step['title']}</div>
                    <div class="step-desc">{step['description'] or ''}</div>
                    <div class="image-container">
                        <img src="{step_img_path}" alt="步骤{idx+1}">
                    </div>
                </div>
            </div>
            """
        
        html += """
        </div>
        
        <div class="result-box">
            <h3>🎯 算法原理</h3>
            <p><strong>技术栈:</strong> YOLOv8 + OpenCV + 霍夫变换</p>
            <p><strong>检测流程:</strong></p>
            <ol>
                <li><strong>目标检测:</strong> YOLOv8识别灭火器位置</li>
                <li><strong>区域定位:</strong> 霍夫圆检测找到压力表</li>
                <li><strong>特征提取:</strong> 霍夫直线检测指针方向</li>
                <li><strong>规则判断:</strong> 根据角度判断区域 (绿区:0-120°, 黄区:120-240°, 红区:240-360°)</li>
            </ol>
            
            <p><strong>输出格式:</strong> JSON结构化数据，包含检测结果、置信度、推理过程、证据数据</p>
        </div>
        
        <div class="result-box">
            <h3>🔧 技术验证状态</h3>
            <p>✅ <strong>技术链路验证完成:</strong> CV工具 + API + Web + Docker + OpenClaw调用</p>
            <p>⏳ <strong>待验证:</strong> 真实环境算法准确率测试</p>
            <p>📈 <strong>目标准确率:</strong> >80% (需真实数据验证)</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666; font-size: 0.9em;">
            <p>隐患检测MVP - 可视化报告 | 生成时间: 2026-03-21</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML可视化报告已保存: {output_path}")
        return output_path

def main():
    """主函数"""
    print("🎨 生成隐患检测算法可视化报告...")
    
    # 创建检测器
    detector = VisualDetector()
    
    # 模拟检测过程
    print("1. 模拟检测流程...")
    detector.simulate_detection("test_images/fire_extinguisher_green.jpg")
    
    # 生成可视化报告
    print("2. 生成可视化图像...")
    img_path = detector.create_visualization_report()
    
    # 生成HTML报告
    print("3. 生成HTML报告...")
    html_path = detector.create_html_report()
    
    print("\n" + "="*60)
    print("📊 可视化报告生成完成！")
    print("="*60)
    print(f"📷 图像报告: {img_path}")
    print(f"🌐 HTML报告: {html_path}")
    print("\n📋 报告包含:")
    print("   • 6步检测流程可视化")
    print("   • 算法原理说明")
    print("   • 技术验证状态")
    print("   • 交互式HTML界面")
    
    # 如果环境允许，尝试显示图像
    try:
        import matplotlib.pyplot as plt
        img = plt.imread(img_path)
        plt.figure(figsize=(12, 8))
        plt.imshow(img)
        plt.axis('off')
        plt.title("隐患检测算法工作流程", fontsize=14, fontweight='bold')
        plt.show()
    except:
        print("\n⚠️ 无法显示图像，请查看生成的文件")

if __name__ == "__main__":
    main()