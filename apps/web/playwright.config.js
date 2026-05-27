// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  use: {
    headless: true,
    baseURL: 'http://host.docker.internal:3000',
    viewport: { width: 1280, height: 720 }
  }
});
