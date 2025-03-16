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
    base_url="https://api.chatanywhere.org"
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key="sk-SfzXTk3x7Fumt6LV0u6Ps7lPvnoh9tSSVVHwUkewi7XkyEZM",
    openai_api_base="https://api.chatanywhere.org"
)


# Create Prompt template to instruct AI to answer based solely on knowledge graph content, Prompt template for ReAct agent
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

# Cypher queries dictionary
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

# Attribute mapping
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

# Synonym Mapping
synonyms = {
    # 1. Available Since
    "release date": "available since",
    "launch date": "available since",


    # 2. Available to Order
    "preorder": "available to order",
    "ordering": "available to order",
    "how to order": "available to order",

    # 3. Price
    "cost": "price",
    "msrp": "price",

    # 4. Battery
    "battery size": "battery",
    "battery capacity": "battery",
    "akku capacity": "battery",

    # 5. Real Range
    "range": "real range",
    "battery life": "real range",

    # 6. Performance
    "acceleration": "performance",
    "torque": "performance",
    "horsepower": "performance",
    "power": "performance",
    "speed": "performance",
    "hp": "performance",
    "ps": "performance",
    "max speed": "performance",
    "top speed": "performance",
    "0-100": "performance",
    "0-60": "performance",

    # 7. Charging
    "charging speed": "charging",
    "charge time": "charging",
    "fast charging": "charging",
    "dc charging": "charging",
    "ac charging": "charging",
    "home charging": "charging",

    # 8. Bidirectional Charging
    "v2l": "bidirectional charging",
    "v2g": "bidirectional charging",
    "v2h": "bidirectional charging",
    "vehicle-to-load": "bidirectional charging",
    "vehicle-to-grid": "bidirectional charging",
    "vehicle-to-home": "bidirectional charging",

    # 9. Energy Consumption
    "co2": "energy consumption",
    "emission": "energy consumption",
    "emissions": "energy consumption",
    "fuel equivalent": "energy consumption",
    "energy usage": "energy consumption",

    # 10. Real Energy Consumption
    "real consumption": "real energy consumption",
    "actual consumption": "real energy consumption",
    "city consumption": "real energy consumption",
    "highway consumption": "real energy consumption",

    # 11. Dimensions and Weight
    "dimension": "dimensions and weight",
    "size": "dimensions and weight",
    "length": "dimensions and weight",
    "width": "dimensions and weight",
    "height": "dimensions and weight",
    "wheelbase": "dimensions and weight",
    "payload": "dimensions and weight",
    "weight": "dimensions and weight",

    # 12. URL
    "official website": "url",
}

# Function to parse questions
async def parse_question(question, session):

    doc = nlp(question)
    entity = None
    attribute = None

    # If the user uses "this car" / "this vehicle" and session.last_entity is not empty, the last car model is used directly
    if ("this car" in question.lower() or "this vehicle" in question.lower()) and session.last_entity:
        entity = session.last_entity
    else:
        # Otherwise try to extract the new model name from the user input
        for car in car_models:
            if car.lower() in question.lower():
                entity = car
                break

        # # Extract entity (car model)
        # for ent in doc.ents:
        #     if ent.label_ in ["PRODUCT", "ORG"]:
        #         entity = ent.text
        #         break

    # Identify the attributes that the user wants to query
    attribute_candidates = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "ADJ"]]



    for word in attribute_candidates:
        if word in synonyms:
            attribute = synonyms[word]
            break
        elif word in attribute_mapping:
            attribute = word
            break


    # If NLP fails to identify the attribute, LLM is called for intelligent reasoning
    if not attribute:
        # list all available properties
        valid_attributes = [
            "available since",
            "available to order",
            "price",
            "battery",
            "real range",
            "performance",
            "charging",
            "bidirectional charging",
            "energy consumption",
            "real energy consumption",
            "dimensions and weight",
            "url"
        ]

        # Prepare system prompt: Only one of the 12 attributes is allowed to be output. If none of them match, output unknown
        system_prompt = (
            "You are an assistant to parse car data queries into a fixed set of attributes. "
            "You must output exactly one of the following valid attributes (in lowercase) "
            "that best matches the user's question:\n\n"
            "1) available since\n"
            "2) available to order\n"
            "3) price\n"
            "4) battery\n"
            "5) real range\n"
            "6) performance\n"
            "7) charging\n"
            "8) bidirectional charging\n"
            "9) energy consumption\n"
            "10) real energy consumption\n"
            "11) dimensions and weight\n"
            "12) url\n\n"
            "If none of the above seem relevant, output exactly 'unknown'. "
            "Respond with only a single line that is exactly one of those attributes or 'unknown'."
        )

        # Prepare the user prompt for the model
        user_prompt = (
            f"The user asked: \"{question}\"\n"
            "Which single attribute from the list above best fits the user’s request? "
            "If none apply, return 'unknown'."
        )


        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50,
            temperature=0.0,
        )


        attribute_candidate = response.choices[0].message.content.strip().lower()


        if attribute_candidate not in valid_attributes and attribute_candidate != "unknown":
            attribute = "unknown"
        else:
            attribute = attribute_candidate

    # Get relationship based on attribute_mapping
    relationship = attribute_mapping.get(attribute, None)

    print(f"Parsed Entities: {entity}, Parsed attributes: {attribute}")
    return entity, relationship


# Used to generate Cypher query statements
# def generate_cypher_query(entity, relationship):
#     if not entity or not relationship:
#         return None
#
#     query = f"""
#     MATCH (m:Model)
#     WHERE toLower(m.name) CONTAINS toLower('{entity}')
#     MATCH (m)-[:{relationship}]->(info)
#     RETURN info.details AS Details
#     """
#     return query

# Executing Neo4j queries
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
            if "\t" in line:  # Check if it is a valid price line
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


async def generate_cypher_query(entity, relationship, user_question):
    """
    Use LLM to generate Cypher queries instead of templates.
    entity: car model name
    relationship: relationship name (such as "HAS_PRICE")
    user_question: user's original question
    """
    if not entity or not relationship:
        return None

    system_prompt = (
        "You are a helpful assistant for generating Neo4j Cypher queries. "
        "We have a knowledge graph about car models. Each model has relationships like:\n"
        "- [:HAS_AVAILABLE_SINCE]->(AvailableSince {date, model})\n"
        "- [:HAS_AVAILABLE_TO_ORDER]->(AvailableToOrder {details, model})\n"
        "- [:HAS_PRICE]->(Price {details, model})\n"
        "- [:HAS_BATTERY]->(Battery {details, model})\n"
        "- [:HAS_REAL_RANGE]->(RealRange {details, model})\n"
        "- [:HAS_PERFORMANCE]->(Performance {details, model})\n"
        "- [:HAS_CHARGING]->(Charging {details, model})\n"
        "- [:HAS_BIDIRECTIONAL_CHARGING]->(BidirectionalCharging {details, model})\n"
        "- [:HAS_ENERGY_CONSUMPTION]->(EnergyConsumption {details, model})\n"
        "- [:HAS_REAL_ENERGY_CONSUMPTION]->(RealEnergyConsumption {details, model})\n"
        "- [:HAS_DIMENSIONS_AND_WEIGHT]->(DimensionsAndWeight {details, model})\n"
        "- [:HAS_URL]->(URL {link, model})\n"
        "The user will provide a car's name (property: name in node Model) and the relationship type (e.g. HAS_PRICE). "
        "We want a query that:\n"
        "1) matches the Model whose name property matches (case-insensitive) the user's input.\n"
        "2) uses the corresponding relationship type.\n"
        "3) returns the relevant property from that related node as 'Details' (if 'details' exists) or 'date' as 'Details' (for AvailableSince node)."
    )

    user_prompt = (
        f"The user asked: {user_question}\n\n"
        f"We identified the car model entity as: {entity}, relationship as: {relationship}. "
        "Please generate a single valid Cypher query that:\n"
        "- Finds the Model node where toLower(m.name) CONTAINS toLower('<entity>')\n"
        "- Follows the [:<relationship>] relationship to a node we call 'info'\n"
        "- Returns 'info.details AS Details' (if 'details' exists) or 'info.date AS Details' (if the node is AvailableSince)\n\n"
        "Please respond with ONLY the Cypher query, nothing else (no ```cypher code blocks``` please)."
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=300,
        temperature=0.3,
    )

    generated_text = response.choices[0].message.content.strip()

    cleaned_text = re.sub(r"```[\s\S]*?```", "", generated_text).strip()

    cleaned_text = cleaned_text.replace("cypher", "").strip()

    print("[LLM Generated Query] Before cleaning:")
    print(generated_text)
    print("[LLM Generated Query] After cleaning:")
    print(cleaned_text)

    return cleaned_text

# LangChain tool: Knowledge graph query tool
async def knowledge_graph_tool(input_text, session):
    entity, relationship = await parse_question(input_text, session)
    if not entity or not relationship:
        print("Failed to parse question or map to a valid relationship.")
        return "I couldn't understand your question."

    # Generate queries based on attributes
    query = f"""
    MATCH (m:Model {{name: '{entity}'}})-[:{relationship}]->(r)
    RETURN r.details AS Details
    """

    print(f"Generated Cypher Query: {query}")

    # Execute a query
    result = query_knowledge_graph(query)

    if not result:
        print("No data found for the given query.")
        return "I couldn't find any relevant information in the knowledge graph."

    # Extracting the return value
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


# Initialize Agent with knowledge graph query tool
agent = create_react_agent(
    tools=[knowledge_graph_tool_obj],
    llm=llm,
    prompt=react_agent_prompt,
)


# Calling LLM to integrate database results into natural language answers
async def generate_response_with_openai(history, extracted_context):
    user_message = history[-1]['user'] if history else "The user asked a question."

    conversation = [
        {
            "role": "system",
            "content": (
                "You are an expert on new energy vehicles, helping users answer questions about cars. "
                "Please keep the model name as it is and do not simplify it into other names."
            )
        },
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": f"Here is the knowledge graph data:\n{extracted_context}"},
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


async def generate_response_with_openai_no_history(_history, extracted_context):
    last_user_question = "The user asked a question."
    if _history and "user" in _history[-1]:
        last_user_question = _history[-1]["user"]

    conversation = [
        {
            "role": "system",
            "content": (
                "You have the following data from the knowledge graph (shown as plain text). "
                "Do your best to interpret all lines and provide a direct, accurate, and detailed summary. "
                "You must only use the data in the text below to form your answer, providing a direct, accurate, and detailed summary. "
                "Do not mention or use any other data or context from previous questions. "
                "If the text doesn't mention a piece of data, do not infer it. "
                "Each time a user asks a question, only answer the current question and do not add previous questions in your reply"
                "Whenever you receive a new question, only reply to the new question, and do not answer previous questions."
                "When a user asks a question, you should only answer the current question. Do not include content from previous questions when responding."
                "For example, when I ask you about the real range of a certain car, you give me the real range, but when I ask you about the price of the car, you only give me the price without mentioning the real range."
                "Do not say 'Not available' unless there's absolutely no useful info."
            )
        },

        {
            "role": "user",
            "content": (
                f"---\n{extracted_context}\n---\n"
                "Please summarize or respond based ONLY on the above text."
            )
        },
        {
            "role": "assistant",
            "content": (
                "Below is the relevant data from the knowledge graph:\n"
                f"---\n{extracted_context}\n---\n"
            )
        },
        {
            "role": "user",
            "content": "Please provide a detailed English answer based ONLY on the data above, including as many specifics as possible. Whenever you receive a new question, only reply to the new question, and do not answer previous questions."
        }

    ]
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        max_tokens=500,
        temperature=1,
    )
    return response.choices[0].message.content.strip()


def get_matching_models(base_model):
    """
    Query the database to get all matching models
    :param base_model: User-entered base vehicle model (E.g. "Tesla Model 3")
    :return: Complete list of matching models (如 ["Tesla Model 3 Long Range", "Tesla Model 3 Performance"])
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
    Processes the model selection (a number) entered by the user and performs the final query.
    This function is called when the user input is a string of numbers.
    """
    try:
        base_model = session.get_last_entity()
        if not base_model:
            return "I couldn't determine which car you're referring to."

        matching_models = get_matching_models(base_model)
        if not matching_models:
            return "No matching models found."

        user_choice = int(user_input) - 1
        if user_choice < 0 or user_choice >= len(matching_models):
            return "Invalid selection. Please choose a valid number from the list."

        chosen_model = matching_models[user_choice]
        session.last_entity = chosen_model


        last_user_question = None
        for record in reversed(session.history):
            if "user" in record:
                last_user_question = record["user"]
                break

        if not last_user_question:
            return "I couldn't retrieve the original question. Please ask again."

        # analyze the problem again and get the relationship
        entity, relationship = await parse_question(last_user_question, session)
        # Mandatory use of the final selected model
        entity = chosen_model

        return await do_final_query(entity, relationship, session, last_user_question)

    except ValueError:
        return "Please enter a valid number corresponding to the model."
    except Exception as e:
        print(f"Error in handle_model_selection: {e}")
        return f"An error occurred: {str(e)}"


async def do_final_query(chosen_model, relationship, session, original_question):
    """
    Final query and answer：
    1. Generate Cypher queries
    2. query_knowledge_graph gets the result
    3. Call generate_response_with_openai to convert the result into a natural language answer
    """
    try:
        query = await generate_cypher_query(chosen_model, relationship, original_question)

        if not query:
            return "Sorry, I couldn't generate a valid query."

        print(f"Generated Cypher Query:\n{query}")

        results = query_knowledge_graph(query)
        if not results:
            bot_answer = f"Sorry, I couldn't find any relevant information for {chosen_model}."
        else:
            extracted_results = [record.get("Details") for record in results if record.get("Details")]
            extracted_context = "\n".join(extracted_results)  # Original query results

            # 1. Here we first print or log the original Neo4j query results.
            print("\n--- Neo4j raw query results (Raw Result) ---")
            print(extracted_context)
            print("--- End of Raw Result ---\n")

            attr_name = relationship.replace("HAS_", "").replace("_", " ").lower()  # 例如 "price"
            if attr_name == "price":
                formatted_price_str = format_response("price", extracted_context)

            # Calling LLM rewrite with history
            # llm_answer = await generate_response_with_openai(session.history, extracted_context)

            #Calling LLM rewrite without history
                llm_answer = await generate_response_with_openai_no_history(session.history, formatted_price_str)
                bot_answer = llm_answer
            else:
                llm_answer = await generate_response_with_openai_no_history(session.history, extracted_context)
                bot_answer = llm_answer

            # The final answer returned to the user is only the answer rewritten by LLM.
            #bot_answer = llm_answer

        session.add_message(original_question, bot_answer, chosen_model)
        return bot_answer

    except Exception as e:
        print(f"Error in do_final_query: {e}")
        return f"An error occurred: {str(e)}"




# Define function to answer questions
async def answer_question(question, session):
    """
    When a user asks a normal question, if only one car model is matched, the query will be made directly,
    If multiple car models are matched, a list of options is returned for the user to select one.
    """
    try:
        parsed_entity, relationship = await parse_question(question, session)
        if parsed_entity:
            entity = parsed_entity
        else:
            # If the new model is not analyzed, use the last one.
            if session.get_last_entity():
                entity = session.get_last_entity()
            else:
                return "I couldn't understand which car you're referring to."

        session.last_entity = entity

        if not entity or not relationship:
            return "I couldn't understand your question."

        matching_models = get_matching_models(entity)
        if len(matching_models) > 1:

            choices = "\n".join([f"{i + 1}. {model}" for i, model in enumerate(matching_models)])
            session.add_message(question, f"There are multiple versions of {entity}. Please select one:\n{choices}", entity)
            return f"There are multiple versions of {entity}. Please select one:\n{choices}"

        elif len(matching_models) == 1:
            entity = matching_models[0]

        # If only one match is found, go to search
        query = await generate_cypher_query(entity, relationship, question)
        if not query:
            return "Sorry, I couldn't generate a valid query."

        print(f"Generated Cypher Query:\n{query}")

        results = query_knowledge_graph(query)
        if not results:
            bot_message = f"Sorry, I couldn't find any relevant information for {entity}."
        else:
            extracted_results = [record.get("Details") for record in results if record.get("Details")]
            extracted_context = "\n".join(extracted_results)

            print("\n--- Neo4j raw query results (Raw Result) ---")
            print(extracted_context)
            print("--- End of Raw Result ---\n")

            attr_name = relationship.replace("HAS_", "").replace("_", " ").lower()
            if attr_name == "price":
                extracted_context = format_response("price", extracted_context)

            llm_answer = await generate_response_with_openai_no_history(session.history, extracted_context)
            bot_message = llm_answer

        session.add_message(question, bot_message, entity)
        return bot_message

    except Exception as e:
        print(f"Error in answer_question: {e}")
        return f"An error occurred: {str(e)}"



# Conversation context management
class ChatSession:
    def __init__(self):
        self.history = []
        self.last_entity = None  # Record the most recently mentioned car models

    def add_message(self, user_message, bot_message, entity=None):
        self.history.append({"user": user_message, "bot": bot_message})
        if entity:
            self.last_entity = entity  # Record the latest model

    def get_last_entity(self):
        return self.last_entity  # Return the most recently searched models

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

        # If the user enters a number, process the car model selection
        if user_input.isdigit():
            answer = await handle_model_selection(user_input, session)
        else:
            answer = await answer_question(user_input, session)

        print(f"Bot: {answer}")


# Start conversation
if __name__ == "__main__":
    asyncio.run(start_conversation())
