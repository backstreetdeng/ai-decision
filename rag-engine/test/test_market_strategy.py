"""
Market Strategy Agent 测试脚本
测试市场战略分析师的功能
"""

import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_strategy import MarketStrategyAgent, MarketInput, AnalysisType


def test_data_summary():
    """测试数据总览"""
    print("=" * 70)
    print("测试1: 数据总览")
    print("=" * 70)

    agent = MarketStrategyAgent()
    summary = agent.get_data_summary()

    print("\n📊 数据统计:")
    for name, count in summary.get("tables", {}).items():
        print(f"   {name}: {count:,} 条")

    print(f"\n📅 销量数据时间范围:")
    date_range = summary.get("sales_date_range", {})
    print(f"   {date_range.get('start')} - {date_range.get('end')}")

    print(f"\n⚡ 技术类型分布:")
    for tech in summary.get("tech_types", []):
        print(f"   {tech.get('技术类型')}: {tech.get('cnt'):,} 辆")

    agent.kb.close()
    print("\n✅ 测试通过!")


def test_market_overview():
    """测试市场概况查询"""
    print("\n" + "=" * 70)
    print("测试2: 市场概况查询")
    print("=" * 70)

    agent = MarketStrategyAgent()
    kb = agent.kb

    # 获取市场概况
    overview = kb.get_market_overview()
    print("\n📊 市场概况:")
    print(f"   总销量: {overview.get('total_sales', 0):,} 辆")
    print(f"   月均销量: {overview.get('avg_monthly_sales', 0):,.0f} 辆")
    print(f"   品牌数: {overview.get('brand_count', 0)}")
    print(f"   车型数: {overview.get('model_count', 0)}")
    print(f"   数据周期: {overview.get('data_period')}")

    # 获取品牌排名
    brand_ranking = kb.get_sales_by_brand(top_n=10)
    print("\n🏢 品牌排名 (Top 10):")
    for i, brand in enumerate(brand_ranking, 1):
        brand_name = brand.get('brand') or 'N/A'
        sales = brand.get('sales') or 0
        share = brand.get('share') or 0
        print(f"   {i:2d}. {brand_name:<20} {sales:>10,} 辆  {share:>5.1f}%")

    # 获取细分市场
    segment_dist = kb.get_segment_distribution()
    print("\n📦 细分市场分布:")
    for seg in segment_dist:
        segment_name = seg.get('segment') or '未知'
        sales = seg.get('sales') or 0
        share = seg.get('share') or 0
        print(f"   {segment_name:<10} {sales:>10,} 辆  {share:>5.1f}%")

    # 获取销量趋势
    trend = kb.get_sales_trend()
    print("\n📈 销量趋势 (最近6个月):")
    for month_data in trend[-6:]:
        month = month_data.get('month') or 'N/A'
        sales = month_data.get('sales') or 0
        yoy = month_data.get('yoy_growth') or 0
        print(f"   {month}  {sales:>10,} 辆  同比: {yoy:>+6.1f}%")

    agent.kb.close()
    print("\n✅ 测试通过!")


def test_competitor_analysis():
    """测试竞品分析"""
    print("\n" + "=" * 70)
    print("测试3: 竞品分析")
    print("=" * 70)

    agent = MarketStrategyAgent()
    kb = agent.kb

    # 获取车型排名
    model_ranking = kb.get_sales_by_model(top_n=20)
    print("\n🚗 车型排名 (Top 20):")
    for i, model in enumerate(model_ranking, 1):
        model_name = model.get('model') or 'N/A'
        brand_name = model.get('brand') or 'N/A'
        sales = model.get('sales') or 0
        print(f"   {i:2d}. {model_name:<15} {brand_name:<20} {sales:>8,} 辆")

    # 竞品对比
    brands = ["比亚迪", "特斯拉", "吉利"]
    comparison = kb.compare_competitors(brands)
    print("\n🔍 竞品对比:")
    for brand in brands:
        info = comparison["brands"].get(brand, {})
        total_sales = info.get('total_sales') or 0
        model_count = info.get('model_count') or 0
        print(f"   {brand}: 销量 {total_sales:,} 辆, 车型数 {model_count}")

    # 获取配置数据
    configs = kb.get_competitor_configs(energy_type="纯电动", top_n=5)
    print("\n⚙️ 纯电动车型配置 (Top 5):")
    for cfg in configs:
        car_name = cfg.get('车型名称') or 'N/A'
        price = cfg.get('厂商指导价') or 'N/A'
        range_cltc = cfg.get('CLTC纯电续航里程') or 'N/A'
        power = cfg.get('电动机总功率') or 'N/A'
        print(f"   {car_name:<15} {price:>8} 续航: {range_cltc:>5}km 功率: {power:>5}kW")

    agent.kb.close()
    print("\n✅ 测试通过!")


def test_agent_analyze():
    """测试Agent分析功能"""
    print("\n" + "=" * 70)
    print("测试4: Agent分析功能")
    print("=" * 70)

    agent = MarketStrategyAgent()

    # 创建分析输入
    input_data = MarketInput(
        query="分析当前乘用车市场整体情况",
        analysis_type=AnalysisType.FULL_ANALYSIS,
        time_range="最近12个月"
    )

    # 执行分析
    print("\n🔄 正在分析...")
    output = agent.analyze(input_data)

    # 输出结果
    print("\n📋 分析结果:")
    print(f"   成功: {output.success}")
    print(f"   置信度: {output.confidence:.1%}")

    if output.market_overview:
        mo = output.market_overview
        print(f"\n📊 市场概况:")
        print(f"   规模: {mo.scale}")
        print(f"   增速: {mo.growth_rate}")
        print(f"   集中度: {mo.concentration}")
        print(f"   趋势: {mo.trend}")

    if output.competitors:
        print(f"\n🏢 头部竞品 (Top 5):")
        for i, comp in enumerate(output.competitors[:5], 1):
            share = comp.market_share if comp.market_share else 0
            print(f"   {i}. {comp.name} - 份额 {share:.1f}%")

    if output.opportunities:
        print(f"\n💡 识别到的机会:")
        for opp in output.opportunities:
            print(f"   - {opp.item} (置信度: {opp.confidence:.0%})")

    if output.risks:
        print(f"\n⚠️ 风险预警:")
        for risk in output.risks:
            print(f"   - {risk.item} (概率: {risk.probability}, 影响: {risk.impact})")

    if output.suggestions:
        print(f"\n💬 建议:")
        for suggestion in output.suggestions:
            print(f"   - {suggestion}")

    print("\n✅ 测试通过!")


def test_specific_query():
    """测试特定查询"""
    print("\n" + "=" * 70)
    print("测试5: 特定查询分析")
    print("=" * 70)

    agent = MarketStrategyAgent()

    queries = [
        ("30万纯电SUV市场机会分析", AnalysisType.OPPORTUNITY_ANALYSIS),
        ("比亚迪和特斯拉的竞争格局", AnalysisType.COMPETITOR_ANALYSIS),
        ("新能源政策对市场的影响", AnalysisType.POLICY_IMPACT),
    ]

    for query_text, analysis_type in queries:
        print(f"\n🔍 查询: {query_text}")

        input_data = MarketInput(
            query=query_text,
            analysis_type=analysis_type
        )

        output = agent.analyze(input_data)

        print(f"   成功: {output.success}, 置信度: {output.confidence:.1%}")

        if output.market_overview:
            mo = output.market_overview
            print(f"   市场规模: {mo.scale}, 增速: {mo.growth_rate}")

        if output.competitors:
            print(f"   竞品数: {len(output.competitors)}")

        if output.opportunities:
            print(f"   机会数: {len(output.opportunities)}")

    agent.kb.close()
    print("\n✅ 测试通过!")


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("🧪 Market Strategy Agent 功能测试")
    print("=" * 70)

    try:
        test_data_summary()
        test_market_overview()
        test_competitor_analysis()
        test_agent_analyze()
        test_specific_query()

        print("\n" + "=" * 70)
        print("✅ 所有测试通过!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
