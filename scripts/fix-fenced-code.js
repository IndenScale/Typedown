#!/usr/bin/env node
/**
 * 自动为无语言标识的代码块添加 `text` 签名
 * 
 * 使用方法:
 *   node scripts/fix-fenced-code.js <file1.md> [file2.md ...]
 */

const fs = require('fs');
const path = require('path');
const { globSync } = require('glob');

// 匹配没有语言标识的代码块围栏 ```（只在代码块开始处）
function fixContent(content) {
  const lines = content.split('\n');
  let inCodeBlock = false;
  let modified = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const fenceMatch = line.match(/^(```)\s*$/);
    
    if (fenceMatch) {
      if (!inCodeBlock) {
        // 这是代码块的开始，且没有语言标识
        lines[i] = '```text';
        modified = true;
        inCodeBlock = true;
      } else {
        // 这是代码块的结束
        inCodeBlock = false;
      }
    } else if (line.match(/^```/)) {
      // 有语言标识的代码块开始或结束
      if (!inCodeBlock) {
        inCodeBlock = true;
      } else {
        // 检查是否是结束标记（行中只有 ``` 或后面只有空格）
        if (line.match(/^```\s*$/)) {
          inCodeBlock = false;
        }
      }
    }
  }
  
  return modified ? lines.join('\n') : content;
}

function fixFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const newContent = fixContent(content);
  
  if (newContent !== content) {
    fs.writeFileSync(filePath, newContent, 'utf8');
    console.log(`✓ Fixed: ${filePath}`);
    return true;
  }
  
  return false;
}

function findFiles(pattern) {
  if (pattern.includes('*')) {
    return globSync(pattern, { 
      absolute: true,
      ignore: ['node_modules/**', '.venv/**', 'dist/**', 'build/**', 'website/node_modules/**']
    });
  }
  return [path.resolve(pattern)];
}

// 主程序
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node fix-fenced-code.js <file1.md> [file2.md ...]');
    console.log('       node fix-fenced-code.js "**/*.md"');
    process.exit(1);
  }
  
  let changedCount = 0;
  let processedCount = 0;
  
  for (const arg of args) {
    const files = findFiles(arg);
    
    for (const file of files) {
      if (path.extname(file) === '.md' && fs.existsSync(file)) {
        processedCount++;
        if (fixFile(file)) changedCount++;
      }
    }
  }
  
  console.log(`\nProcessed: ${processedCount} files`);
  console.log(`Fixed: ${changedCount} files`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
