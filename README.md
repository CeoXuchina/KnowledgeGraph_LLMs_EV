# EV Knowledge Graph Assistant

## 💡 Project Overview
This project is an intelligent Q&A system that integrates a Neo4j-based knowledge graph with a language model (OpenAI GPT). It is designed to help users retrieve detailed information about electric vehicles (EVs) such as price, battery, performance, charging speed, and more.

## 📁 Project Structure
- `Cypher Create.txt`: Cypher statements to create and populate the EV knowledge graph in Neo4j.
- `test.py`: Core backend script integrating NLP, knowledge graph queries, and LLM-based response generation.
- `web.py`: Flask server providing API endpoints for the frontend and managing conversations.
- `evaluation.py`: Script for evaluating the performance or response quality (if implemented).
- `applied_data_delete_safe_Mis.csv`: Source dataset used to populate the knowledge graph.
- `README.md`: Project documentation file.
- `templates/`: Folder containing HTML templates for rendering frontend views.
  - `index.html`: Main user interface for chatting and querying.
  - `graph.html`: Additional graph visualization interface (if used).
- `static/`: Folder for frontend static resources.
  - `style.css`: Styling for the frontend interface.
  - `icons/`: Folder containing images for bot and user avatars.

## 🚀 How to Run
### Prerequisites:
- Neo4j Desktop or Neo4j Aura set up
- Python 3.8+
- Install dependencies:
```bash
pip install flask neo4j langchain openai spacy flask-cors
python -m spacy download en_core_web_sm
```

### Steps to Start:
1. Import the Cypher script (`Cypher Create.txt`) into Neo4j to create the database.
2. Run the Flask server:
```bash
python web.py
```
3. Open a browser and go to: `http://localhost:8000`

## ✨ Features
- Natural Language Question Parsing
- Knowledge Graph-Based Querying
- Intelligent Answer Generation via OpenAI GPT
- Multi-turn Conversation Handling
- Model Recommendation and Question Suggestion
- Feedback Submission and Logging

## 📝 Example Questions
- What is the price of Tesla Model 3?
- How fast can Kia EV6 charge?
- What’s the battery capacity of BYD SEAL?
- What is the performance of Hyundai IONIQ 5?

## ⚠️ Notes
- Ensure Neo4j is running before launching the backend.
- Replace the demo OpenAI API key with your own key in `test.py`.

## 👨‍💻 Author
Weiyuan Xu 



