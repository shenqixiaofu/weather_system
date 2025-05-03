// static/js/login.js

// 页面加载动画和消息提示淡出
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

// 临时提示功能
function showComingSoon() {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info cosmic-alert';
    alertDiv.innerHTML = `
        <i class="fas fa-rocket"></i>
        该功能正在空间站研发中，敬请期待！
    `;
    document.querySelector('.flash-container').appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 3000);
}

// 防止重复提交
document.querySelector('form').addEventListener('submit', function(e) {
    const btn = this.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = '轨道对接中...';
});
