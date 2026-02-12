const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  saveFileDialog: () => ipcRenderer.invoke('save-file-dialog'),
  callPythonAgent: (message, context) => ipcRenderer.invoke('call-python-agent', { message, context }),
  readExcelFile: (filePath) => ipcRenderer.invoke('read-excel-file', { filePath }),
  createExcelFile: (data, fileName) => ipcRenderer.invoke('create-excel-file', { data, fileName }),
  openFile: (filePath) => ipcRenderer.invoke('open-file', { filePath })
});