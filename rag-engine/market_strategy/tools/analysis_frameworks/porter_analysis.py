"""
波特五力分析框架
Porter's Five Forces = 现有竞争者 + 新进入者 + 替代品 + 供应商 + 买方
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any
from dataclasses import dataclass

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class PorterForce:
    """波特五力中的单一力量"""
    name: str
    score: int  # 1-10
    level: str  # "very_high" / "high" / "medium" / "low"
    description: str
    factors: List[str]
    impact: str  # "threat" / "opportunity"


class PorterAnalyzer:
    """波特五力分析器"""

    def __init__(self, segment: str = "乘用车"):
        self.segment = segment

    def analyze_competitive_rivalry(self, market_data: Dict = None) -> PorterForce:
        """
        分析现有竞争者威胁
        影响因素：市场集中度、产品差异化、品牌忠诚度、退出壁垒
        """
        # 基于市场数据的分析
        cr3 = 0
        cr5 = 0

        if market_data and 'brand_ranking' in market_data:
            brands = market_data['brand_ranking']
            if len(brands) >= 3:
                cr3 = sum(b.get('share', 0) for b in brands[:3])
            if len(brands) >= 5:
                cr5 = sum(b.get('share', 0) for b in brands[:5])

        # 计算竞争强度得分
        score = 5
        factors = []

        if cr3 >= 50:
            score += 2
            factors.append(f"头部集中(CR3={cr3:.1f}%)")
        elif cr3 >= 30:
            score += 1
            factors.append(f"中等集中(CR3={cr3:.1f}%)")

        factors.append("价格战激烈")
        factors.append("产品同质化严重")
        factors.append("品牌忠诚度下降")

        level = "very_high" if score >= 8 else "high" if score >= 6 else "medium"

        return PorterForce(
            name="现有竞争者威胁",
            score=min(score, 10),
            level=level,
            description=f"市场竞争激烈，CR3={cr3:.1f}%，头部品牌占据主导地位",
            factors=factors,
            impact="threat"
        )

    def analyze_new_entrant_threat(self) -> PorterForce:
        """
        分析新进入者威胁
        影响因素：资本壁垒、技术壁垒、渠道壁垒、政策壁垒
        """
        score = 7
        factors = [
            "造车资质门槛降低",
            "新能源赛道吸引资本",
            "代工模式降低门槛",
            "科技公司跨界造车"
        ]

        level = "high"

        return PorterForce(
            name="新进入者威胁",
            score=score,
            level=level,
            description="新能源赛道吸引大量新进入者，威胁持续存在",
            factors=factors,
            impact="threat"
        )

    def analyze_substitute_threat(self) -> PorterForce:
        """
        分析替代品威胁
        影响因素：公共交通、共享出行、远程办公
        """
        score = 4
        factors = [
            "共享出行快速发展（滴滴、高德）",
            "公共交通网络完善",
            "远程办公降低通勤需求",
            "但私家车需求仍刚性"
        ]

        level = "medium"

        return PorterForce(
            name="替代品威胁",
            score=score,
            level=level,
            description="共享出行有一定替代，但私家车仍是主流选择",
            factors=factors,
            impact="neutral"
        )

    def analyze_supplier_power(self, market_data: Dict = None) -> PorterForce:
        """
        分析供应商议价能力
        影响因素：电池厂商集中度、芯片厂商、锂矿资源
        """
        score = 6
        factors = [
            "宁德时代电池份额领先",
            "芯片厂商话语权强（英伟达、地平线）",
            "锂矿资源集中",
            "电池成本占比高"
        ]

        level = "high"

        return PorterForce(
            name="供应商议价能力",
            score=score,
            level=level,
            description="电池和芯片是关键零部件，供应商议价能力强",
            factors=factors,
            impact="threat"
        )

    def analyze_buyer_power(self) -> PorterForce:
        """
        分析买方议价能力
        影响因素：信息透明度、转换成本、价格敏感度
        """
        score = 5
        factors = [
            "汽车之家/懂车帝等信息透明",
            "消费者比价方便",
            "品牌切换成本低",
            "价格敏感度高"
        ]

        level = "medium"

        return PorterForce(
            name="买方议价能力",
            score=score,
            level=level,
            description="信息透明化提升了买方议价能力",
            factors=factors,
            impact="threat"
        )

    def full_analysis(self, market_data: Dict = None) -> Dict[str, Any]:
        """执行完整波特五力分析"""

        forces = {
            "competitive_rivalry": self.analyze_competitive_rivalry(market_data),
            "new_entrant_threat": self.analyze_new_entrant_threat(),
            "substitute_threat": self.analyze_substitute_threat(),
            "supplier_power": self.analyze_supplier_power(market_data),
            "buyer_power": self.analyze_buyer_power()
        }

        # 计算整体行业吸引力
        total_score = sum(f.score for f in forces.values())
        avg_score = total_score / 5

        if avg_score >= 7:
            industry_attractiveness = "低吸引力 - 竞争激烈，利润压缩"
        elif avg_score >= 5:
            industry_attractiveness = "中等吸引力 - 机遇与挑战并存"
        else:
            industry_attractiveness = "较高吸引力 - 相对蓝海"

        return {
            "segment": self.segment,
            "forces": {k: {
                "name": v.name,
                "score": v.score,
                "level": v.level,
                "description": v.description,
                "factors": v.factors,
                "impact": v.impact
            } for k, v in forces.items()},
            "summary": {
                "industry_attractiveness": industry_attractiveness,
                "overall_score": round(avg_score, 1),
                "most_threatening_force": max(forces.items(), key=lambda x: x[1].score)[1].name,
                "strategic_recommendations": self._generate_recommendations(forces)
            }
        }

    def _generate_recommendations(self, forces: Dict[str, PorterForce]) -> List[str]:
        """生成战略建议"""
        recommendations = []

        # 基于各力量的建议
        if forces["competitive_rivalry"].score >= 7:
            recommendations.append("差异化竞争：聚焦细分市场，避免正面价格战")

        if forces["new_entrant_threat"].score >= 6:
            recommendations.append("构建壁垒：强化品牌、技术、渠道优势")

        if forces["supplier_power"].score >= 6:
            recommendations.append("垂直整合：考虑自建或战略合作保障供应链安全")

        if forces["buyer_power"].score >= 5:
            recommendations.append("提升体验：强化服务、口碑和用户忠诚度")

        return recommendations


def main():
    parser = argparse.ArgumentParser(description='波特五力分析工具')
    parser.add_argument('--segment', type=str, default='乘用车',
                       help='细分市场')
    parser.add_argument('--cr3', type=float, default=None,
                       help='CR3市场集中度')
    parser.add_argument('--output', type=str, default=None,
                       help='输出文件路径')

    args = parser.parse_args()

    # 如果提供了 CR3，可以传入 market_data
    market_data = None
    if args.cr3:
        market_data = {
            "brand_ranking": [
                {"share": args.cr3 / 3},
                {"share": args.cr3 / 3},
                {"share": args.cr3 / 3}
            ]
        }

    analyzer = PorterAnalyzer(segment=args.segment)
    result = analyzer.full_analysis(market_data)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(json.dumps({"success": True, "output": args.output}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
