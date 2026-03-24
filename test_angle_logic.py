#!/usr/bin/env python3
"""
测试灭火器压力表角度判断逻辑
分析为什么即使角度划分可能不准确，但结果仍然正确
"""

import math

def simple_judge(angle):
    """简单的0-360°判断"""
    if 0 <= angle < 120:
        return "绿区"
    elif 120 <= angle < 240:
        return "黄区"
    else:  # 240-360
        return "红区"

def realistic_judge(angle, gauge_start=225, gauge_range=90):
    """实际的灭火器压力表判断"""
    # 将角度映射到压力表范围
    if angle < gauge_start:
        mapped = 0
    elif angle > gauge_start + gauge_range:
        mapped = 100
    else:
        mapped = ((angle - gauge_start) / gauge_range) * 100
    
    # 根据映射值判断
    if mapped < 33:
        return "绿区"
    elif mapped < 66:
        return "黄区"
    else:
        return "红区"

def test_angles():
    """测试不同角度下的判断结果"""
    print("角度测试分析")
    print("=" * 60)
    print(f"{'角度(°)':<10} {'简单判断':<10} {'实际判断':<10} {'是否一致':<10}")
    print("-" * 60)
    
    test_cases = [
        (220, "绿区边缘"),
        (230, "绿区中间"),
        (250, "黄区中间"),
        (270, "黄区偏右"),
        (290, "红区中间"),
        (310, "红区边缘"),
    ]
    
    consistent = 0
    total = len(test_cases)
    
    for angle, desc in test_cases:
        simple = simple_judge(angle)
        realistic = realistic_judge(angle)
        same = "✓" if simple == realistic else "✗"
        
        if simple == realistic:
            consistent += 1
        
        print(f"{angle:>5}° {desc:<12} {simple:<10} {realistic:<10} {same:<10}")
    
    print("-" * 60)
    print(f"一致性: {consistent}/{total} ({consistent/total*100:.1f}%)")

def analyze_reasons():
    """分析可能的原因"""
    print("\n🔍 为什么结果可能正确？")
    print("=" * 60)
    
    reasons = [
        "1. 实际代码可能已经做了角度偏移校正",
        "2. 测试图片的角度分布恰好匹配简单划分",
        "3. 算法可能使用相对位置而非绝对角度",
        "4. 压力表范围可能接近120°而非90°",
        "5. 指针检测可能有一定误差，但仍在正确区间内",
        "6. 颜色区域边界有重叠，容错性较高",
    ]
    
    for reason in reasons:
        print(reason)

def simulate_real_scenarios():
    """模拟真实场景"""
    print("\n🎯 真实场景模拟")
    print("=" * 60)
    
    # 假设压力表实际范围：225°-315° (90°)
    # 绿区：225°-255° (30°)
    # 黄区：255°-285° (30°)
    # 红区：285°-315° (30°)
    
    scenarios = [
        ("绿区正常", 240),
        ("绿黄边界", 255),
        ("黄区中间", 270),
        ("黄红边界", 285),
        ("红区危险", 300),
    ]
    
    for desc, real_angle in scenarios:
        simple = simple_judge(real_angle)
        realistic = realistic_judge(real_angle)
        
        print(f"{desc}: {real_angle}° → 简单: {simple}, 实际: {realistic}", end="")
        
        if simple == realistic:
            print(" ✅")
        else:
            print(" ❌ (可能误判)")
            
            # 计算误判时的角度
            if simple == "绿区" and realistic == "黄区":
                print(f"   警告: 绿区边缘可能被误判为黄区")
            elif simple == "黄区" and realistic == "红区":
                print(f"   警告: 黄区边缘可能被误判为红区")

def main():
    print("🔥 灭火器压力表角度判断分析")
    print("=" * 60)
    
    test_angles()
    analyze_reasons()
    simulate_real_scenarios()
    
    print("\n" + "=" * 60)
    print("💡 结论:")
    print("1. 如果压力表范围接近120°，简单划分可能偶然正确")
    print("2. 测试图片可能避开了边界情况")
    print("3. 实际代码可能有隐藏的校正逻辑")
    print("4. 建议查看实际代码确认实现")
    print("=" * 60)

if __name__ == "__main__":
    main()