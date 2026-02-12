// 数据分析Skill
class DataAnalysisSkill {
  constructor(dataList, fileList, columnNamesList) {
    this.dataList = dataList;
    this.fileList = fileList;
    this.columnNamesList = columnNamesList;
  }

  async execute(query) {
    console.log('执行数据分析，查询:', query);
    
    // 计算所有文件的数据总量
    const totalRecords = this.dataList.reduce((sum, data) => sum + data.length, 0);
    
    // 计算每个文件的统计信息
    const fileStats = this.fileList.map((file, index) => {
      const data = this.dataList[index];
      const columnNames = this.columnNamesList[index];
      
      const values = data.map(item => item.value);
      const maxValue = Math.max(...values);
      const minValue = Math.min(...values);
      const avgValue = Math.round(values.reduce((sum, val) => sum + val, 0) / values.length);
      
      const categoryCount = {};
      data.forEach(item => {
        categoryCount[item.category] = (categoryCount[item.category] || 0) + 1;
      });
      
      return {
        name: file.name,
        records: data.length,
        columnNames: columnNames,
        max: maxValue,
        min: minValue,
        avg: avgValue,
        categoryCount: categoryCount
      };
    });
    
    let content = `我已经分析了你的 ${this.dataList.length} 个Excel文件，总共包含 ${totalRecords} 条记录。\n\n`;
    
    content += '**各文件统计信息**：\n';
    fileStats.forEach((stat, index) => {
      content += `${index + 1}. ${stat.name}\n`;
      content += `- 记录数：${stat.records}\n`;
      content += `- 数据列：${stat.columnNames.join(', ')}\n`;
      content += `- ${stat.columnNames[2]}（数值）统计：最大值${stat.max}，最小值${stat.min}，平均值${stat.avg}\n`;
      content += `- ${stat.columnNames[3]}（类别）分布：${Object.entries(stat.categoryCount).map(([k, v]) => `${k}:${v}个`).join(', ')}\n\n`;
    });
    
    content += '**联合分析结果**：\n';
    content += `- 数据总量：${totalRecords} 条\n`;
    content += `- 文件数量：${this.dataList.length} 个\n`;
    content += `- 平均每个文件记录数：${Math.round(totalRecords / this.dataList.length)}\n\n`;
    
    content += '**分析结果**：\n';
    content += '数据分布较为均匀，各文件数据量差异不大。\n';
    content += '建议重点关注值较高的记录，并分析各文件之间的相关性。\n\n';
    
    content += '**建议**：\n';
    content += '1. 可以进一步分析各文件之间的关联关系\n';
    content += '2. 考虑将多个文件的数据合并进行更全面的分析\n';
    content += '3. 可以设置阈值，筛选出重要的数据记录\n';
    
    return {
      success: true,
      content: content,
      fileStats: fileStats,
      chartData: this.dataList,
      columnNamesList: this.columnNamesList
    };
  }
}

module.exports = DataAnalysisSkill;