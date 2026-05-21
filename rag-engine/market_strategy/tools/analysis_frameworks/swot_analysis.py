"""
SWOT 分析框架
SWOT = Strengths + Weaknesses + Opportunities + Threats
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class SWOTItem:
    """SWOT 分析项目"""
    item: str
    evidence: str
    confidence: float  # 0-1
    weight: str  # "high" / "medium" / "low"


class SWOTAnalyzer:
    """SWOT 分析器"""

    def __init__(self, brand: str = "目标品牌", market_data: Dict = None):
        self.brand = brand
        self.market_data = market_data or {}
        self.strengths = []
        self.weaknesses = []
        self.opportunities = []
        self.threats = []

    def analyze_from_market_data(self) -> None:
        """基于市场数据分析 SWOT"""
        brand_ranking = self.market_data.get('brand_ranking', [])

        # 查找该品牌的市场表现
        brand_data = None
        for b in brand_ranking:
            if self.brand in b.get('brand', ''):
                brand_data = b
                break

        if brand_data:
            share = brand_data.get('share', 0)
            sales = brand_data.get('sales', 0)

            # 优势
            if share >= 10:
                self.strengths.append(SWOTItem(
                    item="市场份额领先",
                    evidence=f"市场份额{share:.1f}%，处于第一梯队",
                    confidence=0.95,
                    weight="high"
                ))
            elif share >= 5:
                self.strengths.append(SWOTItem(
                    item="市场份额较高",
                    evidence=f"市场份额{share:.1f}%",
                    confidence=0.90,
                    weight="medium"
                ))

            self.strengths.append(SWOTItem(
                item="销量规模",
                evidence=f"年销量{sales:,}辆",
                confidence=0.95,
                weight="medium"
            ))

        # 劣势 - 基于一般假设
        self.weaknesses.append(SWOTItem(
            item="产品线覆盖可能不完整",
            evidence="需要根据实际情况调整",
            confidence=0.60,
            weight="medium"
        ))

        # 机会
        self.opportunities.append(SWOTItem(
            item="新能源市场快速增长",
            evidence="政策支持和消费升级驱动",
            confidence=0.85,
            weight="high"
        ))

        self.opportunities.append(SWOTItem(
            item="出口市场增长",
            evidence="中国品牌国际化加速",
            confidence=0.80,
            weight="medium"
        ))

        # 威胁
        self.threats.append(SWOTItem(
            item="价格战加剧",
            evidence="市场竞争激烈，频繁降价",
            confidence=0.90,
            weight="high"
        ))

        self.threats.append(SWOTItem(
            item="新势力围攻",
            evidence="蔚小理、零跑等新品牌崛起",
            confidence=0.85,
            weight="high"
        ))

    def add_strength(self, item: str, evidence: str, confidence: float = 0.8) -> None:
        """添加优势项"""
        self.strengths.append(SWOTItem(item, evidence, confidence, "high"))

    def add_weakness(self, item: str, evidence: str, confidence: float = 0.7) -> None:
        """添加劣势项"""
        self.weaknesses.append(SWOTItem(item, evidence, confidence, "medium"))

    def add_opportunity(self, item: str, evidence: str, confidence: float = 0.8) -> None:
        """添加机会项"""
        self.opportunities.append(SWOTItem(item, evidence, confidence, "high"))

    def add_threat(self, item: str, evidence: str, confidence: float = 0.8) -> None:
        """添加威胁项"""
        self.threats.append(SWOTItem(item, evidence, confidence, "high"))

    def generate_full_analysis(self) -> Dict[str, Any]:
        """生成完整 SWOT 分析"""

        # 如果没有自定义数据，尝试从市场数据分析
        if not self.strengths and not self.weaknesses:
            self.analyze_from_market_data()

        # 默认 SWOT 项目
        if not self.strengths:
            self.strengths = [
                SWOTItem("品牌知名度高", "市场认知度好", 0.85, "high"),
                SWOTItem("技术积累深厚", "研发实力强", 0.80, "medium"),
                SWOTItem("渠道网络覆盖广", "销售网络完善", 0.85, "medium"),
            ]

        if not self.weaknesses:
            self.weaknesses = [
                SWOTItem("智能化配置可能存在短板", "智驾能力待提升", 0.70, "medium"),
                SWOTItem("产品线可能过于单一", "细分市场覆盖不足", 0.65, "medium"),
                SWOTItem("品牌形象可能老化", "年轻化不足", 0.60, "low"),
            ]

        if not self.opportunities:
            self.opportunities = [
                SWOTItem("新能源市场增速超预期", "政策+消费双重驱动", 0.90, "high"),
                SWOTItem("出口市场增长空间大", "海外市场拓展加速", 0.85, "high"),
                SWOTItem("下沉市场增量机会", "三四线城市需求释放", 0.80, "medium"),
            ]

        if not self.threats:
            self.threats = [
                SWOTItem("价格战持续加剧", "利润率承压", 0.90, "high"),
                SWOTItem("新势力品牌围攻", "竞争格局重塑", 0.85, "high"),
                SWOTItem("原材料成本波动", "供应链风险", 0.75, "medium"),
            ]

        # 生成策略建议
        strategies = self._generate_strategies()

        return {
            "brand": self.brand,
            "swot": {
                "strengths": [self._item_to_dict(s) for s in self.strengths],
                "weaknesses": [self._item_to_dict(w) for w in self.weaknesses],
                "opportunities": [self._item_to_dict(o) for o in self.opportunities],
                "threats": [self._item_to_dict(t) for t in self.threats]
            },
            "strategies": strategies,
            "summary": self._generate_summary()
        }

    def _item_to_dict(self, item: SWOTItem) -> Dict:
        return {
            "item": item.item,
            "evidence": item.evidence,
            "confidence": item.confidence,
            "weight": item.weight
        }

    def _generate_strategies(self) -> Dict[str, List[str]]:
        """生成 SWOT 策略矩阵"""
        strategies = {
            "SO_strategy": [],  # 优势+机会
            "WO_strategy": [],  # 劣势+机会
            "ST_strategy": [],  # 优势+威胁
            "WT_strategy": []   # 劣势+威胁
        }

        # SO 策略
        strategies["SO_strategy"] = [
            "利用品牌优势，抓住新能源增长红利",
            "发挥技术积累，加速产品智能化",
            "借助渠道优势，拓展海外市场"
        ]

        # WO 策略
        strategies["WO_strategy"] = [
            "加大智能化投入，抓住技术升级机会",
            "丰富产品线，把握细分市场机会",
            "年轻化品牌形象，吸引Z世代"
        ]

        # ST 策略
        strategies["ST_strategy"] = [
            "发挥成本优势，应对价格战",
            "强化品牌形象，抵御新势力冲击",
            "利用技术壁垒，构建护城河"
        ]

        # WT 策略
        strategies["WT_strategy"] = [
            "收缩战线，聚焦核心市场",
            "控制成本，提升运营效率",
            "寻求战略合作，增强竞争力"
        ]

        return strategies

    def _generate_summary(self) -> Dict[str, Any]:
        """生成 SWOT 分析摘要"""
        avg_confidence = (
            sum(s.confidence for s in self.strengths) / max(len(self.strengths), 1) +
            sum(w.confidence for w in self.weaknesses) / max(len(self.weaknesses), 1)
        ) / 2

        return {
            "overall_confidence": round(avg_confidence, 2),
            "key_strength": self.strengths[0].item if self.strengths else "N/A",
            "key_weakness": self.weaknesses[0].item if self.weaknesses else "N/A",
            "main_opportunity": self.opportunities[0].item if self.opportunities else "N/A",
            "main_threat": self.threats[0].item if self.threats else "N/A",
            "strategic_posture": "进攻型" if len(self.strengths) > len(self.weaknesses) else "防御型"
        }


def main():
    parser = argparse.ArgumentParser(description='SWOT 分析工具')
    parser.add_argument('--brand', type=str, required=True,
                       help='分析品牌')
    parser.add_argument('--use_market_data', type=bool, default=False,
                       help='是否使用市场数据')
    parser.add_argument('--output', type=str, default=None,
                       help='输出文件路径')

    args = parser.parse_args()

    analyzer = SWOTAnalyzer(brand=args.brand)

    if args.use_market_data:
        # 尝试从市场数据加载
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            from market_strategy.knowledge_base import MarketKnowledgeBase
            kb = MarketKnowledgeBase()
            brands = kb.get_sales_by_brand(top_n=50)
            analyzer.market_data = {'brand_ranking': brands}
            kb.close()
        except Exception as e:
            print(f"Warning: 无法加载市场数据，使用默认分析: {e}")

    result = analyzer.generate_full_analysis()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(json.dumps({"success": True, "output": args.output}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
