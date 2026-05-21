"""
数据总览工具
命令行接口：python data_summary.py
"""

import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_strategy.knowledge_base import MarketKnowledgeBase


def main():
    """获取数据总览"""
    kb = MarketKnowledgeBase()
    try:
        summary = kb.get_data_summary()

        output = {
            "success": True,
            "type": "data_summary",
            **summary
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))
    finally:
        kb.close()


if __name__ == '__main__':
    main()
