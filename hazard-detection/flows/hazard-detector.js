const APIClient = require('../api/api-client');

class HazardDetector {
  constructor(apiBaseURL = 'http://localhost:3001') {
    this.apiClient = new APIClient(apiBaseURL);
  }

  /**
   * 隐患1: 用餐场所使用气瓶
   * 判断逻辑: scene == restaurant AND 存在 gas_cylinder
   */
  async detectGasCylinderInRestaurant(imageUrl, debug = false) {
    const apiResults = {};
    const reasoning = [];
    
    try {
      // 调用场景识别API
      const sceneResult = await this.apiClient.recognizeScene(imageUrl);
      apiResults.scene = sceneResult;
      reasoning.push(`场景识别结果: ${sceneResult.scene} (置信度: ${sceneResult.confidence})`);

      // 调用目标检测API
      const objects = await this.apiClient.detectObjects(imageUrl);
      apiResults.objects = objects;
      
      const gasCylinder = objects.find(obj => obj.label === 'gas_cylinder');
      reasoning.push(`目标检测结果: 找到${objects.length}个对象`);
      if (gasCylinder) {
        reasoning.push(`发现气瓶: 置信度 ${gasCylinder.confidence}`);
      } else {
        reasoning.push('未发现气瓶');
      }

      // 判断隐患
      const isRestaurant = sceneResult.scene === 'restaurant' && sceneResult.confidence > 0.7;
      const hasGasCylinder = gasCylinder && gasCylinder.confidence > 0.7;
      
      let hazard = null;
      if (isRestaurant && hasGasCylinder) {
        hazard = {
          hazard_name: '用餐场所使用气瓶',
          confidence: Math.min(sceneResult.confidence, gasCylinder.confidence),
          reasoning: reasoning,
          suggestion: '餐厅等用餐场所禁止使用液化气瓶，建议改用电磁炉等安全设备'
        };
      }

      return debug ? { api_results: apiResults, final_result: hazard } : hazard;

    } catch (error) {
      console.error('检测用餐场所气瓶失败:', error);
      return debug ? { api_results: apiResults, error: error.message } : null;
    }
  }

  /**
   * 隐患2: 无入户安检码
   * 判断逻辑: has_qr == false OR qr_valid == false
   */
  async detectNoInspectionQR(imageUrl, debug = false) {
    const apiResults = {};
    const reasoning = [];
    
    try {
      // 调用二维码解析API
      const codeResult = await this.apiClient.parseCode(imageUrl);
      apiResults.code = codeResult;
      
      reasoning.push(`二维码检测: ${codeResult.has_qr ? '有二维码' : '无二维码'}`);
      if (codeResult.has_qr) {
        reasoning.push(`二维码有效性: ${codeResult.qr_valid ? '有效' : '无效'}`);
        if (codeResult.inspection_date) {
          reasoning.push(`检查日期: ${codeResult.inspection_date}`);
        }
      }

      // 判断隐患
      const hasValidQR = codeResult.has_qr && codeResult.qr_valid;
      
      let hazard = null;
      if (!hasValidQR) {
        hazard = {
          hazard_name: '无入户安检码',
          confidence: 0.9,
          reasoning: reasoning,
          suggestion: '请张贴有效的入户安检二维码，确保安全检查信息可追溯'
        };
      }

      return debug ? { api_results: apiResults, final_result: hazard } : hazard;

    } catch (error) {
      console.error('检测安检码失败:', error);
      return debug ? { api_results: apiResults, error: error.message } : null;
    }
  }

  /**
   * 隐患3: 安检超期
   * 判断逻辑: inspection_date == null OR 当前时间 - inspection_date > 180天
   */
  async detectInspectionExpired(imageUrl, debug = false) {
    const apiResults = {};
    const reasoning = [];
    
    try {
      // 调用二维码解析API
      const codeResult = await this.apiClient.parseCode(imageUrl);
      apiResults.code = codeResult;
      
      reasoning.push(`二维码检测: ${codeResult.has_qr ? '有二维码' : '无二维码'}`);
      
      let hazard = null;
      
      if (codeResult.has_qr && codeResult.qr_valid && codeResult.inspection_date) {
        const inspectionDate = new Date(codeResult.inspection_date);
        const now = new Date();
        const daysDiff = Math.floor((now - inspectionDate) / (1000 * 60 * 60 * 24));
        
        reasoning.push(`检查日期: ${codeResult.inspection_date}`);
        reasoning.push(`距离今天: ${daysDiff} 天`);
        
        if (daysDiff > 180) {
          hazard = {
            hazard_name: '安检超期',
            confidence: 0.95,
            reasoning: reasoning,
            suggestion: `安全检查已超期${daysDiff - 180}天，请立即安排重新检查`
          };
        } else {
          reasoning.push(`安全检查在有效期内（剩余${180 - daysDiff}天）`);
        }
      } else {
        reasoning.push('无有效检查日期信息');
      }

      return debug ? { api_results: apiResults, final_result: hazard } : hazard;

    } catch (error) {
      console.error('检测安检超期失败:', error);
      return debug ? { api_results: apiResults, error: error.message } : null;
    }
  }

  /**
   * 隐患4: 报警器高度异常
   * 判断逻辑: distance_cm > 30
   */
  async detectAlarmHeightAbnormal(imageUrl, points = [], debug = false) {
    const apiResults = {};
    const reasoning = [];
    
    try {
      // 调用距离测量API
      const distanceResult = await this.apiClient.measureDistance(imageUrl, points);
      apiResults.distance = distanceResult;
      
      reasoning.push(`测量距离: ${distanceResult.distance_cm}cm (置信度: ${distanceResult.confidence})`);
      
      let hazard = null;
      
      if (distanceResult.distance_cm > 30 && distanceResult.confidence > 0.7) {
        hazard = {
          hazard_name: '报警器高度异常',
          confidence: distanceResult.confidence,
          reasoning: reasoning,
          suggestion: `报警器安装高度${distanceResult.distance_cm}cm超过标准30cm，建议调整至合适高度`
        };
      } else if (distanceResult.confidence > 0.7) {
        reasoning.push(`报警器高度正常: ${distanceResult.distance_cm}cm`);
      }

      return debug ? { api_results: apiResults, final_result: hazard } : hazard;

    } catch (error) {
      console.error('检测报警器高度失败:', error);
      return debug ? { api_results: apiResults, error: error.message } : null;
    }
  }

  /**
   * 隐患5: 疏散指示标志异常
   * 判断逻辑: is_lit == false OR is_damaged == true
   */
  async detectExitSignAbnormal(imageUrl, debug = false) {
    const apiResults = {};
    const reasoning = [];
    
    try {
      // 调用状态识别API
      const statusResult = await this.apiClient.detectStatus(imageUrl);
      apiResults.status = statusResult;
      
      reasoning.push(`疏散标志状态: ${statusResult.is_lit ? '亮起' : '未亮起'}, ${statusResult.is_damaged ? '损坏' : '完好'}`);
      
      let hazard = null;
      
      if (!statusResult.is_lit || statusResult.is_damaged) {
        hazard = {
          hazard_name: '疏散指示标志异常',
          confidence: 0.9,
          reasoning: reasoning,
          suggestion: '疏散指示标志应保持常亮且完好无损，请立即维修或更换'
        };
      } else {
        reasoning.push('疏散指示标志状态正常');
      }

      return debug ? { api_results: apiResults, final_result: hazard } : hazard;

    } catch (error) {
      console.error('检测疏散标志失败:', error);
      return debug ? { api_results: apiResults, error: error.message } : null;
    }
  }

  /**
   * 执行所有隐患检测
   */
  async detectAllHazards(imageUrl, points = [], debug = false) {
    const hazards = [];
    const apiResults = {};
    const debugResults = {};

    console.log(`开始检测图片: ${imageUrl}`);
    
    try {
      // 并行执行所有隐患检测
      const [
        hazard1,
        hazard2,
        hazard3,
        hazard4,
        hazard5
      ] = await Promise.all([
        this.detectGasCylinderInRestaurant(imageUrl, debug),
        this.detectNoInspectionQR(imageUrl, debug),
        this.detectInspectionExpired(imageUrl, debug),
        this.detectAlarmHeightAbnormal(imageUrl, points, debug),
        this.detectExitSignAbnormal(imageUrl, debug)
      ]);

      // 收集所有隐患
      if (hazard1 && (debug ? hazard1.final_result : hazard1)) {
        hazards.push(debug ? hazard1.final_result : hazard1);
      }
      if (hazard2 && (debug ? hazard2.final_result : hazard2)) {
        hazards.push(debug ? hazard2.final_result : hazard2);
      }
      if (hazard3 && (debug ? hazard3.final_result : hazard3)) {
        hazards.push(debug ? hazard3.final_result : hazard3);
      }
      if (hazard4 && (debug ? hazard4.final_result : hazard4)) {
        hazards.push(debug ? hazard4.final_result : hazard4);
      }
      if (hazard5 && (debug ? hazard5.final_result : hazard5)) {
        hazards.push(debug ? hazard5.final_result : hazard5);
      }

      // 收集调试信息
      if (debug) {
        debugResults.gas_cylinder = hazard1;
        debugResults.no_qr = hazard2;
        debugResults.expired = hazard3;
        debugResults.height = hazard4;
        debugResults.exit_sign = hazard5;
      }

      console.log(`检测完成，发现 ${hazards.length} 个隐患`);

      if (debug) {
        return {
          api_results: debugResults,
          final_result: {
            hazards: hazards,
            summary: {
              total_hazards: hazards.length,
              image_url: imageUrl,
              timestamp: new Date().toISOString()
            }
          }
        };
      } else {
        return {
          hazards: hazards,
          summary: {
            total_hazards: hazards.length,
            image_url: imageUrl,
            timestamp: new Date().toISOString()
          }
        };
      }

    } catch (error) {
      console.error('整体检测失败:', error);
      return debug ? 
        { api_results: {}, error: error.message } : 
        { hazards: [], error: error.message };
    }
  }
}

module.exports = HazardDetector;