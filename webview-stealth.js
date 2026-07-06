// 降低 Electron 环境被 Cloudflare 识别的概率
(() => {
  try {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined,
      configurable: true
    });

    if (!window.chrome) {
      window.chrome = { runtime: {} };
    }

    Object.defineProperty(navigator, 'languages', {
      get: () => ['zh-CN', 'zh', 'en-US', 'en'],
      configurable: true
    });

    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5],
      configurable: true
    });
  } catch (e) {
    // 忽略注入失败
  }
})();
