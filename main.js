const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile('index_final.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
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

// 调用Python智能体
ipcMain.handle('call-python-agent', async (event, data) => {
  const { message, context = {} } = data;
  
  console.log('收到调用Python智能体的请求:', { message, context });
  
  return new Promise((resolve, reject) => {
    try {
      // 检查Python是否可用
      const { execSync } = require('child_process');
      let pythonCommand = 'py';
      
      try {
        execSync('py --version', { stdio: 'ignore' });
        console.log('使用 py 命令');
      } catch (error) {
        try {
          execSync('python --version', { stdio: 'ignore' });
          pythonCommand = 'python';
          console.log('使用 python 命令');
        } catch (error) {
          try {
            execSync('python3 --version', { stdio: 'ignore' });
            pythonCommand = 'python3';
            console.log('使用 python3 命令');
          } catch (error) {
            console.error('Python未安装或未添加到PATH环境变量');
            reject({
              success: false,
              error: 'Python未安装或未添加到PATH环境变量。请先安装Python并确保可以在命令行中运行python命令。'
            });
            return;
          }
        }
      }
      
      // 创建临时输入文件
      const tempDir = os.tmpdir();
      const inputFile = path.join(tempDir, `agent_input_${Date.now()}.json`);
      
      const inputData = {
        message: message,
        context: context,
        api_key: 'iNjoFN6OE1BS_tio6SWa478Dw6DPbIuKpccEOp7wKOh_f3xf6eDxS0EGgHTYYJG-j3tp-TdGuNATgl0l2WJ0wQ',
        api_endpoint: 'https://api.modelarts-maas.com/openai/v1/chat/completions',
        model: 'qwen3-coder-480b-a35b-instruct'
      };
      
      console.log('创建临时输入文件:', inputFile);
      fs.writeFileSync(inputFile, JSON.stringify(inputData, null, 2), 'utf-8');
      
      // 调用Python脚本
      const pythonScript = path.join(__dirname, 'agent_simple.py');
      console.log('调用Python脚本:', pythonScript);
      const pythonProcess = spawn(pythonCommand, [pythonScript, inputFile]);
      
      let stdout = '';
      let stderr = '';
      
      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        console.log('Python脚本执行完成，退出码:', code);
        console.log('stdout:', stdout);
        console.log('stderr:', stderr);
        
        // 删除临时文件
        try {
          fs.unlinkSync(inputFile);
        } catch (err) {
          console.error('删除临时文件失败:', err);
        }
        
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (err) {
            console.error('解析输出失败:', err);
            resolve({
              success: false,
              error: `解析输出失败: ${err.message}`,
              stdout: stdout,
              stderr: stderr
            });
          }
        } else {
          console.error('Python脚本执行失败，退出码:', code);
          reject({
            success: false,
            error: `Python脚本执行失败，退出码: ${code}`,
            stderr: stderr
          });
        }
      });
      
      pythonProcess.on('error', (err) => {
        console.error('启动Python进程失败:', err);
        reject({
          success: false,
          error: `启动Python进程失败: ${err.message}`
        });
      });
      
    } catch (error) {
      console.error('调用Python智能体失败:', error);
      reject({
        success: false,
        error: error.message
      });
    }
  });
});