"""
增强版市场战略分析 Agent
集成了结构化查询 + RAG 语义检索 + LLM 生成
"""

import json
import re
from typing import Optional, Dict, Any, List
from pathlib import Path

from .schemas import (
    MarketInput,
    MarketOutput,
    MarketOverview,
    Competitor,
    Opportunity,
    RiskWarning,
    AnalysisType
)
from .knowledge_base import MarketKnowledgeBase


class HybridMarketAgent:
    """
    混合市场分析 Agent

    结合两种能力：
    1. 结构化查询 - PostgreSQL 销量/配置数据
    2. RAG 检索 - 向量数据库中的非结构化文档
    3. LLM 生成 - 综合分析输出（可选）
    """

    def __init__(self, llm_gateway=None):
        self.kb = MarketKnowledgeBase()
        self.llm = llm_gateway
        self._rag_available = False
        self._load_prompts()

        # 尝试初始化 RAG
        self._init_rag()

    def _load_prompts(self):
        """加载 Prompt 模板"""
        prompts_dir = Path(__file__).parent / "prompts"

        system_prompt_path = prompts_dir / "system.txt"
        if system_prompt_path.exists():
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = ""

        user_prompt_path = prompts_dir / "user.txt"
        if user_prompt_path.exists():
            with open(user_prompt_path, "r", encoding="utf-8") as f:
                self.user_prompt_template = f.read()
        else:
            self.user_prompt_template = ""

    def _init_rag(self):
        """初始化 RAG 组件"""
        try:
            from retrieval.retriever import retrieve
            from rerank.rerank_service import rerank
            self._retrieve = retrieve
            self._rerank = rerank
            self._rag_available = True
        except Exception as e:
            print(f"Warning: RAG 组件初始化失败: {e}")
            self._rag_available = False

    def analyze(self, input: MarketInput) -> MarketOutput:
        """
        执行混合市场分析

        流程：
        1. 结构化查询 - 获取销量/品牌数据
        2. RAG 检索 - 获取相关文档上下文
        3. 综合分析 - 输出洞察
        """
        try:
            # 1. 获取结构化数据
            market_data = self._retrieve_market_data(input)

            # 2. 获取 RAG 上下文（如果可用）
            rag_context = []
            if self._rag_available and input.query:
                rag_context = self._retrieve_rag_context(input.query)

            # 3. 综合分析
            if self.llm and rag_context:
                # LLM + RAG 模式
                output = self._llm_analysis(input, market_data, rag_context)
            else:
                # 结构化分析模式
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
        """检索市场结构化数据"""
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

    def _retrieve_rag_context(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """检索 RAG 上下文"""
        try:
            if not self._rag_available:
                return []

            # 向量检索
            docs = self._retrieve(query=query, top_k=top_k * 3)

            if not docs:
                return []

            # 重排序
            if len(docs) > top_k:
                reranked = self._rerank(
                    query=query,
                    documents=[
                        {"content": d["document"], "metadata": d.get("metadata", {})}
                        for d in docs
                    ],
                    top_k=top_k
                )
                return reranked
            else:
                return [
                    {
                        "content": d["document"],
                        "metadata": d.get("metadata", {}),
                        "score": d.get("score", 0)
                    }
                    for d in docs
                ]

        except Exception as e:
            print(f"RAG 检索失败: {e}")
            return []

    def _format_market_data(self, data: Dict) -> str:
        """格式化市场数据"""
        lines = []

        if "market_overview" in data:
            overview = data["market_overview"]
            lines.append("=== 市场概况 ===")
            lines.append(f"总销量: {overview.get('total_sales', 0):,}辆")
            lines.append(f"月均销量: {overview.get('avg_monthly_sales', 0):,.0f}辆")
            lines.append("")

        if "brand_ranking" in data and data["brand_ranking"]:
            lines.append("=== 品牌排名 (Top 10) ===")
            for i, brand in enumerate(data["brand_ranking"][:10], 1):
                lines.append(
                    f"{i}. {brand.get('brand', 'N/A')} - "
                    f"销量: {brand.get('sales', 0):,}辆, "
                    f"份额: {brand.get('share', 0):.1f}%"
                )
            lines.append("")

        return "\n".join(lines)

    def _format_rag_context(self, context: List[Dict]) -> str:
        """格式化 RAG 上下文"""
        if not context:
            return "（无相关文档）"

        lines = ["=== 参考文档 ==="]
        for i, doc in enumerate(context, 1):
            content = doc.get('content', '')[:500]  # 限制长度
            metadata = doc.get('metadata', {})
            source = metadata.get('source', '未知来源')
            lines.append(f"[{i}] 来源: {source}")
            lines.append(f"内容: {content}...")
            lines.append("")

        return "\n".join(lines)

    def _llm_analysis(
        self,
        input: MarketInput,
        market_data: Dict,
        rag_context: List[Dict]
    ) -> MarketOutput:
        """LLM + RAG 分析模式"""
        # 构建完整上下文
        structured_text = self._format_market_data(market_data)
        rag_text = self._format_rag_context(rag_context)

        prompt = f"""
## 用户查询
{input.query}

## 结构化数据
{structured_text}

## 参考文档
{rag_text}

## 分析要求
请基于以上数据进行分析，输出：
1. 市场洞察
2. 竞品分析
3. 机会与风险
4. 置信度评估
"""

        # 调用 LLM
        try:
            response = self.llm.generate(self.system_prompt, prompt)
            # 解析响应（简化处理）
            return MarketOutput(
                success=True,
                query=input.query,
                analysis_type=input.analysis_type,
                confidence=0.85,
                suggestions=["请查看 LLM 生成的分析报告"]
            )
        except Exception as e:
            # LLM 失败，降级到结构化分析
            return self._structured_analysis(input, market_data)

    def _structured_analysis(
        self,
        input: MarketInput,
        market_data: Dict
    ) -> MarketOutput:
        """结构化分析模式（无 LLM）"""
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
            suggestions=self._generate_suggestions(market_data)
        )

    def _calculate_growth_rate(self, trend: list) -> str:
        if len(trend) < 2:
            return "数据不足"
        recent = trend[-1].get('sales', 0)
        previous = trend[-2].get('sales', 0)
        if previous == 0:
            return "数据不足"
        growth = (recent - previous) / previous * 100
        return f"{growth:+.1f}%"

    def _calculate_concentration(self, brand_ranking: list) -> str:
        if not brand_ranking:
            return "数据不足"
        cr3 = sum(b.get('share', 0) for b in brand_ranking[:3])
        cr5 = sum(b.get('share', 0) for b in brand_ranking[:5])
        return f"CR3={cr3:.1f}%, CR5={cr5:.1f}%"

    def _analyze_trend(self, trend: list) -> str:
        if len(trend) < 3:
            return "数据不足"
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
        return [
            {"rank": i + 1, "name": b.get('brand', 'N/A'), "share": b.get('share', 0)}
            for i, b in enumerate(brands)
        ]

    def _identify_opportunities(self, market_data: Dict) -> list:
        opportunities = []
        segment_dist = market_data.get("segment_distribution", [])

        if segment_dist:
            top_seg = segment_dist[0]
            opportunities.append(Opportunity(
                item=f"{top_seg.get('segment', 'N/A')}细分市场增长强劲",
                scale=f"{top_seg.get('sales', 0):,}辆",
                confidence=0.75,
                evidence=["市场份额第一"]
            ))

        return opportunities

    def _identify_risks(self, market_data: Dict) -> list:
        risks = []
        trend = market_data.get("sales_trend", [])

        if len(trend) >= 2:
            recent_growth = trend[-1].get('yoy_growth', 0)
            if recent_growth < -10:
                risks.append(RiskWarning(
                    item="销量同比下滑",
                    probability="高",
                    impact="高",
                    mitigation="关注市场动态"
                ))

        return risks

    def _calculate_confidence(self, market_data: Dict) -> float:
        confidence = 0.7
        overview = market_data.get("market_overview", {})
        if overview.get('total_sales', 0) > 5000000:
            confidence += 0.1
        trend = market_data.get("sales_trend", [])
        if len(trend) >= 12:
            confidence += 0.1
        elif len(trend) >= 6:
            confidence += 0.05
        return min(confidence, 0.95)

    def _generate_suggestions(self, market_data: Dict) -> list:
        suggestions = []
        suggestions.append("建议补充更多历史数据以提高分析准确性")
        if self._rag_available:
            suggestions.append("可使用 RAG 检索获取更多上下文信息")
        return suggestions

    def rag_retrieve(self, query: str, top_k: int = 5, metadata_filter: dict = None) -> Dict:
        """
        直接调用 RAG 检索

        Args:
            query: 检索查询
            top_k: 返回数量
            metadata_filter: 元数据过滤

        Returns:
            检索结果
        """
        if not self._rag_available:
            return {
                "success": False,
                "error": "RAG 组件未初始化",
                "results": []
            }

        try:
            docs = self._retrieve(query=query, top_k=top_k * 3, metadata_filter=metadata_filter)

            if not docs:
                return {"success": True, "query": query, "results": [], "message": "未找到相关文档"}

            # 重排序
            if len(docs) > top_k:
                reranked = self._rerank(
                    query=query,
                    documents=[{"content": d["document"], "metadata": d.get("metadata", {})} for d in docs],
                    top_k=top_k
                )
                results = reranked
            else:
                results = [
                    {"content": d["document"], "score": d.get("score", 0), "metadata": d.get("metadata", {})}
                    for d in docs
                ]

            return {
                "success": True,
                "query": query,
                "results": results,
                "total_found": len(docs),
                "returned": len(results)
            }

        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据总览"""
        return self.kb.get_data_summary()
