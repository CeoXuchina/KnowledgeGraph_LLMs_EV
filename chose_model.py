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

#NLP spacy model
nlp = spacy.load("en_core_web_sm")
#define Car model
car_models = ['Tesla Model 3', 'BYD ATTO 3', 'Kia EV3 Long Range', 'Tesla Model Y Long Range Dual Motor', 'Tesla Model 3 Long Range Dual Motor', 'Tesla Model 3 Long Range RWD', 'Tesla Model Y', 'BYD DOLPHIN 60.4 kWh', 'Hongqi E-HS9 99 kWh', 'MG MG4 Electric 64 kWh', 'BYD SEAL 82.5 kWh AWD Excellence', 'Renault 5 E-Tech 52kWh 150hp', 'Tesla Model Y Long Range RWD', 'Volkswagen ID.4 Pro', 'BMW iX xDrive40', 'Mercedes-Benz EQB 250+', 'Skoda Elroq 85', 'BYD HAN', 'Kia Niro EV', 'Tesla Model S Dual Motor', 'Tesla Model Y Performance', 'Hyundai Kona Electric 65 kWh', 'BYD TANG', 'Volvo EX30 Single Motor ER', 'Tesla Model S Plaid', 'BYD SEAL 82.5 kWh RWD Design', 'BMW iX1 xDrive30', 'Tesla Model 3 Performance', 'Fiat 500e Hatchback 42 kWh', 'Hyundai INSTER Long Range', 'Renault Scenic E-Tech EV87 220hp', 'Citroen e-C3', 'Kia EV3 Standard Range', 'Renault Megane E-Tech EV60 220hp', 'Mercedes-Benz EQS 450+', 'Skoda Enyaq 85', 'Hyundai INSTER Standard Range', 'Rolls-Royce Spectre', 'Kia EV6 Long Range 2WD', 'Volkswagen ID.7 Pro', 'MG Cyberster GT', 'Kia EV9 99.8 kWh AWD', 'BYD SEAL U 71.8 kWh Comfort', 'Hyundai IONIQ 5 84 kWh RWD', 'BMW iX xDrive50', 'Toyota bZ4X FWD', 'BMW i5 eDrive40 Sedan', 'Mercedes-Benz EQA 250', 'Zeekr 001 Long Range RWD', 'Peugeot e-3008 97 kWh Long Range', 'KGM Torres EVX', 'Audi Q8 e-tron 55 quattro', 'Audi A6 Sportback e-tron performance', 'BMW i4 eDrive40', 'Nissan Leaf', 'MG ZS EV Long Range', 'Honda e:Ny1', 'Audi Q6 e-tron quattro', 'Mini Countryman E', 'MG MG4 Electric 51 kWh', 'Ford Explorer Extended Range RWD', 'Nissan Ariya 87kWh', 'Porsche Macan 4 Electric', 'Mazda MX-30', 'Audi Q4 e-tron 45', 'Hyundai IONIQ 6 Long Range 2WD', 'Dacia Spring Electric 45', 'Leapmotor T03', 'Citroen e-C4', 'Peugeot e-3008 73 kWh', 'BMW i7 xDrive60', 'MG MG5 Electric Long Range', 'BMW iX1 eDrive20', 'Lynk&Co 02', 'Audi A6 Avant e-tron performance', 'Audi A6 Avant e-tron', 'Zeekr 001 Performance AWD', 'Volkswagen ID.3 Pro', 'Jeep Avenger Electric', 'Fiat Grande Panda', 'Audi A6 Sportback e-tron quattro', 'XPENG G6 RWD Long Range', 'Hyundai IONIQ 5 N', 'Kia EV6 GT', 'Hyundai IONIQ 5 63 kWh RWD', 'Peugeot e-5008 73 kWh', 'Lucid Air Grand Touring', 'Audi A6 Avant e-tron quattro', 'Volvo EX30 Twin Motor Performance', 'Volkswagen ID. Buzz NWB Pro', 'Volkswagen ID.7 Tourer Pro S', 'Peugeot e-5008 97 kWh Long Range', 'CUPRA Tavascan VZ', 'Opel Astra Electric', 'Volvo EX30 Single Motor', 'Mercedes-Benz G 580', 'Volkswagen ID.7 Pro S', 'Lexus RZ 450e', 'BYD SEAL U 87 kWh Design', 'Hyundai IONIQ 5 84 kWh AWD', 'Maxus MIFA 9', 'NIO ET5 Long Range', 'XPENG G6 RWD Standard Range', 'Smart #1 Pro+', 'Volkswagen ID.5 Pro', 'Mercedes-Benz EQE 350+', 'Hyundai IONIQ 6 Long Range AWD', 'Opel Mokka-e 50 kWh', 'NIO EL8 Long Range', 'Kia EV6 Long Range AWD', 'Polestar 2 Long Range Single Motor', 'CUPRA Born 170 kW - 59 kWh', 'Volkswagen ID.3 Pure', 'MG MG4 Electric 77 kWh', 'Tesla Model X Dual Motor', 'BMW i4 eDrive35', 'Peugeot e-208 50 kWh', 'Renault 5 E-Tech 40kWh 95hp', 'Porsche Taycan Plus', 'Smart #3 Brabus', 'Leapmotor C10', 'Tesla Model X Plaid', 'Mercedes-Benz EQA 250+', 'Subaru Solterra AWD', 'Volvo EX40 Single Motor ER', 'Mini Cooper SE', 'Hyundai IONIQ 6 Standard Range 2WD', 'BYD DOLPHIN 44.9 kWh Active', 'Toyota bZ4X AWD', 'CUPRA Born 170 kW - 77 kWh', 'Volkswagen ID.4 Pure', 'Volkswagen ID.7 Tourer Pro', 'Fiat 600e', 'BMW i5 M60 xDrive Sedan', 'Dacia Spring Electric 65', 'MG MG4 Electric XPOWER', 'Mercedes-Benz EQB 300 4MATIC', 'Ford Explorer Extended Range AWD', 'Dongfeng Box 42.3 kWh', 'Peugeot e-2008 54 kWh', 'Citroen e-C4 X 54 kWh', 'CUPRA Tavascan Endurance', 'XPENG G9 RWD Long Range', 'XPENG G9 RWD Standard Range', 'BMW i4 M50', 'Kia EV6 Standard Range 2WD', 'NIO ET7 Standard Range', 'BMW i5 eDrive40 Touring', 'Mercedes-Benz EQS SUV 580 4MATIC', 'Skoda Enyaq Coupe 85', 'Polestar 4 Long Range Single Motor', 'Lancia Ypsilon', 'Opel Corsa Electric 51 kWh', 'Porsche Macan Electric', 'Voyah Free 106 kWh', 'BMW iX2 xDrive30', 'Smart #1 Brabus', 'Volkswagen ID.3 Pro S', 'Zeekr X Privilege AWD', 'Mercedes-Benz EQB 350 4MATIC', 'Omoda E5', 'MG ZS EV Standard Range', 'Polestar 4 Long Range Dual Motor', 'Nissan Leaf e+', 'Skoda Elroq 50', 'Opel Frontera 44 kWh', 'Skoda Enyaq 85x', 'Porsche Macan Turbo Electric', 'Volvo EX40 Single Motor', 'Kia EV9 99.8 kWh RWD', 'BMW iX2 eDrive20', 'Audi Q6 e-tron performance', 'Nissan Ariya 63kWh', 'BMW i7 M70 xDrive', 'Ford Capri Extended Range AWD']


# Define function to query Neo4j
# def query_knowledge_graph(query):
#     try:
#         with driver.session() as session:
#             result = session.run(query)
#             data = [record.data() for record in result]
#             print(f"Query executed. Results: {data}")
#             return data
#     except Exception as e:
#         print(f"Error executing query: {e}")
#         return []

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
    doc = nlp(question)

    entity = None
    attribute = None

    # 提取实体（车型）
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "ORG"]:
            entity = ent.text

    for car in car_models:
        if car.lower() in question.lower():
            entity = car
            break

    if entity and entity.lower() in ["this car", "this vehicle"]:
        entity = session.get_last_entity()  # 使用上次查询的车型
        print(f"补全实体为: {entity}")
    # 解析问题中的属性
    attribute_candidates = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "ADJ"]]

    # 同义词映射
    synonyms = {
        "range": "real range",
        "battery life": "real range",
        "power": "performance",
        "speed": "performance",
        "cost": "price",
        "charging speed": "charging",
        "dimensions": "dimensions and weight"
    }

    for word in attribute_candidates:
        if word in synonyms:
            attribute = synonyms[word]
            break
        elif word in attribute_mapping:
            attribute = word
            break

    if entity and entity.lower() in ["this car", "this vehicle"]:
        entity = session.get_last_entity()

    # 若NLP未识别出属性，调用LLM进行智能推理
    if not attribute:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "你是一个帮助解析汽车数据查询的助手，请将用户问题映射到属性（如续航里程、电池容量、价格等）。"},
                {"role": "user", "content": f"问题：{question} 对应的汽车数据属性是什么？"}
            ],
            max_tokens=50,
            temperature=0.5,
        )
        attribute = response.choices[0].message.content.strip().lower()

    if entity:
        entity = entity.title()  # 确保格式化为标题格式
        session.last_entity = entity

    print(f"解析出的实体: {entity}, 解析出的属性: {attribute}")
    return entity, attribute_mapping.get(attribute, None)



def generate_cypher_query(entity, relationship):
    if not entity or not relationship:
        return None

    query = f"""
    MATCH (m:Model)
    WHERE toLower(m.name) CONTAINS toLower('{entity}')
    MATCH (m)-[:{relationship}]->(info)
    RETURN info.details AS Details
    """
    return query


def query_knowledge_graph(query):
    try:
        with driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]
            return data
    except Exception as e:
        print(f"Error executing query: {e}")
        return []

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



async def generate_response_with_openai(history, extracted_context):
    user_message = history[-1]['user'] if history else "The user asked a question."

    conversation = [
        {
            "role": "system",
            "content": "You are an expert on new energy vehicles, helping users answer questions about cars. Please keep the model name as it is and do not simplify it into other names."
        },
        {
            "role": "user",
            "content": user_message
        },
        {
            "role": "assistant",
            "content": f"Here is the knowledge graph data:\n{extracted_context}"
        },
        {
            "role": "user",
            "content": "Based on the above data, please generate a complete answer in English."
        }
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def get_matching_models(base_model):
    """
    查询数据库，获取所有匹配的车型
    :param base_model: 用户输入的基础车型 (如 "Tesla Model 3")
    :return: 匹配的完整车型列表 (如 ["Tesla Model 3 Long Range", "Tesla Model 3 Performance"])
    """
    query = f"""
    MATCH (m:Model)
    WHERE toLower(m.name) CONTAINS toLower('{base_model}')
    RETURN DISTINCT m.name AS ModelName
    """

    results = query_knowledge_graph(query)
    return [record["ModelName"] for record in results] if results else []


async def handle_model_selection(user_input, session):
    """
    处理用户输入的车型选择（数字），并执行最终查询。
    该函数在用户输入是一串数字时被调用。
    """
    try:
        base_model = session.get_last_entity()
        if not base_model:
            return "I couldn't determine which car you're referring to."

        matching_models = get_matching_models(base_model)
        if not matching_models:
            return "No matching models found."

        # 将用户输入的数字转化为索引
        user_choice = int(user_input) - 1
        if user_choice < 0 or user_choice >= len(matching_models):
            return "Invalid selection. Please choose a valid number from the list."

        # 用户选择了第 user_choice 项
        chosen_model = matching_models[user_choice]
        session.last_entity = chosen_model  # 将用户最终选择的车型存起来

        # 在 session.history 中找上一条真正的问题
        last_user_question = None
        for record in reversed(session.history):
            if "user" in record:
                last_user_question = record["user"]
                break

        if not last_user_question:
            return "I couldn't retrieve the original question. Please ask again."

        # 解析上一次真正的问题，以获取 relationship
        entity, relationship = await parse_question(last_user_question, session)
        # 强制 entity 为用户选择的车型
        entity = chosen_model

        return await do_final_query(entity, relationship, session, last_user_question)

    except ValueError:
        return "Please enter a valid number corresponding to the model."
    except Exception as e:
        print(f"Error in handle_model_selection: {e}")
        return f"An error occurred: {str(e)}"



async def do_final_query(chosen_model, relationship, session, original_question):
    """
    最终查询并回答：
    1. 生成 Cypher 查询
    2. query_knowledge_graph 拿到结果
    3. 调用 generate_response_with_openai 将结果转化为自然语言回答
    """
    try:
        # 1. 生成 Cypher
        query = generate_cypher_query(chosen_model, relationship)
        if not query:
            return "Sorry, I couldn't generate a valid query."

        results = query_knowledge_graph(query)
        if not results:
            bot_answer = f"Sorry, I couldn't find any relevant information for {chosen_model}."
        else:
            # 拼接结果文本
            extracted_results = [record.get("Details") for record in results if record.get("Details")]
            extracted_context = "\n".join(extracted_results)

            # 2. 调用 LLM 生成回答
            bot_answer = await generate_response_with_openai(session.history, extracted_context)

        # 记录到 session.history
        session.add_message(
            user_message=original_question,
            bot_message=bot_answer,
            entity=chosen_model
        )

        return bot_answer

    except Exception as e:
        print(f"Error in do_final_query: {e}")
        return f"An error occurred: {str(e)}"




# Define function to answer questions
async def answer_question(question, session):
    try:
        # **解析问题，获取 `entity` 和 `relationship`**
        entity, relationship = await parse_question(question, session)

        # **如果 `session.last_entity` 已经存储了具体车型，直接使用**
        if session.get_last_entity():
            entity = session.get_last_entity()

        # **如果 `entity` 仍然为空，则无法查询**
        if not entity or not relationship:
            return "I couldn't understand your question."

        # **查询数据库中匹配的车型**
        matching_models = get_matching_models(entity)

        if len(matching_models) > 1:
            # **多个车型，返回选择列表**
            choices = "\n".join([f"{i + 1}. {model}" for i, model in enumerate(matching_models)])
            session.last_entity = entity  # 存储基础车型
            bot_message = f"There are multiple versions of {entity}. Please select one:\n{choices}"

            # ✅ **存储用户的原始问题**
            session.add_message(user_message=question, bot_message=bot_message, entity=entity)
            return bot_message

        elif len(matching_models) == 1:
            # **只有一个车型，直接使用**
            entity = matching_models[0]

        # **执行查询**
        query = generate_cypher_query(entity, relationship)
        if not query:
            return "Sorry, I couldn't generate a valid query."

        print(f"Generated Cypher Query: {query}")

        query_results = query_knowledge_graph(query)
        if not query_results:
            bot_message = f"Sorry, I couldn't find any relevant information for {entity}."
        else:
            extracted_results = [record.get("Details") for record in query_results if record.get("Details")]
            extracted_context = "\n".join(extracted_results)

            # 让 LLM 生成自然语言回答
            bot_message = await generate_response_with_openai(session.history, extracted_context)

        # ✅ **存储用户问题和回答**
        session.add_message(user_message=question, bot_message=bot_message, entity=entity)

    except Exception as e:
        bot_message = f"An error occurred: {str(e)}"
        print(f"Error in answer_question: {e}")

    return bot_message


# Conversation context management
class ChatSession:
    def __init__(self):
        self.history = []
        self.last_entity = None  # 记录最近提及的车型

    def add_message(self, user_message, bot_message, entity=None):
        self.history.append({"user": user_message, "bot": bot_message})
        if entity:
            self.last_entity = entity  # 记录最近的车型

    def get_last_entity(self):
        return self.last_entity  # 返回最近查询的车型

    def get_context(self):
        return "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in self.history])


# Implement multi-turn conversation
async def start_conversation():
    session = ChatSession()

    print("Hello! Ask me anything about electric vehicles. Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # **如果用户输入的是数字，则处理车型选择**
        if user_input.isdigit():
            answer = await handle_model_selection(user_input, session)
        else:
            answer = await answer_question(user_input, session)

        print(f"Bot: {answer}")




# Start conversation
if __name__ == "__main__":
    asyncio.run(start_conversation())
