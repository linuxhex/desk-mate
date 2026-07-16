const { app, BrowserWindow, ipcMain, dialog, session, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const XLSX = require('xlsx');
const http = require('http');

// Python服务配置
const PYTHON_SERVICE_PORT = 5000;
const PYTHON_SERVICE_URL = `http://localhost:${PYTHON_SERVICE_PORT}`;
let pythonServiceProcess = null;
let isPythonServiceRunning = false;

let mainWindow = null;

// 固定 UA，全平台一致，避免重启后登录态失效
const BROWSER_USER_AGENT =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.291 Safari/537.36';

function getBrowserUserAgent() {
  return BROWSER_USER_AGENT;
}

const STEALTH_SCRIPT = `
  try {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined, configurable: true });
    if (!window.chrome) window.chrome = { runtime: {} };
  } catch (e) {}
`;

app.commandLine.appendSwitch('disable-blink-features', 'AutomationControlled');

const gotSingleInstanceLock = app.requestSingleInstanceLock();
if (!gotSingleInstanceLock) {
  app.quit();
}

// ChatGPT：收起的侧栏图标横向排列在顶部
const CHATGPT_NO_SIDEBAR_CSS = `
  /* 只隐藏展开的侧边栏 */
  #stage-slideover-sidebar {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
  }

  /* 保留收起的侧边栏，改为横向布局在顶部 */
  #stage-sidebar-tiny-bar {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    height: auto !important;
    min-height: 48px !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    padding: 8px 16px !important;
    background: #202123 !important;
    z-index: 10000 !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  }

  /* 让图标横向排列 */
  #stage-sidebar-tiny-bar > * {
    margin: 4px 8px !important;
  }

  /* 调整主要内容区域 */
  #stage-sidebar-tiny-bar + * {
    margin-left: 0 !important;
    padding-left: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    padding-top: 56px !important;
  }
`;

// 智谱：隐藏侧边栏（基于真实DOM结构）
const ZHIPU_SIDEBAR_CSS = `
  /* 隐藏 Element UI 侧边栏 */
  .el-aside,
  .aside-container,
  .aside-subjects,
  .subjects.limitation {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    overflow: hidden !important;
    flex-shrink: 0 !important;
  }
  
  /* 调整主内容区域 */
  .el-container,
  .el-main,
  .detail-container,
  .session-container,
  .conversation-container {
    margin-left: 0 !important;
    padding-left: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    flex: 1 !important;
  }
  
  /* 确保页面完全填充 */
  body,
  html,
  #app {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
    overflow: hidden !important;
  }
`;

const chatgptCssKeys = new WeakMap();
const zhipuCssKeys = new WeakMap();
const guestInitialized = new WeakSet();

function clearStaleIndexedDBLocks() {
  if (!gotSingleInstanceLock) {
    return;
  }

  const partitionsDir = path.join(app.getPath('userData'), 'Partitions');
  if (!fs.existsSync(partitionsDir)) {
    return;
  }

  for (const partitionDir of fs.readdirSync(partitionsDir)) {
    const indexedDbDir = path.join(partitionsDir, partitionDir, 'IndexedDB');
    if (!fs.existsSync(indexedDbDir)) {
      continue;
    }

    for (const dbDir of fs.readdirSync(indexedDbDir)) {
      const lockFile = path.join(indexedDbDir, dbDir, 'LOCK');
      if (!fs.existsSync(lockFile)) {
        continue;
      }

      try {
        fs.unlinkSync(lockFile);
      } catch {
        // 仍有活跃进程占用，跳过
      }
    }
  }
}

function isChatGPTWebview(contents) {
  const url = contents.getURL() || '';
  return /chatgpt\.com|chat\.openai\.com/.test(url);
}

function isZhipuWebview(contents) {
  const url = contents.getURL() || '';
  return url.includes('chatglm');
}

function injectChatGPTSidebarCSS(contents) {
  if (!isChatGPTWebview(contents)) {
    return;
  }

  const previousKey = chatgptCssKeys.get(contents);
  if (previousKey) {
    contents.removeInsertedCSS(previousKey).catch(() => {});
  }

  contents
    .insertCSS(CHATGPT_NO_SIDEBAR_CSS)
    .then((key) => {
      chatgptCssKeys.set(contents, key);
      console.log('✅ ChatGPT 侧边栏 CSS 注入成功');
    })
    .catch((error) => {
      console.error('❌ ChatGPT 侧边栏 CSS 注入失败:', error);
      // 延迟重试一次
      setTimeout(() => {
        contents.insertCSS(CHATGPT_NO_SIDEBAR_CSS)
          .then((key) => chatgptCssKeys.set(contents, key))
          .catch(() => console.error('重试失败'));
      }, 2000);
    });
}

function injectZhipuSidebarCSS(contents) {
  if (!isZhipuWebview(contents)) {
    return;
  }

  const previousKey = zhipuCssKeys.get(contents);
  if (previousKey) {
    contents.removeInsertedCSS(previousKey).catch(() => {});
  }

  contents
    .insertCSS(ZHIPU_SIDEBAR_CSS)
    .then((key) => {
      zhipuCssKeys.set(contents, key);
    })
    .catch(() => {});

  contents.executeJavaScript(`
    (function() {
      function hideZhipuSidebar() {
        const sidebarSelectors = [
          '.el-aside',
          '.aside-container',
          '.aside-subjects',
          '.subjects.limitation'
        ];
        
        let hiddenCount = 0;
        
        sidebarSelectors.forEach(selector => {
          document.querySelectorAll(selector).forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0) {
              el.style.setProperty('display', 'none', 'important');
              el.style.setProperty('width', '0', 'important');
              el.style.setProperty('min-width', '0', 'important');
              el.style.setProperty('max-width', '0', 'important');
              hiddenCount++;
            }
          });
        });
        
        if (hiddenCount > 0) {
          const contentSelectors = [
            '.el-container',
            '.el-main',
            '.detail-container',
            '.session-container',
            '.conversation-container'
          ];
          
          contentSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
              el.style.setProperty('margin-left', '0', 'important');
              el.style.setProperty('padding-left', '0', 'important');
              el.style.setProperty('width', '100%', 'important');
              el.style.setProperty('max-width', '100%', 'important');
              el.style.setProperty('flex', '1', 'important');
            });
          });
          
          document.querySelectorAll('.el-container').forEach(parent => {
            const visibleChildren = Array.from(parent.children).filter(c => c.style.display !== 'none');
            if (visibleChildren.length > 0) {
              visibleChildren.forEach(child => {
                child.style.setProperty('flex', '1', 'important');
                child.style.setProperty('width', '100%', 'important');
              });
            }
          });
        }
      }

      function startMonitoring() {
        let runCount = 0;
        const maxInitialRuns = 30;
        
        function run() {
          runCount++;
          hideZhipuSidebar();
          
          if (runCount < maxInitialRuns) {
            setTimeout(run, 500);
          }
        }
        
        run();
        
        if (document.body) {
          const observer = new MutationObserver(() => {
            setTimeout(hideZhipuSidebar, 200);
          });
          observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true
          });
        }
      }

      setTimeout(startMonitoring, 5000);
    })();
  `).catch(() => {});
}

function configurePlatformSessions() {
  const ua = getBrowserUserAgent();
  const partitions = ['persist:chatgpt', 'persist:kimi', 'persist:deepseek', 'persist:yuanbao', 'persist:doubao', 'persist:zhipu', 'persist:minimax'];

  partitions.forEach((partition) => {
    const platformSession = session.fromPartition(partition);
    platformSession.setUserAgent(ua);
    platformSession.setPermissionRequestHandler((_webContents, _permission, callback) => {
      callback(true);
    });
    platformSession.webRequest.onBeforeSendHeaders((details, callback) => {
      details.requestHeaders['User-Agent'] = ua;
      callback({ requestHeaders: details.requestHeaders });
    });
  });
}

function setupWebviewGuest(contents) {
  if (contents.getType() !== 'webview') {
    return;
  }

  contents.setUserAgent(getBrowserUserAgent());

  function injectSidebarStyles() {
    contents.executeJavaScript(STEALTH_SCRIPT).catch(() => {});

    setTimeout(() => {
      injectChatGPTSidebarCSS(contents);
      injectZhipuSidebarCSS(contents);
    }, 3000);
  }

  contents.on('did-finish-load', () => {
    injectSidebarStyles();
  });

  contents.on('did-navigate-in-page', () => {
    injectSidebarStyles();
  });
}

// 启动Python服务
function startPythonService() {
  return new Promise((resolve, reject) => {
    if (isPythonServiceRunning) {
      resolve(true);
      return;
    }
    
    console.log('正在启动Python服务...');
    
    // 检测Python命令
    const pythonCommands = ['py', 'python', 'python3'];
    let pythonCommand = null;
    
    for (const cmd of pythonCommands) {
      try {
        const result = require('child_process').spawnSync(cmd, ['--version'], { encoding: 'utf8' });
        if (result.status === 0) {
          pythonCommand = cmd;
          console.log(`使用 ${cmd} 命令`);
          break;
        }
      } catch (e) {
        // 继续尝试下一个命令
      }
    }
    
    if (!pythonCommand) {
      reject(new Error('Python未安装或未添加到PATH环境变量'));
      return;
    }
    
    // 启动Python服务
    const serviceScript = path.join(__dirname, 'agent_service.py');
    console.log('启动Python服务:', serviceScript);
    
    const env = Object.assign({}, process.env, {
      PYTHONIOENCODING: 'utf-8',
      PYTHONUTF8: '1'
    });
    
    pythonServiceProcess = spawn(pythonCommand, [serviceScript], {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: env,
      detached: false
    });
    
    pythonServiceProcess.stdout.on('data', (data) => {
      console.log(`Python服务: ${data.toString()}`);
    });
    
    pythonServiceProcess.stderr.on('data', (data) => {
      console.error(`Python服务错误: ${data.toString()}`);
    });
    
    pythonServiceProcess.on('close', (code) => {
      console.log(`Python服务已停止，退出码: ${code}`);
      isPythonServiceRunning = false;
      pythonServiceProcess = null;
    });
    
    // 等待服务启动
    let attempts = 0;
    const maxAttempts = 30; // 最多等待30秒
    
    const checkService = setInterval(() => {
      attempts++;
      
      console.log(`检查Python服务状态...（第${attempts}次）`);
      
      // 检查服务是否启动
      const req = http.request(
        {
          hostname: '127.0.0.1',  // 使用明确的IPv4地址
          port: PYTHON_SERVICE_PORT,
          path: '/health',
          method: 'GET',
          timeout: 2000
        },
        (res) => {
          console.log(`健康检查响应状态码: ${res.statusCode}`);
          
          if (res.statusCode === 200) {
            clearInterval(checkService);
            isPythonServiceRunning = true;
            console.log('Python服务启动成功');
            resolve(true);
          }
          
          let data = '';
          res.on('data', (chunk) => {
            data += chunk;
          });
          
          res.on('end', () => {
            console.log('健康检查响应:', data);
          });
        }
      );
      
      req.on('error', (error) => {
        console.log(`健康检查失败: ${error.message}`);
        // 服务还未启动，继续等待
      });
      
      req.on('timeout', () => {
        console.log('健康检查超时');
        req.destroy();
      });
      
      req.end();
      
      if (attempts >= maxAttempts) {
        clearInterval(checkService);
        console.error('Python服务启动超时，但服务可能已经在运行');
        // 即使超时，也尝试标记为运行中
        isPythonServiceRunning = true;
        resolve(true);
      }
    }, 1000);
  });
}

// 停止Python服务
function stopPythonService() {
  if (pythonServiceProcess) {
    console.log('正在停止Python服务...');
    
    // 尝试优雅关闭
    pythonServiceProcess.kill('SIGTERM');
    
    // 等待3秒，如果进程还未退出，强制杀死
    setTimeout(() => {
      if (pythonServiceProcess) {
        console.log('Python服务未响应，强制终止...');
        pythonServiceProcess.kill('SIGKILL');
      }
    }, 3000);
    
    pythonServiceProcess = null;
    isPythonServiceRunning = false;
    console.log('Python服务已停止');
  }
}

// 调用Python服务
function callPythonService(message, context) {
  return new Promise((resolve, reject) => {
    if (!isPythonServiceRunning) {
      reject(new Error('Python服务未运行'));
      return;
    }
    
    const postData = JSON.stringify({
      message: message,
      context: context,
      api_key: 'iNjoFN6OE1BS_tio6SWa478Dw6DPbIuKpccEOp7wKOh_f3xf6eDxS0EGgHTYYJG-j3tp-TdGuNATgl0l2WJ0wQ',
      api_endpoint: 'https://api.modelarts-maas.com/openai/v1/chat/completions',
      model: 'qwen3-coder-480b-a35b-instruct',  // 恢复到可用的模型
      session_id: 'default'
    });
    
    const req = http.request(
      {
        hostname: '127.0.0.1',  // 使用明确的IPv4地址
        port: PYTHON_SERVICE_PORT,
        path: '/chat',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: 120000 // 120秒超时
      },
      (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          try {
            const result = JSON.parse(data);
            resolve(result);
          } catch (e) {
            reject(new Error(`解析响应失败: ${e.message}`));
          }
        });
      }
    );
    
    req.on('error', (e) => {
      reject(new Error(`请求失败: ${e.message}`));
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('请求超时'));
    });
    
    req.write(postData);
    req.end();
  });
}

function createWindow() {
  const iconPath = path.join(__dirname, 'icons', process.platform === 'darwin' ? 'icon.icns' : 'app-icon.png');
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    autoHideMenuBar: true,
    icon: iconPath,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webviewTag: true,
      webSecurity: false,
      allowRunningInsecureContent: true
    }
  });

  mainWindow.loadFile('index.html');
}

ipcMain.handle('open-external-url', async (_event, url) => {
  if (!url || typeof url !== 'string') {
    return { success: false, error: '无效的 URL' };
  }
  await shell.openExternal(url);
  return { success: true };
});

app.whenReady().then(() => {
  clearStaleIndexedDBLocks();
  configurePlatformSessions();
  app.on('web-contents-created', (_event, contents) => {
    setupWebviewGuest(contents);
  });
  createWindow();

  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) {
        mainWindow.restore();
      }
      mainWindow.focus();
    }
  });

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  // 停止Python服务
  stopPythonService();
  
  if (process.platform !== 'darwin') app.quit();
});

// 应用退出时停止Python服务
app.on('before-quit', () => {
  stopPythonService();
});

ipcMain.handle('open-file-dialog', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [
      { name: 'Excel Files', extensions: ['xlsx', 'xls', 'csv'] }
    ]
  });
  if (!canceled) {
    return filePaths[0];
  }
  return null;
});

ipcMain.handle('save-file-dialog', async () => {
  const { canceled, filePath } = await dialog.showSaveDialog({
    filters: [
      { name: 'Excel Files', extensions: ['xlsx'] }
    ]
  });
  if (!canceled) {
    return filePath;
  }
  return null;
});

// 读取Excel文件
ipcMain.handle('read-excel-file', async (event, data) => {
  const { filePath } = data;
  
  try {
    console.log('读取Excel文件:', filePath);
    
    // 读取Excel文件
    const workbook = XLSX.readFile(filePath);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    
    // 转换为JSON
    const jsonData = XLSX.utils.sheet_to_json(worksheet);
    
    // 获取列名
    const columns = Object.keys(jsonData[0] || {});
    
    console.log('Excel文件读取成功，数据行数:', jsonData.length);
    
    return {
      success: true,
      data: jsonData,
      columns: columns,
      sheetName: sheetName
    };
  } catch (error) {
    console.error('读取Excel文件失败:', error);
    return {
      success: false,
      error: error.message
    };
  }
});

// 创建Excel文件
ipcMain.handle('create-excel-file', async (event, data) => {
  const { data: excelData, fileName } = data;
  
  try {
    console.log('创建Excel文件:', fileName);
    
    // 创建工作簿
    const workbook = XLSX.utils.book_new();
    
    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(excelData);
    
    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
    
    // 生成Excel文件
    const excelBuffer = XLSX.write(workbook, { type: 'buffer', bookType: 'xlsx' });
    
    // 让用户选择保存路径
    const result = await dialog.showSaveDialog({
      title: '保存Excel文件',
      defaultPath: fileName || 'output.xlsx',
      filters: [
        { name: 'Excel文件', extensions: ['xlsx', 'xls'] }
      ]
    });
    
    if (result.filePath) {
      // 写入文件
      fs.writeFileSync(result.filePath, excelBuffer);
      console.log('Excel文件创建成功:', result.filePath);
      
      return {
        success: true,
        filePath: result.filePath
      };
    } else {
      return {
        success: false,
        error: '用户取消了保存'
      };
    }
  } catch (error) {
    console.error('创建Excel文件失败:', error);
    return {
      success: false,
      error: error.message
    };
  }
});

// 调用Python智能体
ipcMain.handle('call-python-agent', async (event, data) => {
  const { message, context = {}, api_key, api_endpoint, model } = data;
  
  console.log('收到调用Python智能体的请求:', { message, context, api_key, api_endpoint, model });
  
  try {
    // 检查Python服务是否运行
    if (!isPythonServiceRunning) {
      console.log('Python服务未运行，尝试启动...');
      try {
        await startPythonService();
        console.log('Python服务已重新启动');
      } catch (startError) {
        console.error('启动Python服务失败:', startError);
        return {
          success: false,
          error: 'Python服务启动失败，请检查Python环境'
        };
      }
    }
    
    // 使用HTTP请求调用Python服务
    const result = await callPythonService(message, context, api_key, api_endpoint, model);
    return result;
  } catch (error) {
    console.error('调用Python服务失败:', error);
    return {
      success: false,
      error: error.message || '调用Python服务失败'
    };
  }
});

// 打开文件
ipcMain.handle('open-file', async (event, data) => {
  const { filePath } = data;
  
  console.log('打开文件:', filePath);
  
  try {
    const { shell } = require('electron');
    await shell.openPath(filePath);
    return { success: true };
  } catch (error) {
    console.error('打开文件失败:', error);
    return { success: false, error: error.message };
  }
});

// 打开AI平台
ipcMain.handle('open-ai-platform', async (event, data) => {
  const { platform } = data;
  
  console.log('打开AI平台:', platform);
  
  const platformUrls = {
    'chatgpt': 'https://chatgpt.com/',
    'kimi': 'https://kimi.moonshot.cn/',
    'deepseek': 'https://chat.deepseek.com/',
    'yuanbao': 'https://yuanbao.tencent.com/',
    'doubao': 'https://doubao.com/'
  };
  
  const url = platformUrls[platform];
  if (!url) {
    return { success: false, error: '不支持的平台' };
  }
  
  try {
    const { shell } = require('electron');
    await shell.openExternal(url);
    return { success: true };
  } catch (error) {
    console.error('打开AI平台失败:', error);
    return { success: false, error: error.message };
  }
});