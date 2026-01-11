# Knowledge Graph Builder

[![GitHub stars](https://img.shields.io/github/stars/Gail-peng/EASY-Knowledge-Graph-Builder)](https://github.com/Gail-peng/EASY-Knowledge-Graph-Builder/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Gail-peng/EASY-Knowledge-Graph-Builder)](https://github.com/Gail-peng/EASY-Knowledge-Graph-Builder/network)
[![GitHub issues](https://img.shields.io/github/issues/Gail-peng/EASY-Knowledge-Graph-Builder)](https://github.com/Gail-peng/EASY-Knowledge-Graph-Builder/issues)

## 项目简介

Knowledge Graph Builder 是一个强大的AI驱动知识图谱构建工具，能够将非结构化文本转换为结构化的知识图谱。通过结合大语言模型(LLM)的文本理解能力和图数据库的存储优势，实现从原始文本到语义网络的自动化转换。

## 功能特点

- 🎯 **多模型支持**：兼容多种主流LLM模型，包括智谱AI GLM系列、OpenAI GPT系列、Anthropic Claude系列、Google Gemini系列等
- 📊 **可视化界面**：基于Streamlit构建的直观用户界面，支持步骤式操作
- 📚 **文档处理**：支持多种文档格式的上传和解析（.txt, .docx等）
- 🔗 **知识抽取**：自动从文本中提取实体、关系和属性，构建三元组
- 📝 **Schema定义**：支持自定义本体Schema，规范知识图谱的结构
- 🗄️ **图数据库集成**：与Neo4j无缝集成，实现知识的高效存储和查询
- ⚡ **实时进度**：提供实时的处理进度和状态更新

## 技术栈

- **前端框架**：Streamlit
- **后端语言**：Python
- **LLM框架**：LangChain
- **图数据库**：Neo4j
- **文档处理**：python-docx
- **配置管理**：YAML

## 项目结构

```
Knowledge-Graph-Builder/
├── app.py                    # 主应用入口
├── components/               # UI组件目录
│   ├── __init__.py
│   └── ui_components.py      # 自定义UI组件
├── config/                   # 配置文件目录
│   └── app_config.py         # 应用配置
├── data/                     # 示例数据
│   └── test.docx
├── styles/                   # 样式文件目录
│   ├── main.css              # 自定义CSS
│   └── main.js               # 自定义JavaScript
├── utils/                    # 工具函数目录
│   ├── config_manager.py     # 配置管理
│   ├── doc_loader.py         # 文档加载
│   ├── graph_db.py           # 图数据库操作
│   └── llm_extractor.py      # LLM抽取
├── config.yaml               # 示例本体配置
├── requirements.txt          # 依赖列表
└── README.md                 # 项目说明
```

## 快速开始

### 环境要求

- Python 3.8+
- Neo4j 4.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. **Neo4j数据库配置**
   - 安装并启动Neo4j数据库
   - 默认配置：URI: `bolt://localhost:7687`，用户名: `neo4j`，密码: `password`
   - 可在应用中修改数据库配置

2. **LLM API Key配置**
   - 在应用中根据选择的LLM模型输入对应的API Key

### 启动项目

```bash
python -m streamlit run app.py
```

访问 `http://localhost:8502` 即可使用应用。

## 使用指南

### 步骤1：配置Schema

- **方式1：上传Schema文件**
  - 上传YAML格式的本体定义文件
  - 示例格式见 `config.yaml`

- **方式2：手动输入Schema**
  - 在文本框中输入YAML格式的本体定义

本体Schema定义示例：

```yaml
entities:
  - name: "Person"
    properties:
      - "name"
      - "age"
      - "birthDate"
  - name: "Organization"
    properties:
      - "name"
      - "industry"

relationships:
  - head: "Person"
    relation: "worksAt"
    tail: "Organization"
  - head: "Person"
    relation: "livesIn"
    tail: "Location"
```

### 步骤2：上传文档

- 支持上传 `.txt` 和 `.docx` 格式的文档
- 系统会自动将文档分割成合适大小的文本块

### 步骤3：配置LLM和数据库

- **选择LLM模型**：从下拉菜单中选择要使用的LLM模型
- **输入API Key**：根据选择的模型输入对应的API Key
- **配置Neo4j**：输入Neo4j数据库的连接信息（URI、用户名、密码）

### 步骤4：构建知识图谱

- 点击"Build Knowledge Graph"按钮开始构建过程
- 系统会实时显示处理进度
- 构建完成后，可查看抽取的三元组和知识图谱统计信息

## 模块说明

### app.py
主应用入口，负责界面渲染和业务流程控制。

### components/ui_components.py
包含自定义UI组件，如页面头部、步骤导航、加载状态等。

### utils/doc_loader.py
负责文档的加载和预处理，支持多种文档格式。

### utils/llm_extractor.py
核心模块，使用LLM从文本中抽取实体、关系和属性，构建三元组。

### utils/graph_db.py
负责与Neo4j数据库的交互，执行Cypher语句进行数据存储。

### utils/config_manager.py
配置管理工具，负责加载和保存应用配置。

### styles/main.css 和 styles/main.js
自定义样式和脚本，用于美化界面和增强用户体验。

## 开发

### 环境搭建

```bash
# 克隆项目
git clone https://github.com/Gail-peng/EASY-Knowledge-Graph-Builder.git
cd Knowledge-Graph-Builder

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python -m streamlit run app.py
```

### 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 感谢所有贡献者
- 感谢Streamlit、LangChain和Neo4j等开源项目的支持

## 声明

如果您觉得这个项目对您有帮助，请给它一个⭐️！

如果您基于此项目进行二次开发，请在代码中注明来源：

```
基于 Knowledge Graph Builder 项目开发
原项目地址：https://github.com/Gail-peng/EASY-Knowledge-Graph-Builder
```

---

**Enjoy building knowledge graphs! 🎉**