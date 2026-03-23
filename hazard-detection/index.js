const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// 导入流程管理器
const FlowManager = require('./flows/flow-manager');
const HazardDetector = require('./flows/hazard-detector');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(cors());
app.use(express.json());
app.use('/uploads', express.static('uploads'));

// 创建必要的目录
if (!fs.existsSync('uploads')) fs.mkdirSync('uploads');
if (!fs.existsSync('data')) fs.mkdirSync('data');

// 初始化流程管理器
const flowManager = new FlowManager();
const hazardDetector = new HazardDetector();

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 单图隐患检测
app.post('/detect', upload.single('image'), async (req, res) => {
  try {
    const imagePath = req.file ? req.file.path : null;
    const imageUrl = req.body.image_url || (imagePath ? `/uploads/${path.basename(imagePath)}` : null);
    const points = req.body.points || [];
    const debug = req.body.debug === 'true';

    if (!imageUrl) {
      return res.status(400).json({ error: '必须提供图片URL或上传图片' });
    }

    console.log(`开始检测隐患: ${imageUrl}`);
    
    // 执行所有隐患检测流程
    const results = await hazardDetector.detectAllHazards(imageUrl, points, debug);
    
    res.json(results);
  } catch (error) {
    console.error('检测失败:', error);
    res.status(500).json({ error: error.message });
  }
});

// 批量测试
app.post('/batch-test', async (req, res) => {
  try {
    const testCases = req.body.test_cases || [];
    const results = [];

    for (const testCase of testCases) {
      try {
        const result = await hazardDetector.detectAllHazards(
          testCase.image_url, 
          testCase.points || [],
          true
        );
        
        const hasHazard = result.hazards.length > 0;
        const expectedHasHazard = testCase.expected === '有隐患';
        const correct = hasHazard === expectedHasHazard;
        
        results.push({
          image_url: testCase.image_url,
          expected: testCase.expected,
          actual: hasHazard ? '有隐患' : '无隐患',
          correct: correct,
          hazards: result.hazards,
          error: correct ? null : '判断错误'
        });
      } catch (error) {
        results.push({
          image_url: testCase.image_url,
          error: error.message
        });
      }
    }

    const correctCount = results.filter(r => r.correct).length;
    const accuracy = testCases.length > 0 ? (correctCount / testCases.length * 100).toFixed(2) : 0;

    res.json({
      summary: {
        total: testCases.length,
        correct: correctCount,
        accuracy: `${accuracy}%`
      },
      results: results
    });
  } catch (error) {
    console.error('批量测试失败:', error);
    res.status(500).json({ error: error.message });
  }
});

// 获取支持的隐患类型
app.get('/hazard-types', (req, res) => {
  const hazardTypes = [
    {
      id: 'gas_cylinder_in_restaurant',
      name: '用餐场所使用气瓶',
      description: '检测餐厅场景中是否存在气瓶',
      api_required: ['recognize_scene', 'detect_objects']
    },
    {
      id: 'no_inspection_qr',
      name: '无入户安检码',
      description: '检测是否缺少有效二维码',
      api_required: ['parse_code']
    },
    {
      id: 'inspection_expired',
      name: '安检超期',
      description: '检测安检是否超过180天',
      api_required: ['parse_code']
    },
    {
      id: 'alarm_height_abnormal',
      name: '报警器高度异常',
      description: '检测报警器高度是否超过30cm',
      api_required: ['measure_distance']
    },
    {
      id: 'exit_sign_abnormal',
      name: '疏散指示标志异常',
      description: '检测疏散指示标志是否损坏或不亮',
      api_required: ['detect_status']
    }
  ];
  
  res.json({ hazard_types: hazardTypes });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`隐患识别平台运行在 http://localhost:${PORT}`);
  console.log('可用端点:');
  console.log('  GET  /health - 健康检查');
  console.log('  POST /detect - 单图隐患检测');
  console.log('  POST /batch-test - 批量测试');
  console.log('  GET  /hazard-types - 获取隐患类型');
});