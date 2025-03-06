一款轻量级Python工具，用于批量检测域名在Bing搜索引擎中的收录情况。具有彩色命令行界面、自动保存机制和详细的HTML分析功能，无需第三方依赖。

![BingIndexTracker界面预览](https://i.imgur.com/example.png)

## ✨ 功能特点

- 🔍 **批量查询** - 一次性检查多个域名的Bing收录状态
- 🌈 **彩色界面** - 美观的命令行彩色输出，查询过程一目了然
- 💾 **自动保存** - 定期保存结果，意外中断也不丢失数据
- 📊 **结果排序** - 按收录页面数量从高到低排序，突出重要域名
- 🔄 **断点续传** - 程序中断时会保存当前进度，支持后续恢复
- 🚀 **零依赖** - 仅使用Python标准库，无需安装额外包（除colorama外）

## 🔧 安装方法

### 方法1：直接下载可执行文件

从[Releases](https://github.com/xiaoxin3242/BingIndexTracker/releases)页面下载最新的可执行文件，无需安装Python环境。

### 方法2：从源码运行

1. 确保已安装Python 3.6或更高版本
2. 克隆此仓库：
   ```
   git clone https://github.com/xiaoxin3242/BingIndexTracker.git
   cd BingIndexTracker
   ```
3. 安装colorama库：
   ```
   pip install colorama
   ```
4. 运行脚本：
   ```
   python bing_index_tracker.py
   ```

## 📖 使用说明

1. 启动程序后，将会弹出文件选择对话框
2. 选择包含域名列表的文本文件（每行一个域名）
3. 选择结果保存位置
4. 设置是否启用调试模式和查询延迟
5. 按Enter键开始查询
6. 查询完成后，结果将保存为CSV文件，可用Excel打开

### 域名文件格式

域名列表文件应为纯文本格式，每行一个域名：

```
example.com
mywebsite.org
test-site.net
```

## 🛡️ 数据保护机制

本工具具有多重数据保护机制：

- **定期自动保存**：每查询10个域名后自动保存临时结果
- **意外中断保护**：程序被强制关闭时自动保存当前结果
- **错误恢复**：发生错误时保存已查询数据
- **系统信号处理**：捕获Ctrl+C等中断信号并安全退出

## 🔄 版本历史

- **v1.1** - 添加自动保存功能和异常处理机制
- **v1.0** - 初始版本，基本查询功能和彩色界面

## 📝 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 👨‍💻 作者

本软件由AI编写，博客：[blog.xiaoxinbk.cn](http://blog.xiaoxinbk.cn)

## 🔗 相关链接

- [博客文章：如何批量检查网站收录情况](http://blog.xiaoxinbk.cn)
- [提交问题或建议](https://github.com/xiaoxin3242/BingIndexTracker/issues)

## ⭐ 支持项目

如果您觉得这个工具有用，请考虑给它一个星标 ⭐

