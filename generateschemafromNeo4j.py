import re
from neo4j import GraphDatabase
import openai
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, create_react_agent
from langchain_openai import ChatOpenAI
import asyncio
# from openai import OpenAI
from openai import AsyncOpenAI
import spacy
import asyncio


# 🟢 配置 OpenAI API
OPENAI_API_KEY = "sk-SfzXTk3x7Fumt6LV0u6Ps7lPvnoh9tSSVVHwUkewi7XkyEZM"

# 🟢 配置 Neo4j 数据库
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"  # Neo4j username
NEO4J_PASSWORD = "xuweiyuan"  # Neo4j password

# 连接 Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# 🟢 OpenAI LLM 初始化
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key="sk-SfzXTk3x7Fumt6LV0u6Ps7lPvnoh9tSSVVHwUkewi7XkyEZM",
    openai_api_base="https://api.chatanywhere.org"
)

# 🟢 1️⃣ 获取 Neo4j Schema
def get_neo4j_schema():
    """从 Neo4j 查询 Schema 结构"""
    schema_query = """
    CALL db.schema.visualization()
    """
    with driver.session() as session:
        result = session.run(schema_query)
        records = result.single()

        if not records:
            return "No schema found."

        nodes = records["nodes"]
        relationships = records["relationships"]

        # 解析节点
        node_labels = {}
        for node in nodes:
            label = list(node["labels"])[0]
            properties = node["properties"]
            node_labels[label] = properties

        # 解析关系
        relationship_types = {}
        for rel in relationships:
            rel_type = rel["type"]
            start_label = list(rel["start"]["labels"])[0]
            end_label = list(rel["end"]["labels"])[0]
            properties = rel["properties"]
            relationship_types[f"{start_label}-[:{rel_type}]->{end_label}"] = properties

        # 组合 Schema 结构
        schema_description = "Nodes:\n"
        for label, props in node_labels.items():
            schema_description += f"- (: {label} {{{', '.join(props.keys())}}})\n"

        schema_description += "\nRelationships:\n"
        for rel, props in relationship_types.items():
            schema_description += f"- {rel} {{{', '.join(props.keys())}}}\n"

        return schema_description

# 🟢 2️⃣ 让 OpenAI 解析 Schema 并生成更易读的版本
async def generate_schema_description():
    """调用 OpenAI API 让 GPT-4 解析 Schema"""
    raw_schema = get_neo4j_schema()

    print(f"🔵 原始 Schema:\n{raw_schema}")

    # 让 OpenAI 生成更易读的 Schema 说明
    response = await llm.apredict(
        f"""
        The following is the raw schema of a Neo4j database:

        {raw_schema}

        Please generate a well-structured summary of this schema that clearly explains:
        - What kind of entities (nodes) exist and their properties
        - What kind of relationships exist between nodes
        - The general structure of the graph database

        The output should be clear, structured, and easy to understand.
        """
    )

    print(f"🟢 GPT-4 生成的 Schema 说明:\n{response}")
    return response

# 🟢 运行测试
async def main():
    schema_description = await generate_schema_description()
    print("\n🟣 最终 Schema 说明:\n", schema_description)

# 运行
if __name__ == "__main__":
    asyncio.run(main())
