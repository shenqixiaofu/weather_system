// static/js/profile.js

document.addEventListener('DOMContentLoaded', function () {

    // 处理夜间模式切换
    const darkModeToggle = document.getElementById('darkModeToggle');

    // 初始化主题
    function applyTheme(isDark) {
        if (isDark) {
            document.body.classList.add('dark-mode');
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            document.documentElement.setAttribute('data-theme', 'light');
        }
    }

    // 从HTML属性读取当前主题设置 - 检查多个可能的来源
    const htmlTheme = document.documentElement.getAttribute('data-theme');
    const bodyTheme = document.body.getAttribute('data-theme');
    const bodyClass = document.body.classList.contains('dark-mode');

    // 确定当前实际的主题状态
    const isDarkMode = (htmlTheme === 'dark' || bodyTheme === 'dark' || bodyClass);

    // 应用主题无论开关是否存在
    applyTheme(isDarkMode);

    // 只有在开关存在的情况下才处理开关逻辑
    if (darkModeToggle) {
        // 强制设置开关状态与实际主题一致
        darkModeToggle.checked = isDarkMode;

        darkModeToggle.addEventListener('change', function () {
            const isDark = this.checked;
            // 应用主题
            applyTheme(isDark);
            // 发送AJAX请求更新用户主题偏好
            fetch('/profile/update_preference', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    preference: 'theme',
                    value: isDark ? 'dark' : 'light'
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('主题偏好已保存到服务器');
                    } else {
                        console.error('保存主题偏好失败:', data.message);
                        // 如果保存失败，回滚开关状态
                        this.checked = !isDark;
                        applyTheme(!isDark);
                    }
                })
                .catch(error => {
                    console.error('请求出错:', error);
                    // 如果请求出错，回滚开关状态
                    this.checked = !isDark;
                    applyTheme(!isDark);
                });
        });
    }


    // 处理邮件通知切换
    const emailNotifyToggle = document.getElementById('emailNotifyToggle');
    if (emailNotifyToggle) {
        emailNotifyToggle.addEventListener('change', function () {
            // 发送AJAX请求更新用户通知偏好
            fetch('/profile/update_preference', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    preference: 'email_weather_alerts',
                    value: this.checked
                })
            });
        });
    }

    // 处理添加位置表单提交
    const addLocationForm = document.getElementById('addLocationForm');
    if (addLocationForm) {
        addLocationForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const cityName = document.getElementById('cityName').value;
            // 更新表单action
            this.action = `/favorite/add/${encodeURIComponent(cityName)}`;
            this.submit();
        });
    }

    // 获取所有清空表单
    const clearForms = document.querySelectorAll('.clear-activity-form');
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmClearModal'));
    let formToSubmit = null;

    // 为每个表单添加点击事件
    clearForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            formToSubmit = this;
            confirmModal.show();
        });
    });

    // 确认按钮点击事件
    document.getElementById('confirmClearBtn').addEventListener('click', function () {
        if (formToSubmit) {
            formToSubmit.submit();
        }
        confirmModal.hide();
    });

});

$(document).ready(function () {
    $('#load-more-btn').click(function () {
        var button = $(this);
        var page = button.data('page');
        var type = button.data('type');

        $.ajax({
            url: '/profile/load_more_activities',
            type: 'GET',
            data: {
                page: page,
                activity_type: type
            },
            success: function (data) {
                // 添加新内容到活动列表
                $('#activities-container').append(data.html);

                // 更新按钮状态
                if (data.has_more) {
                    button.data('page', data.next_page);
                } else {
                    $('#load-more-container').hide();
                }
            },
            error: function () {
                alert('加载更多活动时出错，请刷新页面重试。');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // 获取所有警告消息
    const alerts = document.querySelectorAll('.alert');

    // 设置3秒后自动消失
    alerts.forEach(alert => {
        setTimeout(function() {
            // 使用Bootstrap的dismiss方法关闭提示
            const closeBtn = alert.querySelector('.btn-close');
            if(closeBtn) closeBtn.click();
        }, 3000);
    });
});

