# Bộ test tự động — Suối Tiên CMS

Bộ test tự động kiểm tra 2 phần: **API Public** (dùng cho FE khách) và **Django Admin** (giao diện quản trị nội bộ). Gồm test backend (Django) chạy nhanh trên DB test riêng, và test giao diện (Playwright) chạy trên trình duyệt thật.

## Cấu trúc

```
tests/
├── backend/                        # Test Django (Python) — chạy trên DB test riêng, không đụng data thật
│   ├── test_public_api.py          # 23 test: 11 API Public (/api/public/)
│   ├── test_admin_smoke.py         # 8 test: quét toàn bộ trang Django Admin + StatusSwitchWidget
│   └── test_admin_business_logic.py # 20 test: email, giá sản phẩm, đổi mật khẩu, upload ảnh,
│                                     #          Sidebar/JSON widget, Dashboard, bộ lọc changelist
└── e2e/                             # Test Playwright (TypeScript) — chạy trên trình duyệt thật
    ├── auth.setup.ts                # Đăng nhập Admin, lưu cookie dùng lại cho các test sau
    ├── public_api.spec.ts           # 11 test: gọi HTTP thật vào 11 API Public (không cần browser)
    └── admin_widgets.spec.ts        # 6 test: các widget JS trong Admin (Image Picker, Menu Builder,
                                      #          TinyMCE, Sortable ▲▼, Category checkbox, Status switch)
```

## Phạm vi kiểm tra

**API Public** (`test_public_api.py` + `public_api.spec.ts`):
- Giá đơn (vé/món) luôn tính lại từ DB, không tin giá client gửi lên.
- Throttle 20 request/phút/IP chặn spam cho API ghi dữ liệu.
- Tra cứu đơn bắt buộc khớp đúng mã đơn + số điện thoại, không lộ đơn người khác.
- Dữ liệu ẩn/chưa duyệt không lộ qua API đọc công khai.
- Validate input đầy đủ cho từng endpoint.

**Django Admin** (`test_admin_smoke.py` + `test_admin_business_logic.py` + `admin_widgets.spec.ts`):
- Toàn bộ trang Admin (danh sách/sửa/thêm) không lỗi 500.
- `StatusSwitchWidget` (vùng từng có bug thật về logic đảo ngược `ticlock`).
- Category checkbox dropdown, Menu Builder (kéo-thả/thêm/đổi cấp/xóa), Sortable (▲▼ đổi thứ tự), TinyMCE, Image Picker (chọn ảnh).
- Nút "Gửi lại email xác nhận" đơn vé/đơn món (email được chặn lại, không gửi thật khi test).
- Form giá sản phẩm (giá bán/giá khuyến mãi lưu qua bảng Meta riêng).
- Form đổi mật khẩu Admin/Thành viên (hash kiểu PHP cũ `md5(md5())`).
- Upload ảnh mới qua popup Image Picker (lưu đúng thư mục, không đè file trùng tên, chặn đúng định dạng).
- `SidebarCheckboxWidget`, `JSONTextAreaWidget`.
- Dashboard trang chủ Admin (thống kê, biểu đồ) không lỗi cả khi có/không có dữ liệu.
- Bộ lọc (`list_filter`) và tìm kiếm trên changelist trả đúng kết quả, không chỉ load được trang.

## Cách chạy

### 1. Test Django (backend)

Cần MySQL đang chạy (Django tự tạo + xóa database test riêng, không đụng data thật):

```bash
python manage.py test tests.backend
```

Chạy riêng từng file:

```bash
python manage.py test tests.backend.test_public_api
python manage.py test tests.backend.test_admin_smoke
python manage.py test tests.backend.test_admin_business_logic
```

### 2. Test Playwright (giao diện)

Cài đặt 1 lần: `npm install`

Cần 1 server Django đang chạy (local hoặc server test) khớp với `baseURL` trong `playwright.config.ts`, có sẵn user đăng nhập Admin (`admin` / `admin123` — sửa lại trong `tests/e2e/auth.setup.ts` nếu khác).

```bash
npx playwright test --project=api         # Test API Public, không cần login
npx playwright test --project=chromium    # Test giao diện Admin, cần login
```

Xem báo cáo HTML sau khi chạy: `npx playwright show-report`

## Lưu ý

- Mọi dữ liệu Playwright tạo ra đều có tiền tố `TEST_PLAYWRIGHT` và tự xóa ở cuối mỗi bộ test (`test.afterAll`) — không để lại rác trên DB.
- Test Django dùng database test riêng do Django tự quản lý (`test_<tên_db>`), độc lập hoàn toàn với database thật.
- `playwright.config.ts` đang trỏ `baseURL` về `http://127.0.0.1:8000` (local) — đổi lại nếu muốn chạy nhằm vào server khác.

---

*Developed by Huy*