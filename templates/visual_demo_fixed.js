// 可视化演示 - 修复版本

// 全局变量
let selectedFile = null;
let originalImageData = null;

// 初始化 - 确保DOM完全加载
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 修复版JS加载完成');
    
    // 获取DOM元素
    const fileInput = document.getElementById('fileInput');
    const detectBtn = document.getElementById('detectBtn');
    const originalImage = document.getElementById('originalImage');
    
    console.log('DOM元素检查:');
    console.log('- fileInput:', fileInput ? '找到' : '未找到');
    console.log('- detectBtn:', detectBtn ? '找到' : '未找到');
    console.log('- originalImage:', originalImage ? '找到' : '未找到');
    
    if (!fileInput) {
        console.error('❌ 关键元素fileInput未找到，检查HTML');
        return;
    }
    
    // 修复1: 直接绑定事件，避免HTML中的onclick问题
    fileInput.addEventListener('change', handleFileSelectFixed);
    
    // 修复2: 确保按钮点击触发文件选择
    if (detectBtn) {
        detectBtn.addEventListener('click', function() {
            console.log('检测按钮被点击');
            if (selectedFile) {
                processImage();
            } else {
                alert('请先选择图片');
            }
        });
    }
    
    // 修复3: 添加上传区域点击事件
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.addEventListener('click', function() {
            console.log('上传区域被点击');
            fileInput.click();
        });
    }
});

// 修复的文件选择处理函数
function handleFileSelectFixed(event) {
    console.log('🔧 handleFileSelectFixed被调用');
    
    const files = event.target.files;
    if (!files || files.length === 0) {
        console.log('没有选择文件');
        return;
    }
    
    const file = files[0];
    console.log('选择文件:', file.name, file.type, file.size + ' bytes');
    
    // 验证文件类型
    if (!file.type.match('image.*')) {
        alert('请选择图片文件（JPG、PNG）');
        return;
    }
    
    selectedFile = file;
    
    // 使用更可靠的方式预览
    previewImage(file);
}

// 独立的图片预览函数
function previewImage(file) {
    console.log('开始预览图片...');
    
    const reader = new FileReader();
    const originalImage = document.getElementById('originalImage');
    const detectBtn = document.getElementById('detectBtn');
    
    if (!originalImage) {
        console.error('originalImage元素未找到');
        return;
    }
    
    reader.onload = function(e) {
        console.log('FileReader读取成功');
        originalImageData = e.target.result;
        
        // 设置图片源
        originalImage.src = originalImageData;
        
        // 添加加载事件监听
        originalImage.onload = function() {
            console.log('✅ 图片加载完成:', originalImage.naturalWidth + 'x' + originalImage.naturalHeight);
            
            // 启用检测按钮
            if (detectBtn) {
                detectBtn.disabled = false;
                detectBtn.textContent = '开始检测';
                console.log('检测按钮已启用');
            }
            
            // 显示成功消息
            showMessage('图片已选择，点击"开始检测"查看算法可视化', 'success');
        };
        
        originalImage.onerror = function() {
            console.error('❌ 图片加载失败');
            showMessage('图片加载失败，请检查文件格式', 'error');
        };
    };
    
    reader.onerror = function(e) {
        console.error('FileReader错误:', e.target.error);
        showMessage('文件读取失败: ' + e.target.error.message, 'error');
    };
    
    reader.readAsDataURL(file);
}

// 显示消息的辅助函数
function showMessage(text, type) {
    console.log('显示消息:', text, type);
    
    // 尝试更新页面上的消息区域
    const successBox = document.getElementById('successBox');
    const errorBox = document.getElementById('errorBox');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    
    if (type === 'success' && successBox && successMessage) {
        successMessage.textContent = text;
        successBox.style.display = 'block';
        if (errorBox) errorBox.style.display = 'none';
    } else if (type === 'error' && errorBox && errorMessage) {
        errorMessage.textContent = text;
        errorBox.style.display = 'block';
        if (successBox) successBox.style.display = 'none';
    } else {
        // 如果找不到消息元素，使用alert
        alert(text);
    }
}

// 简化的处理图片函数
function processImage() {
    console.log('开始处理图片...');
    
    if (!selectedFile) {
        showMessage('请先选择图片', 'error');
        return;
    }
    
    const detectBtn = document.getElementById('detectBtn');
    if (detectBtn) {
        detectBtn.disabled = true;
        detectBtn.textContent = '检测中...';
    }
    
    // 模拟检测过程
    setTimeout(function() {
        console.log('模拟检测完成');
        
        // 显示模拟结果
        const annotatedImage = document.getElementById('annotatedImage');
        if (annotatedImage && originalImageData) {
            annotatedImage.src = originalImageData;
        }
        
        // 显示结果区域
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        // 恢复按钮
        if (detectBtn) {
            detectBtn.disabled = false;
            detectBtn.textContent = '重新检测';
        }
        
        showMessage('检测完成！查看下方可视化结果', 'success');
        
    }, 1500); // 模拟1.5秒检测时间
}

// 测试函数
function testFileAPI() {
    console.log('测试File API...');
    console.log('FileReader:', typeof FileReader);
    console.log('File:', typeof File);
    console.log('Blob:', typeof Blob);
    
    // 创建测试图片
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 150;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#4CAF50';
    ctx.fillRect(0, 0, 200, 150);
    ctx.fillStyle = 'white';
    ctx.font = '24px Arial';
    ctx.fillText('测试图片', 50, 80);
    
    const dataUrl = canvas.toDataURL('image/jpeg');
    console.log('测试图片创建成功');
    
    // 模拟文件选择
    const byteString = atob(dataUrl.split(',')[1]);
    const mimeString = dataUrl.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], {type: mimeString});
    const file = new File([blob], 'test.jpg', {type: mimeString});
    
    const event = {
        target: {
            files: [file]
        }
    };
    
    handleFileSelectFixed(event);
}