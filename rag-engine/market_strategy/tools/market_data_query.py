"""
市场数据查询工具
命令行接口：python market_data_query.py --action overview --top_n 10
"""

import sys
import os
import json
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_strategy.knowledge_base import MarketKnowledgeBase


def query_overview(kb: MarketKnowledgeBase, time_range: str = "最近12个月",
                   tech_type: str = None, segment: str = None, level: str = None):
    """查询市场概况"""
    data = kb.get_market_overview(
        time_range=time_range,
        tech_type=tech_type,
        segment=segment,
        level=level
    )
    return {
        "type": "market_overview",
        "data": {
            "total_sales": data.get('total_sales', 0),
            "avg_monthly_sales": data.get('avg_monthly_sales', 0),
            "brand_count": data.get('brand_count', 0),
            "model_count": data.get('model_count', 0),
            "data_period": data.get('data_period', 'N/A'),
            "monthly_data": data.get('monthly_data', [])
        }
    }


def query_brand(kb: MarketKnowledgeBase, time_range: str = "最近12个月",
                top_n: int = 10, tech_type: str = None):
    """查询品牌排名"""
    data = kb.get_sales_by_brand(
        time_range=time_range,
        top_n=top_n,
        tech_type=tech_type
    )
    return {
        "type": "brand_ranking",
        "count": len(data),
        "data": data
    }


def query_model(kb: MarketKnowledgeBase, time_range: str = "最近12个月",
                top_n: int = 20, brand: str = None, tech_type: str = None):
    """查询车型排名"""
    data = kb.get_sales_by_model(
        time_range=time_range,
        top_n=top_n,
        brand=brand,
        tech_type=tech_type
    )
    return {
        "type": "model_ranking",
        "count": len(data),
        "data": data
    }


def query_trend(kb: MarketKnowledgeBase, tech_type: str = None, segment: str = None):
    """查询销量趋势"""
    data = kb.get_sales_trend(
        tech_type=tech_type,
        segment=segment
    )
    return {
        "type": "sales_trend",
        "count": len(data),
        "data": data
    }


def query_segment(kb: MarketKnowledgeBase, time_range: str = "最近12个月"):
    """查询细分市场分布"""
    data = kb.get_segment_distribution(time_range=time_range)
    return {
        "type": "segment_distribution",
        "count": len(data),
        "data": data
    }


def main():
    parser = argparse.ArgumentParser(description='市场数据查询工具')
    parser.add_argument('--action', type=str, required=True,
                       choices=['overview', 'brand', 'model', 'trend', 'segment'],
                       help='查询类型')
    parser.add_argument('--time_range', type=str, default='最近12个月',
                       help='时间范围')
    parser.add_argument('--tech_type', type=str, default=None,
                       help='技术类型: 纯电动/插电式混合动力/常规混合动力')
    parser.add_argument('--segment', type=str, default=None,
                       help='细分市场: SUV/A/B/C/MPV')
    parser.add_argument('--level', type=str, default=None,
                       help='车型级别')
    parser.add_argument('--top_n', type=int, default=10,
                       help='返回数量')
    parser.add_argument('--brand', type=str, default=None,
                       help='品牌名称')

    args = parser.parse_args()

    kb = MarketKnowledgeBase()
    try:
        if args.action == 'overview':
            result = query_overview(kb, args.time_range, args.tech_type, args.segment, args.level)
        elif args.action == 'brand':
            result = query_brand(kb, args.time_range, args.top_n, args.tech_type)
        elif args.action == 'model':
            result = query_model(kb, args.time_range, args.top_n, args.brand, args.tech_type)
        elif args.action == 'trend':
            result = query_trend(kb, args.tech_type, args.segment)
        elif args.action == 'segment':
            result = query_segment(kb, args.time_range)
        else:
            result = {"success": False, "error": f"未知动作: {args.action}"}

        output = {
            "success": True,
            "action": args.action,
            **result
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))
    finally:
        kb.close()


if __name__ == '__main__':
    main()
