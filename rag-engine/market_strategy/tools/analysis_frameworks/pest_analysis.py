"""
PEST 宏观环境分析框架
PEST = Political + Economic + Social + Technological
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class PESTItem:
    """PEST 分析项目"""
    item: str
    impact: str  # "positive" / "negative" / "neutral"
    level: str   # "high" / "medium" / "low"
    description: str
    confidence: float


@dataclass
class PESTDimension:
    """PEST 分析维度"""
    dimension: str
    items: List[PESTItem]
    overall_impact: str
    confidence: float


class PESTAnalyzer:
    """PEST 宏观环境分析器"""

    # 政治/政策因素 (Political)
    POLITICAL_FACTORS = [
        {
            "name": "新能源汽车购置税减免政策",
            "impact": "positive",
            "level": "high",
            "description": "2025年延续购置税减免政策，推动新能源消费"
        },
        {
            "name": "双积分政策走向",
            "impact": "negative",
            "level": "high",
            "description": "双积分考核趋严，倒逼企业加速新能源转型"
        },
        {
            "name": "地方补贴退坡节奏",
            "impact": "neutral",
            "level": "medium",
            "description": "各地补贴政策陆续退坡，影响部分地区销量"
        },
        {
            "name": "碳排放法规（国七）",
            "impact": "negative",
            "level": "high",
            "description": "国七排放标准实施在即，燃油车压力加大"
        },
        {
            "name": "限牌限购政策",
            "impact": "positive",
            "level": "medium",
            "description": "部分城市对新能源车有牌照优惠"
        },
        {
            "name": "汽车出口关税调整",
            "impact": "neutral",
            "level": "medium",
            "description": "贸易摩擦影响出口，需关注关税变化"
        }
    ]

    # 经济因素 (Economic)
    ECONOMIC_FACTORS = [
        {
            "name": "GDP增速与消费信心",
            "impact": "positive",
            "level": "high",
            "description": "经济复苏带动消费信心回升"
        },
        {
            "name": "贷款利率水平（车贷利率）",
            "impact": "positive",
            "level": "high",
            "description": "利率下行降低购车成本，刺激消费"
        },
        {
            "name": "居民可支配收入增长",
            "impact": "positive",
            "level": "high",
            "description": "收入增长提升购车能力"
        },
        {
            "name": "原材料价格（锂、钴、镍）",
            "impact": "negative",
            "level": "medium",
            "description": "原材料价格波动影响电池成本"
        },
        {
            "name": "二手车市场成熟度",
            "impact": "neutral",
            "level": "medium",
            "description": "二手车市场发展影响新车置换需求"
        },
        {
            "name": "汇率波动",
            "impact": "neutral",
            "level": "medium",
            "description": "影响进口零部件成本和出口竞争力"
        }
    ]

    # 社会文化因素 (Social)
    SOCIAL_FACTORS = [
        {
            "name": "城镇化率提升",
            "impact": "positive",
            "level": "high",
            "description": "城镇化带来新增购车需求"
        },
        {
            "name": "环保意识增强",
            "impact": "positive",
            "level": "high",
            "description": "环保意识提升促进新能源消费"
        },
        {
            "name": "Z世代购车偏好",
            "impact": "positive",
            "level": "medium",
            "description": "Z世代成为购车主力，注重科技感和个性化"
        },
        {
            "name": "家庭结构变化（小型化）",
            "impact": "neutral",
            "level": "medium",
            "description": "小型家庭增多影响车型选择"
        },
        {
            "name": "共享出行渗透率",
            "impact": "negative",
            "level": "medium",
            "description": "共享出行发展可能抑制私家车需求"
        },
        {
            "name": "女性购车群体崛起",
            "impact": "positive",
            "level": "medium",
            "description": "女性购车比例提升，市场需求多样化"
        }
    ]

    # 技术因素 (Technological)
    TECHNOLOGICAL_FACTORS = [
        {
            "name": "纯电/插混/增程技术路线演进",
            "impact": "positive",
            "level": "high",
            "description": "技术进步提升产品竞争力"
        },
        {
            "name": "智能驾驶（L2/L3/L4）普及率",
            "impact": "positive",
            "level": "high",
            "description": "智驾成为核心竞争维度"
        },
        {
            "name": "800V高压平台渗透",
            "impact": "positive",
            "level": "medium",
            "description": "超充技术解决里程焦虑"
        },
        {
            "name": "固态电池商业化进程",
            "impact": "positive",
            "level": "low",
            "description": "固态电池是未来方向，但商业化尚需时间"
        },
        {
            "name": "OTA升级能力",
            "impact": "positive",
            "level": "medium",
            "description": "软件定义汽车成为趋势"
        },
        {
            "name": "芯片供应格局",
            "impact": "negative",
            "level": "medium",
            "description": "高端芯片依赖进口，存在供应链风险"
        }
    ]

    def __init__(self, market: str = "乘用车"):
        self.market = market
        self.analysis = {}

    def analyze_political(self) -> PESTDimension:
        """分析政治/政策环境"""
        items = [
            PESTItem(
                item=f["name"],
                impact=f["impact"],
                level=f["level"],
                description=f["description"],
                confidence=0.9 if f["level"] == "high" else 0.7
            )
            for f in self.POLITICAL_FACTORS
        ]

        # 计算整体影响
        positive_count = sum(1 for i in items if i.impact == "positive")
        negative_count = sum(1 for i in items if i.impact == "negative")

        if positive_count > negative_count:
            overall = "positive"
        elif negative_count > positive_count:
            overall = "negative"
        else:
            overall = "neutral"

        return PESTDimension(
            dimension="Political",
            items=items,
            overall_impact=overall,
            confidence=0.85
        )

    def analyze_economic(self) -> PESTDimension:
        """分析经济环境"""
        items = [
            PESTItem(
                item=f["name"],
                impact=f["impact"],
                level=f["level"],
                description=f["description"],
                confidence=0.9 if f["level"] == "high" else 0.7
            )
            for f in self.ECONOMIC_FACTORS
        ]

        positive_count = sum(1 for i in items if i.impact == "positive")
        overall = "positive" if positive_count > len(items) / 2 else "negative"

        return PESTDimension(
            dimension="Economic",
            items=items,
            overall_impact=overall,
            confidence=0.80
        )

    def analyze_social(self) -> PESTDimension:
        """分析社会文化环境"""
        items = [
            PESTItem(
                item=f["name"],
                impact=f["impact"],
                level=f["level"],
                description=f["description"],
                confidence=0.85
            )
            for f in self.SOCIAL_FACTORS
        ]

        positive_count = sum(1 for i in items if i.impact == "positive")
        overall = "positive" if positive_count > len(items) / 2 else "neutral"

        return PESTDimension(
            dimension="Social",
            items=items,
            overall_impact=overall,
            confidence=0.75
        )

    def analyze_technological(self) -> PESTDimension:
        """分析技术环境"""
        items = [
            PESTItem(
                item=f["name"],
                impact=f["impact"],
                level=f["level"],
                description=f["description"],
                confidence=0.9 if f["level"] == "high" else 0.7
            )
            for f in self.TECHNOLOGICAL_FACTORS
        ]

        positive_count = sum(1 for i in items if i.impact == "positive")
        overall = "positive" if positive_count > len(items) / 2 else "neutral"

        return PESTDimension(
            dimension="Technological",
            items=items,
            overall_impact=overall,
            confidence=0.80
        )

    def full_analysis(self) -> Dict[str, Any]:
        """执行完整 PEST 分析"""
        political = self.analyze_political()
        economic = self.analyze_economic()
        social = self.analyze_social()
        technological = self.analyze_technological()

        return {
            "market": self.market,
            "dimensions": {
                "political": asdict(political),
                "economic": asdict(economic),
                "social": asdict(social),
                "technological": asdict(technological)
            },
            "summary": {
                "overall_sentiment": self._calculate_overall_sentiment([
                    political, economic, social, technological
                ]),
                "key_opportunities": self._extract_opportunities([
                    political, economic, social, technological
                ]),
                "key_threats": self._extract_threats([
                    political, economic, social, technological
                ])
            }
        }

    def _calculate_overall_sentiment(self, dimensions: List[PESTDimension]) -> str:
        """计算整体情绪"""
        positive = sum(1 for d in dimensions if d.overall_impact == "positive")
        negative = sum(1 for d in dimensions if d.overall_impact == "negative")

        if positive >= 3:
            return "非常积极"
        elif positive == 2:
            return "积极"
        elif negative >= 2:
            return "谨慎"
        else:
            return "中性"

    def _extract_opportunities(self, dimensions: List[PESTDimension]) -> List[str]:
        """提取机会"""
        opportunities = []
        for dim in dimensions:
            for item in dim.items:
                if item.impact == "positive" and item.level == "high":
                    opportunities.append(f"[{dim.dimension}] {item.item}")
        return opportunities[:5]

    def _extract_threats(self, dimensions: List[PESTDimension]) -> List[str]:
        """提取威胁"""
        threats = []
        for dim in dimensions:
            for item in dim.items:
                if item.impact == "negative" and item.level == "high":
                    threats.append(f"[{dim.dimension}] {item.item}")
        return threats[:5]


def main():
    parser = argparse.ArgumentParser(description='PEST 宏观环境分析工具')
    parser.add_argument('--market', type=str, default='乘用车',
                       help='目标市场')
    parser.add_argument('--output', type=str, default=None,
                       help='输出文件路径')

    args = parser.parse_args()

    analyzer = PESTAnalyzer(market=args.market)
    result = analyzer.full_analysis()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(json.dumps({"success": True, "output": args.output}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
