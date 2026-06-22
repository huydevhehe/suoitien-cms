import { test, expect, Page } from '@playwright/test';

// Test các widget JS-heavy trong Django Admin (Image Picker, Menu Builder,
// TinyMCE, Sortable move up/down, Category checkbox, Status switch) — những
// thứ Django test thuần (tests/backend/test_admin_smoke.py) KHÔNG thấy được vì
// chạy ở client-side. Test này cần trình duyệt thật + storageState đăng nhập
// admin (xem tests/e2e/auth.setup.ts) → chạy bằng `npx playwright test --project=chromium`.
//
// Mọi dữ liệu test đều tự tạo (tiêu đề bắt đầu "TEST_PLAYWRIGHT_") và tự xóa ở
// cuối, không đụng vào nội dung thật trên server đang chạy.

const TAG = 'TEST_PLAYWRIGHT_WIDGETS';

async function saveAndWait(page: Page) {
  await page.locator('button[name="_save"], input[name="_save"]').first().click();
  await page.waitForLoadState('networkidle');
}

async function createPost(page: Page, opts: { adminPath: string; title: string; alias: string; sort?: number; titleFieldId?: string }) {
  await page.goto(`/admin/suoi_tien/${opts.adminPath}/add/`);
  await page.locator(`#${opts.titleFieldId ?? 'id_title_vn_0'}`).fill(opts.title);
  const aliasInput = page.locator('#id_alias');
  if (await aliasInput.count() > 0) {
    await aliasInput.fill(opts.alias);
  }
  if (opts.sort !== undefined) {
    const sortInput = page.locator('#id_sort');
    if (await sortInput.count() > 0) {
      await sortInput.fill(String(opts.sort));
    }
  }
  // Dùng "Lưu và tiếp tục sửa" (_continue) thay vì "Lưu" (_save) vì _save mặc định
  // chuyển về trang changelist (không có ID trong URL), còn _continue giữ nguyên
  // trang chi tiết .../<id>/change/ để lấy được ID vừa tạo.
  await page.locator('button[name="_continue"], input[name="_continue"]').first().click();
  await page.waitForLoadState('networkidle');
  const url = page.url();
  const match = url.match(/\/(\d+)\/change\/?/);
  return match ? match[1] : null;
}

async function deleteByTitleSearch(page: Page, adminPath: string, searchTerm: string) {
  await page.goto(`/admin/suoi_tien/${adminPath}/?q=${encodeURIComponent(searchTerm)}`);
  const checkboxes = page.locator('input[name="_selected_action"]');
  const count = await checkboxes.count();
  if (count === 0) return;
  for (let i = 0; i < count; i++) {
    await checkboxes.nth(i).check();
  }
  await page.locator('select[name="action"]').selectOption('delete_selected');
  await page.locator('button[type="submit"][name="index"], button:has-text("Thực hiện")').first().click();
  const confirmBtn = page.locator('button[type="submit"]:has-text("Có"), input[type="submit"][value*="chắc"]');
  if (await confirmBtn.count() > 0) {
    await confirmBtn.first().click();
  }
}

test.describe.serial('Admin - Widget JS (Image Picker, Menu Builder, TinyMCE, Sortable...)', () => {
  test.describe.configure({ timeout: 60000 });

  test('Category checkbox dropdown: chọn chuyên mục, lưu, load lại vẫn đúng', async ({ page }) => {
    const catId = await createPost(page, {
      adminPath: 'postcategoryproxy',
      title: `${TAG}_CAT`,
      alias: `${TAG.toLowerCase()}-cat`,
    });
    test.skip(!catId, 'Không tạo được chuyên mục test.');

    const postId = await createPost(page, {
      adminPath: 'postproxy',
      title: `${TAG}_POST_CATTEST`,
      alias: `${TAG.toLowerCase()}-post-cattest`,
    });
    test.skip(!postId, 'Không tạo được bài viết test.');

    await page.goto(`/admin/suoi_tien/postproxy/${postId}/change/`);
    await page.locator('.category-dropdown-header').click();
    const checkbox = page.locator(`.category-checkbox-widget input[type="checkbox"][value="${catId}"]`);
    await expect(checkbox).toBeVisible();
    await checkbox.check();
    await expect(page.locator('.category-dropdown-selected-text')).toContainText(TAG);

    await saveAndWait(page);
    await page.goto(`/admin/suoi_tien/postproxy/${postId}/change/`);
    await page.locator('.category-dropdown-header').click();
    await expect(page.locator(`.category-checkbox-widget input[type="checkbox"][value="${catId}"]`)).toBeChecked();
  });

  test('Status switch: hiển thị đúng trạng thái Hiện/Ẩn khi tải lại trang', async ({ page }) => {
    const postId = await createPost(page, {
      adminPath: 'postproxy',
      title: `${TAG}_POST_SWITCH`,
      alias: `${TAG.toLowerCase()}-post-switch`,
    });
    test.skip(!postId, 'Không tạo được bài viết test.');

    await page.goto(`/admin/suoi_tien/postproxy/${postId}/change/`);
    const ticlockSwitch = page.locator('input[name="ticlock"]');
    // Bài mới tạo mặc định ticlock='0' (Hiện) → switch phải đang ON.
    await expect(ticlockSwitch).toBeChecked();

    await ticlockSwitch.click(); // tắt switch → Ẩn
    await saveAndWait(page);

    await page.goto(`/admin/suoi_tien/postproxy/${postId}/change/`);
    await expect(page.locator('input[name="ticlock"]')).not.toBeChecked();
  });

  test('Sortable move up/down: bấm nút ▲ đổi đúng thứ tự trong changelist', async ({ page }) => {
    const idA = await createPost(page, {
      adminPath: 'postproxy', title: `${TAG}_SORT_A`, alias: `${TAG.toLowerCase()}-sort-a`, sort: 999990,
    });
    const idB = await createPost(page, {
      adminPath: 'postproxy', title: `${TAG}_SORT_B`, alias: `${TAG.toLowerCase()}-sort-b`, sort: 999991,
    });
    test.skip(!idA || !idB, 'Không tạo được 2 bài viết test để so sánh thứ tự.');

    await page.goto(`/admin/suoi_tien/postproxy/?q=${encodeURIComponent(TAG + '_SORT')}`);
    const rowA = page.locator('#result_list tbody tr').filter({ hasText: `${TAG}_SORT_A` });
    const rowB = page.locator('#result_list tbody tr').filter({ hasText: `${TAG}_SORT_B` });
    await expect(rowA).toHaveCount(1);
    await expect(rowB).toHaveCount(1);

    // Đọc trực tiếp số thứ tự (sort) hiển thị trong đúng dòng của từng bài viết
    // — không dựa vào vị trí dòng trên/dưới, vì changelist không mặc định sắp
    // theo cột "Thứ tự".
    const sortCellA = rowA.locator('td[data-label="Thứ tự"]');
    const sortBefore = (await sortCellA.innerText()).match(/\d+/)?.[0];
    expect(sortBefore).toBe('999990');

    await rowB.locator('a[href*="/move-up/"]').click();
    await page.waitForLoadState('networkidle');

    await page.goto(`/admin/suoi_tien/postproxy/?q=${encodeURIComponent(TAG + '_SORT')}`);
    const sortAfter = (await page.locator('#result_list tbody tr')
      .filter({ hasText: `${TAG}_SORT_A` })
      .locator('td[data-label="Thứ tự"]').innerText()).match(/\d+/)?.[0];

    expect(sortAfter, 'Bấm ▲ ở dòng SORT_B phải hoán đổi sort với SORT_A').toBe('999991');
  });

  test('Menu Builder: thêm trang vào menu, đổi cấp, rồi xóa khỏi menu', async ({ page }) => {
    const pageId = await createPost(page, {
      adminPath: 'pageproxy', title: `${TAG}_PAGE`, alias: `${TAG.toLowerCase()}-page`,
    });
    test.skip(!pageId, 'Không tạo được trang tĩnh test.');

    const menuId = await createPost(page, {
      adminPath: 'halinkmenu', title: `${TAG}_MENU`, alias: '', titleFieldId: 'id_title_cat_0',
    });
    test.skip(!menuId, 'Không tạo được menu test (lưu ý: HalinkMenu không có field alias, có thể fail ở bước tạo).');

    await page.goto(`/admin/suoi_tien/halinkmenu/${menuId}/change/`);

    // Nhóm "Trang tĩnh" mặc định thu gọn, phải bấm mở trước khi thấy checkbox bên trong.
    const pagesGroupHeader = page.locator('h4', { hasText: 'Trang tĩnh' }).first();
    if (await pagesGroupHeader.count() > 0) {
      await pagesGroupHeader.click();
    }

    const pageCheckbox = page.locator('ul#list-pages input[type="checkbox"]').filter({
      has: page.locator(`xpath=ancestor::label[contains(., "${TAG}_PAGE")]`),
    });
    await expect(pageCheckbox).toBeVisible();
    await pageCheckbox.check();
    await page.locator('button:has-text("Thêm vào menu")').first().click();

    const menuItem = page.locator(`#sortable-menu li.sortable-item:has-text("${TAG}_PAGE")`);
    await expect(menuItem).toBeVisible();

    await menuItem.locator('.btn-indent', { hasText: '➡️' }).click();
    await expect(menuItem).toHaveAttribute('data-level', '1');

    page.once('dialog', (dialog) => dialog.accept()); // nút Xóa có confirm() của trình duyệt
    await menuItem.locator('.btn-remove').click();
    await expect(page.locator(`#sortable-menu li.sortable-item:has-text("${TAG}_PAGE")`)).toHaveCount(0);

    await saveAndWait(page);
  });

  test('Image Picker: mở popup chọn ảnh, ảnh được set vào input + preview', async ({ page, context }) => {
    const postId = await createPost(page, {
      adminPath: 'postproxy', title: `${TAG}_IMG`, alias: `${TAG.toLowerCase()}-img`,
    });
    test.skip(!postId, 'Không tạo được bài viết test.');

    await page.goto(`/admin/suoi_tien/postproxy/${postId}/change/`);

    const popupPromise = context.waitForEvent('page');
    await page.locator('button.image-picker-btn').first().click();
    const popup = await popupPromise;
    await popup.waitForLoadState();

    const firstImage = popup.locator('.grid .img-item').first();
    const hasImage = await firstImage.count() > 0;
    test.skip(!hasImage, 'Không có ảnh sẵn nào trên thư mục media của staging để test chọn.');

    await firstImage.click();
    await expect(page.locator('#id_post_image')).not.toHaveValue('');
    await expect(page.locator('#id_post_image_preview img')).toBeVisible();
  });

  test('TinyMCE: gõ chữ và bấm Bold, nội dung HTML có <strong>', async ({ page }) => {
    const postId = await createPost(page, {
      adminPath: 'postproxy', title: `${TAG}_TINYMCE`, alias: `${TAG.toLowerCase()}-tinymce`,
    });
    test.skip(!postId, 'Không tạo được bài viết test.');

    await page.goto(`/admin/suoi_tien/postproxy/${postId}/change/`);

    const editorFrame = page.frameLocator('#id_content_vn_0_ifr');
    await expect(editorFrame.locator('body')).toBeVisible({ timeout: 30000 });

    await editorFrame.locator('body').click();
    await page.keyboard.type('Nội dung test TinyMCE');
    await page.keyboard.press('Control+A');
    // Toolbar TinyMCE bị responsive co hẹp (chỉ còn hiện "Đoạn văn", các nút
    // khác như Bold bị ẩn vào menu "..."), nên dùng phím tắt Ctrl+B (lệnh bold
    // chuẩn của TinyMCE) thay vì bấm nút toolbar — đáng tin cậy hơn vì không
    // phụ thuộc độ rộng container hay ngôn ngữ hiển thị.
    await page.keyboard.press('Control+B');

    const html = await editorFrame.locator('body').innerHTML();
    expect(html.toLowerCase()).toContain('<strong');
  });

  test.afterAll(async ({ browser }) => {
    test.setTimeout(60000);
    const page = await browser.newPage({ storageState: 'playwright/.auth/admin.json' });
    await deleteByTitleSearch(page, 'postproxy', TAG);
    await deleteByTitleSearch(page, 'postcategoryproxy', TAG);
    await deleteByTitleSearch(page, 'pageproxy', TAG);
    await deleteByTitleSearch(page, 'halinkmenu', TAG);
    await page.close();
  });
});
