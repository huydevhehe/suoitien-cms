document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!(form instanceof HTMLFormElement) || !form.id) return;

    // Unfold đặt nút Lưu/Lưu và tiếp tục/... NẰM NGOÀI <form>, liên kết qua thuộc tính
    // HTML5 form="<id>" (xem unfold/templates/admin/submit_line.html) - không thể querySelector
    // bên trong form như Django Admin gốc, phải tìm theo thuộc tính form ở toàn trang.
    var relatedButtons = document.querySelectorAll('[form="' + form.id + '"]');
    if (relatedButtons.length === 0) return; // không phải form add/change của Unfold Admin

    if (form.dataset.submitting === '1') {
        // Bấm Lưu lần 2 khi form đang gửi lần 1 -> chặn để tránh lưu trùng (double submit)
        e.preventDefault();
        return;
    }
    form.dataset.submitting = '1';

    relatedButtons.forEach(function (btn) {
        btn.disabled = true;
        btn.style.opacity = '0.6';
        btn.style.cursor = 'not-allowed';
    });
});
