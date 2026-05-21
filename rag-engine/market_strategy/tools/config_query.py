"""
竞品配置查询工具
命令行接口：python config_query.py --energy_type 纯电动 --top_n 10
"""

import sys
import os
import json
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_strategy.knowledge_base import MarketKnowledgeBase


def query_configs(brand: str = None, energy_type: str = None,
                 level: str = None, top_n: int = 50):
    """查询竞品配置"""
    kb = MarketKnowledgeBase()
    try:
        data = kb.get_competitor_configs(
            brand=brand,
            energy_type=energy_type,
            level=level,
            top_n=top_n
        )
        return {
            "type": "config_query",
            "filters": {
                "brand": brand,
                "energy_type": energy_type,
                "level": level
            },
            "count": len(data),
            "data": data
        }
    finally:
        kb.close()


def main():
    parser = argparse.ArgumentParser(description='竞品配置查询工具')
    parser.add_argument('--brand', type=str, default=None,
                       help='品牌名称')
    parser.add_argument('--energy_type', type=str, default=None,
                       help='能源类型: 纯电动/插电式混合动力')
    parser.add_argument('--level', type=str, default=None,
                       help='级别: A00/A/B/C/D')
    parser.add_argument('--top_n', type=int, default=50,
                       help='返回数量')

    args = parser.parse_args()

    try:
        result = query_configs(
            brand=args.brand,
            energy_type=args.energy_type,
            level=args.level,
            top_n=args.top_n
        )

        output = {
            "success": True,
            **result
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
