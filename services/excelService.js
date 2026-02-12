const XLSX = require('xlsx');
const fs = require('fs');

class ExcelService {
  static readExcel(filePath) {
    try {
      const workbook = XLSX.readFile(filePath);
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(worksheet);
      return {
        success: true,
        data,
        sheets: workbook.SheetNames
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  static writeExcel(data, filePath) {
    try {
      const worksheet = XLSX.utils.json_to_sheet(data);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
      XLSX.writeFile(workbook, filePath);
      return {
        success: true
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  static getSheetNames(filePath) {
    try {
      const workbook = XLSX.readFile(filePath);
      return {
        success: true,
        sheets: workbook.SheetNames
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  static readSpecificSheet(filePath, sheetName) {
    try {
      const workbook = XLSX.readFile(filePath);
      const worksheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(worksheet);
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
}