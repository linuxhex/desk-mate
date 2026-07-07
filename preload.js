const { contextBridge } = require('electron');

// 预留 IPC 接口，当前 UI 仅使用 webview，不主动调用
contextBridge.exposeInMainWorld('electronAPI', {});
