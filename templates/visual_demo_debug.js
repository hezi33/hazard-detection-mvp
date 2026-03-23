// 可视化演示 - 调试版本

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

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 调试: 页面加载完成');
    console.log('DOM元素检查:');
    console.log('- fileInput:', fileInput ? '找到' : '未找到');
    console.log('- originalImage:', originalImage ? '找到' : '未找到');
    console.log('- detectBtn:', detectBtn ? '找到' : '未找到');
    
    // 设置拖拽功能
    setupDragAndDrop();
    
    // 文件选择事件 - 添加详细日志
    fileInput.addEventListener('change', function(e) {
        console.log('🔍 调试: fileInput change事件触发');
        console.log('事件对象:', e);
        console.log('files:', e.target.files);
        handleFileSelect(e);
    });
});

// 处理文件选择 - 调试版本
function handleFileSelect(event) {
    console.log('🔍 调试: handleFileSelect被调用');
    console.log('event:', event);
    console.log('event.target:', event.target);
    console.log('event.target.files:', event.target.files);
    
    const files = event.target.files;
    if (!files) {
        console.error('❌ 错误: files为null或undefined');
        showError('无法获取文件列表');
        return;
    }
    
    if (files.length === 0) {
        console.warn('⚠️ 警告: 文件列表为空');
        return;
    }
    
    const file = files[0];
    console.log('🔍 文件信息:');
    console.log('- 名称:', file.name);
    console.log('- 类型:', file.type);
    console.log('- 大小:', file.size, 'bytes');
    console.log('- 最后修改:', file.lastModified);
    
    // 验证文件类型
    if (!file.type.match('image.*')) {
        console.error('❌ 错误: 非图片文件类型:', file.type);
        showError('请选择图片文件（JPG、PNG）');
        return;
    }
    
    selectedFile = file;
    console.log('✅ 文件验证通过，selectedFile已设置');
    
    // 预览原始图片
    const reader = new FileReader();
    
    reader.onloadstart = function() {
        console.log('🔍 FileReader: 开始读取文件');
    };
    
    reader.onprogress = function(e) {
        if (e.lengthComputable) {
            const percent = (e.loaded / e.total * 100).toFixed(1);
            console.log(`📊 FileReader: 读取进度 ${percent}%`);
        }
    };
    
    reader.onload = function(e) {
        console.log('✅ FileReader: 文件读取成功');
        console.log('结果类型:', typeof e.target.result);
        console.log('结果长度:', e.target.result.length);
        console.log('结果前100字符:', e.target.result.substring(0, 100));
        
        originalImageData = e.target.result;
        
        // 检查图片元素
        if (!originalImage) {
            console.error('❌ 错误: originalImage元素未找到');
            showError('页面元素加载不完整');
            return;
        }
        
        // 设置图片源
        originalImage.src = originalImageData;
        console.log('✅ 图片源已设置');
        
        // 检查图片加载
        originalImage.onload = function() {
            console.log('✅ 图片加载完成');
            console.log('图片尺寸:', originalImage.naturalWidth + 'x' + originalImage.naturalHeight);
        };
        
        originalImage.onerror = function() {
            console.error('❌ 图片加载失败');
            showError('图片加载失败，请检查文件格式');
        };
        
        // 启用检测按钮
        if (detectBtn) {
            detectBtn.disabled = false;
            detectBtn.textContent = '开始检测';
            console.log('✅ 检测按钮已启用');
        } else {
            console.error('❌ 错误: detectBtn元素未找到');
        }
        
        // 隐藏之前的结果和错误
        if (resultsSection) resultsSection.style.display = 'none';
        if (errorBox) errorBox.style.display = 'none';
        if (successBox) successBox.style.display = 'none';
        
        // 显示预览提示
        showSuccess('图片已选择，点击"开始检测"查看算法可视化');
        console.log('✅ 文件选择流程完成');
    };
    
    reader.onerror = function(e) {
        console.error('❌ FileReader错误:', e.target.error);
        showError('文件读取失败: ' + e.target.error.message);
    };
    
    reader.onabort = function() {
        console.warn('⚠️ FileReader: 读取被取消');
    };
    
    // 开始读取
    console.log('🔍 开始FileReader.readAsDataURL');
    reader.readAsDataURL(file);
}

// 简化的显示函数
function showError(message) {
    console.error('显示错误:', message);
    if (errorMessage) errorMessage.textContent = message;
    if (errorBox) errorBox.style.display = 'block';
}

function showSuccess(message) {
    console.log('显示成功:', message);
    if (successMessage) successMessage.textContent = message;
    if (successBox) successBox.style.display = 'block';
}

// 简化的其他函数
function setupDragAndDrop() {
    console.log('🔍 设置拖拽功能');
    // 简化实现
}

function processImage() {
    console.log('🔍 processImage被调用');
    alert('检测功能需要完整JS，请使用原版visual_demo.js');
}