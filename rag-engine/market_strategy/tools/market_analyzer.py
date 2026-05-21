"""
市场分析工具
命令行接口：python market_analyzer.py --query "分析比亚迪市场策略" --time_range 最近12个月
"""

import sys
import os
import json
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_strategy.agent import MarketStrategyAgent
from market_strategy.schemas import MarketInput, AnalysisType


def analyze(query: str, time_range: str = "最近12个月",
           tech_type: str = None, segment: str = None, power_type: str = None):
    """执行市场分析"""
    agent = MarketStrategyAgent()

    try:
        input_data = MarketInput(
            query=query,
            analysis_type=AnalysisType.FULL_ANALYSIS,
            time_range=time_range,
            power_type=power_type or tech_type,
            segment=segment
        )

        output = agent.analyze(input_data)

        # 转换为字典
        result = {
            "success": output.success,
            "query": output.query,
            "analysis_type": str(output.analysis_type),
            "confidence": output.confidence
        }

        if output.market_overview:
            result["market_overview"] = {
                "scale": output.market_overview.scale,
                "growth_rate": output.market_overview.growth_rate,
                "concentration": output.market_overview.concentration,
                "trend": output.market_overview.trend
            }

        if output.competitors:
            result["competitors"] = [
                {
                    "name": c.name,
                    "market_share": c.market_share,
                    "sales_volume": c.sales_volume
                }
                for c in output.competitors[:10]
            ]

        if output.opportunities:
            result["opportunities"] = [
                {
                    "item": o.item,
                    "confidence": o.confidence,
                    "scale": o.scale
                }
                for o in output.opportunities
            ]

        if output.risks:
            result["risks"] = [
                {
                    "item": r.item,
                    "probability": r.probability,
                    "impact": r.impact
                }
                for r in output.risks
            ]

        if output.suggestions:
            result["suggestions"] = output.suggestions

        if output.error:
            result["error"] = output.error

        return result

    finally:
        agent.kb.close()


def main():
    parser = argparse.ArgumentParser(description='市场分析工具')
    parser.add_argument('--query', type=str, required=True,
                       help='分析查询')
    parser.add_argument('--time_range', type=str, default='最近12个月',
                       help='时间范围')
    parser.add_argument('--tech_type', type=str, default=None,
                       help='技术类型')
    parser.add_argument('--segment', type=str, default=None,
                       help='细分市场')
    parser.add_argument('--power_type', type=str, default=None,
                       help='动力类型')

    args = parser.parse_args()

    try:
        result = analyze(
            query=args.query,
            time_range=args.time_range,
            tech_type=args.tech_type,
            segment=args.segment,
            power_type=args.power_type
        )

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
