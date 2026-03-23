const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// 模拟数据生成器
class MockDataGenerator {
  static generateObjects(imageUrl) {
    // 根据图片URL生成不同的对象检测结果
    const url = imageUrl.toLowerCase();
    const objects = [];

    if (url.includes('restaurant') || url.includes('kitchen')) {
      objects.push(
        { label: 'gas_cylinder', confidence: 0.92 },
        { label: 'stove', confidence: 0.88 },
        { label: 'table', confidence: 0.95 }
      );
    } else if (url.includes('exit') || url.includes('sign')) {
      objects.push(
        { label: 'exit_sign', confidence: 0.96 },
        { label: 'alarm', confidence: 0.85 },
        { label: 'fire_extinguisher', confidence: 0.78 }
      );
    } else {
      // 默认对象
      objects.push(
        { label: 'person', confidence: 0.90 },
        { label: 'chair', confidence: 0.85 },
        { label: 'door', confidence: 0.88 }
      );
    }

    return objects;
  }

  static generateScene(imageUrl) {
    const url = imageUrl.toLowerCase();
    
    if (url.includes('restaurant') || url.includes('kitchen') || url.includes('food')) {
      return { scene: 'restaurant', confidence: 0.91 };
    } else if (url.includes('office') || url.includes('desk')) {
      return { scene: 'office', confidence: 0.87 };
    } else if (url.includes('home') || url.includes('house')) {
      return { scene: 'home', confidence: 0.89 };
    } else {
      return { scene: 'unknown', confidence: 0.5 };
    }
  }

  static generateCode(imageUrl) {
    const url = imageUrl.toLowerCase();
    const hasQr = !url.includes('no_qr');
    const qrValid = hasQr && !url.includes('invalid');
    
    let inspectionDate = null;
    if (qrValid) {
      // 随机生成检查日期
      const daysAgo = Math.floor(Math.random() * 365);
      const date = new Date();
      date.setDate(date.getDate() - daysAgo);
      inspectionDate = date.toISOString().split('T')[0];
    }

    return {
      has_qr: hasQr,
      qr_valid: qrValid,
      inspection_date: inspectionDate
    };
  }

  static generateDistance(imageUrl, points) {
    // 如果提供了点位，基于点位生成距离
    let distance = 25; // 默认25cm
    
    if (points && points.length >= 2) {
      // 简单计算两点距离（假设图片尺寸为1000x1000）
      const [x1, y1] = points[0];
      const [x2, y2] = points[1];
      const pixelDistance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
      distance = Math.round((pixelDistance / 1000) * 100); // 转换为cm
    } else if (imageUrl.includes('high') || imageUrl.includes('tall')) {
      distance = 45; // 高度异常
    } else if (imageUrl.includes('low') || imageUrl.includes('short')) {
      distance = 15; // 高度正常
    }

    return {
      distance_cm: distance,
      confidence: 0.85
    };
  }

  static generateStatus(imageUrl) {
    const url = imageUrl.toLowerCase();
    const isLit = !url.includes('dark') && !url.includes('off');
    const isDamaged = url.includes('broken') || url.includes('damaged') || url.includes('crack');

    return {
      is_lit: isLit,
      is_damaged: isDamaged
    };
  }
}

// API端点

// 目标检测
app.post('/detect_objects', (req, res) => {
  const { image_url } = req.body;
  console.log(`目标检测请求: ${image_url}`);
  
  const objects = MockDataGenerator.generateObjects(image_url);
  res.json({ objects });
});

// 场景识别
app.post('/recognize_scene', (req, res) => {
  const { image_url } = req.body;
  console.log(`场景识别请求: ${image_url}`);
  
  const scene = MockDataGenerator.generateScene(image_url);
  res.json(scene);
});

// 二维码解析
app.post('/parse_code', (req, res) => {
  const { image_url } = req.body;
  console.log(`二维码解析请求: ${image_url}`);
  
  const code = MockDataGenerator.generateCode(image_url);
  res.json(code);
});

// 距离测量
app.post('/measure_distance', (req, res) => {
  const { image_url, points } = req.body;
  console.log(`距离测量请求: ${image_url}, 点位:`, points);
  
  const distance = MockDataGenerator.generateDistance(image_url, points);
  res.json(distance);
});

// 状态识别
app.post('/detect_status', (req, res) => {
  const { image_url } = req.body;
  console.log(`状态识别请求: ${image_url}`);
  
  const status = MockDataGenerator.generateStatus(image_url);
  res.json(status);
});

// 批量调用（调试用）
app.post('/batch_call', async (req, res) => {
  const { image_url, points } = req.body;
  console.log(`批量API调用请求: ${image_url}`);
  
  try {
    const results = {
      objects: MockDataGenerator.generateObjects(image_url),
      scene: MockDataGenerator.generateScene(image_url),
      code: MockDataGenerator.generateCode(image_url),
      distance: MockDataGenerator.generateDistance(image_url, points),
      status: MockDataGenerator.generateStatus(image_url)
    };
    
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Mock API服务器运行在 http://localhost:${PORT}`);
  console.log('可用端点:');
  console.log('  POST /detect_objects - 目标检测');
  console.log('  POST /recognize_scene - 场景识别');
  console.log('  POST /parse_code - 二维码解析');
  console.log('  POST /measure_distance - 距离测量');
  console.log('  POST /detect_status - 状态识别');
  console.log('  POST /batch_call - 批量调用所有API');
});