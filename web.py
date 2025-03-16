from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from test import answer_question, ChatSession, handle_model_selection, driver
import asyncio
import threading
import datetime
from time import time

web = Flask(__name__)
CORS(web)

global_session = ChatSession()


@web.route('/')
def home():
    return render_template('index.html')

@web.route('/graph')
def show_graph():
    return render_template('graph.html')

@web.route('/graph-data/init')
def get_initial_graph():
    try:
        query = """
        MATCH (car:CAR)-[:INCLUDES]->(brand:Brand)
        OPTIONAL MATCH (brand)-[:HAS_MODEL]->(model:Model)
        RETURN DISTINCT 
            id(car) as sourceId, labels(car)[0] as sourceLabel, coalesce(car.name, '') as sourceName,
            'INCLUDES' as relation,
            id(brand) as targetId, labels(brand)[0] as targetLabel, coalesce(brand.name, '') as targetName
        UNION
        MATCH (brand:Brand)-[:HAS_MODEL]->(model:Model)
        RETURN DISTINCT 
            id(brand) as sourceId, labels(brand)[0] as sourceLabel, coalesce(brand.name, '') as sourceName,
            'HAS_MODEL' as relation,
            id(model) as targetId, labels(model)[0] as targetLabel, coalesce(model.name, '') as targetName
        """
        with driver.session() as session:
            result = session.run(query)
            nodes = {}
            links = []
            for record in result:
                s_id = record['sourceId']
                t_id = record['targetId']
                if s_id not in nodes:
                    nodes[s_id] = {"id": s_id, "label": record['sourceLabel'], "name": record['sourceName']}
                if t_id not in nodes:
                    nodes[t_id] = {"id": t_id, "label": record['targetLabel'], "name": record['targetName']}
                links.append({"source": s_id, "target": t_id, "type": record['relation']})
            return jsonify({"nodes": list(nodes.values()), "links": links})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@web.route('/graph-data/model-details')
def get_model_details():
    try:
        model_name = request.args.get('name')
        if not model_name:
            return jsonify({"error": "Missing model name"}), 400

        query = """
        MATCH (m:Model) WHERE m.name = $model_name
        MATCH (m)-[r]->(attr)
        RETURN DISTINCT 
            id(m) as sourceId, labels(m)[0] as sourceLabel, coalesce(m.name, '') as sourceName,
            type(r) as relation,
            id(attr) as targetId, labels(attr)[0] as targetLabel,
            coalesce(attr.name, attr.details, attr.date, attr.link, '') as targetName
        """
        with driver.session() as session:
            result = session.run(query, parameters={"model_name": model_name})
            nodes = {}
            links = []
            for record in result:
                s_id = record['sourceId']
                t_id = record['targetId']
                if s_id not in nodes:
                    nodes[s_id] = {"id": s_id, "label": record['sourceLabel'], "name": record['sourceName']}
                if t_id not in nodes:
                    nodes[t_id] = {"id": t_id, "label": record['targetLabel'], "name": record['targetName']}
                links.append({"source": s_id, "target": t_id, "type": record['relation']})
            return jsonify({"nodes": list(nodes.values()), "links": links})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@web.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        start_time = time()

        def run_async_task():
            global answer
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            answer = loop.run_until_complete(
                handle_model_selection(question, global_session)
                if question.isdigit()
                else answer_question(question, global_session)
            )

        thread = threading.Thread(target=run_async_task)
        thread.start()
        thread.join()

        end_time = time()
        response_time = round(end_time - start_time, 2)

        return jsonify({"answer": answer, "time": response_time})
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@web.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    question = data.get('question', '')
    answer = data.get('answer', '')
    correctness = data.get('correctness', None)
    response_time = data.get('response_time', None)


    try:
        with open("chat_history_log.txt", "a", encoding="utf-8") as f:

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n========== Feedback Received at {timestamp} ==========\n")


            f.write(f"[User Feedback]\n")
            f.write(f"Question: {question}\n")
            f.write(f"Answer: {answer}\n")
            f.write(f"Correctness: {correctness}\n")
            f.write(f"Response Time: {response_time} seconds\n")


            f.write("\n[Full Conversation History]\n")
            for i, msg in enumerate(global_session.history, 1):
                user_msg = msg.get("user", "")
                bot_msg = msg.get("bot", "")
                f.write(f"Round {i}:\n  User: {user_msg}\n  Bot: {bot_msg}\n")

            f.write("=====================================================\n\n")

    except Exception as e:
        print(f"Error writing to log file: {e}")

    print("========== User Feedback ==========")
    print("Question:", question)
    print("Answer:", answer)
    print("Correctness:", correctness)
    print("===================================")

    return jsonify({"status": "success", "message": "Feedback received."}), 200


if __name__ == '__main__':
    web.run(debug=True, port=8000)