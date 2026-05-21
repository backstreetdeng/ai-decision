"""
RAG 检索工具
提供语义搜索能力，检索市场相关的非结构化文档
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from retrieval.retriever import retrieve
from rerank.rerank_service import rerank


def rag_retrieve(
    query: str,
    top_k: int = 5,
    use_rerank: bool = True,
    metadata_filter: dict = None
) -> Dict[str, Any]:
    """
    RAG 语义检索

    Args:
        query: 检索查询
        top_k: 返回数量
        use_rerank: 是否使用重排序
        metadata_filter: 元数据过滤条件
            {
                "source": "乘联会",
                "brand": "比亚迪",
                "category": "行业报告"
            }

    Returns:
        {
            "success": true,
            "query": str,
            "results": [
                {
                    "content": str,
                    "score": float,
                    "metadata": {
                        "source": str,
                        "brand": str,
                        "category": str,
                        "publish_date": str
                    }
                }
            ]
        }
    """
    try:
        # 1. 向量检索（初始取更多，方便 rerank）
        initial_k = top_k * 3 if use_rerank else top_k
        docs = retrieve(
            query=query,
            top_k=initial_k,
            metadata_filter=metadata_filter
        )

        if not docs:
            return {
                "success": True,
                "query": query,
                "results": [],
                "message": "未找到相关文档"
            }

        # 2. 重排序
        if use_rerank and len(docs) > top_k:
            reranked = rerank(
                query=query,
                documents=[
                    {"content": d["document"], "metadata": d.get("metadata", {})}
                    for d in docs
                ],
                top_k=top_k
            )
            results = reranked[:top_k]
        else:
            results = [
                {
                    "content": d["document"],
                    "score": d.get("score", 0),
                    "metadata": d.get("metadata", {})
                }
                for d in docs[:top_k]
            ]

        return {
            "success": True,
            "query": query,
            "results": results,
            "total_found": len(docs),
            "returned": len(results)
        }

    except Exception as e:
        return {
            "success": False,
            "query": query,
            "error": str(e)
        }


def rag_chat(
    question: str,
    session_id: str = None,
    top_k: int = 5,
    metadata_filter: dict = None
) -> Dict[str, Any]:
    """
    RAG 对话（带记忆）

    Args:
        question: 用户问题
        session_id: 会话ID（用于记忆管理）
        top_k: 检索数量
        metadata_filter: 元数据过滤

    Returns:
        {
            "success": true,
            "answer": str,
            "citations": [
                {"content": str, "metadata": dict}
            ]
        }
    """
    try:
        # 延迟导入，避免循环依赖
        from chat.rag_chat_pipeline import chat

        result = chat(
            question=question,
            session_id=session_id,
            top_k=top_k,
            metadata_filter=metadata_filter,
            stream=False
        )

        return {
            "success": True,
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "sources": result.get("sources", [])
        }

    except Exception as e:
        return {
            "success": False,
            "question": question,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description='RAG 检索工具')
    parser.add_argument('--query', type=str, required=True,
                       help='检索查询')
    parser.add_argument('--top_k', type=int, default=5,
                       help='返回数量')
    parser.add_argument('--no_rerank', action='store_true',
                       help='禁用重排序')
    parser.add_argument('--source', type=str, default=None,
                       help='来源过滤（如：乘联会）')
    parser.add_argument('--brand', type=str, default=None,
                       help='品牌过滤（如：比亚迪）')
    parser.add_argument('--category', type=str, default=None,
                       help='类别过滤（如：行业报告）')
    parser.add_argument('--chat', action='store_true',
                       help='使用 RAG 对话模式')
    parser.add_argument('--session_id', type=str, default=None,
                       help='会话ID')

    args = parser.parse_args()

    # 构建 metadata filter
    metadata_filter = {}
    if args.source:
        metadata_filter["source"] = args.source
    if args.brand:
        metadata_filter["brand"] = args.brand
    if args.category:
        metadata_filter["category"] = args.category

    try:
        if args.chat:
            result = rag_chat(
                question=args.query,
                session_id=args.session_id,
                top_k=args.top_k,
                metadata_filter=metadata_filter if metadata_filter else None
            )
        else:
            result = rag_retrieve(
                query=args.query,
                top_k=args.top_k,
                use_rerank=not args.no_rerank,
                metadata_filter=metadata_filter if metadata_filter else None
            )

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
