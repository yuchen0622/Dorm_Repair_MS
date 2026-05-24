/**
 * 宿舍报修管理系统 - 前端交互脚本
 */

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initMessages();
    initForms();
});

/**
 * 初始化消息提示
 * 5秒后自动隐藏消息
 */
function initMessages() {
    var messages = document.querySelectorAll('.message');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * 初始化表单验证
 * 检查必填字段是否已填写
 */
function initForms() {
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var requiredFields = form.querySelectorAll('[required]');
            var isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('请填写所有必填项');
            }
        });
    });
}

/**
 * 删除确认弹窗
 * @param {string} message - 确认提示信息
 * @returns {boolean} 用户是否确认
 */
function confirmDelete(message) {
    return confirm(message || '确定要删除吗？');
}

/**
 * 显示按钮加载状态
 * @param {HTMLElement} button - 按钮元素
 */
function showLoading(button) {
    var originalText = button.textContent;
    button.disabled = true;
    button.textContent = '处理中...';
    button.dataset.originalText = originalText;
}

/**
 * 恢复按钮原始状态
 * @param {HTMLElement} button - 按钮元素
 */
function hideLoading(button) {
    button.disabled = false;
    button.textContent = button.dataset.originalText;
}
