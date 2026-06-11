document.addEventListener('DOMContentLoaded', function() {
    // Chỉ kích hoạt TinyMCE cho các trường soạn thảo nội dung/mô tả HTML
    var selectors = [
        'textarea#id_content_vn',
        'textarea#id_content_vn_0',
        'textarea#id_content_vn_1',
        'textarea#id_description_vn',
        'textarea#id_description_vn_0',
        'textarea#id_description_vn_1',
        'textarea#id_message',
        'textarea#id_slogan',
        'textarea#id_description'
    ].join(', ');

    function initTinyMCE() {
        // Detect dark mode từ class .dark của Unfold Admin
        var isDark = document.documentElement.classList.contains('dark');

        tinymce.init({
            selector: selectors,
            height: 400,
            menubar: true,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | blocks | ' +
                     'bold italic backcolor | alignleft aligncenter ' +
                     'alignright alignjustify | bullist numlist outdent indent | ' +
                     'removeformat | link image media code fullscreen',

            // Dark mode: tự động đổi skin theo chế độ của Unfold Admin
            skin: isDark ? 'oxide-dark' : 'oxide',
            content_css: isDark ? 'dark' : 'default',
            content_style: isDark
                ? 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px; background:#1a1a1a; color:#e5e5e5; }'
                : 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px; }',

            // QUAN TRỌNG: Cấu hình để quản lý code legacy không bị tự động làm sạch/sanitize
            verify_html: false,       // Tắt tính năng tự động loại bỏ thẻ lạ
            cleanup: false,           // Tắt dọn dẹp HTML tự động
            valid_elements: '*[*]',   // Cho phép tất cả các thẻ và tất cả thuộc tính
            extended_valid_elements: 'script[src|async|defer|type|charset],iframe[src|width|height|frameborder|allowfullscreen|sandbox]',

            // Tránh parse đường dẫn URL tuyệt đối thành tương đối
            convert_urls: false,

            // Hỗ trợ tiếng Việt
            language: 'vi',
            language_url: 'https://cdn.jsdelivr.net/npm/tinymce-i18n@23/langs5/vi.js'
        });
    }

    // Polling: chờ TinyMCE CDN load xong rồi mới init (tối đa 10 giây)
    // Sửa lỗi Cốc Cốc và các trình duyệt load CDN chậm hơn Chrome
    var attempts = 0;
    var maxAttempts = 50; // 50 x 200ms = 10 giây
    var timer = setInterval(function() {
        attempts++;
        if (typeof tinymce !== 'undefined') {
            clearInterval(timer);
            initTinyMCE();
        } else if (attempts >= maxAttempts) {
            clearInterval(timer);
            console.warn('[TinyMCE] Không thể tải TinyMCE sau 10 giây. Kiểm tra kết nối mạng hoặc CDN.');
        }
    }, 200);
});
