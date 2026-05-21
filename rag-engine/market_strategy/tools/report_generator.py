"""
市场分析报告生成工具
命令行接口：python report_generator.py --title "比亚迪市场策略分析" --analysis_type full --output report.md
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_strategy.agent import MarketStrategyAgent
from market_strategy.schemas import MarketInput, AnalysisType
from market_strategy.knowledge_base import MarketKnowledgeBase


def generate_market_report(title: str, time_range: str = "最近12个月",
                          tech_type: str = None, segment: str = None) -> str:
    """生成完整市场分析报告"""
    agent = MarketStrategyAgent()
    kb = agent.kb

    try:
        # 获取数据
        overview = kb.get_market_overview(time_range=time_range, tech_type=tech_type, segment=segment)
        brand_ranking = kb.get_sales_by_brand(time_range=time_range, top_n=10, tech_type=tech_type)
        segment_dist = kb.get_segment_distribution(time_range=time_range)
        trend = kb.get_sales_trend(tech_type=tech_type, segment=segment)

        # 计算集中度
        cr3 = sum(b.get('share', 0) for b in brand_ranking[:3])
        cr5 = sum(b.get('share', 0) for b in brand_ranking[:5])

        # 计算趋势
        recent_growth = trend[-1].get('yoy_growth', 0) if trend else 0

        report = f"""# {title}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**分析周期**: {overview.get('data_period', 'N/A')}

---

## 一、市场概况

### 1.1 规模指标

| 指标 | 数值 |
|------|------|
| 总销量 | {overview.get('total_sales', 0):,} 辆 |
| 月均销量 | {overview.get('avg_monthly_sales', 0):,.0f} 辆 |
| 品牌数 | {overview.get('brand_count', 0)} |
| 车型数 | {overview.get('model_count', 0)} |

### 1.2 市场集中度

| 指标 | 数值 |
|------|------|
| CR3 (Top 3) | {cr3:.1f}% |
| CR5 (Top 5) | {cr5:.1f}% |

---

## 二、竞争格局

### 2.1 品牌排名 (Top 10)

| 排名 | 品牌 | 销量 | 份额 |
|------|------|------|------|
"""
        for i, brand in enumerate(brand_ranking[:10], 1):
            report += f"| {i} | {brand.get('brand', 'N/A')} | {brand.get('sales', 0):,} | {brand.get('share', 0):.1f}% |\n"

        report += f"""
### 2.2 细分市场分布

| 细分市场 | 销量 | 份额 |
|----------|------|------|
"""
        for seg in segment_dist:
            report += f"| {seg.get('segment', 'N/A')} | {seg.get('sales', 0):,} | {seg.get('share', 0):.1f}% |\n"

        report += f"""
---

## 三、市场趋势

### 3.1 销量趋势 (最近6个月)

| 月份 | 销量 | 同比增速 |
|------|------|----------|
"""
        for month_data in trend[-6:]:
            report += f"| {month_data.get('month', 'N/A')} | {month_data.get('sales', 0):,} | {month_data.get('yoy_growth', 0):+.1f}% |\n"

        report += f"""
### 3.2 趋势判断

- **近期增速**: {recent_growth:+.1f}%
- **市场判断**: {'增长态势' if recent_growth > 0 else '增长放缓' if recent_growth > -10 else '明显下滑'}

---

## 四、机会与风险

### 4.1 市场机会

"""
        # 识别机会
        if segment_dist:
            top_seg = segment_dist[0]
            report += f"- **{top_seg.get('segment', 'N/A')}细分市场** 份额最高({top_seg.get('share', 0):.1f}%)，增长强劲\n"

        if cr5 < 50:
            tail_share = 100 - cr5
            report += f"- **市场分散度较高**，尾部品牌占据 {tail_share:.1f}% 份额，存在进入空间\n"

        report += """
### 4.2 风险提示

"""
        # 识别风险
        if recent_growth < -10:
            report += f"- ⚠️ **销量下滑风险**: 同比下降 {abs(recent_growth):.1f}%，需关注\n"

        if cr3 > 50:
            report += f"- ⚠️ **头部集中风险**: CR3达 {cr3:.1f}%，新进入者面临较高壁垒\n"

        report += f"""
---

## 五、分析结论

基于以上数据分析，当前市场呈现以下特征：

1. **市场规模**: {overview.get('total_sales', 0):,} 辆，整体{'向好' if recent_growth > 0 else '承压'}
2. **竞争格局**: {'高度集中' if cr3 > 40 else '相对分散'}，CR3={cr3:.1f}%
3. **趋势判断**: {'快速增长' if recent_growth > 10 else '温和增长' if recent_growth > 0 else '增速放缓' if recent_growth > -10 else '明显下滑'}
4. **机会识别**: 建议关注 {segment_dist[0].get('segment', 'N/A') if segment_dist else '主流细分市场'} 细分市场

---

## 六、下一步建议

1. 持续监控头部品牌动态，特别是比亚迪、特斯拉等
2. 关注 {segment_dist[0].get('segment', 'N/A') if segment_dist else 'SUV'} 细分市场机会
3. 建立政策跟踪机制，预警政策变化风险
4. 建议补充用户洞察数据，验证市场机会

---

*本报告由市场战略分析师 Agent 自动生成*
*数据来源: vectordb.sales_import*
"""

        return report

    finally:
        kb.close()


def generate_pest_report(title: str) -> str:
    """生成PEST分析报告框架"""
    return f"""# {title}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**分析类型**: PEST 宏观环境分析

---

## 一、PEST分析框架

### P - 政治/政策环境 (Political)

| 因素 | 影响 | 置信度 |
|------|------|--------|
| 新能源购置税减免政策 | 利好 | 高 |
| 双积分政策走向 | 压力 | 高 |
| 地方补贴退坡节奏 | 影响分化 | 中 |
| 碳排放法规（国七） | 压力 | 中 |
| 进口关税调整 | 影响进口车 | 中 |

### E - 经济环境 (Economic)

| 因素 | 影响 | 置信度 |
|------|------|--------|
| GDP增速 | 正相关 | 高 |
| 贷款利率水平 | 负相关 | 高 |
| 居民可支配收入 | 正相关 | 高 |
| 原材料价格（锂、钴） | 成本影响 | 中 |
| 二手车市场成熟度 | 置换影响 | 中 |

### S - 社会文化环境 (Social)

| 因素 | 影响 | 置信度 |
|------|------|--------|
| 城镇化率提升 | 正相关 | 高 |
| 环保意识增强 | 正相关 | 高 |
| Z世代购车偏好 | 趋势变化 | 中 |
| 家庭结构小型化 | 影响车型选择 | 中 |
| 共享出行渗透率 | 替代效应 | 中 |

### T - 技术环境 (Technology)

| 因素 | 影响 | 置信度 |
|------|------|--------|
| 纯电/插混技术路线 | 主导方向 | 高 |
| 智能驾驶（L2/L3）普及 | 竞争力核心 | 高 |
| 800V高压平台渗透 | 加速 | 中 |
| 固态电池商业化 | 未来方向 | 低 |
| OTA升级能力 | 软实力 | 中 |

---

## 二、PEST综合评估

| 维度 | 整体影响 | 机会还是威胁 |
|------|----------|--------------|
| P | 短期利好，长期压力 | 把握窗口期 |
| E | 经济承压，消费谨慎 | 性价比优先 |
| S | 消费升级与分化并存 | 精准定位 |
| T | 技术驱动变革 | 加速创新 |

---

## 三、战略建议

基于PEST分析，建议：

1. **政策窗口期**: 把握当前补贴政策，持续加大新能源投入
2. **经济应对**: 优化成本结构，提升产品性价比
3. **社会洞察**: 关注Z世代和家庭结构变化，调整产品定位
4. **技术创新**: 加大智驾和电池技术投入，构建技术壁垒

---

*本报告由市场战略分析师 Agent 自动生成*
"""


def generate_swot_report(brand: str, market_data: dict = None) -> str:
    """生成SWOT分析报告"""
    report = f"""# {brand} SWOT分析

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**分析对象**: {brand}

---

## 二、SWOT分析矩阵

|  | **积极** | **消极** |
|--|---------|---------|
| **内部** | 优势 Strengths | 劣势 Weaknesses |
| **外部** | 机会 Opportunities | 威胁 Threats |

### S - 优势 (Strengths)

"""

    if market_data and 'brand_ranking' in market_data:
        # 根据市场排名填充优势
        report += f"- 市场份额领先: {brand} 在市场中占据重要地位\n"
        report += "- 产品线相对完整\n"
        report += "- 品牌认知度较高\n"
    else:
        report += "- 品牌知名度高\n"
        report += "- 技术积累深厚\n"
        report += "- 渠道网络覆盖广\n"
        report += "- 用户基盘大\n"

    report += """
### W - 劣势 (Weaknesses)

"""
    report += "- 智能化配置可能存在短板\n"
    report += "- 产品线可能过于单一\n"
    report += "- 二三线城市渗透可能不足\n"
    report += "- 服务体验可能存在差距\n"

    report += """
### O - 机会 (Opportunities)

"""
    report += "- 新能源市场增速超预期\n"
    report += "- 出口市场增长空间大\n"
    report += "- 下沉市场增量机会\n"
    report += "- 政策持续利好\n"

    report += """
### T - 威胁 (Threats)

"""
    report += "- 价格战持续加剧\n"
    report += "- 新势力品牌围攻\n"
    report += "- 原材料成本波动\n"
    report += "- 消费信心不足\n"

    report += f"""
---

## 三、SWOT策略建议

### SO 策略 (优势+机会)

- 利用品牌优势，抓住新能源增长红利
- 发挥渠道优势，拓展下沉市场

### WO 策略 (劣势+机会)

- 加大智能化投入，抓住技术升级机会
- 丰富产品线，把握细分市场机会

### ST 策略 (优势+威胁)

- 发挥成本优势应对价格战
- 强化品牌形象抵御新势力冲击

### WT 策略 (劣势+威胁)

- 收缩战线，聚焦核心市场
- 控制成本，提升运营效率

---

*本报告由市场战略分析师 Agent 自动生成*
"""
    return report


def main():
    parser = argparse.ArgumentParser(description='市场分析报告生成工具')
    parser.add_argument('--title', type=str, required=True,
                       help='报告标题')
    parser.add_argument('--analysis_type', type=str, default='full',
                       choices=['full', 'pest', 'swot', 'porter', 'marketing'],
                       help='分析类型')
    parser.add_argument('--brand', type=str, default=None,
                       help='分析品牌（SWOT/营销分析用）')
    parser.add_argument('--output', type=str, default=None,
                       help='输出文件路径')
    parser.add_argument('--time_range', type=str, default='最近12个月',
                       help='时间范围')
    parser.add_argument('--tech_type', type=str, default=None,
                       help='技术类型')

    args = parser.parse_args()

    try:
        if args.analysis_type == 'full':
            report = generate_market_report(
                title=args.title,
                time_range=args.time_range,
                tech_type=args.tech_type
            )
        elif args.analysis_type == 'pest':
            report = generate_pest_report(title=args.title)
        elif args.analysis_type == 'swot':
            report = generate_swot_report(brand=args.brand or "目标品牌")
        elif args.analysis_type == 'porter':
            report = f"""# {args.title}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**分析类型**: 波特五力分析

(待实现：需要结合市场数据)
"""
        elif args.analysis_type == 'marketing':
            report = f"""# {args.title}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**分析类型**: 4P营销组合分析

(待实现：需要结合市场数据)
"""
        else:
            report = "不支持的分析类型"

        # 输出
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')
            print(json.dumps({"success": True, "output": str(output_path.absolute())}, ensure_ascii=False, indent=2))
        else:
            print(report)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
