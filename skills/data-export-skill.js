// 数据导出Skill
class DataExportSkill {
  constructor(dataList, fileList, columnNamesList) {
    this.dataList = dataList;
    this.fileList = fileList;
    this.columnNamesList = columnNamesList;
  }

  async execute(query) {
    console.log('执行数据导出，查询:', query);
    
    const timestamp = new Date().getTime();
    const fileName = `分析结果_${timestamp}.csv`;
    
    // 合并所有文件的数据，保持列名一致
    const mergedData = [];
    const allColumnNames = ['ID', '项目名称', '数值', '类别', '日期', '来源文件'];
    
    this.dataList.forEach((data, fileIndex) => {
      const sourceFile = this.fileList[fileIndex].name;
      data.forEach(item => {
        mergedData.push({
          id: item.id,
          name: item.name,
          value: item.value,
          category: item.category,
          date: item.date,
          source: sourceFile
        });
      });
    });
    
    // 生成CSV内容
    const csvContent = allColumnNames.join(',') + '\n';
    mergedData.forEach(item => {
      csvContent += `${item.id},${item.name},${item.value},${item.category},${item.date},${item.source}\n`;
    });
    
    // 创建Blob对象
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    console.log('生成Excel文件完成，数据量:', mergedData.length);
    
    return {
      success: true,
      content: `新Excel文件已生成！\n\n**文件信息**：\n- 文件名：${fileName}\n- 数据量：${mergedData.length} 条\n- 包含列：${allColumnNames.join(', ')}\n\n文件已准备好下载，请点击下方链接打开。`,
      fileName: fileName,
      fileUrl: url,
      downloadBlob: blob,
      mergedData: mergedData,
      allColumnNames: allColumnNames
    };
  }
}

module.exports = DataExportSkill;