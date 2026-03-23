#!/usr/bin/env node

const axios = require('axios');
const fs = require('fs');
const path = require('path');

class DebugTool {
  constructor(serverURL = 'http://localhost:3000') {
    this.serverURL = serverURL;
    this.client = axios.create({
      baseURL: serverURL,
      timeout: 60000
    });
  }

  /**
   * 单图调试
   */
  async debugSingleImage(imageUrl, points = []) {
    console.log('🚀 开始单图调试...');
    console.log(`📷 图片: ${imageUrl}`);
    if (points.length > 0) {
      console.log(`📍 点位: ${JSON.stringify(points)}`);
    }
    console.log('─'.repeat(50));

    try {
      const response = await this.client.post('/detect', {
        image_url: imageUrl,
        points: points,
        debug: 'true'
      });

      const result = response.data;
      
      // 显示API结果
      console.log('\n📊 API调用结果:');
      console.log('─'.repeat(50));
      
      if (result.api_results) {
        Object.entries(result.api_results).forEach(([hazardType, hazardResult]) => {
          console.log(`\n🔍 ${this.getHazardName(hazardType)}:`);
          if (hazardResult.api_results) {
            Object.entries(hazardResult.api_results).forEach(([apiName, apiResult]) => {
              console.log(`  ${this.getAPIName(apiName)}:`, JSON.stringify(apiResult, null, 2));
            });
          }
          if (hazardResult.final_result) {
            console.log('  ✅ 发现隐患:', JSON.stringify(hazardResult.final_result, null, 2));
          } else if (hazardResult.error) {
            console.log('  ❌ 错误:', hazardResult.error);
          } else {
            console.log('  ✓ 未发现隐患');
          }
        });
      }

      // 显示最终结果
      console.log('\n🎯 最终检测结果:');
      console.log('─'.repeat(50));
      
      if (result.final_result && result.final_result.hazards) {
        const hazards = result.final_result.hazards;
        console.log(`发现 ${hazards.length} 个隐患:`);
        
        hazards.forEach((hazard, index) => {
          console.log(`\n${index + 1}. ${hazard.hazard_name} (置信度: ${hazard.confidence})`);
          console.log('   推理过程:');
          hazard.reasoning.forEach((reason, i) => {
            console.log(`     ${i + 1}. ${reason}`);
          });
          console.log(`   建议: ${hazard.suggestion}`);
        });
      } else {
        console.log('✅ 未发现任何隐患');
      }

      console.log('\n📈 统计信息:');
      console.log('─'.repeat(50));
      if (result.final_result && result.final_result.summary) {
        console.log(JSON.stringify(result.final_result.summary, null, 2));
      }

      return result;

    } catch (error) {
      console.error('❌ 调试失败:', error.message);
      if (error.response) {
        console.error('服务器响应:', error.response.data);
      }
      throw error;
    }
  }

  /**
   * 批量测试
   */
  async runBatchTest(testCases) {
    console.log('🧪 开始批量测试...');
    console.log(`测试用例数量: ${testCases.length}`);
    console.log('─'.repeat(50));

    try {
      const response = await this.client.post('/batch-test', {
        test_cases: testCases
      });

      const result = response.data;
      
      // 显示测试结果
      console.log('\n📋 测试结果:');
      console.log('─'.repeat(50));
      
      result.results.forEach((testResult, index) => {
        console.log(`\n测试 ${index + 1}: ${testResult.image_url}`);
        console.log(`  预期: ${testResult.expected}`);
        console.log(`  实际: ${testResult.actual}`);
        
        if (testResult.correct !== undefined) {
          if (testResult.correct) {
            console.log('  ✅ 正确');
          } else {
            console.log('  ❌ 错误');
            if (testResult.error) {
              console.log(`  原因: ${testResult.error}`);
            }
          }
        }
        
        if (testResult.hazards && testResult.hazards.length > 0) {
          console.log(`  发现隐患: ${testResult.hazards.length} 个`);
          testResult.hazards.forEach(hazard => {
            console.log(`    - ${hazard.hazard_name}`);
          });
        }
      });

      // 显示统计信息
      console.log('\n📊 测试统计:');
      console.log('─'.repeat(50));
      console.log(JSON.stringify(result.summary, null, 2));

      return result;

    } catch (error) {
      console.error('❌ 批量测试失败:', error.message);
      throw error;
    }
  }

  /**
   * 从文件加载测试用例
   */
  loadTestCasesFromFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const testCases = JSON.parse(content);
      
      if (!Array.isArray(testCases)) {
        throw new Error('测试用例文件必须包含数组');
      }
      
      return testCases;
    } catch (error) {
      console.error(`加载测试用例文件失败: ${error.message}`);
      return [];
    }
  }

  /**
   * 生成测试报告
   */
  generateReport(testResults, outputPath) {
    const report = {
      timestamp: new Date().toISOString(),
      summary: testResults.summary,
      details: testResults.results
    };

    fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
    console.log(`📄 测试报告已保存到: ${outputPath}`);
  }

  getHazardName(type) {
    const names = {
      'gas_cylinder': '用餐场所使用气瓶',
      'no_qr': '无入户安检码',
      'expired': '安检超期',
      'height': '报警器高度异常',
      'exit_sign': '疏散指示标志异常'
    };
    return names[type] || type;
  }

  getAPIName(api) {
    const names = {
      'scene': '场景识别',
      'objects': '目标检测',
      'code': '二维码解析',
      'distance': '距离测量',
      'status': '状态识别'
    };
    return names[api] || api;
  }
}

// 命令行接口
async function main() {
  const debugTool = new DebugTool();
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('使用方法:');
    console.log('  node debug-single.js <image_url> [points_json]');
    console.log('  node debug-single.js --batch <test_cases_file>');
    console.log('  node debug-single.js --test-report <output_file>');
    return;
  }

  if (args[0] === '--batch') {
    if (args.length < 2) {
      console.error('请提供测试用例文件路径');
      return;
    }
    
    const testCases = debugTool.loadTestCasesFromFile(args[1]);
    if (testCases.length === 0) {
      console.error('未找到有效的测试用例');
      return;
    }
    
    const results = await debugTool.runBatchTest(testCases);
    
    if (args[2] === '--save') {
      const outputFile = args[3] || `test-report-${Date.now()}.json`;
      debugTool.generateReport(results, outputFile);
    }
    
  } else {
    const imageUrl = args[0];
    let points = [];
    
    if (args.length > 1) {
      try {
        points = JSON.parse(args[1]);
      } catch (error) {
        console.error('点位参数必须是有效的JSON数组');
        return;
      }
    }
    
    await debugTool.debugSingleImage(imageUrl, points);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = DebugTool;