import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  timeout: 10000,
  expect: { timeout: 10000 },
  testDir: './tests/e2e',
  fullyParallel: false, // Chạy tuần tự để dễ nhìn quá trình test
  retries: 0,
  workers: 1,
  reporter: 'html', // Báo cáo HTML siêu đẹp
  use: {
    baseURL: 'http://127.0.0.1:8000',
    trace: 'on', // Ghi lại toàn bộ lịch sử (Time-travel)
    video: 'on', // Quay video lại toàn bộ quá trình test
    viewport: { width: 1280, height: 720 },
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    // Test giao diện Admin (cần browser + đăng nhập) — chạy: npx playwright test --project=chromium
    {
      name: 'chromium',
      testMatch: /admin_widgets\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/admin.json',
      },
      dependencies: ['setup'],
    },
    // Test API Public bằng HTTP request thuần, không cần browser/login — chạy: npx playwright test --project=api
    { name: 'api', testMatch: /public_api\.spec\.ts/ },
  ],
});
