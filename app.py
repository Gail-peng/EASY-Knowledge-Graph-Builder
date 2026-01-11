import streamlit as st
import yaml
import os
import json
import tempfile
import shutil
from datetime import datetime
from utils.doc_loader import load_document
from utils.graph_db import Neo4jHandler
from utils.llm_extractor import process_text_with_llm, generate_cypher

# 页面配置
st.set_page_config(page_title="KG AI Builder", layout="wide", page_icon="🔗")

# --- 自定义CSS样式 --- 
# 从外部文件加载CSS样式
with open("styles/main.css", "r", encoding="utf-8") as f:
    custom_css = f.read()
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# 页面标题和副标题
st.markdown("""
<h1>KG AI Builder</h1>
<p class="page-subtitle">Transform raw text into structured insights</p>
""", unsafe_allow_html=True)

# 添加JavaScript来禁用输入框的回车提交功能
# 从外部文件加载JavaScript脚本
with open("styles/main.js", "r", encoding="utf-8") as f:
    custom_js = f.read()
st.markdown(f"<script>{custom_js}</script>", unsafe_allow_html=True)

# --- 步骤式主界面 ---

# 主要内容区域
main_col = st.container()

with main_col:
    # 步骤导航
    st.markdown("""
    <div class="steps-container">
        <div class="step-nav">
            <div class="step-item">
                <div class="step-number active">1</div>
                <div class="step-title">SCHEMA CONFIG</div>
                <div class="step-description">Define entity and relationship types</div>
            </div>
            <div class="step-item">
                <div class="step-number">2</div>
                <div class="step-title">SOURCE DOCS</div>
                <div class="step-description">Upload text documents</div>
            </div>
            <div class="step-item">
                <div class="step-number">3</div>
                <div class="step-title">STORAGE</div>
                <div class="step-description">Configure database&LLM settings</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with main_col:
    # 步骤 1: Schema 配置 (YAML)
    st.markdown('<h3>Schema Configuration</h3>', unsafe_allow_html=True)
    uploaded_yaml = st.file_uploader("Upload YAML Schema", type=["yaml", "yml"])

    ontology_content = ""
    if uploaded_yaml:
        try:
            ontology_data = yaml.safe_load(uploaded_yaml)

            ontology_content = yaml.dump(ontology_data, allow_unicode=True)

            # 终端风格展示 YAML 解析结果（统一为一个完整的终端）
            # 使用紧凑的字符串拼接避免多余空白
            terminal_content = '<div class="terminal-container"><div class="terminal-header"><div class="terminal-dot close"></div><div class="terminal-dot minimize"></div><div class="terminal-dot maximize"></div><div class="terminal-title">YAML Schema Analysis</div></div><div class="terminal"><span class="command">$</span> <span class="path">analyze-yaml</span> <span class="result">{0}</span><br><span class="success">✓</span> <span class="info">YAML schema loaded successfully</span><br><br>'.format(
                uploaded_yaml.name)

            # 检查YAML结构，可能键名是'relationships'而不是'relations'
            entities_key = 'entities' if 'entities' in ontology_data else 'entity_types'
            relations_key = 'relations' if 'relations' in ontology_data else 'relationships'

            # 按实体和关系分类展示
            if entities_key in ontology_data:
                terminal_content += '<span class="info">Entities defined:</span><br>'
                for i, entity in enumerate(ontology_data[entities_key]):
                    terminal_content += '<span class="sentence">[{0:2d}] {1}</span><br>'.format(i + 1, entity)

            terminal_content += '<br>'

            if relations_key in ontology_data:
                terminal_content += '<span class="info">Relationships defined:</span><br>'
                for i, relation in enumerate(ontology_data[relations_key]):
                    terminal_content += '<span class="sentence">[{0:2d}] {1}</span><br>'.format(i + 1, relation)

            terminal_content += '</div></div>'
            st.markdown(terminal_content, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"YAML 解析错误: {e}")

    # 提供默认模板
    else:
        st.info("Please upload a YAML file defining entities and relationships")

    # 步骤 2: 上传文档
    # st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Source Documents</h3>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Text Document", type=["pdf", "docx", "xlsx"])

    # 文本块大小配置
    col1, col2 = st.columns(2)
    with col1:
        max_chunk_size = st.number_input("最大文本块大小 (字符数)", min_value=500, max_value=4000,
                                         value=2000, step=100,
                                         key="max_chunk_input")
    with col2:
        min_chunk_size = st.number_input("最小文本块大小 (字符数)", min_value=100, max_value=2000,
                                         value=500, step=50,
                                         key="min_chunk_input")

    chunks = []
    if uploaded_file:
        with st.spinner("智能解析文档中..."):
            chunks_list, err = load_document(uploaded_file, max_chunk_size, min_chunk_size)
            if err:
                st.error(err)
            else:
                chunks = chunks_list
                st.success(f"智能切分完成！共生成 {len(chunks)} 个语义块")

                # 保存文件信息到session state
                st.session_state['uploaded_files'] = [{
                    'name': uploaded_file.name,
                    'size': uploaded_file.size,
                    'chunks_count': len(chunks),
                    'uploaded_at': datetime.now().isoformat()
                }]

                # 显示统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总文本块数", len(chunks))
                with col2:
                    avg_size = sum(len(chunk) for chunk in chunks) // len(chunks) if chunks else 0
                    st.metric("平均块大小", f"{avg_size} 字符")
                with col3:
                    total_chars = sum(len(chunk) for chunk in chunks)
                    st.metric("总字符数", f"{total_chars} 字符")

                # 终端风格展示解析内容
                terminal_content = '<div class="terminal-container"><div class="terminal-header"><div class="terminal-dot close"></div><div class="terminal-dot minimize"></div><div class="terminal-dot maximize"></div><div class="terminal-title">Document Parsing Results</div></div><div class="terminal"><span class="command">$</span> <span class="path">smart-parse-document</span> <span class="result">{0}</span><br><span class="success">✓</span> <span class="info">Document parsed successfully with smart segmentation</span><br><span class="info">Total semantic chunks:</span> <span class="result">{1}</span><br><span class="info">Average chunk size:</span> <span class="result">{2} chars</span><br><br><span class="info">Sample chunks:</span><br>'.format(
                    uploaded_file.name, len(chunks), avg_size)

                # 显示前3个文本块
                for i, chunk in enumerate(chunks[:3]):
                    preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                    terminal_content += '<span class="sentence">[{0:2d}] {1}</span><br>'.format(i + 1, preview)

                # 如果文本块数量超过3个，显示省略号
                if len(chunks) > 3:
                    terminal_content += '<span class="info">... and {0} more chunks</span><br>'.format(len(chunks) - 3)

                terminal_content += '</div></div>'
                st.markdown(terminal_content, unsafe_allow_html=True)

    # 步骤 3: 存储配置
    # st.markdown('<h3>Storage Configuration</h3>', unsafe_allow_html=True)

    # LLM 模型选择
    st.subheader("LLM Configuration")
    llm_options = [
        {"name": "GLM-4-Flash (智谱AI)", "key": "glm4", "model_name": "glm-4-flash",
         "api_key_label": "Zhipu AI API Key"},
        {"name": "GLM-4 (智谱AI)", "key": "glm4_full", "model_name": "glm-4", "api_key_label": "Zhipu AI API Key"},
        {"name": "GPT-4 (OpenAI)", "key": "gpt4", "model_name": "gpt-4", "api_key_label": "OpenAI API Key"},
        {"name": "GPT-3.5-Turbo (OpenAI)", "key": "gpt35", "model_name": "gpt-3.5-turbo",
         "api_key_label": "OpenAI API Key"},
        {"name": "GPT-4-Turbo (OpenAI)", "key": "gpt4_turbo", "model_name": "gpt-4-turbo",
         "api_key_label": "OpenAI API Key"},
        {"name": "Claude 3-Opus (Anthropic)", "key": "claude3_opus", "model_name": "claude-3-opus-20240229",
         "api_key_label": "Anthropic API Key"},
        {"name": "Claude 3-Sonnet (Anthropic)", "key": "claude3_sonnet", "model_name": "claude-3-sonnet-20240229",
         "api_key_label": "Anthropic API Key"},
        {"name": "Claude 3-Haiku (Anthropic)", "key": "claude3_haiku", "model_name": "claude-3-haiku-20240307",
         "api_key_label": "Anthropic API Key"},
        {"name": "Gemini-Pro (Google)", "key": "gemini_pro", "model_name": "gemini-pro",
         "api_key_label": "Google API Key"},
        {"name": "Gemini-Pro-Vision (Google)", "key": "gemini_pro_vision", "model_name": "gemini-pro-vision",
         "api_key_label": "Google API Key"},
        {"name": "Qwen-Turbo (阿里云通义千问)", "key": "qwen_turbo", "model_name": "qwen-turbo",
         "api_key_label": "Aliyun API Key"},
        {"name": "Qwen-Plus (阿里云通义千问)", "key": "qwen_plus", "model_name": "qwen-plus",
         "api_key_label": "Aliyun API Key"},
        {"name": "Llama 3-8B (Meta)", "key": "llama3_8b", "model_name": "llama3-8b",
         "api_key_label": "Llama 3 API Key"},
        {"name": "Llama 3-70B (Meta)", "key": "llama3_70b", "model_name": "llama3-70b",
         "api_key_label": "Llama 3 API Key"}
    ]

    # 渲染模型选择下拉框
    default_llm_index = 0

    llm_choice = st.selectbox(
        "Select LLM Model",
        options=llm_options,
        index=default_llm_index,
        format_func=lambda x: x["name"]
    )

    # 根据选择的模型显示对应的API Key输入框，使用缓存数据
    selected_llm_key = llm_choice["key"]
    selected_model_name = llm_choice["model_name"]
    api_key_label = llm_choice["api_key_label"]
    api_key = st.text_input(api_key_label,
                            value='',
                            type="password",
                            key="api_key_input")

    # 数据库配置，使用缓存数据
    st.subheader("Database (Neo4j)")

    # 添加说明文字
    st.markdown("💡 **大多数情况下，您只需要设置密码即可连接本地Neo4j数据库。**")
    st.markdown("默认配置：URI: `bolt://localhost:7687`，用户名: `neo4j`")

    # 使用默认值
    default_uri = 'bolt://localhost:7687'
    default_user = 'neo4j'

    # 初始化变量
    neo4j_uri = default_uri
    neo4j_user = default_user

    # 使用session_state来跟踪折叠面板状态
    if 'neo4j_expander_expanded' not in st.session_state:
        st.session_state.neo4j_expander_expanded = False

    # 使用折叠面板让高级配置可选
    expander_expanded = st.checkbox("🔧 显示高级配置（如需修改默认设置）",
                                    value=st.session_state.neo4j_expander_expanded,
                                    key="neo4j_expander_checkbox")

    # 更新session_state
    st.session_state.neo4j_expander_expanded = expander_expanded

    if expander_expanded:
        with st.expander("高级配置", expanded=True):
            # 使用不同的变量名，然后在外部更新
            uri_input = st.text_input("Neo4j URI",
                                      value=default_uri,
                                      placeholder="bolt://localhost:7687",
                                      key="neo4j_uri_input",
                                      help="Neo4j数据库连接地址，默认使用本地7687端口")
            user_input = st.text_input("Neo4j Username",
                                       value=default_user,
                                       placeholder="neo4j",
                                       key="neo4j_user_input",
                                       help="Neo4j数据库用户名，默认为neo4j")
        # 在expander块外更新外部变量
        neo4j_uri = uri_input
        neo4j_user = user_input
    else:
        # 使用默认值，不显示高级配置
        neo4j_uri = default_uri
        neo4j_user = default_user

    # 密码输入框始终显示
    neo4j_pwd = st.text_input("Neo4j Password",
                              value='',
                              type="password",
                              placeholder="请输入您的Neo4j密码",
                              key="neo4j_pwd_input",
                              help="Neo4j数据库密码，这是必填项")

    # 缓存管理已移除，仅保留自动保存

    # 初始化session_state用于构建结果
    if 'build_success' not in st.session_state:
        st.session_state.build_success = None
    if 'build_error' not in st.session_state:
        st.session_state.build_error = None
    if 'build_stats' not in st.session_state:
        st.session_state.build_stats = None
    if 'build_traceback' not in st.session_state:
        st.session_state.build_traceback = None
    if 'current_chunk' not in st.session_state:
        st.session_state.current_chunk = None
    if 'processing_progress' not in st.session_state:
        st.session_state.processing_progress = 0
    if 'current_chunk_content' not in st.session_state:
        st.session_state.current_chunk_content = None
    if 'current_triples' not in st.session_state:
        st.session_state.current_triples = None

    # 生成图谱按钮，使用参考图片样式
    build_button_clicked = st.button("▶ Build Graph", type="primary", use_container_width=True)

    # 创建动态更新容器
    progress_container = st.empty()
    result_container = st.empty()
    loading_container = st.empty()

    # 按钮点击事件处理逻辑
    if build_button_clicked:
        # 立即显示加载动画
        loading_html = """
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">正在初始化处理...</div>
            <div class="loading-subtext">正在验证配置和建立连接</div>
            <div class="progressive-loader">
                <div class="progressive-loader-bar"></div>
            </div>
        </div>
        """
        loading_container.markdown(loading_html, unsafe_allow_html=True)

        # 验证所有必需配置
        missing_items = []
        if not neo4j_uri:
            missing_items.append("Neo4j URI")
        if not api_key:
            missing_items.append("API Key")
        if not ontology_content:
            missing_items.append("YAML Schema Configuration")
        if not chunks:
            missing_items.append("Source Documents")

        if missing_items:
            loading_container.empty()
            st.error(f"⚠️ 请完成以下配置: {', '.join(missing_items)}")
            st.stop()

        # 初始化数据库连接
        db_handler = Neo4jHandler(neo4j_uri, neo4j_user, neo4j_pwd)
        conn_success, _ = db_handler.test_connection()

        if not conn_success:
            loading_container.empty()
            st.error("数据库连接失败，无法继续。")
            st.stop()

        total_chunks = len(chunks)
        total_triples = 0

        try:
            # 重置进度状态
            st.session_state.processing_progress = 0
            st.session_state.current_chunk = None
            st.session_state.current_chunk_content = None
            st.session_state.current_triples = None

            # 等待加载条完成动画
            import time

            time.sleep(1)  # 等待1秒让加载条完成加载动画

            # 初始化完成，显示初始处理界面
            loading_container.empty()

            # 实时更新进度显示
            with progress_container.container():
                st.markdown("---")
                # 显示处理进度
                progress_col1, progress_col2 = st.columns([1, 3])
                with progress_col1:
                    st.metric("处理进度", f"{st.session_state.processing_progress}%")
                with progress_col2:
                    st.progress(st.session_state.processing_progress / 100)
                st.info("📄 准备开始处理文本块...")
                st.write("正在初始化处理环境，请稍候...")

            # 使用智能切分的文本块进行处理
            for i, chunk in enumerate(chunks):
                # 更新进度信息
                progress_percent = int((i + 1) / total_chunks * 100)
                st.session_state.processing_progress = progress_percent
                st.session_state.current_chunk = f"第 {i + 1}/{total_chunks} 块"

                # 保存当前文本块内容用于显示
                st.session_state.current_chunk_content = chunk
                st.session_state.current_triples = None

                # 实时更新进度显示（开始处理新块）
                with progress_container.container():
                    st.markdown("---")
                    # 显示处理进度
                    progress_col1, progress_col2 = st.columns([1, 3])
                    with progress_col1:
                        st.metric("处理进度", f"{st.session_state.processing_progress}%")
                    with progress_col2:
                        st.progress(st.session_state.processing_progress / 100)

                    # 显示当前处理的文本块信息
                    st.info(f"📄 正在处理文本块: {st.session_state.current_chunk}")

                    # 显示当前文本块内容（限制长度）
                    st.subheader("当前处理的文本内容")
                    chunk_preview = st.session_state.current_chunk_content
                    if len(chunk_preview) > 300:
                        chunk_preview = chunk_preview[:300] + "..."
                    st.markdown('<div class="chunk-container">', unsafe_allow_html=True)
                    st.text_area("文本内容预览", chunk_preview, height=100, key=f"chunk_preview_{i}")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # 显示正在进行LLM抽取
                    st.info("🧠 正在进行知识抽取...")
                    st.write("请稍候，正在使用LLM分析文本内容并抽取三元组...")

                # 1. LLM 抽取（耗时操作）
                triples = process_text_with_llm(chunk, ontology_content, api_key, selected_model_name)

                if triples:
                    total_triples += len(triples)
                    # 保存当前三元组用于显示
                    st.session_state.current_triples = triples

                    # 实时更新进度显示（LLM抽取完成）
                    with progress_container.container():
                        st.markdown("---")
                        # 显示处理进度
                        progress_col1, progress_col2 = st.columns([1, 3])
                        with progress_col1:
                            st.metric("处理进度", f"{st.session_state.processing_progress}%")
                        with progress_col2:
                            st.progress(st.session_state.processing_progress / 100)

                        # 显示当前处理的文本块信息
                        st.info(f"📄 正在处理文本块: {st.session_state.current_chunk}")

                        # 显示当前文本块内容（限制长度）
                        st.subheader("当前处理的文本内容")
                        chunk_preview = st.session_state.current_chunk_content
                        if len(chunk_preview) > 300:
                            chunk_preview = chunk_preview[:300] + "..."
                        st.markdown('<div class="chunk-container">', unsafe_allow_html=True)
                        st.text_area("文本内容预览", chunk_preview, height=100, key=f"chunk_preview_{i}_2")
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 显示抽取的三元组信息
                        st.subheader("抽取的三元组")
                        for j, triple in enumerate(triples):
                            # 美化三元组显示
                            triple_html = f"""
                            <div class="triple-card" style="animation-delay: {j * 0.1}s;">
                                <div class="triple-content">
                                    <div class="entity">
                                        <div class="entity-name">{triple.head}</div>
                                        <div class="entity-type">{triple.head_type}</div>
                                        <div class="entity-properties">
                                            {', '.join([f'{k}: {v}' for k, v in triple.head_properties.items()])}
                                        </div>
                                    </div>
                                    <div class="relation">{triple.relation}</div>
                                    <div class="entity">
                                        <div class="entity-name">{triple.tail}</div>
                                        <div class="entity-type">{triple.tail_type}</div>
                                        <div class="entity-properties">
                                            {', '.join([f'{k}: {v}' for k, v in triple.tail_properties.items()])}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """
                            st.markdown(triple_html, unsafe_allow_html=True)

                        # 显示正在执行Cypher
                        st.info("🗄️ 正在保存到数据库...")
                        st.write("正在生成并执行Cypher查询，将知识图谱保存到Neo4j数据库...")

                    # 2. 生成并执行 Cypher（耗时操作）
                    cypher_queries = generate_cypher(triples)
                    db_handler.execute_cypher(cypher_queries)

                    # 添加短暂延迟以便用户能看到处理内容
                    import time

                    time.sleep(0.5)

            # 保存构建结果到session_state
            st.session_state.build_success = True
            st.session_state.build_error = None
            st.session_state.build_stats = {
                "total_chunks": total_chunks,
                "total_triples": total_triples,
                "efficiency": round(total_triples / total_chunks, 2) if total_chunks > 0 else 0
            }
            # 清空当前处理信息
            st.session_state.current_chunk = None
            st.session_state.processing_progress = 0
            st.session_state.current_chunk_content = None
            st.session_state.current_triples = None

            # 处理完成，清空进度容器并立即显示结果
            progress_container.empty()

            # 显示最终结果
            with result_container.container():
                st.success(
                    f"✅ 任务完成！共处理 {st.session_state.build_stats['total_chunks']} 个语义块，提取并入库了 {st.session_state.build_stats['total_triples']} 个三元组。")

                # 显示统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("处理块数", st.session_state.build_stats['total_chunks'])
                with col2:
                    st.metric("总三元组数", st.session_state.build_stats['total_triples'])
                with col3:
                    st.metric("平均效率", f"{st.session_state.build_stats['efficiency']} 三元组/块")

        except Exception as e:
            st.session_state.build_success = False
            st.session_state.build_error = str(e)
            st.session_state.build_stats = None
            import traceback

            st.session_state.build_traceback = traceback.format_exc()
            # 清空当前处理信息
            st.session_state.current_chunk = None
            st.session_state.processing_progress = 0
            st.session_state.current_chunk_content = None
            st.session_state.current_triples = None

            # 异常情况下，清空进度容器并立即显示错误
            progress_container.empty()

            # 显示最终结果
            with result_container.container():
                st.error(f"❌ 处理过程中发生错误: {st.session_state.build_error}")
                if st.session_state.build_traceback:
                    st.code(st.session_state.build_traceback)
        finally:
            db_handler.close()
            # 重置进度状态
            st.session_state.current_chunk = None
            st.session_state.processing_progress = 0
            st.session_state.current_chunk_content = None
            st.session_state.current_triples = None
    else:
        # 非构建状态下显示静态结果
        with result_container.container():
            if st.session_state.build_success is not None:
                if st.session_state.build_success:
                    st.success(
                        f"✅ 任务完成！共处理 {st.session_state.build_stats['total_chunks']} 个语义块，提取并入库了 {st.session_state.build_stats['total_triples']} 个三元组。")

                    # 显示统计信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("处理块数", st.session_state.build_stats['total_chunks'])
                    with col2:
                        st.metric("总三元组数", st.session_state.build_stats['total_triples'])
                    with col3:
                        st.metric("平均效率", f"{st.session_state.build_stats['efficiency']} 三元组/块")
                else:
                    st.error(f"❌ 处理过程中发生错误: {st.session_state.build_error}")
                    if st.session_state.build_traceback:
                        st.code(st.session_state.build_traceback)