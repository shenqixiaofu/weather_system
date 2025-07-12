// static/js/register.js

// 显示错误消息的函数
function showError(message) {
    const errorContainer = document.getElementById('error-container');
    const errorText = document.getElementById('error-text');
    errorText.textContent = message;
    errorContainer.style.display = 'block';
    
    // 5秒后自动隐藏错误消息
    setTimeout(() => {
        errorContainer.style.display = 'none';
    }, 5000);
}

// 表单提交处理
document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    // 清除之前的错误消息
    document.getElementById('error-container').style.display = 'none';
    
    // 验证密码匹配
    if (password !== confirmPassword) {
        showError('两次输入的密码不匹配');
        return;
    }
    
    // 验证密码强度
    if (password.length < 8) {
        showError('密码长度至少需要8个字符');
        return;
    }
    
    // 验证用户名格式
    if (!/^[A-Za-z0-9]{4,20}$/.test(username)) {
        showError('用户名必须是4-20位字母数字组合');
        return;
    }
    
    // 如果验证通过，提交表单
    this.submit();
});

// 密码强度检查
function checkPasswordStrength(input) {
    const password = input.value;
    const strengthIndicator = input.parentElement.querySelector('.password-strength');
    
    if (!strengthIndicator) {
        const indicator = document.createElement('div');
        indicator.className = 'password-strength';
        input.parentElement.appendChild(indicator);
    }
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    const strengthText = ['弱', '较弱', '中等', '较强', '强'];
    const strengthColors = ['#ff4136', '#ff851b', '#ffdc00', '#2ecc40', '#0074d9'];
    
    strengthIndicator.textContent = `密码强度: ${strengthText[strength-1]}`;
    strengthIndicator.style.color = strengthColors[strength-1];
}

document.querySelector('[data-security-check]').addEventListener('input', checkPasswordStrength);
// 确认密码匹配检查 (与之前类似)
document.querySelector('[data-match]').addEventListener('input', function() {
    const password = document.getElementById('password').value;
    const confirmPassword = this.value;
    const matchIcon = this.nextElementSibling.querySelector('i'); // 获取 label 中的图标

    if (password === confirmPassword) {
        this.setCustomValidity('');
        matchIcon.style.color = '#2ecc40'; // 绿色
    } else {
        this.setCustomValidity('两次输入的密码不匹配');
        matchIcon.style.color = '#ff4136'; // 红色
    }
});

// 页面加载动画和消息提示淡出... (与之前相同)
document.addEventListener('DOMContentLoaded', function() {
    // 消息提示淡出
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => alert.style.opacity = 0);
    }, 3000);

    // 页面加载动画（可选）
    const container = document.querySelector('.auth-container');
        container.style.opacity = 0;
        container.style.transform = 'scale(0.9)';
        let opacity = 0;
        let scale = 0.9;
        const interval = setInterval(() => {
            opacity += 0.05;
            scale += 0.01;
            container.style.opacity = opacity;
            container.style.transform = `scale(${scale})`;
            if (opacity >= 1) clearInterval(interval);
        }, 20);
});

// 临时提示功能...
function showComingSoon() {
    showError('该功能正在研发中，敬请期待！');
}
