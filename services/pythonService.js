const { PythonShell } = require('python-shell');

class PythonService {
  static executePython(code, options = {}) {
    return new Promise((resolve, reject) => {
      const pyshell = new PythonShell('temp_script.py', {
        mode: 'text',
        ...options
      });

      let output = '';
      let error = '';

      pyshell.on('message', (message) => {
        output += message + '\n';
      });

      pyshell.on('error', (err) => {
        error += err.message + '\n';
      });

      pyshell.on('close', (code) => {
        if (code === 0 && error === '') {
          resolve({ success: true, output });
        } else {
          resolve({ success: false, error: error || `Python script exited with code ${code}` });
        }
      });

      pyshell.send(code);
      pyshell.end();
    });
  }

  static executePythonFile(filePath, args = []) {
    return new Promise((resolve, reject) => {
      PythonShell.run(filePath, {
        args: args
      }, (err, results) => {
        if (err) {
          resolve({ success: false, error: err.message });
        } else {
          resolve({ success: true, output: results.join('\n') });
        }
      });
    });
  }
}