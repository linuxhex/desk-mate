const axios = require('axios');

class AIService {
  static async chatWithAI(messages, model = 'qwen3-coder-480b-a35b-instruct') {
    try {
      const response = await axios.post(
        'https://api.modelarts-maas.com/openai/v1/chat/completions',
        {
          model: model,
          messages: messages,
          temperature: 0.7,
          max_tokens: 1000
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer iNjoFN6OE1BS_tio6SWa478Dw6DPbIuKpccEOp7wKOh_f3xf6eDxS0EGgHTYYJG-j3tp-TdGuNATgl0l2WJ0wQ'
          }
        }
      );

      return {
        success: true,
        content: response.data.choices[0].message.content
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  static async analyzeExcel(data, query) {
    const messages = [
      {
        role: 'system',
        content: '你是一个专业的数据分析助手，擅长分析Excel数据并提供见解。'
      },
      {
        role: 'user',
        content: `请分析以下Excel数据并回答问题：\n\n数据：${JSON.stringify(data.slice(0, 50))}\n\n问题：${query}\n\n请提供详细的分析结果，包括数据洞察、趋势分析和建议。`
      }
    ];

    return this.chatWithAI(messages);
  }

  static async generatePythonCode(data, query) {
    const messages = [
      {
        role: 'system',
        content: '你是一个专业的Python编程助手，擅长生成数据分析代码。'
      },
      {
        role: 'user',
        content: `请根据以下数据和需求生成Python代码：\n\n数据结构：${JSON.stringify(data[0])}\n\n需求：${query}\n\n请生成完整的Python代码，确保代码可以直接运行，并且返回分析结果。`
      }
    ];

    return this.chatWithAI(messages);
  }
}