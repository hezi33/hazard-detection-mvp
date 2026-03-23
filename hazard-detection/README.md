# 隐患识别平台 (Hazard Detection Platform)

基于图片的隐患识别平台（MVP版本），具备AI能力调用、规则判断和可解释输出功能。

## 🎯 项目目标

构建一个基于图片的隐患识别平台，具备以下能力：

### ✅ 输入
- 图片（必选）
- 用户点击点位（用于测量，可选）

### ✅ 输出
系统返回结构化隐患结果：
```json
{
  "hazards": [
    {
      "hazard_name": "",
      "confidence": 0.0,
      "reasoning": [],
      "suggestion": ""
    }
  ]
}
```

### ✅ 核心能力
- 调用外部AI能力API
- 执行隐患判断规则
- 输出可解释结果
- 支持单图调试与批量测试

## 🏗️ 系统架构

```
用户输入（图片）
  ↓
OpenClaw流程编排
  ↓
调用外部API（HTTP）
  ↓
规则判断
  ↓
输出隐患结果
```

## 📦 安装与运行

### 1. 安装依赖
```bash
cd hazard-detection
npm install
```

### 2. 启动Mock API服务器（用于测试）
```bash
npm run mock-api
```
Mock API服务器将在 http://localhost:3001 运行

### 3. 启动主服务器
```bash
npm start
```
主服务器将在 http://localhost:3000 运行

### 4. 访问Web界面
打开浏览器访问：http://localhost:3000/web/index.html

## 🔧 API接口

### 主服务器 (端口: 3000)

#### 1. 健康检查
```
GET /health
```

#### 2. 单图隐患检测
```
POST /detect
Content-Type: multipart/form-data 或 application/json

参数：
- image_url: 图片URL（可选）
- image: 上传的图片文件（可选）
- points: 测量点位 [[x1,y1], [x2,y2]]（可选）
- debug: true/false（可选，是否返回调试信息）
```

#### 3. 批量测试
```
POST /batch-test
Content-Type: application/json

参数：
- test_cases: 测试用例数组
```

#### 4. 获取支持的隐患类型
```
GET /hazard-types
```

### Mock API服务器 (端口: 3001)

#### 1. 目标检测
```
POST /detect_objects
```

#### 2. 场景识别
```
POST /recognize_scene
```

#### 3. 二维码解析
```
POST /parse_code
```

#### 4. 距离测量
```
POST /measure_distance
```

#### 5. 状态识别
```
POST /detect_status
```

## 🚨 支持的隐患类型

### 1. 用餐场所使用气瓶
- **判断逻辑**: `scene == restaurant AND 存在 gas_cylinder`
- **所需API**: 场景识别 + 目标检测

### 2. 无入户安检码
- **判断逻辑**: `has_qr == false OR qr_valid == false`
- **所需API**: 二维码解析

### 3. 安检超期
- **判断逻辑**: `inspection_date == null OR 当前时间 - inspection_date > 180天`
- **所需API**: 二维码解析

### 4. 报警器高度异常
- **判断逻辑**: `distance_cm > 30`
- **所需API**: 距离测量

### 5. 疏散指示标志异常
- **判断逻辑**: `is_lit == false OR is_damaged == true`
- **所需API**: 状态识别

## 🧪 测试与调试

### 单图调试
```bash
node debug/debug-single.js <image_url> [points_json]
```

示例：
```bash
node debug/debug-single.js "https://example.com/test.jpg" "[[100,100],[200,200]]"
```

### 批量测试
```bash
node debug/debug-single.js --batch data/minimal-dataset.json
```

### 自动化测试
```bash
node test/test-runner.js data/minimal-dataset.json --html --json
```

## 📁 项目结构

```
hazard-detection/
├── api/                    # API客户端
│   └── api-client.js      # API调用封装
├── flows/                 # 隐患流程
│   ├── flow-manager.js    # 流程管理器
│   └── hazard-detector.js # 隐患检测器
├── mock/                  # Mock API
│   └── mock-server.js     # 模拟API服务器
├── debug/                 # 调试工具
│   └── debug-single.js    # 单图调试工具
├── test/                  # 测试工具
│   └── test-runner.js     # 测试运行器
├── data/                  # 测试数据
│   └── minimal-dataset.json # 最小数据集
├── web/                   # Web界面
│   └── index.html         # 前端界面
├── index.js              # 主服务器
├── package.json          # 项目配置
└── README.md             # 项目文档
```

## 🔌 接入真实AI能力

要接入真实AI能力，需要：

1. **替换Mock API**：将 `mock/mock-server.js` 中的模拟函数替换为真实API调用
2. **配置API密钥**：在环境变量中设置AI服务API密钥
3. **调整API端点**：修改 `api/api-client.js` 中的API端点

### 推荐的真实AI服务：
- **目标检测**: YOLO, TensorFlow Object Detection API
- **场景识别**: CLIP, Scene Recognition models
- **二维码解析**: ZXing, Quirc
- **距离测量**: 基于深度学习的单目测距
- **状态识别**: 图像分类模型

## 📊 性能指标

- **响应时间**: < 5秒（包含所有API调用）
- **准确率**: 可通过批量测试验证
- **可扩展性**: 支持新增隐患类型和API
- **可解释性**: 提供完整的推理过程

## 🚀 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd hazard-detection
```

2. **安装并运行**
```bash
npm install
npm run mock-api  # 在第一个终端
npm start         # 在第二个终端
```

3. **打开Web界面**
访问 http://localhost:3000/web/index.html

4. **测试功能**
- 上传图片或输入图片URL
- 点击"开始检测"
- 查看检测结果和推理过程

## 📝 开发指南

### 添加新的隐患类型

1. 在 `flows/hazard-detector.js` 中添加新的检测方法
2. 在 `flows/flow-manager.js` 中注册新流程
3. 更新Web界面显示新的隐患类型

### 添加新的API

1. 在 `api/api-client.js` 中添加新的API调用方法
2. 在 `mock/mock-server.js` 中添加对应的Mock API
3. 更新相关隐患检测流程

### 扩展调试功能

1. 修改 `debug/debug-single.js` 添加新的调试选项
2. 更新Web界面的调试面板

## 🔒 安全注意事项

1. **API密钥管理**: 不要将API密钥硬编码在代码中
2. **输入验证**: 对所有用户输入进行验证和清理
3. **文件上传**: 限制上传文件类型和大小
4. **错误处理**: 避免泄露敏感信息在错误消息中

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 📞 支持与反馈

如有问题或建议，请提交Issue或联系维护者。

---

**注意**: 本系统为MVP版本，实际生产使用需要接入真实AI能力和进行充分的测试验证。