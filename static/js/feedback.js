// static/js/feedback.js
$(document).ready(function() {
    // 初始化Toast组件
    const toastElement = document.getElementById('feedbackToast');
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });

    // 表单提交处理
    $('#feedbackForm').submit(function(e) {
        e.preventDefault();
        // 确保加载动画元素存在
        if (!$('#loader').length) {
            $('body').append('<div id="loader" class="d-none position-fixed top-0 start-0 w-100 h-100 bg-white bg-opacity-75 justify-content-center align-items-center" style="z-index: 1000"><div class="spinner-border text-primary" role="status"></div></div>');
        }
        // 显示加载动画
        $('#loader').removeClass('d-none').addClass('d-flex');

        // 从隐藏元素获取用户ID
        const userId = $('#current-user-id').val();

        const formData = {
            type: $('select[name="type"]').val(),
            content: $('textarea[name="content"]').val(),
            contact: $('input[name="contact"]').val(),
            user_id: userId || null // 如果不存在则传null
        };

        // AJAX请求配置
        $.ajax({
            type: 'POST',
            url: '/submit_feedback',
            contentType: 'application/json',    // 声明发送JSON格式数据
            data: JSON.stringify(formData),     // 将表单数据序列化为JSON字符串
            success: function(response) {
                // 隐藏加载动画
                $('#loader').removeClass('d-flex').addClass('d-none');
                // 显示成功消息
                $('.toast-body').text(response.message || '反馈提交成功，感谢您的支持！');
                $('.toast-header i').removeClass('text-danger').addClass('text-primary');
                toast.show();
                // 重置表单
                if (response.status === 'success') {
                    $('#feedbackForm')[0].reset();
                }
            },
            // xhr是XMLHttpRequest对象
            error: function(xhr) {
                // 隐藏加载动画
                $('#loader').removeClass('d-flex').addClass('d-none');
                // 显示错误消息
                const errorMsg = xhr.responseJSON?.message || '提交失败，请稍后重试';
                $('.toast-body').text(errorMsg);
                $('.toast-header i').removeClass('text-primary').addClass('text-danger');
                toast.show();
            }
        });
    });
});