const axios = require('axios');

class APIClient {
  constructor(baseURL = 'http://localhost:3001') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * 目标检测
   * @param {string} imageUrl - 图片URL
   * @returns {Promise<Array>} 检测到的对象列表
   */
  async detectObjects(imageUrl) {
    try {
      const response = await this.client.post('/detect_objects', {
        image_url: imageUrl
      });
      return response.data.objects || [];
    } catch (error) {
      console.error('目标检测API调用失败:', error.message);
      return [];
    }
  }

  /**
   * 场景识别
   * @param {string} imageUrl - 图片URL
   * @returns {Promise<Object>} 场景识别结果
   */
  async recognizeScene(imageUrl) {
    try {
      const response = await this.client.post('/recognize_scene', {
        image_url: imageUrl
      });
      return response.data;
    } catch (error) {
      console.error('场景识别API调用失败:', error.message);
      return { scene: 'unknown', confidence: 0 };
    }
  }

  /**
   * 二维码解析
   * @param {string} imageUrl - 图片URL
   * @returns {Promise<Object>} 二维码解析结果
   */
  async parseCode(imageUrl) {
    try {
      const response = await this.client.post('/parse_code', {
        image_url: imageUrl
      });
      return response.data;
    } catch (error) {
      console.error('二维码解析API调用失败:', error.message);
      return { has_qr: false, qr_valid: false, inspection_date: null };
    }
  }

  /**
   * 距离测量
   * @param {string} imageUrl - 图片URL
   * @param {Array} points - 点位坐标 [[x1,y1], [x2,y2]]
   * @returns {Promise<Object>} 距离测量结果
   */
  async measureDistance(imageUrl, points) {
    try {
      const response = await this.client.post('/measure_distance', {
        image_url: imageUrl,
        points: points
      });
      return response.data;
    } catch (error) {
      console.error('距离测量API调用失败:', error.message);
      return { distance_cm: 0, confidence: 0 };
    }
  }

  /**
   * 状态识别
   * @param {string} imageUrl - 图片URL
   * @returns {Promise<Object>} 状态识别结果
   */
  async detectStatus(imageUrl) {
    try {
      const response = await this.client.post('/detect_status', {
        image_url: imageUrl
      });
      return response.data;
    } catch (error) {
      console.error('状态识别API调用失败:', error.message);
      return { is_lit: false, is_damaged: false };
    }
  }

  /**
   * 批量调用所有API（用于调试）
   * @param {string} imageUrl - 图片URL
   * @param {Array} points - 点位坐标
   * @returns {Promise<Object>} 所有API结果
   */
  async callAllAPIs(imageUrl, points = []) {
    const results = {};
    
    try {
      console.log('开始调用所有API...');
      
      // 并行调用所有API
      const [
        objects,
        scene,
        code,
        distance,
        status
      ] = await Promise.all([
        this.detectObjects(imageUrl),
        this.recognizeScene(imageUrl),
        this.parseCode(imageUrl),
        this.measureDistance(imageUrl, points),
        this.detectStatus(imageUrl)
      ]);

      results.objects = objects;
      results.scene = scene;
      results.code = code;
      results.distance = distance;
      results.status = status;

      console.log('所有API调用完成');
      return results;
    } catch (error) {
      console.error('批量API调用失败:', error.message);
      return results;
    }
  }
}

module.exports = APIClient;