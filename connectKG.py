import re
from neo4j import GraphDatabase
import openai
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, create_react_agent
from langchain_openai import ChatOpenAI
import asyncio
# from openai import OpenAI
from openai import AsyncOpenAI

# Configure Neo4j connection
# Use for Neo4J desktop
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"  # Neo4j username
NEO4J_PASSWORD = "xuweiyuan"  # Neo4j password

#Use for Neo4J Aura
#NEO4J_URI = "neo4j+s://1b1bfaa0.databases.neo4j.io"
#NEO4J_USER = "neo4j"
#NEO4J_PASSWORD = "x2EMv0LaSyYXkXvLn53R99mAq-L6CkEOcuNRBSJXxEQ"
# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# Define function to query Neo4j
def query_knowledge_graph(query):
    try:
        with driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]
            print(f"Query executed. Results: {data}")
            return data
    except Exception as e:
        print(f"Error executing query: {e}")
        return []

# Configure ChatOpenAI
# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     openai_api_key="sk-SfzXTk3x7Fumt6LV0u6Ps7lPvnoh9tSSVVHwUkewi7XkyEZM",
#     openai_api_base="https://api.chatanywhere.tech/v1"
# )

client = AsyncOpenAI(
    api_key="sk-SfzXTk3x7Fumt6LV0u6Ps7lPvnoh9tSSVVHwUkewi7XkyEZM",
    base_url="https://api.chatanywhere.tech/v1"
)

# client = OpenAI(
#     api_key= "sk-SfzXTk3x7Fumt6LV0u6Ps7lPvnoh9tSSVVHwUkewi7XkyEZM",
#     base_url= "https://api.chatanywhere.tech/v1"
# )

cypher_queries = {
    "available_since": "MATCH (m:Model {name: '{entity}'})-[:HAS_AVAILABLE_SINCE]->(info) RETURN info.details AS Details",
    "available_to_order": "MATCH (m:Model {name: '{entity}'})-[:HAS_AVAILABLE_TO_ORDER]->(info) RETURN info.details AS Details",
    "price": "MATCH (m:Model {name: '{entity}'})-[:HAS_PRICE]->(info) RETURN info.details AS Details",
    "battery": "MATCH (m:Model {name: '{entity}'})-[:HAS_BATTERY]->(info) RETURN info.details AS Details",
    "real_range": "MATCH (m:Model {name: '{entity}'})-[:HAS_REAL_RANGE]->(info) RETURN info.details AS Details",
    "performance": "MATCH (m:Model {name: '{entity}'})-[:HAS_PERFORMANCE]->(info) RETURN info.details AS Details",
    "charging": "MATCH (m:Model {name: '{entity}'})-[:HAS_CHARGING]->(info) RETURN info.details AS Details",
    "bidirectional_charging": "MATCH (m:Model {name: '{entity}'})-[:HAS_BIDIRECTIONAL_CHARGING]->(info) RETURN info.details AS Details",
    "energy_consumption": "MATCH (m:Model {name: '{entity}'})-[:HAS_ENERGY_CONSUMPTION]->(info) RETURN info.details AS Details",
    "real_energy_consumption": "MATCH (m:Model {name: '{entity}'})-[:HAS_REAL_ENERGY_CONSUMPTION]->(info) RETURN info.details AS Details",
    "dimensions_and_weight": "MATCH (m:Model {name: '{entity}'})-[:HAS_DIMENSIONS_AND_WEIGHT]->(info) RETURN info.details AS Details",
    "url": "MATCH (m:Model {name: '{entity}'})-[:HAS_URL]->(info) RETURN info.details AS Details"
}


attribute_mapping = {
    "available since": "HAS_AVAILABLE_SINCE",
    "available to order": "HAS_AVAILABLE_TO_ORDER",
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


# Function to parse questions
async def parse_question(question, session):
    attribute_match = re.search(r"(?:What|When|Tell me about|Give me|How much is|Show me|Is|When will) (the )?([\w\s]+?) (?:of|for|about|to|be|can) ([\w\s]+)\??", question, re.IGNORECASE)

    attribute = attribute_match.group(2).strip().lower() if attribute_match else None
    entity = attribute_match.group(3).strip() if attribute_match else None

    # Handle references like 'this car'
    if entity and entity.lower() in ["this car", "this vehicle"]:
        entity = session.last_entity

    # Normalize entity name (e.g., proper casing, remove leading 'the')
    if entity:
        entity = entity.lower().replace("the ", "").strip()
        entity = " ".join(word.capitalize() for word in entity.split())

    # Explicit handling for phrases like 'available to order'
    if attribute in ["is this car available", "availability status", "available to order", "can available", "available"]:
        attribute = "available to order"

    # Use LLM to better understand ambiguous attributes if not mapped explicitly
    if attribute and attribute not in attribute_mapping:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that helps map ambiguous phrases to known attributes for electric vehicle data."},
                {"role": "user", "content": f"What attribute best matches '{attribute}' for an electric vehicle? The options include availability, price, range, performance, charging, and more."}
            ],
            max_tokens=50,
            temperature=0.5,
        )
        attribute = response.choices[0].message.content.strip().lower()

    # Fuzzy matching to handle variations in attribute names
    relationship = None
    if attribute:
        for key in attribute_mapping:
            if key in attribute:
                relationship = attribute_mapping[key]
                break

    print(f"Extracted Attribute: {attribute}")
    print(f"Parsed Entity: {entity}, Mapped Relationship: {relationship}")

    # 返回实体名和关系类型
    return entity, relationship

# Function to format response
def format_response(attribute, raw_data):
    if attribute == "price":
        lines = raw_data.split("\n")
        price_info = {}
        for line in lines:
            if "\t" in line:  # 检查是否为有效的价格行
                country, price = line.split("\t", 1)
                price_info[country.strip()] = price.strip()
        response = "Here is the pricing information:\n"
        for country, price in price_info.items():
            response += f"- {country}: {price}\n"
        return response
    else:
        lines = raw_data.split("\n")
        formatted = "\n".join([f"- {line.strip()}" for line in lines if line.strip()])
        return f"The following information was retrieved:\n{formatted}"


# LangChain tool: Knowledge graph query tool
async def knowledge_graph_tool(input_text, session):
    entity, relationship = await parse_question(input_text, session)
    if not entity or not relationship:
        print("Failed to parse question or map to a valid relationship.")
        return "I couldn't understand your question."

    # 根据属性生成查询
    query = f"""
    MATCH (m:Model {{name: '{entity}'}})-[:{relationship}]->(r)
    RETURN r.details AS Details
    """

    print(f"Generated Cypher Query: {query}")

    # 执行查询
    result = query_knowledge_graph(query)

    if not result:
        print("No data found for the given query.")
        return "I couldn't find any relevant information in the knowledge graph."

    # 提取返回值
    extracted_results = [record.get("Details", "N/A") for record in result]
    if not extracted_results or all(res == "N/A" for res in extracted_results):
        return f"I couldn't find any information about the {relationship.split('_')[1].lower()} of {entity}."
    extracted_context = "\n".join(extracted_results)
    return format_response(relationship.split('_')[1].lower(), extracted_context)


# Create LangChain tool object for knowledge graph queries
knowledge_graph_tool_obj = Tool(
    name="KnowledgeGraphTool",
    func=lambda input_text: asyncio.run(knowledge_graph_tool(input_text, session=ChatSession())),
    description="Query the knowledge graph to get relevant information"
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key="sk-SfzXTk3x7Fumt6LV0u6Ps7lPvnoh9tSSVVHwUkewi7XkyEZM",
    openai_api_base="https://api.chatanywhere.tech/v1"
)

# Create Prompt template to instruct AI to answer based solely on knowledge graph content
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

# Initialize Agent with knowledge graph query tool
agent = create_react_agent(
    tools=[knowledge_graph_tool_obj],
    llm=llm,
    prompt=react_agent_prompt,
)


# Conversation context management
class ChatSession:
    def __init__(self):
        self.history = []
        self.last_entity = None  # 存储上一个提到的实体

    def add_message(self, user_message, bot_message, entity=None):
        self.history.append({"user": user_message, "bot": bot_message})
        if entity:
            self.last_entity = entity

    def get_context(self):
        return "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in self.history])


async def generate_response_with_openai(history, extracted_context):
    user_message = history[-1]['user'] if history else "The user asked a question."
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that answers questions using knowledge graph data."},
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": f"The knowledge graph returned the following information:\n{extracted_context}"},
        {"role": "user", "content": "Provide a detailed answer based on the above price information, specifying prices for different regions if available."}
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()



# Define function to answer questions
async def answer_question(question, session):
    try:
        entity, relationship = await parse_question(question, session)
        if not entity or not relationship:
            return "I couldn't understand your question."

        # 根据属性生成查询
        query = f"""
        MATCH (m:Model {{name: '{entity}'}})-[:{relationship}]->(r)
        RETURN r.details AS Details
        """

        print(f"Generated Cypher Query: {query}")

        # 执行查询
        query_results = query_knowledge_graph(query)

        if not query_results:
            print("Query returned no results.")
            bot_message = "I couldn't find any relevant information in the knowledge graph."
        else:
            # 提取对应关系的值
            extracted_results = [record.get("Details") for record in query_results if record.get("Details") is not None]
            if extracted_results:
                bot_message = format_response(relationship.split('_')[1].lower(), extracted_results[0])
            else:
                bot_message = "I couldn't find any relevant information."

        session.add_message(question, bot_message, entity=entity)

    except Exception as e:
        bot_message = f"An error occurred: {str(e)}"
        print(f"Error in answer_question: {e}")

    return bot_message



# Implement multi-turn conversation
async def start_conversation():
    session = ChatSession()

    print("Hello! Ask me anything about electric vehicles. Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        answer = await answer_question(user_input, session)
        print(f"Bot: {answer}")


# Start conversation
if __name__ == "__main__":
    asyncio.run(start_conversation())
