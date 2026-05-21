"""
Market Strategy Agent - 知识库检索
负责从数据库检索市场数据、竞品信息、政策文件等
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from embedding import embedding_service

# 数据库配置
DB_CONFIG = {
    'host': '192.168.3.146',
    'port': 5432,
    'database': 'vectordb',
    'user': 'vectordb',
    'password': 'vectordb123'
}


class MarketKnowledgeBase:
    """市场分析知识库"""

    def __init__(self):
        self.embed_service = embedding_service
        self._conn = None

    def _get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(
            **DB_CONFIG,
            cursor_factory=RealDictCursor
        )

    @property
    def conn(self):
        """懒加载连接"""
        if self._conn is None or self._conn.closed:
            self._conn = self._get_connection()
        return self._conn

    def close(self):
        """关闭连接"""
        if self._conn and not self._conn.closed:
            self._conn.close()

    # ==================== 销量数据查询 ====================

    def get_market_overview(
        self,
        time_range: str = "最近12个月",
        tech_type: Optional[str] = None,
        segment: Optional[str] = None,
        level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取市场概况

        Returns:
            {
                "total_sales": int,
                "avg_monthly_sales": float,
                "brand_count": int,
                "model_count": int,
                "monthly_data": [...]
            }
        """
        conn = self.conn
        cur = conn.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if tech_type:
            conditions.append("\"技术类型\" = %s")
            params.append(tech_type)

        if segment:
            conditions.append("\"乘用车细分\" = %s")
            params.append(segment)

        if level:
            conditions.append("\"车型级别\" = %s")
            params.append(level)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 获取最新月份
        cur.execute("SELECT MAX(\"销售日期\") as max_date FROM sales_import")
        max_date = cur.fetchone()['max_date']

        # 计算时间范围（默认最近12个月）
        if time_range == "最近12个月":
            year = int(str(max_date)[:4])
            month = int(str(max_date)[4:])
            cur.execute("""
                SELECT MIN(\"销售日期\") as min_date FROM sales_import
                WHERE "销售日期" > %s OR "销售日期" = %s
            """, (str(year - 1) + str(month).zfill(2), max_date))
            min_date = cur.fetchone()['min_date']
        else:
            min_date = str(202501)  # 默认从2025年1月开始

        where_clause += f' AND "销售日期" >= {min_date} AND "销售日期" <= {max_date}'

        # 总销量 - 分步查询
        cur.execute(f"""
            SELECT
                SUM("销量") as total_sales,
                COUNT(DISTINCT "企业名称") as brand_count,
                COUNT(DISTINCT "通用名称") as model_count
            FROM sales_import
            WHERE {where_clause}
        """, params if params else None)

        result = cur.fetchone()

        # 月度数据用于计算平均
        cur.execute(f"""
            SELECT AVG(monthly) as avg_monthly
            FROM (
                SELECT SUM("销量") as monthly
                FROM sales_import
                WHERE {where_clause}
                GROUP BY "销售日期"
            ) m
        """, params if params else None)

        avg_result = cur.fetchone()
        avg_monthly = avg_result["avg_monthly"] if avg_result else 0

        # 月度数据
        cur.execute(f"""
            SELECT
                "销售日期",
                SUM("销量") as monthly_sales,
                COUNT(DISTINCT "通用名称") as model_count
            FROM sales_import
            WHERE {where_clause}
            GROUP BY "销售日期"
            ORDER BY "销售日期"
        """, params if params else None)

        monthly_data = [dict(row) for row in cur.fetchall()]

        cur.close()

        return {
            "total_sales": result['total_sales'] or 0,
            "avg_monthly_sales": avg_monthly or 0,
            "brand_count": result['brand_count'] or 0,
            "model_count": result['model_count'] or 0,
            "monthly_data": monthly_data,
            "data_period": f"{min_date} - {max_date}"
        }

    def get_sales_by_brand(
        self,
        time_range: str = "最近12个月",
        top_n: int = 20,
        tech_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        按品牌统计销量

        Returns:
            [{"brand": str, "sales": int, "share": float, "count": int}, ...]
        """
        conn = self.conn
        cur = conn.cursor()

        conditions = []
        params = []

        if tech_type:
            conditions.append("\"技术类型\" = %s")
            params.append(tech_type)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 获取最新月份
        cur.execute("SELECT MAX(\"销售日期\") as max_date FROM sales_import")
        max_date = cur.fetchone()['max_date']

        # 计算时间范围
        year = int(str(max_date)[:4])
        month = int(str(max_date)[4:])
        min_date = str(year - 1) + str(month).zfill(2)

        where_clause += f' AND "销售日期" >= {min_date} AND "销售日期" <= {max_date}'

        # 按品牌统计
        sql = f"""
            SELECT
                "企业名称" as brand,
                SUM("销量") as sales,
                COUNT(DISTINCT "通用名称") as model_count
            FROM sales_import
            WHERE {where_clause}
            GROUP BY "企业名称"
            ORDER BY sales DESC
            LIMIT %s
        """

        cur.execute(sql, params + [top_n])
        brand_data = [dict(row) for row in cur.fetchall()]

        # 计算总销量
        cur.execute(f"""
            SELECT SUM("销量") as total FROM sales_import
            WHERE {where_clause}
        """, params)
        total = cur.fetchone()['total']

        # 计算份额
        for item in brand_data:
            item['share'] = round(item['sales'] / total * 100, 2) if total else 0

        cur.close()
        return brand_data

    def get_sales_by_model(
        self,
        time_range: str = "最近12个月",
        top_n: int = 20,
        brand: Optional[str] = None,
        tech_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        按车型统计销量

        Returns:
            [{"model": str, "brand": str, "sales": int, "share": float}, ...]
        """
        conn = self.conn
        cur = conn.cursor()

        conditions = []
        params = []

        if brand:
            conditions.append("\"企业名称\" LIKE %s")
            params.append(f"%{brand}%")

        if tech_type:
            conditions.append("\"技术类型\" = %s")
            params.append(tech_type)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 获取最新月份
        cur.execute("SELECT MAX(\"销售日期\") as max_date FROM sales_import")
        max_date = cur.fetchone()['max_date']

        year = int(str(max_date)[:4])
        month = int(str(max_date)[4:])
        min_date = str(year - 1) + str(month).zfill(2)

        where_clause += f' AND "销售日期" >= {min_date} AND "销售日期" <= {max_date}'

        sql = f"""
            SELECT
                "通用名称" as model,
                "企业名称" as brand,
                SUM("销量") as sales
            FROM sales_import
            WHERE {where_clause}
            GROUP BY "通用名称", "企业名称"
            ORDER BY sales DESC
            LIMIT %s
        """

        cur.execute(sql, params + [top_n])
        model_data = [dict(row) for row in cur.fetchall()]

        cur.close()
        return model_data

    def get_sales_trend(
        self,
        tech_type: Optional[str] = None,
        segment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取销量趋势数据

        Returns:
            [{"month": str, "sales": int, "yoy_growth": float}, ...]
        """
        conn = self.conn
        cur = conn.cursor()

        conditions = []
        params = []

        if tech_type:
            conditions.append("\"技术类型\" = %s")
            params.append(tech_type)

        if segment:
            conditions.append("\"乘用车细分\" = %s")
            params.append(segment)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
            SELECT
                "销售日期",
                SUM("销量") as sales
            FROM sales_import
            WHERE {where_clause}
            GROUP BY "销售日期"
            ORDER BY "销售日期"
        """

        cur.execute(sql, params)
        monthly_data = [dict(row) for row in cur.fetchall()]

        # 计算同比
        result = []
        for i, item in enumerate(monthly_data):
            month = str(item['销售日期'])
            # 找到去年同期
            prev_year_month = str(int(month[:4]) - 1) + month[4:]
            prev_sales = 0
            for d in monthly_data:
                if str(d['销售日期']) == prev_year_month:
                    prev_sales = d['sales']
                    break

            yoy_growth = 0
            if prev_sales > 0:
                yoy_growth = round((item['sales'] - prev_sales) / prev_sales * 100, 2)

            result.append({
                "month": month,
                "sales": item['sales'],
                "yoy_growth": yoy_growth
            })

        cur.close()
        return result

    def get_segment_distribution(
        self,
        time_range: str = "最近12个月"
    ) -> List[Dict[str, Any]]:
        """
        获取细分市场分布

        Returns:
            [{"segment": str, "sales": int, "share": float}, ...]
        """
        conn = self.conn
        cur = conn.cursor()

        # 获取最新月份
        cur.execute("SELECT MAX(\"销售日期\") as max_date FROM sales_import")
        max_date = cur.fetchone()['max_date']

        year = int(str(max_date)[:4])
        month = int(str(max_date)[4:])
        min_date = str(year - 1) + str(month).zfill(2)

        sql = """
            SELECT
                "乘用车细分" as segment,
                SUM("销量") as sales
            FROM sales_import
            WHERE "销售日期" >= %s AND "销售日期" <= %s
            GROUP BY "乘用车细分"
            ORDER BY sales DESC
        """

        cur.execute(sql, (min_date, max_date))
        segment_data = [dict(row) for row in cur.fetchall()]

        # 计算总销量和份额
        total = sum(item['sales'] for item in segment_data)
        for item in segment_data:
            item['share'] = round(item['sales'] / total * 100, 2) if total else 0

        cur.close()
        return segment_data

    # ==================== 配置数据查询 ====================

    def get_competitor_configs(
        self,
        brand: Optional[str] = None,
        energy_type: Optional[str] = None,
        level: Optional[str] = None,
        top_n: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取竞品配置信息

        Returns:
            [{"model_name": str, "brand": str, "energy_type": str, ...}, ...]
        """
        conn = self.conn
        cur = conn.cursor()

        conditions = []
        params = []

        if brand:
            conditions.append("\"厂商\" LIKE %s")
            params.append(f"%{brand}%")

        if energy_type:
            conditions.append("\"能源类型\" = %s")
            params.append(energy_type)

        if level:
            conditions.append("\"级别\" = %s")
            params.append(level)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
            SELECT
                "车型名称",
                "款型名称",
                "厂商",
                "能源类型",
                "级别",
                "电动机总功率",
                "CLTC纯电续航里程",
                "百公里耗电量",
                "厂商指导价"
            FROM config_data
            WHERE {where_clause}
            LIMIT %s
        """

        cur.execute(sql, params + [top_n])
        config_data = [dict(row) for row in cur.fetchall()]

        cur.close()
        return config_data

    # ==================== 竞品对比查询 ====================

    def compare_competitors(
        self,
        brands: List[str]
    ) -> Dict[str, Any]:
        """
        竞品对比分析

        Args:
            brands: 品牌列表

        Returns:
            {
                "brands": {...},
                "sales_comparison": [...],
                "config_comparison": [...]
            }
        """
        conn = self.conn
        cur = conn.cursor()

        result = {
            "brands": {},
            "sales_comparison": [],
            "config_comparison": []
        }

        # 获取各品牌销量
        for brand in brands:
            cur.execute("""
                SELECT
                    COALESCE(SUM("销量"), 0) as total_sales,
                    COUNT(DISTINCT "通用名称") as model_count
                FROM sales_import
                WHERE "企业名称" LIKE %s
            """, (f"%{brand}%",))

            row = cur.fetchone()
            result["brands"][brand] = {
                "total_sales": row["total_sales"] if isinstance(row, dict) else row[0],
                "model_count": row["model_count"] if isinstance(row, dict) else row[1]
            }

        # 获取最新月份销量对比
        cur.execute("SELECT MAX(\"销售日期\") as max_date FROM sales_import")
        max_date = cur.fetchone()['max_date']

        year = int(str(max_date)[:4])
        month = int(str(max_date)[4:])
        min_date = str(year - 1) + str(month).zfill(2)

        for brand in brands:
            cur.execute("""
                SELECT COALESCE(SUM("销量"), 0) as sales
                FROM sales_import
                WHERE "企业名称" LIKE %s
                AND "销售日期" >= %s AND "销售日期" <= %s
            """, (f"%{brand}%", min_date, max_date))

            row = cur.fetchone()
            result["sales_comparison"].append({
                "brand": brand,
                "sales": row["sales"] if isinstance(row, dict) else row[0]
            })

        cur.close()
        return result

    # ==================== 汇总查询 ====================

    def search_market_data(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        综合检索市场数据

        Args:
            query: 查询文本
            top_k: 返回数量

        Returns:
            综合市场数据
        """
        # 获取市场概况
        overview = self.get_market_overview()

        # 获取品牌排名
        brand_ranking = self.get_sales_by_brand(top_n=10)

        # 获取细分市场分布
        segment_dist = self.get_segment_distribution()

        # 获取销量趋势
        trend = self.get_sales_trend()

        return {
            "market_overview": overview,
            "brand_ranking": brand_ranking,
            "segment_distribution": segment_dist,
            "sales_trend": trend
        }

    def get_data_summary(self) -> Dict[str, Any]:
        """
        获取数据总览

        Returns:
            数据统计信息
        """
        conn = self.conn
        cur = conn.cursor()

        # 各表数据量
        tables = [
            ("tech_data", "技术数据"),
            ("config_data", "配置数据"),
            ("sales_import", "销量数据")
        ]

        summary = {"tables": {}}

        for table, name in tables:
            cur.execute(f"SELECT COUNT(*) as cnt FROM {table}")
            cnt = cur.fetchone()['cnt']
            summary["tables"][name] = cnt

        # 销量数据时间范围
        cur.execute("""
            SELECT MIN("销售日期") as min_date, MAX("销售日期") as max_date
            FROM sales_import
        """)
        date_range = cur.fetchone()
        summary["sales_date_range"] = {
            "start": str(date_range['min_date']),
            "end": str(date_range['max_date'])
        }

        # 技术类型分布
        cur.execute("""
            SELECT "技术类型", COUNT(*) as cnt
            FROM sales_import
            GROUP BY "技术类型"
            ORDER BY cnt DESC
        """)
        summary["tech_types"] = [dict(row) for row in cur.fetchall()]

        cur.close()
        return summary


# 便捷函数
def get_market_kb() -> MarketKnowledgeBase:
    """获取市场知识库实例"""
    return MarketKnowledgeBase()
