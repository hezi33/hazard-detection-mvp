class FlowManager {
  constructor() {
    this.flows = new Map();
    this.initializeFlows();
  }

  initializeFlows() {
    // 定义5个隐患流程
    this.flows.set('gas_cylinder_in_restaurant', {
      id: 'gas_cylinder_in_restaurant',
      name: '用餐场所使用气瓶',
      description: '检测餐厅场景中是否存在气瓶',
      apis: ['recognize_scene', 'detect_objects'],
      enabled: true
    });

    this.flows.set('no_inspection_qr', {
      id: 'no_inspection_qr',
      name: '无入户安检码',
      description: '检测是否缺少有效二维码',
      apis: ['parse_code'],
      enabled: true
    });

    this.flows.set('inspection_expired', {
      id: 'inspection_expired',
      name: '安检超期',
      description: '检测安检是否超过180天',
      apis: ['parse_code'],
      enabled: true
    });

    this.flows.set('alarm_height_abnormal', {
      id: 'alarm_height_abnormal',
      name: '报警器高度异常',
      description: '检测报警器高度是否超过30cm',
      apis: ['measure_distance'],
      enabled: true
    });

    this.flows.set('exit_sign_abnormal', {
      id: 'exit_sign_abnormal',
      name: '疏散指示标志异常',
      description: '检测疏散指示标志是否损坏或不亮',
      apis: ['detect_status'],
      enabled: true
    });
  }

  /**
   * 获取所有流程
   */
  getAllFlows() {
    return Array.from(this.flows.values());
  }

  /**
   * 获取启用的流程
   */
  getEnabledFlows() {
    return this.getAllFlows().filter(flow => flow.enabled);
  }

  /**
   * 启用/禁用流程
   */
  setFlowEnabled(flowId, enabled) {
    if (this.flows.has(flowId)) {
      this.flows.get(flowId).enabled = enabled;
      return true;
    }
    return false;
  }

  /**
   * 添加新流程
   */
  addFlow(flow) {
    if (!flow.id || this.flows.has(flow.id)) {
      return false;
    }
    
    this.flows.set(flow.id, {
      ...flow,
      enabled: flow.enabled !== undefined ? flow.enabled : true
    });
    
    return true;
  }

  /**
   * 删除流程
   */
  removeFlow(flowId) {
    return this.flows.delete(flowId);
  }

  /**
   * 获取流程执行计划
   * 优化API调用，避免重复调用相同API
   */
  getExecutionPlan() {
    const enabledFlows = this.getEnabledFlows();
    const apiDependencies = {};
    
    // 收集每个API依赖哪些流程
    enabledFlows.forEach(flow => {
      flow.apis.forEach(api => {
        if (!apiDependencies[api]) {
          apiDependencies[api] = [];
        }
        apiDependencies[api].push(flow.id);
      });
    });

    return {
      flows: enabledFlows,
      apiDependencies: apiDependencies,
      totalAPICalls: Object.keys(apiDependencies).length
    };
  }

  /**
   * 验证流程配置
   */
  validateFlow(flow) {
    const errors = [];
    
    if (!flow.id) errors.push('流程ID不能为空');
    if (!flow.name) errors.push('流程名称不能为空');
    if (!Array.isArray(flow.apis) || flow.apis.length === 0) {
      errors.push('必须指定至少一个API');
    }
    
    // 验证API名称
    const validAPIs = ['detect_objects', 'recognize_scene', 'parse_code', 'measure_distance', 'detect_status'];
    flow.apis.forEach(api => {
      if (!validAPIs.includes(api)) {
        errors.push(`无效的API名称: ${api}`);
      }
    });

    return {
      valid: errors.length === 0,
      errors: errors
    };
  }

  /**
   * 导出流程配置
   */
  exportConfig() {
    return {
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      total_flows: this.flows.size,
      enabled_flows: this.getEnabledFlows().length,
      flows: this.getAllFlows()
    };
  }

  /**
   * 导入流程配置
   */
  importConfig(config) {
    if (!config.flows || !Array.isArray(config.flows)) {
      return false;
    }

    this.flows.clear();
    config.flows.forEach(flow => {
      const validation = this.validateFlow(flow);
      if (validation.valid) {
        this.flows.set(flow.id, flow);
      } else {
        console.warn(`跳过无效流程 ${flow.id}:`, validation.errors);
      }
    });

    return true;
  }
}

module.exports = FlowManager;