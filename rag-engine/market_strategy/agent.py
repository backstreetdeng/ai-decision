"""
Market Strategy Agent - 市场战略分析师核心类
负责市场分析、竞品研究、政策解读和机会识别
"""

import json
import re
from typing import Optional, Dict, Any
from pathlib import Path

from .schemas import (
    MarketInput,
    MarketOutput,
    MarketOverview,
    Competitor,
    Opportunity,
    RiskWarning,
    PolicyImpact,
    AnalysisType
)
from .knowledge_base import MarketKnowledgeBase


class MarketStrategyAgent:
    """市场战略分析Agent"""

    def __init__(self, llm_gateway=None):
        """
        初始化Agent

        Args:
            llm_gateway: LLM网关实例（可选，用于复杂分析）
        """
        self.kb = MarketKnowledgeBase()
        self.llm = llm_gateway
        self._load_prompts()

    def _load_prompts(self):
        """加载Prompt模板"""
        prompts_dir = Path(__file__).parent / "prompts"

        # 加载System Prompt
        system_prompt_path = prompts_dir / "system.txt"
        if system_prompt_path.exists():
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = self._get_default_system_prompt()

        # 加载User Prompt模板
        user_prompt_path = prompts_dir / "user.txt"
        if user_prompt_path.exists():
            with open(user_prompt_path, "r", encoding="utf-8") as f:
                self.user_prompt_template = f.read()
        else:
            self.user_prompt_template = self._get_default_user_prompt()

    def _get_default_system_prompt(self) -> str:
        """默认System Prompt"""
        return """你是 **市场战略分析师**，一位专精乘用车市场宏观分析、竞品格局研究和政策影响评估的战略研究专家。

## 你的核心使命
1. 市场宏观分析：分析乘用车市场大盘数据（销量、增速、份额、格局）
2. 竞品格局研究：解析主要竞品的市场定位、产品策略、价格体系
3. 政策影响评估：解读购置税减免、新能源补贴、限牌限购等政策
4. 市场机会识别：评估机会的规模、增速、竞争强度

## 你必须遵守的关键规则
1. **数据优先**：区分事实（数据）和推断（观点），明确标注
2. **战略视角**：关注长期趋势而非短期波动
3. **客观中立**：公正呈现市场格局，不偏袒任何品牌
4. **审慎评估**：承认不确定性，给出置信度评估

## 约束边界
- ✅ 可以：市场规模分析、竞品格局、政策影响、风险预警
- ❌ 不可以：具体定价建议、营销策略建议

## 输出格式
请以JSON格式输出分析结果。
"""

    def _get_default_user_prompt(self) -> str:
        """默认User Prompt模板"""
        return """## 查询
{query}

## 市场数据
{market_data}

## 分析要求
1. 分析市场规模和增速
2. 分析竞争格局（头部品牌、份额、集中度）
3. 识别机会点和风险
4. 给出置信度评估

## 输出要求
以JSON格式输出完整分析报告。
"""

    def analyze(self, input: MarketInput) -> MarketOutput:
        """
        执行市场分析

        Args:
            input: MarketInput 输入

        Returns:
            MarketOutput 输出
        """
        try:
            # 1. 检索市场数据
            market_data = self._retrieve_market_data(input)

            # 2. 构建分析Prompt
            prompt = self._build_prompt(input, market_data)

            # 3. 调用LLM进行推理
            if self.llm:
                response = self.llm.generate(self.system_prompt, prompt)
                output = self._parse_llm_response(response, input)
            else:
                # 无LLM时，直接基于数据进行结构化分析
                output = self._structured_analysis(input, market_data)

            return output

        except Exception as e:
            return MarketOutput(
                success=False,
                query=input.query,
                error=str(e)
            )
        finally:
            self.kb.close()

    def _retrieve_market_data(self, input: MarketInput) -> Dict[str, Any]:
        """检索市场数据"""
        data = {}

        # 市场概况
        overview = self.kb.get_market_overview(
            time_range=input.time_range,
            tech_type=input.power_type,
            segment=input.segment
        )
        data["market_overview"] = overview

        # 品牌排名
        brand_ranking = self.kb.get_sales_by_brand(
            time_range=input.time_range,
            top_n=20,
            tech_type=input.power_type
        )
        data["brand_ranking"] = brand_ranking

        # 细分市场分布
        segment_dist = self.kb.get_segment_distribution()
        data["segment_distribution"] = segment_dist

        # 销量趋势
        trend = self.kb.get_sales_trend(
            tech_type=input.power_type,
            segment=input.segment
        )
        data["sales_trend"] = trend

        return data

    def _build_prompt(self, input: MarketInput, market_data: Dict) -> str:
        """构建Prompt"""
        # 格式化市场数据
        market_data_text = self._format_market_data(market_data)

        return self.user_prompt_template.format(
            query=input.query,
            market_data=market_data_text
        )

    def _format_market_data(self, data: Dict) -> str:
        """格式化市场数据为文本"""
        lines = []

        # 市场概况
        if "market_overview" in data:
            overview = data["market_overview"]
            lines.append("=== 市场概况 ===")
            lines.append(f"总销量: {overview.get('total_sales', 0):,}辆")
            lines.append(f"月均销量: {overview.get('avg_monthly_sales', 0):,.0f}辆")
            lines.append(f"品牌数: {overview.get('brand_count', 0)}")
            lines.append(f"车型数: {overview.get('model_count', 0)}")
            lines.append(f"数据周期: {overview.get('data_period', 'N/A')}")
            lines.append("")

        # 品牌排名
        if "brand_ranking" in data and data["brand_ranking"]:
            lines.append("=== 品牌排名 (Top 10) ===")
            for i, brand in enumerate(data["brand_ranking"][:10], 1):
                lines.append(
                    f"{i}. {brand.get('brand', 'N/A')} - "
                    f"销量: {brand.get('sales', 0):,}辆, "
                    f"份额: {brand.get('share', 0):.1f}%"
                )
            lines.append("")

        # 细分市场
        if "segment_distribution" in data and data["segment_distribution"]:
            lines.append("=== 细分市场分布 ===")
            for seg in data["segment_distribution"]:
                lines.append(
                    f"- {seg.get('segment', 'N/A')}: "
                    f"{seg.get('sales', 0):,}辆 ({seg.get('share', 0):.1f}%)"
                )
            lines.append("")

        # 销量趋势
        if "sales_trend" in data and data["sales_trend"]:
            lines.append("=== 销量趋势 (最近6个月) ===")
            for month_data in data["sales_trend"][-6:]:
                lines.append(
                    f"- {month_data.get('month', 'N/A')}: "
                    f"{month_data.get('sales', 0):,}辆, "
                    f"同比: {month_data.get('yoy_growth', 0):+.1f}%"
                )

        return "\n".join(lines)

    def _structured_analysis(
        self,
        input: MarketInput,
        market_data: Dict
    ) -> MarketOutput:
        """
        基于数据执行结构化分析（无LLM时使用）
        """
        overview_data = market_data.get("market_overview", {})
        brand_ranking = market_data.get("brand_ranking", [])
        segment_dist = market_data.get("segment_distribution", [])
        trend = market_data.get("sales_trend", [])

        # 构建市场概况
        market_overview = MarketOverview(
            scale=f"{overview_data.get('total_sales', 0):,}辆",
            growth_rate=self._calculate_growth_rate(trend),
            concentration=self._calculate_concentration(brand_ranking),
            trend=self._analyze_trend(trend),
            top_players=self._format_top_players(brand_ranking[:5])
        )

        # 构建竞品列表
        competitors = []
        for brand in brand_ranking[:10]:
            competitor = Competitor(
                name=brand.get('brand', 'N/A'),
                brand=brand.get('brand', 'N/A'),
                market_share=brand.get('share', 0),
                sales_volume=brand.get('sales', 0)
            )
            competitors.append(competitor)

        # 识别机会和风险
        opportunities = self._identify_opportunities(market_data)
        risks = self._identify_risks(market_data)

        # 计算置信度
        confidence = self._calculate_confidence(market_data)

        return MarketOutput(
            success=True,
            query=input.query,
            analysis_type=input.analysis_type,
            market_overview=market_overview,
            competitors=competitors,
            opportunities=opportunities,
            risks=risks,
            confidence=confidence,
            confidence_factors={
                "data_coverage": "高" if overview_data.get('total_sales', 0) > 1000000 else "中",
                "data_timeliness": "高",
                "analysis_method": "结构化分析（无LLM）"
            },
            suggestions=self._generate_suggestions(market_data)
        )

    def _calculate_growth_rate(self, trend: list) -> str:
        """计算增速"""
        if len(trend) < 2:
            return "数据不足"

        recent = trend[-1].get('sales', 0)
        previous = trend[-2].get('sales', 0)

        if previous == 0:
            return "数据不足"

        growth = (recent - previous) / previous * 100
        return f"{growth:+.1f}%"

    def _calculate_concentration(self, brand_ranking: list) -> str:
        """计算市场集中度"""
        if not brand_ranking:
            return "数据不足"

        # CR3
        cr3 = sum(b.get('share', 0) for b in brand_ranking[:3])
        # CR5
        cr5 = sum(b.get('share', 0) for b in brand_ranking[:5])

        return f"CR3={cr3:.1f}%, CR5={cr5:.1f}%"

    def _analyze_trend(self, trend: list) -> str:
        """分析趋势"""
        if len(trend) < 3:
            return "数据不足"

        # 计算最近3个月的平均增速
        growths = [t.get('yoy_growth', 0) for t in trend[-3:] if t.get('yoy_growth', 0) != 0]
        if not growths:
            return "增速平稳"

        avg_growth = sum(growths) / len(growths)

        if avg_growth > 10:
            return "快速增长"
        elif avg_growth > 0:
            return "温和增长"
        elif avg_growth > -10:
            return "增速放缓"
        else:
            return "明显下滑"

    def _format_top_players(self, brands: list) -> list:
        """格式化头部玩家"""
        return [
            {
                "rank": i + 1,
                "name": b.get('brand', 'N/A'),
                "share": b.get('share', 0),
                "sales": b.get('sales', 0)
            }
            for i, b in enumerate(brands)
        ]

    def _identify_opportunities(self, market_data: Dict) -> list:
        """识别市场机会"""
        opportunities = []
        brand_ranking = market_data.get("brand_ranking", [])
        segment_dist = market_data.get("segment_distribution", [])

        # 识别增速快的细分市场
        if segment_dist:
            top_seg = segment_dist[0]
            opportunities.append(Opportunity(
                item=f"{top_seg.get('segment', 'N/A')}细分市场增长强劲",
                scale=f"{top_seg.get('sales', 0):,}辆",
                confidence=0.75,
                evidence=["市场份额第一"]
            ))

        # 识别市场空白（尾部品牌机会）
        if len(brand_ranking) > 10:
            tail_share = sum(b.get('share', 0) for b in brand_ranking[10:])
            if tail_share > 30:
                opportunities.append(Opportunity(
                    item="尾部品牌仍有较大市场空间",
                    scale=f"占{ tail_share:.1f}%市场份额",
                    confidence=0.70,
                    evidence=["CR10 < 70%"]
                ))

        return opportunities

    def _identify_risks(self, market_data: Dict) -> list:
        """识别市场风险"""
        risks = []
        trend = market_data.get("sales_trend", [])

        # 检查销量下滑
        if len(trend) >= 2:
            recent_growth = trend[-1].get('yoy_growth', 0)
            if recent_growth < -10:
                risks.append(RiskWarning(
                    item="销量同比下滑",
                    probability="高",
                    impact="高",
                    mitigation="关注市场动态，调整策略"
                ))

        # 市场集中度风险
        brand_ranking = market_data.get("brand_ranking", [])
        if brand_ranking:
            cr3 = sum(b.get('share', 0) for b in brand_ranking[:3])
            if cr3 > 60:
                risks.append(RiskWarning(
                    item="头部集中度较高",
                    probability="中",
                    impact="中",
                    mitigation="差异化竞争"
                ))

        return risks

    def _calculate_confidence(self, market_data: Dict) -> float:
        """计算置信度"""
        confidence = 0.7

        # 数据量
        overview = market_data.get("market_overview", {})
        if overview.get('total_sales', 0) > 5000000:
            confidence += 0.1

        # 时间跨度
        trend = market_data.get("sales_trend", [])
        if len(trend) >= 12:
            confidence += 0.1
        elif len(trend) >= 6:
            confidence += 0.05

        # 数据完整性
        if market_data.get("brand_ranking") and len(market_data["brand_ranking"]) >= 10:
            confidence += 0.05

        return min(confidence, 0.95)

    def _generate_suggestions(self, market_data: Dict) -> list:
        """生成建议"""
        suggestions = []

        # 数据驱动建议
        suggestions.append("建议补充更多历史数据以提高分析准确性")
        suggestions.append("建议引入政策数据分析模块")

        return suggestions

    def _parse_llm_response(
        self,
        response: str,
        input: MarketInput
    ) -> MarketOutput:
        """解析LLM响应"""
        try:
            # 提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return MarketOutput(
                    success=True,
                    query=input.query,
                    analysis_type=input.analysis_type,
                    confidence=data.get("confidence", 0.8)
                )
        except json.JSONDecodeError:
            pass

        # 解析失败，返回基础分析
        return MarketOutput(
            success=True,
            query=input.query,
            analysis_type=input.analysis_type,
            confidence=0.6,
            error="LLM响应解析失败，使用基础分析"
        )

    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据总览"""
        return self.kb.get_data_summary()
