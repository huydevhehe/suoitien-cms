import { test as setup, expect } from '@playwright/test';
import * as path from 'path';

const authFile = path.join(__dirname, '../../playwright/.auth/admin.json');

setup('authenticate', async ({ page }) => {
  setup.setTimeout(15000);
  // Đi thẳng vào trang Admin, ép thuộc tính ?next=/admin/ để tránh lỗi 404 profile
  await page.goto('/admin/login/?next=/admin/');
  await page.fill("input[name='username']", "admin");
  await page.fill("input[name='password']", "admin123");
  await page.click("button[type='submit']");
  
  // Chờ cho thanh sidebar bên trái hoặc header xuất hiện (chứng tỏ đã vô được admin)
  await page.waitForSelector("#header, .sidebar, #content");
  
  // Lưu file cookie lại để dùng cho các test Admin (project "chromium") sau đó
  await page.context().storageState({ path: authFile });
});
