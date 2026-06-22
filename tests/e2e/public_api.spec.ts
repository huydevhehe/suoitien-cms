import { test, expect, APIResponse } from '@playwright/test';

// Test khói (smoke test) cho 11 API Public (/api/public/) — gọi thật lên server
// đang chạy (baseURL trong playwright.config.ts), không cần browser/login vì
// toàn bộ API Public là AllowAny. Dữ liệu test (comment/đặt vé/đặt món/liên hệ)
// được tạo thật trên DB của server đang chạy — chỉ chạy project này nhằm vào
// server test/local, không nhằm vào production.

const TEST_TAG = 'TEST_PLAYWRIGHT';

test.describe.serial('API Public - Smoke test', () => {
  let sampleProductId: number | undefined;
  let sampleProductAlias: string | undefined;
  let createdTicketCart: { id_cart: string; phone: string } | undefined;

  async function expectOk(response: APIResponse, label: string) {
    expect(response.ok(), `${label} trả ${response.status()}: ${await response.text()}`).toBeTruthy();
  }

  test('GET /settings/ trả cấu hình công khai', async ({ request }) => {
    const response = await request.get('/api/public/settings/');
    await expectOk(response, 'GET /settings/');
    const body = await response.json();
    expect(body).toHaveProperty('hotline');
    expect(body).not.toHaveProperty('st_accesstoken');
    expect(body).not.toHaveProperty('theme');
  });

  test('GET /menus/ trả cây menu', async ({ request }) => {
    const response = await request.get('/api/public/menus/');
    await expectOk(response, 'GET /menus/');
    const body = await response.json();
    expect(Array.isArray(body)).toBeTruthy();
  });

  test('GET /banners/ trả danh sách banner', async ({ request }) => {
    const response = await request.get('/api/public/banners/');
    await expectOk(response, 'GET /banners/');
    const body = await response.json();
    expect(Array.isArray(body)).toBeTruthy();
  });

  test('GET /posts/?post_type=product trả danh sách sản phẩm', async ({ request }) => {
    const response = await request.get('/api/public/posts/?post_type=product');
    await expectOk(response, 'GET /posts/?post_type=product');
    const body = await response.json();
    expect(Array.isArray(body)).toBeTruthy();

    if (body.length === 0) {
      console.warn('[SKIP] Không có sản phẩm nào — bỏ qua các test phụ thuộc post_id thật.');
      return;
    }
    sampleProductId = body[0].Id;
    sampleProductAlias = body[0].alias;
    expect(sampleProductId).toBeTruthy();
    expect(sampleProductAlias).toBeTruthy();
  });

  test('GET /posts/{alias}/ trả chi tiết sản phẩm', async ({ request }) => {
    test.skip(!sampleProductAlias, 'Không có sản phẩm thật để test chi tiết.');
    const response = await request.get(`/api/public/posts/${sampleProductAlias}/`);
    await expectOk(response, 'GET /posts/{alias}/');
    const body = await response.json();
    expect(body).toHaveProperty('content');
    expect(body.alias).toBe(sampleProductAlias);
  });

  test('GET /comments/?id_post= trả bình luận đã duyệt', async ({ request }) => {
    test.skip(!sampleProductId, 'Không có sản phẩm thật để test bình luận.');
    const response = await request.get(`/api/public/comments/?id_post=${sampleProductId}`);
    await expectOk(response, 'GET /comments/');
    const body = await response.json();
    expect(Array.isArray(body)).toBeTruthy();
  });

  test('POST /comments/ tạo bình luận mới (chờ duyệt)', async ({ request }) => {
    test.skip(!sampleProductId, 'Không có sản phẩm thật để gửi bình luận.');
    const response = await request.post('/api/public/comments/', {
      data: {
        id_post: sampleProductId,
        fullname: TEST_TAG,
        content: `${TEST_TAG} - bình luận test tự động`,
        star: 5,
      },
    });
    expect(response.status(), await response.text()).toBe(201);
  });

  test('POST /ticket-orders/ đặt vé khách vãng lai', async ({ request }) => {
    test.skip(!sampleProductId, 'Không có sản phẩm thật để đặt vé.');
    const phone = '0900000001';
    const response = await request.post('/api/public/ticket-orders/', {
      data: {
        fullname: TEST_TAG,
        phone,
        email: 'playwright-test@example.com',
        address: 'Test',
        dateoforg: new Date().toISOString().slice(0, 10),
        type_payment: 1,
        items: [{ post_id: sampleProductId, quantity: 1 }],
      },
    });
    expect(response.status(), await response.text()).toBe(201);
    const body = await response.json();
    expect(body).toHaveProperty('id_cart');
    createdTicketCart = { id_cart: body.id_cart, phone };
  });

  test('GET /ticket-orders/lookup/ tra cứu đúng mã đơn + SĐT', async ({ request }) => {
    test.skip(!createdTicketCart, 'Chưa tạo được đơn vé ở bước trước.');
    const { id_cart, phone } = createdTicketCart!;

    const okResponse = await request.get(
      `/api/public/ticket-orders/lookup/?id_cart=${id_cart}&phone=${phone}`,
    );
    await expectOk(okResponse, 'GET /ticket-orders/lookup/ (đúng SĐT)');
    const okBody = await okResponse.json();
    expect(okBody.id_cart).toBe(id_cart);

    const wrongPhoneResponse = await request.get(
      `/api/public/ticket-orders/lookup/?id_cart=${id_cart}&phone=0999999999`,
    );
    expect(wrongPhoneResponse.status()).toBe(404);
  });

  test('POST /food-orders/ đặt món khách vãng lai', async ({ request }) => {
    test.skip(!sampleProductId, 'Không có sản phẩm thật để đặt món.');
    const response = await request.post('/api/public/food-orders/', {
      data: {
        fullname: TEST_TAG,
        phone: '0900000002',
        address: 'Test',
        items: [{ post_id: sampleProductId, quantity: 1 }],
      },
    });
    expect(response.status(), await response.text()).toBe(201);
  });

  test('POST /supports/ gửi liên hệ/góp ý', async ({ request }) => {
    const response = await request.post('/api/public/supports/', {
      data: {
        subject: `${TEST_TAG} - liên hệ test`,
        message: `${TEST_TAG} - nội dung test tự động`,
        fullname: TEST_TAG,
        phone: '0900000003',
        email: 'playwright-test@example.com',
      },
    });
    expect(response.status(), await response.text()).toBe(201);
  });
});
