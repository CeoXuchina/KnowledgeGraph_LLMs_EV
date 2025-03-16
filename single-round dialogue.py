import re
from neo4j import GraphDatabase
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, create_react_agent
from langchain_openai import ChatOpenAI

# 配置Neo4j连接信息
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"  # Neo4j用户名
NEO4J_PASSWORD = "xuweiyuan"  # Neo4j密码

# 初始化Neo4j驱动
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# 定义查询Neo4j的函数
def query_knowledge_graph(query):
    with driver.session() as session:
        result = session.run(query)
        data = [record["m"] for record in result]
        print(f"Cypher Query: {query}")
        print(f"Query Result: {data}")
        return data

# 配置ChatOpenAI的基础信息
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key="sk-SfzXTk3x7Fumt6LV0u6Ps7lPvnoh9tSSVVHwUkewi7XkyEZM",
    openai_api_base="https://api.chatanywhere.tech/v1"
)

attribute_mapping = {
    "available since": "HAS_AVAILABLE_SINCE",
    "price": "HAS_PRICE",
    "battery": "HAS_BATTERY",
    "real range": "HAS_REAL_RANGE",
    "performance": "HAS_PERFORMANCE",
    "charging": "HAS_CHARGING",
    "bidirectional charging": "HAS_BIDIRECTIONAL_CHARGING",
    "energy consumption": "HAS_ENERGY_CONSUMPTION",
    "real energy consumption": "HAS_REAL_ENERGY_CONSUMPTION",
    "dimensions and weight": "HAS_DIMENSIONS_AND_WEIGHT",
    "url": "HAS_URL",
}

# 问题解析函数
def parse_question(question):
    # 提取属性
    attribute_match = re.search(r"(?:What|When) is the ([\w\s]+) of the", question, re.IGNORECASE)
    # 提取实体
    entity_match = re.search(r"of the ([\w\s]+)\??", question, re.IGNORECASE)

    attribute = attribute_match.group(1).strip().lower() if attribute_match else None
    entity = entity_match.group(1).strip() if entity_match else None

    # 映射属性到关系类型
    relationship = attribute_mapping.get(attribute)

    print(f"Extracted Attribute (lowercased): {attribute}")
    print(f"Parsed Entity: {entity}, Parsed Relationship: {relationship}")
    return entity, relationship

# LangChain工具：知识图谱查询工具
def knowledge_graph_tool(input_text):
    entity, relationship = parse_question(input_text)
    if not entity or not relationship:
        print("Failed to parse question or map to a valid relationship.")
        return []

    query = f"MATCH (n {{name: '{entity}'}})-[r:{relationship}]->(m) RETURN m"
    result = query_knowledge_graph(query)

    if result:
        # 提取节点中特定的字段，例如 `range`, `details`, 或其他自定义属性
        extracted_results = [
            node.get("range", node.get("details", node.get("value", str(node))))
            for node in result
        ]
        print(f"Extracted Results: {extracted_results}")
        return extracted_results
    else:
        return []



# 创建LangChain工具对象，用于知识图谱查询
knowledge_graph_tool_obj = Tool(
    name="KnowledgeGraphTool",
    func=knowledge_graph_tool,
    description="Query the knowledge graph to get relevant information"
)

# 创建Prompt模板，提醒AI只能基于知识图谱内容回答
react_agent_prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad", "tool_names", "tools"],
    template=(
        "You are an assistant that uses only the provided tools to answer questions based solely on the knowledge graph data.\n"
        "When using a tool, strictly follow this format:\n"
        "Action: <tool_name>\n"
        "Action Input: \"<entity> <attribute>\"\n\n"
        "Available tools:\n{tool_names}\n\n"
        "{tools}\n"
        "Question: {input}\n\n"
        "{agent_scratchpad}\n"
        "Now respond:"
    )
)


# 初始化Agent，包含知识图谱查询工具
agent = create_react_agent(
    tools=[knowledge_graph_tool_obj],
    llm=llm,
    prompt=react_agent_prompt,
)

# 定义问答函数
def answer_question(question):
    # 使用知识图谱工具查询相关内容
    try:
        context = knowledge_graph_tool(question)

        # 如果知识图谱中有结果，提取并打印答案
        if context:
            # 提取纯文本答案
            pure_answer = "\n".join(context)  # 拼接答案为单一输出
            # print(f"Answer: {pure_answer}")  # 打印问题的最终答案
        else:
            pure_answer = "No relevant information in knowledge graph"
            print(pure_answer)
    except Exception as e:
        pure_answer = "An error occurred during the query."
        print(f"Error in answer_question: {e}")

    return pure_answer


# 测试问答系统
question = "What is the Price of the BYD ATTO 3?"
pure_answer = answer_question(question)
print(f"Answer is: {pure_answer}")