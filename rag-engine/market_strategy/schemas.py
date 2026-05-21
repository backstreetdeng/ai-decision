"""
Market Strategy Agent - 数据结构定义
定义市场分析相关的输入输出数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class AnalysisType(Enum):
    """分析类型枚举"""
    MARKET_OVERVIEW = "market_overview"           # 市场概况
    COMPETITOR_ANALYSIS = "competitor_analysis"   # 竞品分析
    POLICY_IMPACT = "policy_impact"               # 政策影响
    OPPORTUNITY_ANALYSIS = "opportunity_analysis" # 机会分析
    FULL_ANALYSIS = "full_analysis"             # 完整分析


@dataclass
class MarketInput:
    """市场分析输入结构"""
    query: str                                       # 用户查询
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文
    analysis_type: AnalysisType = AnalysisType.FULL_ANALYSIS  # 分析类型
    time_range: str = "最近12个月"                # 分析时间范围
    price_range: Optional[str] = None             # 价格带筛选
    power_type: Optional[str] = None              # 动力类型筛选
    segment: Optional[str] = None                  # 细分市场筛选


@dataclass
class MarketOverview:
    """市场概况结构"""
    scale: str                                      # 市场规模
    growth_rate: str                               # 增速
    market_share: Optional[str] = None            # 市场份额
    concentration: Optional[str] = None            # 集中度 (CR3/CR5)
    trend: str = ""                               # 趋势描述
    top_players: List[Dict[str, Any]] = field(default_factory=list)  # 头部玩家
    data_source: str = ""                         # 数据来源
    data_period: str = ""                         # 数据周期


@dataclass
class Competitor:
    """竞品结构"""
    name: str                                      # 竞品名称
    brand: str                                    # 品牌
    market_share: float                           # 市场份额 %
    sales_volume: Optional[int] = None           # 销量
    positioning: str = ""                         # 市场定位
    strengths: List[str] = field(default_factory=list)   # 优势
    weaknesses: List[str] = field(default_factory=list)  # 劣势
    key_models: List[str] = field(default_factory=list)  # 主销车型
    price_range: Optional[str] = None            # 价格区间
    target_segment: Optional[str] = None         # 目标细分市场


@dataclass
class Opportunity:
    """机会点结构"""
    item: str                                      # 机会描述
    scale: Optional[str] = None                   # 市场规模
    growth_rate: Optional[str] = None            # 增速
    confidence: float = 0.8                     # 置信度
    evidence: List[str] = field(default_factory=list)   # 支撑证据
    entry_barrier: Optional[str] = None        # 进入壁垒
    urgency: str = "中"                         # 紧迫性：高/中/低


@dataclass
class RiskWarning:
    """风险预警结构"""
    item: str                                      # 风险描述
    probability: str = "中"                       # 发生概率：高/中/低
    impact: str = "中"                           # 影响程度：高/中/低
    mitigation: Optional[str] = None            # 应对建议
    trend: Optional[str] = None                  # 趋势


@dataclass
class PolicyImpact:
    """政策影响结构"""
    policy_type: str                             # 政策类型
    policy_name: str                             # 政策名称
    effective_date: Optional[str] = None         # 生效日期
    expire_date: Optional[str] = None            # 失效日期
    favorable: List[str] = field(default_factory=list)   # 利好因素
    risks: List[str] = field(default_factory=list)       # 风险因素
    impact_segments: List[str] = field(default_factory=list)  # 影响细分市场
    subsidy_amount: Optional[str] = None        # 补贴金额
    impact_level: str = "中"                   # 影响程度：高/中/低


@dataclass
class PolicyDocument:
    """政策文件结构"""
    id: int
    policy_name: str                             # 政策名称
    policy_type: str                             # 政策类型
    effective_date: str                          # 生效日期
    expire_date: Optional[str] = None            # 失效日期
    content: str = ""                           # 政策内容
    summary: str = ""                           # 要点摘要
    impact_analysis: str = ""                   # 影响分析
    affected_segments: List[str] = field(default_factory=list)  # 影响细分市场


@dataclass
class MarketOutput:
    """市场分析输出结构"""
    success: bool
    query: str = ""                              # 原查询
    analysis_type: Optional[AnalysisType] = None
    market_overview: Optional[MarketOverview] = None
    competitors: List[Competitor] = field(default_factory=list)
    opportunities: List[Opportunity] = field(default_factory=list)
    risks: List[RiskWarning] = field(default_factory=list)
    policy_impact: List[PolicyImpact] = field(default_factory=list)
    confidence: float = 0.0
    confidence_factors: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)  # 建议

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": self.success,
            "query": self.query,
            "confidence": self.confidence
        }

        if self.market_overview:
            result["market_overview"] = {
                "scale": self.market_overview.scale,
                "growth_rate": self.market_overview.growth_rate,
                "market_share": self.market_overview.market_share,
                "concentration": self.market_overview.concentration,
                "trend": self.market_overview.trend,
                "top_players": self.market_overview.top_players
            }

        if self.competitors:
            result["competitors"] = [
                {
                    "name": c.name,
                    "brand": c.brand,
                    "market_share": c.market_share,
                    "positioning": c.positioning,
                    "strengths": c.strengths,
                    "weaknesses": c.weaknesses
                }
                for c in self.competitors
            ]

        if self.opportunities:
            result["opportunities"] = [
                {
                    "item": o.item,
                    "scale": o.scale,
                    "confidence": o.confidence,
                    "urgency": o.urgency
                }
                for o in self.opportunities
            ]

        if self.risks:
            result["risks"] = [
                {
                    "item": r.item,
                    "probability": r.probability,
                    "impact": r.impact
                }
                for r in self.risks
            ]

        if self.policy_impact:
            result["policy_impact"] = [
                {
                    "policy_type": p.policy_type,
                    "policy_name": p.policy_name,
                    "favorable": p.favorable,
                    "risks": p.risks
                }
                for p in self.policy_impact
            ]

        if self.suggestions:
            result["suggestions"] = self.suggestions

        return result


# ============ SQL查询结果结构 ============

@dataclass
class SalesData:
    """销量数据结构"""
    sales_date: int                              # 销售日期 YYYYMM
    product_model: str                           # 产品型号
    brand: str                                   # 品牌
    model_name: str                              # 车型名称
    tech_type: str                               # 技术类型
    segment: str                                  # 细分市场
    level: str                                   # 级别
    sales_volume: int                           # 销量


@dataclass
class ConfigData:
    """配置数据结构"""
    model_id: int                               # 款型ID
    model_name: str                              # 款型名称
    car_name: str                                # 车型名称
    energy_type: str                             # 能源类型
    level: str                                   # 级别
    motor_power: Optional[str] = None           # 电机总功率
    range_cltc: Optional[str] = None            # CLTC续航
    consumption: Optional[str] = None           # 百公里耗电量
    price: Optional[str] = None                 # 指导价
    manufacturer: Optional[str] = None          # 厂商
