"""
双核心智能体调用示例
演示如何使用 market_strategy_agent 和 user_insight_agent 进行协同分析
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class AgentType(Enum):
    """智能体类型枚举"""
    MARKET_STRATEGY = "market_strategy_agent"
    USER_INSIGHT = "user_insight_agent"


@dataclass
class AgentOutput:
    """智能体输出结构"""
    agent_type: AgentType
    success: bool
    data: Dict[str, Any]
    confidence: float
    error: Optional[str] = None


class AgentInvoker:
    """智能体调用器"""

    def __init__(self, llm_gateway, knowledge_base):
        self.llm = llm_gateway
        self.kb = knowledge_base

    def invoke_agent(
        self,
        agent_type: AgentType,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """
        调用单个智能体

        Args:
            agent_type: 智能体类型
            query: 用户查询
            context: 上下文信息

        Returns:
            AgentOutput: 智能体输出
        """
        if agent_type == AgentType.MARKET_STRATEGY:
            return self._invoke_market_strategy_agent(query, context)
        elif agent_type == AgentType.USER_INSIGHT:
            return self._invoke_user_insight_agent(query, context)
        else:
            return AgentOutput(
                agent_type=agent_type,
                success=False,
                data={},
                confidence=0.0,
                error=f"Unknown agent type: {agent_type}"
            )

    def _load_agent_prompt(self, agent_type: AgentType) -> str:
        """加载智能体提示词"""
        agent_prompts = {
            AgentType.MARKET_STRATEGY: """
你是 **汽车市场战略分析师**，一位专精乘用车市场宏观分析、竞品格局研究和政策影响评估的战略研究专家。

## 你的核心使命
- 市场宏观分析：乘用车市场大盘数据分析、趋势识别
- 竞品格局研究：竞品定位、策略、优劣势分析
- 政策影响评估：购置税减免、新能源补贴、限牌限购政策解读
- 市场机会识别：战略机会点评估、风险预警

## 你必须遵守的关键规则
1. 数据优先：区分事实（数据）和推断（观点），明确标注
2. 战略视角：关注长期趋势而非短期波动
3. 客观中立：公正呈现市场格局，不偏袒任何品牌
4. 审慎评估：承认不确定性，给出置信度

## 约束边界
- ✅ 可以：分析市场规模、评估竞品格局、预警风险
- ❌ 不可以：输出具体定价建议、营销策略建议、投资回报率计算

## 输出格式
请以JSON格式输出分析结果，包含以下字段：
- market_overview: 市场概况
- competitive_landscape: 竞争格局
- policy_impact: 政策影响
- opportunities: 机会点列表
- risk_warnings: 风险提示列表
- confidence: 置信度评估
""",
            AgentType.USER_INSIGHT: """
你是 **用户需求洞察分析师**，一位专精用户画像构建、需求挖掘和配置偏好分析的用户研究专家。

## 你的核心使命
- 用户画像生成：基于多源数据构建目标用户画像
- 需求挖掘分析：从用户反馈提取关键需求，区分显性/隐性需求
- 配置偏好分析：分析用户对车型配置的关注度
- 购车决策研究：分析购车决策因子和权重

## 你必须遵守的关键规则
1. 用户中心：始终从用户视角看问题
2. 数据驱动：基于数据而非假设进行洞察
3. 需求分层：区分基础需求、期望需求、兴奋需求
4. 可落地：洞察要转化为可执行的建议

## 约束边界
- ✅ 可以：生成用户画像、分析配置偏好、识别痛点
- ❌ 不可以：直接输出产品定义（配置清单）、具体定价建议

## 输出格式
请以JSON格式输出分析结果，包含以下字段：
- user_persona: 用户画像
- configuration_priority: 配置优先级列表
- decision_factors: 决策因子
- pain_points: 痛点列表
- confidence: 置信度评估
"""
        }
        return agent_prompts.get(agent_type, "")

    def _invoke_market_strategy_agent(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """调用市场战略分析师"""
        try:
            # 1. 检索相关知识
            search_results = self.kb.search(query, top_k=10)

            # 2. 构建Prompt
            system_prompt = self._load_agent_prompt(AgentType.MARKET_STRATEGY)
            user_prompt = f"""
查询：{query}

上下文：{context or {}}

相关知识：
{search_results}

请基于以上信息进行市场分析。
"""
            # 3. 调用LLM
            response = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )

            # 4. 解析结果
            data = self._parse_json_response(response)

            return AgentOutput(
                agent_type=AgentType.MARKET_STRATEGY,
                success=True,
                data=data,
                confidence=data.get("confidence", 0.8)
            )

        except Exception as e:
            return AgentOutput(
                agent_type=AgentType.MARKET_STRATEGY,
                success=False,
                data={},
                confidence=0.0,
                error=str(e)
            )

    def _invoke_user_insight_agent(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """调用用户洞察分析师"""
        try:
            # 1. 检索相关知识
            search_results = self.kb.search(query, top_k=10)

            # 2. 构建Prompt
            system_prompt = self._load_agent_prompt(AgentType.USER_INSIGHT)
            user_prompt = f"""
查询：{query}

上下文：{context or {}}

相关知识：
{search_results}

请基于以上信息进行用户洞察分析。
"""
            # 3. 调用LLM
            response = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )

            # 4. 解析结果
            data = self._parse_json_response(response)

            return AgentOutput(
                agent_type=AgentType.USER_INSIGHT,
                success=True,
                data=data,
                confidence=data.get("confidence", 0.8)
            )

        except Exception as e:
            return AgentOutput(
                agent_type=AgentType.USER_INSIGHT,
                success=False,
                data={},
                confidence=0.0,
                error=str(e)
            )

    def invoke_dual_agents(
        self,
        query: str,
        market_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, AgentOutput]:
        """
        双智能体协同调用

        流程：
        1. market_strategy_agent 先执行（市场背景）
        2. user_insight_agent 后执行（用户画像）
        3. 汇总输出

        Args:
            query: 用户查询
            market_context: 市场分析上下文
            user_context: 用户洞察上下文

        Returns:
            Dict: {"market": 市场分析结果, "user": 用户洞察结果}
        """
        # 步骤1：市场战略分析（先执行）
        market_result = self.invoke_agent(
            AgentType.MARKET_STRATEGY,
            query,
            market_context
        )

        # 步骤2：用户洞察分析（后执行，使用市场分析结果作为背景）
        user_context = user_context or {}
        user_context["market_background"] = market_result.data if market_result.success else {}

        user_result = self.invoke_agent(
            AgentType.USER_INSIGHT,
            query,
            user_context
        )

        return {
            "market": market_result,
            "user": user_result
        }

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON响应"""
        import json
        import re

        # 尝试提取JSON块
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = response

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 返回原始文本
            return {"raw_response": response}


def example_usage():
    """使用示例"""

    # 模拟的LLM和知识库
    class MockLLM:
        def generate(self, system_prompt, user_prompt, temperature):
            return '{"market_overview": {"scale": "年销120万辆"}, "confidence": 0.85}'

    class MockKnowledgeBase:
        def search(self, query, top_k):
            return ["相关知识1", "相关知识2"]

    # 初始化
    invoker = AgentInvoker(MockLLM(), MockKnowledgeBase())

    # 单Agent调用
    print("=== 单Agent调用示例 ===")
    result = invoker.invoke_agent(
        AgentType.MARKET_STRATEGY,
        "30万插混SUV市场机会分析"
    )
    print(f"成功: {result.success}")
    print(f"数据: {result.data}")
    print(f"置信度: {result.confidence}")

    # 双Agent协同调用
    print("\n=== 双Agent协同调用示例 ===")
    dual_results = invoker.invoke_dual_agents(
        query="30万纯电SUV市场机会分析",
        market_context={"focus": "市场机会识别"},
        user_context={"focus": "用户画像生成"}
    )

    print(f"市场分析成功: {dual_results['market'].success}")
    print(f"用户洞察成功: {dual_results['user'].success}")


if __name__ == "__main__":
    example_usage()
