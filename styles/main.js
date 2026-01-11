// 禁用输入框的回车提交功能
function disableEnterSubmit() {
    // 监听所有输入框的keydown事件
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
            // 阻止默认的提交行为
            e.preventDefault();
            e.stopPropagation();
        }
    });
}

// 确保在页面加载完成后执行
document.addEventListener('DOMContentLoaded', disableEnterSubmit);