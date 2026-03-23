// 可视化演示 - JavaScript部分

// 全局变量
let selectedFile = null;
let originalImageData = null;

// DOM元素
const fileInput = document.getElementById('fileInput');
const detectBtn = document.getElementById('detectBtn');
const uploadArea = document.getElementById('uploadArea');
const loading = document.getElementById('loading');
const errorBox = document.getElementById('errorBox');
const errorMessage = document.getElementById('errorMessage');
const successBox = document.getElementById('successBox');
const successMessage = document.getElementById('successMessage');
const resultsSection = document.getElementById('resultsSection');
const originalImage = document.getElementById('originalImage');
const annotatedImage = document.getElementById('annotatedImage');
const statusBadge = document.getElementById('statusBadge');
const hazardName = document.getElementById('hazardName');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceFill = document.getElementById('confidenceFill');
const detectionMode = document.getElementById('detectionMode');
const reasoningList = document.getElementById('reasoningList');
const evidenceTable = document.getElementById('evidenceTable');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('算法可视化演示已加载');
    
    // 设置拖拽功能
    setupDragAndDrop();
    
    // 文件选择事件
    fileInput.addEventListener('change', handleFileSelect);
});

// 设置拖拽功能
function setupDragAndDrop() {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('dragover');
        }, false);
    });
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelect({ target: { files: files } });
        }
    }
}

// 处理文件选择
function handleFileSelect(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    // 验证文件类型
    if (!file.type.match('image.*')) {
        showError('请选择图片文件（JPG、PNG）');
        return;
    }
    
    selectedFile = file;
    
    // 预览原始图片
    const reader = new FileReader();
    reader.onload = function(e) {
        originalImageData = e.target.result;
        originalImage.src = originalImageData;
        
        // 启用检测按钮
        detectBtn.disabled = false;
        detectBtn.textContent = '开始检测';
        
        // 隐藏之前的结果和错误
        resultsSection.style.display = 'none';
        errorBox.style.display = 'none';
        successBox.style.display = 'none';
        
        // 显示预览提示
        showSuccess('图片已选择，点击"开始检测"查看算法可视化');
    };
    reader.readAsDataURL(file);
}

// 使用测试图片
function useTestImage(type) {
    let testUrl = '';
    let testName = '';
    
    switch(type) {
        case 'green':
            testUrl = 'https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=绿区正常+灭火器';
            testName = '绿区正常测试图';
            break;
        case 'yellow':
            testUrl = 'https://via.placeholder.com/600x400/FF9800/FFFFFF?text=黄区警告+灭火器';
            testName = '黄区警告测试图';
            break;
        case 'red':
            testUrl = 'https://via.placeholder.com/600x400/F44336/FFFFFF?text=红区隐患+灭火器';
            testName = '红区隐患测试图';
            break;
        case 'random':
            testUrl = 'https://via.placeholder.com/600x400/2196F3/FFFFFF?text=随机测试+灭火器';
            testName = '随机测试图';
            break;
    }
    
    // 创建模拟文件对象
    selectedFile = {
        name: testName + '.jpg',
        type: 'image/jpeg'
    };
    
    originalImageData = testUrl;
    originalImage.src = testUrl;
    
    detectBtn.disabled = false;
    detectBtn.textContent = '开始检测';
    
    resultsSection.style.display = 'none';
    errorBox.style.display = 'none';
    showSuccess('测试图片已加载，点击"开始检测"查看模拟可视化');
}

// 处理图片
function processImage() {
    if (!selectedFile) {
        showError('请先选择图片');
        return;
    }
    
    // 显示加载
    loading.style.display = 'block';
    resultsSection.style.display = 'none';
    errorBox.style.display = 'none';
    successBox.style.display = 'none';
    detectBtn.disabled = true;
    detectBtn.textContent = '检测中...';
    
    // 如果是测试图片，使用模拟数据
    if (selectedFile.name && selectedFile.name.includes('测试图')) {
        setTimeout(() => {
            showMockResults();
        }, 1500);
        return;
    }
    
    // 真实API调用
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    // 调用可视化API
    fetch('/api/check_visual', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        displayResults(data);
    })
    .catch(error => {
        showError('检测失败: ' + error.message);
        // 失败时显示模拟结果
        showMockResults();
    })
    .finally(() => {
        loading.style.display = 'none';
        detectBtn.disabled = false;
        detectBtn.textContent = '重新检测';
    });
}

// 显示模拟结果（用于演示）
function showMockResults() {
    const isHazard = Math.random() > 0.5;
    const confidence = 0.7 + Math.random() * 0.25;
    const angle = Math.floor(Math.random() * 360);
    
    let zone = 'green';
    let zoneName = '绿区';
    if (angle >= 120 && angle < 240) {
        zone = 'yellow';
        zoneName = '黄区';
    } else if (angle >= 240) {
        zone = 'red';
        zoneName = '红区';
    }
    
    const mockData = {
        detection_result: {
            success: true,
            hazard_detected: isHazard,
            confidence: confidence,
            hazard_name: isHazard ? '灭火器压力表异常' : '灭火器压力表正常',
            reasoning: [
                `模拟检测到灭火器 (置信度: ${(confidence * 0.9).toFixed(2)})`,
                `估计压力表位置 (半径: ${30 + Math.floor(Math.random() * 30)}px)`,
                `模拟指针角度: ${angle.toFixed(1)}°`,
                `指针位于${zoneName}`,
                '注：当前为模拟演示数据'
            ],
            evidence: {
                fire_extinguisher_bbox: [
                    100 + Math.floor(Math.random() * 100),
                    80 + Math.floor(Math.random() * 100),
                    400 + Math.floor(Math.random() * 100),
                    300 + Math.floor(Math.random() * 100)
                ],
                gauge_center: [
                    250 + Math.floor(Math.random() * 100),
                    180 + Math.floor(Math.random() * 100)
                ],
                gauge_radius: 30 + Math.floor(Math.random() * 30),
                pointer_angle: angle,
                zone: zone
            },
            mode: 'simulation'
        },
        annotated_image: originalImageData  // 使用原始图片作为占位
    };
    
    displayResults(mockData);
    loading.style.display = 'none';
    detectBtn.disabled = false;
    detectBtn.textContent = '重新检测';
}

// 显示结果
function displayResults(data) {
    const result = data.detection_result;
    
    // 显示标注图片
    if (data.annotated_image) {
        annotatedImage.src = data.annotated_image;
    } else {
        annotatedImage.src = originalImageData;
    }
    
    // 更新状态
    if (result.hazard_detected) {
        statusBadge.textContent = '隐患 ❌';
        statusBadge.className = 'status-badge status-hazard';
    } else {
        statusBadge.textContent = '正常 ✅';
        statusBadge.className = 'status-badge status-normal';
    }
    
    // 更新隐患名称
    hazardName.textContent = result.hazard_name || '未知状态';
    
    // 更新置信度
    const confidencePercent = Math.round(result.confidence * 100);
    confidenceValue.textContent = confidencePercent + '%';
    confidenceFill.style.width = confidencePercent + '%';
    
    // 更新检测模式
    detectionMode.textContent = result.mode === 'simulation' ? '模拟模式（演示数据）' : '真实检测模式';
    
    // 更新推理过程
    reasoningList.innerHTML = '';
    if (result.reasoning && Array.isArray(result.reasoning)) {
        result.reasoning.forEach(reason => {
            const li = document.createElement('li');
            li.textContent = reason;
            reasoningList.appendChild(li);
        });
    }
    
    // 更新证据表格
    updateEvidenceTable(result.evidence || {});
    
    // 显示成功消息
    showSuccess('检测完成！查看下方可视化结果');
    
    // 显示结果区域
    resultsSection.style.display = 'block';
    
    // 滚动到结果
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// 更新证据表格
function updateEvidenceTable(evidence) {
    const tableBody = document.querySelector('#evidenceTable tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    const evidenceData = [
        { key: '灭火器边界框', value: evidence.fire_extinguisher_bbox ? `[${evidence.fire_extinguisher_bbox.join(', ')}]` : '未检测' },
        { key: '压力表中心', value: evidence.gauge_center ? `(${evidence.gauge_center[0]}, ${evidence.gauge_center[1]})` : '未定位' },
        { key: '压力表半径', value: evidence.gauge_radius ? evidence.gauge_radius + 'px' : '未知' },
        { key: '指针角度', value: evidence.pointer_angle ? evidence.pointer_angle.toFixed(1) + '°' : '未检测' },
        { key: '区域', value: getZoneName(evidence.zone) },
        { key: '检测状态', value: evidence.gauge_detected === false ? '估计值' : '检测值' }
    ];
    
    evidenceData.forEach(item => {
        const row = document.createElement('tr');
        
        const keyCell = document.createElement('td');
        keyCell.textContent = item.key;
        keyCell.style.fontWeight = '600';
        
        const valueCell = document.createElement('td');
        valueCell.textContent = item.value;
        
        row.appendChild(keyCell);
        row.appendChild(valueCell);
        tableBody.appendChild(row);
    });
}

// 获取区域名称
function getZoneName(zone) {
    switch(zone) {
        case 'green': return '绿区（正常）';
        case 'yellow': return '黄区（警告）';
        case 'red': return '红区（隐患）';
        default: return '未知';
    }
}

// 显示错误
function showError(message) {
    errorMessage.textContent = message;
    errorBox.style.display = 'block';
    errorBox.scrollIntoView({ behavior: 'smooth' });
}

// 显示成功
function showSuccess(message) {
    successMessage.textContent = message;
    successBox.style.display = 'block';
}

// 重置表单
function resetForm() {
    fileInput.value = '';
    selectedFile = null;
    originalImageData = null;
    originalImage.src = '';
    annotatedImage.src = '';
    resultsSection.style.display = 'none';
    errorBox.style.display = 'none';
    successBox.style.display = 'none';
    detectBtn.disabled = true;
    detectBtn.textContent = '开始检测';
}

// 测试API连通性
function testAPI() {
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            alert('API服务正常\n' + JSON.stringify(data, null, 2));
        })
        .catch(error => {
            alert('API测试失败: ' + error.message);
        });
}

// 导出功能
function exportResults() {
    const results = {
        timestamp: new Date().toISOString(),
        image: selectedFile ? selectedFile.name : '测试图片',
        results: {
            status: document.querySelector('.status-badge').textContent,
            confidence: confidenceValue.textContent,
            hazardName: hazardName.textContent
        }
    };
    
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `detection_results_${new Date().getTime()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

// 分享功能
function shareResults() {
    if (navigator.share) {
        navigator.share({
            title: '隐患检测结果',
            text: `检测状态: ${hazardName.textContent}, 置信度: ${confidenceValue.textContent}`,
            url: window.location.href
        });
    } else {
        alert('分享功能需要现代浏览器支持。结果已复制到剪贴板。');
        navigator.clipboard.writeText(`隐患检测结果：${hazardName.textContent}，置信度：${confidenceValue.textContent}`);
    }
}