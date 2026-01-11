import streamlit as st


def display_header():
    """显示页面标题和副标题"""
    st.markdown("# 📊 Knowledge Graph Builder")
    st.markdown("### 🔄 从文档到知识图谱的智能转化")



def display_step_navigation(current_step):
    """显示步骤导航"""
    steps = [
        ("上传文档", "上传并预览文档内容"),
        ("配置连接", "设置Neo4j数据库和LLM参数"),
        ("构建图谱", "自动提取三元组并构建知识图谱"),
        ("可视化", "预览和管理生成的知识图谱")
    ]

    col1, col2, col3, col4 = st.columns(4)
    columns = [col1, col2, col3, col4]

    for i, (step_title, step_desc) in enumerate(steps):
        with columns[i]:
            # 步骤编号
            if i == current_step:
                st.markdown(f"<div class='step-number active'>{i + 1}</div>", unsafe_allow_html=True)
            elif i < current_step:
                st.markdown(f"<div class='step-number completed'>✓</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='step-number'>{i + 1}</div>", unsafe_allow_html=True)

            # 步骤标题和描述
            if i == current_step:
                st.markdown(f"<div class='step-title active'>{step_title}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='step-title'>{step_title}</div>", unsafe_allow_html=True)

            st.markdown(f"<div class='step-desc'>{step_desc}</div>", unsafe_allow_html=True)



def display_loading_status():
    """显示加载状态"""
    if st.session_state.building:
        # 显示加载动画
        loading_html = """<div class='loading-container' id='loading-container'>
                    <div class='progress-text'>知识图谱构建中...</div>
                    <div class='progress-bar-container'>
                        <div class='progressive-loader' id='progress-bar'></div>
                    </div>
                    <div class='progress-percentage' id='progress-percentage'>0%</div>
                    <div class='processing-info' id='processing-info'>初始化...</div>
                </div>"""
        st.markdown(loading_html, unsafe_allow_html=True)



def display_triple_cards(triples):
    """显示三元组卡片"""
    if not triples or len(triples) == 0:
        return

    # 每一行显示3个三元组卡片
    for i in range(0, len(triples), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(triples):
                with cols[j]:
                    triple = triples[i + j]
                    card_html = f"""<div class='triple-card'>
                                <div class='triple-item entity'>{triple[0]}</div>
                                <div class='triple-item relation'>{triple[1]}</div>
                                <div class='triple-item entity'>{triple[2]}</div>
                            </div>"""
                    st.markdown(card_html, unsafe_allow_html=True)



def display_neo4j_config():
    """显示Neo4j配置部分"""
    # 默认配置提示
    st.markdown("#### 默认配置")
    st.markdown("如果您是首次使用或只想快速体验，可以直接使用默认配置：")
    st.markdown("- **URI**: neo4j://localhost:7687")
    st.markdown("- **用户名**: neo4j")
    st.markdown("- **密码**: password")
    st.markdown("- 请确保您已经安装并启动了Neo4j数据库服务")

    # 高级配置折叠面板
    with st.expander("🔧 高级配置", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.neo4j_uri = st.text_input("URI", value="neo4j://localhost:7687")
        with col2:
            st.session_state.neo4j_user = st.text_input("用户名", value="neo4j")
        with col3:
            st.session_state.neo4j_password = st.text_input("密码", type="password", value="password")



def display_build_button():
    """显示构建图谱按钮"""
    # 构建按钮
    col1, col2 = st.columns([1, 5])
    with col1:
        build_button = st.button(
            "▶ Build Graph",
            use_container_width=True,
            key="build_graph_button",
            type="primary"
        )
    return build_button