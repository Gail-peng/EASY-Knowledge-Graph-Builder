# 应用配置文件

# 页面配置
PAGE_CONFIG = {
    "page_title": "KG AI Builder",
    "layout": "wide",
    "page_icon": "🔗"
}

# 默认配置
DEFAULT_CONFIG = {
    "neo4j_uri": "neo4j://localhost:7687",
    "neo4j_user": "neo4j",
    "neo4j_password": "password",
    "text_chunk_size": 2000,
    "text_overlap": 100
}

# 状态键名
SESSION_STATE_KEYS = {
    "build_state": "building",
    "build_success": "build_success",
    "current_chunk_index": "current_chunk_index",
    "total_chunks": "total_chunks",
    "processing_start_time": "processing_start_time",
    "total_triples": "total_triples",
    "error_message": "error_message",
    "error_stack": "error_stack",
    "generated_triples": "generated_triples"
}


# 日志级别
LOG_LEVEL = "INFO"