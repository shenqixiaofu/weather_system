// static/js/profile_settings.js

// 添加监听 storage 事件，用于同步不同页面的主题
window.addEventListener('storage', function () {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.body.classList.remove('dark-mode');
        document.documentElement.setAttribute('data-theme', 'light');
    }
});

// 页面滚动时高亮对应的导航项
document.addEventListener('DOMContentLoaded', function () {
    const sections = document.querySelectorAll('.settings-card');
    const navLinks = document.querySelectorAll('.settings-nav-link');

    // 平滑滚动到指定部分
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetSection = document.querySelector(targetId);
                window.scrollTo({
                    top: targetSection.offsetTop - 80,
                    behavior: 'smooth'
                });
                // 更新活动链接
                navLinks.forEach(navLink => navLink.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    // 滚动时更新活动链接
    window.addEventListener('scroll', function () {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                current = `#${section.getAttribute('id')}`;
            }
        });
        if (current) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === current) {
                    link.classList.add('active');
                }
            });
        }
    });

    // 头像上传预览
    const avatarUpload = document.getElementById('avatar-upload');
    if (avatarUpload) {
        avatarUpload.addEventListener('change', function (e) {
            if (e.target.files && e.target.files[0]) {  // 修正这里，需要指定索引<source_id data="0" title="app.py" />
                const reader = new FileReader();
                reader.onload = function (e) {
                    document.querySelector('.profile-picture').setAttribute('src', e.target.result);
                }
                reader.readAsDataURL(e.target.files[0]);
            }
        });
    }

    // 密码表单验证
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            // 验证新密码一致性
            if (newPassword !== confirmPassword) {
                alert('两次输入的密码不匹配，请重新确认');
                return false;
            }

            // 验证密码复杂度
            const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;
            if (!passwordRegex.test(newPassword)) {
                alert('密码不符合要求，需要至少6位，包含字母、数字');
                return false;
            }

            // 使用 fetch 提交表单
            fetch('/profile/change_password', {
                method: 'POST',
                body: new FormData(passwordForm),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => {
                    // 重要：检查响应状态
                    if (!response.ok) {
                        // 如果响应状态不是 200-299 范围
                        return response.json().then(errorData => {
                            throw new Error(errorData.message);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message);
                        // 可以添加重定向或其他操作
                        window.location.reload();
                    }
                })
                .catch(error => {
                    // 捕获并显示具体的错误消息
                    alert(error.message || '发生未知错误，请稍后重试');
                });
        });
    }

    // 处理通知设置复选框
    const notificationCheckboxes = document.querySelectorAll('#notifications-section input[type="checkbox"]');
    notificationCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const settingName = this.id;
            const isEnabled = this.checked;

            // 可选：添加加载状态，给用户视觉反馈
            this.disabled = true;

            fetch('/profile/update-notification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 如果使用 Flask-WTF，需要添加 CSRF token
                    // 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({
                    setting: settingName,
                    enabled: isEnabled
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        // 如果操作失败，恢复复选框状态
                        this.checked = !isEnabled;
                        // 可以使用更友好的通知方式
                        alert('设置保存失败: ' + data.message);
                    }
                })
                .catch(error => {
                    // 出错时恢复复选框状态
                    this.checked = !isEnabled;
                    console.error('Error:', error);
                    alert('设置保存失败，请稍后再试');
                })
                .finally(() => {
                    // 恢复复选框可用状态
                    this.disabled = false;
                });
        });
    });

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

    // 处理偏好设置表单变更
    const prefSelects = document.querySelectorAll('#preferences-section select');
    prefSelects.forEach(select => {
        select.addEventListener('change', function () {
            const prefName = this.id;
            const prefValue = this.value;

            // 存储原始值，以便在出错时恢复
            const originalValue = this.getAttribute('data-original-value');

            // 禁用选择器，防止重复提交
            this.disabled = true;

            // 处理主题切换的特殊逻辑
            if (prefName === 'theme') {
                // 确定是否是深色模式
                const isDark = prefValue === 'dark';

                // 应用主题
                applyTheme(isDark);

                // 如果存在darkModeToggle，同步状态
                if (darkModeToggle) {
                    darkModeToggle.checked = isDark;
                }

                // 发送AJAX请求更新用户主题偏好
                fetch('/profile/update_preference', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        preference: 'theme',
                        value: prefValue
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            console.log('主题偏好已保存到服务器');
                        } else {
                            console.error('保存主题偏好失败:', data.message);
                            // 如果保存失败，恢复原始值
                            this.value = originalValue;
                            applyTheme(originalValue === 'dark');
                            alert('设置保存失败: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('请求出错:', error);
                        // 恢复原始值
                        this.value = originalValue;
                        applyTheme(originalValue === 'dark');
                        alert('设置保存失败，请稍后再试');
                    })
                    .finally(() => {
                        // 恢复选择器可用状态
                        this.disabled = false;
                    });
            }
        });

        // 保存原始值，以便在出错时恢复
        select.setAttribute('data-original-value', select.value);


    });

    // 清除搜索历史
    const clearSearchHistory = document.getElementById('clearSearchHistory');
    if (clearSearchHistory) {
        clearSearchHistory.addEventListener('click', function () {
            if (confirm('确定要清除所有搜索历史吗？')) {
                fetch('/profile/clear_search_history', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('搜索历史已清除');
                        } else {
                            alert('操作失败: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('发生错误，请稍后再试');
                    });
            }
        });
    }

    // 清除浏览数据
    const clearBrowsingData = document.getElementById('clearBrowsingData');
    if (clearBrowsingData) {
        clearBrowsingData.addEventListener('click', function () {
            if (confirm('确定要清除所有浏览数据吗？')) {
                fetch('/profile/clear_browsing_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('浏览数据已清除');
                        } else {
                            alert('操作失败: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('发生错误，请稍后再试');
                    });
            }
        });
    }


    // 管理收藏位置
    const manageFavoritesBtn = document.getElementById('manageFavoritesBtn');
    const manageFavoritesModal =document.getElementById('manageFavoritesModal');
    const favoritesList = document.getElementById('favoritesList');
    const loadingFavorites = document.getElementById('loadingFavorites');
    const noFavoritesMessage = document.getElementById('noFavoritesMessage');

    if (manageFavoritesBtn) {
        manageFavoritesBtn.addEventListener('click', function() {
            // 使用 Bootstrap 的方式显示模态框
            const modal = new bootstrap.Modal(document.getElementById('manageFavoritesModal'));
            modal.show();

            // 加载收藏列表
            loadFavorites();
        });
    }

    // 加载收藏列表
    function loadFavorites() {
        loadingFavorites.classList.remove('d-none');
        noFavoritesMessage.classList.add('d-none');

        // 清空现表（除了加载指示器和无收藏消息）
        const items = favoritesList.querySelectorAll('.favorite-item');
        items.forEach(item => item.remove());

        fetch('/favorites/list')
            .then(response => response.json())
            .then(data => {
                loadingFavorites.classList.add('d-none');

                if (data.favorites && data.favorites.length > 0) {
                    data.favorites.forEach(favorite => {
                        const favoriteItem = document.createElement('div');
                        favoriteItem.className = 'favorite-item d-flex justify-content-between align-items-center p-2 border-bottom';
                        favoriteItem.innerHTML = `
                                <i class="fas fa-map-marker-alt me-2 text-primary"></i>
                                <a href="/weather/${favorite.name}" class="text-decoration-none">${favorite.name}</a>
                            </div>
                            <button class="btn btn-sm btn-outline-danger remove-favorite" data-city="${favorite.name}">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        `;
                        favoritesList.appendChild(favoriteItem);

                        // 添加删除事件监听器
                        const removeBtn = favoriteItem.querySelector('.remove-favorite');
                        removeBtn.addEventListener('click', function() {
                            removeFavorite(favorite.name, favoriteItem);
                        });
                    });
                } else {
                    noFavoritesMessage.classList.remove('d-none');
                }
            })
            .catch(error => {
                console.error('Error loading favorites:', error);
                loadingFavorites.classList.add('d-none');
                favoritesList.innerHTML += `
                    <div class="alert alert-danger" role="alert">
                        加载收藏列表失败，请稍后再试
                    </div>
                `;
            });
    }

    // 删除收藏
    function removeFavorite(cityName, itemElement) {
        if (confirm(`确定要从收藏中移除 ${cityName} 吗？`)) {
            fetch(`/favorite/remove_setting/${cityName}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 从DOM中移除元素
                    itemElement.remove();

                    // 检查是否还有收藏项
                    const remainingItems = favoritesList.querySelectorAll('.favorite-item');
                    if (remainingItems.length === 0) {
                        noFavoritesMessage.classList.remove('d-none');
                    }

                    // 显示成功消息
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success alert-dismissible fade show mt-2';
                    alertDiv.innerHTML = `
                        ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    favoritesList.prepend(alertDiv);

                    // 3秒后自动关闭提示
                    setTimeout(() => {
                        alertDiv.classList.remove('show');
                        setTimeout(() => alertDiv.remove(), 150);
                    }, 3000);
                } else {
                    alert('操作失败: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('发生错误，请稍后再试');
            });
        }
    }

});


$(document).ready(function () {
    // 使用 JSON.stringify 和 HTML data 属性
    const currentUserCity = document.getElementById('defaultCity').dataset.defaultCity;

    $('.select2').select2({
        placeholder: "搜索城市...",
        allowClear: true
    });

    // 从后端获取城市数据并填充下拉菜单
    fetch('/api/cities')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('defaultCity');
            // 清空现有选项
            $(select).empty();

            // 添加一个默认的空选项
            const defaultOption = new Option('请选择城市', '');
            select.appendChild(defaultOption);

            // 动态添加城市选项
            for (const [province, cities] of Object.entries(data)) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = province;

                cities.forEach(city => {
                    const option = new Option(city, city);
                    optgroup.appendChild(option);
                });

                select.appendChild(optgroup);
            }

            // 如果有默认城市，则选中；否则保持默认选项
            if (currentUserCity) {
                $(select).val(currentUserCity).trigger('change');
            }
        });

    // 城市选择变更事件
    $('#defaultCity').on('change', function() {
        const selectedCity = $(this).val();

        // 只有在选择了有效城市时才发送请求
        if (selectedCity) {
            fetch('/profile/update_preference', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    preference: 'defaultCity',
                    value: selectedCity
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.message || '更新失败');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('默认城市已更新');
                } else {
                    alert('更新失败: ' + data.message);
                }
            })
            .catch(error => {
                console.error('请求出错:', error);
                alert('更新失败: ' + error.message);
            });
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const upgradeAdminForm = document.getElementById('upgrade-admin-form');

    if (upgradeAdminForm) {
        upgradeAdminForm.addEventListener('submit', function(event) {
            event.preventDefault(); // 阻止表单的默认提交行为

            fetch(this.action, {
                method: this.method,
                body: new FormData(this),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 升级成功
                    alert(data.message); // 显示成功消息
                    window.location.reload();
                } else {
                    // 升级失败
                    alert(data.message); // 显示错误消息
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('发生错误，请稍后重试。');
            });
        });
    }
});

// 在profile-form的提交处理逻辑中添加页面刷新
document.getElementById('profile-form').addEventListener('submit', function(e) {
    fetch('/profile_settings', {
        method: 'POST',
        body: new FormData(this)
    }).then(response => {
        if(response.ok) {
            window.location.reload(); // 添加页面刷新
        }
    });
});

// 删除账号表单提交逻辑
const deleteAccountForm = document.getElementById('delete-account-form');
if (deleteAccountForm) {
    deleteAccountForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const password = document.getElementById('deleteConfirmPassword').value;
        const confirmChecked = document.getElementById('confirmDelete').checked;
        if (!password) {
            alert('请输入密码');
            return;
        }
        if (!confirmChecked) {
            alert('请勾选确认删除选项');
            return;
        }
        fetch('/profile/delete_account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('账号已成功删除，感谢您的使用！');
                window.location.href = '/';
            } else {
                alert('删除失败: ' + (data.message || '未知错误'));
            }
        })
        .catch(error => {
            alert('请求失败: ' + error.message);
        });
    });
}

// 手机号验证
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // 只允许输入数字
            this.value = this.value.replace(/\D/g, '');
            
            // 限制最大长度为11位
            if (this.value.length > 11) {
                this.value = this.value.slice(0, 11);
            }
        });

        // 添加失去焦点时的验证
        phoneInput.addEventListener('blur', function() {
            const value = this.value.trim();
            if (value && !/^1[3-9]\d{9}$/.test(value)) {
                alert('请输入正确的手机号码格式');
                this.value = '';
            }
        });
    }
});