#!/usr/bin/env node

const axios = require('axios');
const fs = require('fs');
const path = require('path');

class TestRunner {
  constructor(serverURL = 'http://localhost:3000') {
    this.serverURL = serverURL;
    this.client = axios.create({
      baseURL: serverURL,
      timeout: 30000
    });
  }

  /**
   * 运行单个测试用例
   */
  async runTestCase(testCase) {
    try {
      const response = await this.client.post('/detect', {
        image_url: testCase.image_url,
        points: testCase.points || [],
        debug: 'false'
      });

      const hasHazard = response.data.hazards && response.data.hazards.length > 0;
      const expectedHasHazard = testCase.expected === '有隐患';
      
      return {
        test_case: testCase,
        result: response.data,
        passed: hasHazard === expectedHasHazard,
        actual: hasHazard ? '有隐患' : '无隐患',
        hazards_found: response.data.hazards || []
      };
    } catch (error) {
      return {
        test_case: testCase,
        error: error.message,
        passed: false
      };
    }
  }

  /**
   * 运行测试套件
   */
  async runTestSuite(testSuite) {
    console.log(`🧪 运行测试套件: ${testSuite.name || '未命名套件'}`);
    console.log(`测试用例数量: ${testSuite.test_cases.length}`);
    console.log('─'.repeat(50));

    const results = [];
    let passed = 0;
    let failed = 0;

    for (let i = 0; i < testSuite.test_cases.length; i++) {
      const testCase = testSuite.test_cases[i];
      console.log(`\n测试 ${i + 1}/${testSuite.test_cases.length}: ${testCase.image_url}`);
      
      const result = await this.runTestCase(testCase);
      results.push(result);

      if (result.passed) {
        console.log('  ✅ 通过');
        passed++;
      } else {
        console.log('  ❌ 失败');
        if (result.error) {
          console.log(`    错误: ${result.error}`);
        } else {
          console.log(`    预期: ${testCase.expected}`);
          console.log(`    实际: ${result.actual}`);
          if (result.hazards_found.length > 0) {
            console.log(`    发现隐患: ${result.hazards_found.map(h => h.hazard_name).join(', ')}`);
          }
        }
        failed++;
      }
    }

    // 统计信息
    const accuracy = testSuite.test_cases.length > 0 ? 
      (passed / testSuite.test_cases.length * 100).toFixed(2) : 0;

    const summary = {
      total: testSuite.test_cases.length,
      passed: passed,
      failed: failed,
      accuracy: `${accuracy}%`,
      timestamp: new Date().toISOString()
    };

    console.log('\n' + '─'.repeat(50));
    console.log('📊 测试结果汇总:');
    console.log(JSON.stringify(summary, null, 2));

    return {
      summary: summary,
      results: results,
      test_suite: testSuite
    };
  }

  /**
   * 加载测试套件
   */
  loadTestSuite(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const testSuite = JSON.parse(content);
      
      // 验证测试套件格式
      if (!testSuite.test_cases || !Array.isArray(testSuite.test_cases)) {
        throw new Error('测试套件必须包含 test_cases 数组');
      }
      
      // 设置默认名称
      if (!testSuite.name) {
        testSuite.name = path.basename(filePath, '.json');
      }
      
      return testSuite;
    } catch (error) {
      console.error(`加载测试套件失败: ${error.message}`);
      return null;
    }
  }

  /**
   * 生成详细测试报告
   */
  generateDetailedReport(testResults, outputDir = 'test-reports') {
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const reportFile = path.join(outputDir, `test-report-${timestamp}.json`);
    
    const report = {
      metadata: {
        generated_at: new Date().toISOString(),
        server_url: this.serverURL,
        test_suite: testResults.test_suite.name
      },
      summary: testResults.summary,
      detailed_results: testResults.results.map(result => ({
        test_case: result.test_case,
        passed: result.passed,
        actual: result.actual,
        hazards_found: result.hazards_found,
        error: result.error
      }))
    };

    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
    console.log(`📄 详细测试报告已保存到: ${reportFile}`);
    
    return reportFile;
  }

  /**
   * 生成HTML测试报告
   */
  generateHTMLReport(testResults, outputDir = 'test-reports') {
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const htmlFile = path.join(outputDir, `test-report-${timestamp}.html`);
    
    const passed = testResults.summary.passed;
    const total = testResults.summary.total;
    const accuracy = testResults.summary.accuracy;
    
    let html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>隐患识别平台测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .passed { color: green; }
        .failed { color: red; }
        .test-case { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .test-case.passed { background: #e8f5e8; }
        .test-case.failed { background: #ffe8e8; }
        .hazard { background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .error { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🧪 隐患识别平台测试报告</h1>
    
    <div class="summary">
        <h2>测试概览</h2>
        <p><strong>测试套件:</strong> ${testResults.test_suite.name}</p>
        <p><strong>测试时间:</strong> ${new Date().toLocaleString()}</p>
        <p><strong>服务器地址:</strong> ${this.serverURL}</p>
        <p><strong>测试结果:</strong> <span class="${passed === total ? 'passed' : 'failed'}">${passed}/${total} 通过 (${accuracy})</span></p>
    </div>
    
    <h2>详细测试结果</h2>`;

    testResults.results.forEach((result, index) => {
      const testCase = result.test_case;
      const isPassed = result.passed;
      
      html += `
    <div class="test-case ${isPassed ? 'passed' : 'failed'}">
        <h3>测试 ${index + 1}: ${testCase.image_url}</h3>
        <p><strong>状态:</strong> <span class="${isPassed ? 'passed' : 'failed'}">${isPassed ? '✅ 通过' : '❌ 失败'}</span></p>
        <p><strong>预期:</strong> ${testCase.expected}</p>
        <p><strong>实际:</strong> ${result.actual || 'N/A'}</p>`;
      
      if (result.error) {
        html += `<p class="error">错误: ${result.error}</p>`;
      }
      
      if (result.hazards_found && result.hazards_found.length > 0) {
        html += `<p><strong>发现隐患:</strong></p>`;
        result.hazards_found.forEach(hazard => {
          html += `<div class="hazard">
              <strong>${hazard.hazard_name}</strong> (置信度: ${hazard.confidence})<br>
              <em>${hazard.suggestion}</em>
          </div>`;
        });
      }
      
      html += `</div>`;
    });

    html += `
</body>
</html>`;

    fs.writeFileSync(htmlFile, html);
    console.log(`🌐 HTML测试报告已保存到: ${htmlFile}`);
    
    return htmlFile;
  }
}

// 命令行接口
async function main() {
  const testRunner = new TestRunner();
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('使用方法:');
    console.log('  node test-runner.js <test_suite_file>');
    console.log('  node test-runner.js <test_suite_file> --html');
    console.log('  node test-runner.js <test_suite_file> --json');
    console.log('\n示例:');
    console.log('  node test-runner.js test-suites/basic.json');
    console.log('  node test-runner.js test-suites/basic.json --html --json');
    return;
  }

  const testSuiteFile = args[0];
  const generateHTML = args.includes('--html');
  const generateJSON = args.includes('--json') || !generateHTML; // 默认生成JSON
  
  // 加载测试套件
  const testSuite = testRunner.loadTestSuite(testSuiteFile);
  if (!testSuite) {
    console.error('无法加载测试套件');
    process.exit(1);
  }

  // 运行测试
  console.log('🚀 开始运行测试...');
  const results = await testRunner.runTestSuite(testSuite);
  
  // 生成报告
  if (generateJSON) {
    testRunner.generateDetailedReport(results);
  }
  
  if (generateHTML) {
    testRunner.generateHTMLReport(results);
  }
  
  // 根据测试结果退出
  if (results.summary.failed > 0) {
    console.log('\n⚠️  测试失败，请检查失败的测试用例');
    process.exit(1);
  } else {
    console.log('\n🎉 所有测试通过！');
    process.exit(0);
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('测试运行失败:', error);
    process.exit(1);
  });
}

module.exports = TestRunner;