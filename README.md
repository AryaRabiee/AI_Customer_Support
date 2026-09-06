# AI Customer Support AgentW

A smart customer support system designed to speed up response times and reduce customer waiting periods. The system handles everything from answering common questions to managing returns and helping customers find products.

What This System Does

Our system works like a 24/7 customer support team that can:

Answer General Questions — Handles common questions about the company, policies, shipping, warranty, and more.
Track Orders — Checks order status and order details instantly.
Manage Returns & Refunds — Handles return and refund workflows.
Help with Shopping — Helps customers find suitable products based on their needs and budget.
Search the Web — Searches online when the available knowledge base does not contain enough information.

All of this happens automatically. ⚡

## 🔍 RAG System

One of the core components of this project is the RAG (Retrieval-Augmented Generation) system.

The RAG agent answers questions using the company's knowledge base, including:

Return and refund policies
Shipping information
Warranty rules
Company FAQs
General product information

Instead of relying only on the LLM's internal knowledge, the system first retrieves relevant information from the knowledge base and then provides that context to the LLM to generate the final answer.


## 📊 RAG Performance

The retrieval system was evaluated using a custom evaluation dataset.

Metric	Score
Recall@3	70%
Precision@3	67%
F1@3	68%
Average Correctness	0.94
Average Relevance	0.948

These metrics measure both the quality of the retrieval system and the quality of the generated answers.

## 🏗️ System Architecture

The system uses a multi-agent architecture built with LangGraph.

The general request flow is:

                Chat Endpoint   
                       │
                       ▼       
                 Chat Endpoint         

                       │
                       ▼  

                 Validation/Rate Limit    
                       │
                       ▼    

                 Supervisor Agent       
                       │
                       ▼  
       ┌───────┼────────┬──────────┬──────────┐
       ▼       ▼        ▼          ▼          ▼
     Chat    Order     RAG      Refund      Shop
    Agent    Agent    Agent     Agent      Agent
       │       │        │          │          │
       └───────┴────────┴──────────┴──────────┘
                       │
                       ▼
              Tools / Database /
                RAG / Web APIs
                       │
                       ▼
                 Final Response

The Supervisor Agent is responsible for understanding the user's request and routing it to the appropriate specialized agent.

## AI Agents
### Chat Agent

Handles casual conversations that do not require access to the database or the company's knowledge base.

Examples:

"Hello, how are you?"
"Thanks!"
"I'm just looking around."
### Order Info Agent

Handles customer requests related to their orders.

It uses the get_order_info tool to retrieve order information from the database.

The agent can:

Check order status
View order details
Track shipping information
Retrieve information about a specific order

Example:

"Where is my order?"
"What's the status of order 125?"
"Can you show me the details of my order?"
### RAG Agent

Handles general questions that can be answered using the company's knowledge base.

Examples:

"How long do I have to return a product?"
"What are the warranty conditions?"
"How long does shipping take?"

The agent uses the hybrid RAG pipeline described above to retrieve relevant information before generating an answer.

### Refund Agent

Handles the actual return and refund workflow.

The agent uses three tools:

find_product — Checks whether the product exists and belongs to the customer.
check_rule — Checks whether the product is eligible for return based on company policies.
save_refund — Saves the refund or return result in the database.
Refund Workflow
Customer Request
       │
       ▼
 find_product
       │
       ▼
  check_rule
       │
       ▼
  save_refund
       │
       ▼
   Database
### Shop Agent

The Shop Agent helps customers find the right products based on their needs, budget, and preferences.



Instead of simply searching for a product, the agent can have a short conversation with the customer to understand what they're looking for and then find suitable options.



For example:

"I need a keyboard for programming, preferably under $100."

The agent can identify the requirements, search for matching products, retrieve additional product information, and recommend the most suitable options.

Tools

The Shop Agent uses three tools:



shop_find_product — Searches the product database based on the customer's requirements.

product_info_search — Retrieves detailed information about a selected product.

search_product — Searches the web when the available product information is not sufficient.
## Tech Stack
Technology	Purpose
Python 3.13+	Main programming language
FastAPI	API framework
LangChain	LLM and RAG integration
LangGraph	Multi-agent orchestration
Chroma	Vector database
BM25	Keyword-based retrieval
Semantic Search	Meaning-based retrieval
PostgreSQL	Application database
JWT	Authentication
OpenAI	LLM services
Tavily	Web search
Docker	Containerization

## Getting Started
1. Clone the Repository
git clone https://github.com/username/AI_Customer_Support_Agent.git
cd AI_Customer_Support_Agent
2. Install Dependencies

This project uses uv for dependency management.

uv sync

Activate the virtual environment:

Windows:

.venv\Scripts\activate

macOS / Linux:

source .venv/bin/activate
3. Environment Variables

Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=your_database_url
JWT_SECRET_KEY=your_secret_key
ALGORITHM=HS256

Replace the example values with your own credentials.

Important: Never commit your .env file or API keys to GitHub.

4. Run the Application

Start the FastAPI development server:

fastapi dev app/main.py

Or using Uvicorn:

python -m uvicorn app.main:app --reload

The application will be available at:

http://localhost:8000

FastAPI documentation:

http://localhost:8000/docs
5. Run Tests

Run all tests:

pytest -v

Run a specific test:

pytest app/tests/test_order_info_agent.py -v
## Running with Docker

Make sure Docker is installed and running.

Build the Image
docker build -t ai-customer-support .
Run the Container
docker run -p 8000:8000 --env-file .env ai-customer-support

The application will be available at:

http://localhost:8000

FastAPI documentation:

http://localhost:8000/docs

If you are using Docker Compose:

docker compose up
## Evaluation

The project includes evaluation for the main RAG pipeline and Supervisor Agent.

Supervisor

The Supervisor was evaluated on a custom routing dataset.

Total:    55
Correct:  54
Accuracy: 98.18%
RAG

The RAG system was evaluated from both retrieval and generation perspectives.

Metric	Score
Recall@3	70%
Precision@3	67%
F1@3	68%
Average Correctness	0.94
Average Relevance	0.948

Automated tests are also used to verify important application behavior such as agent execution and tool interaction.

🔮 Future Improvements

This project is currently at Version 1, but there are several areas that can be improved in future versions.

Planned improvements include:

🧠 Better Memory — Improve conversation memory and context retention across longer conversations.
🤖 More Agents — Add new specialized agents for additional customer support workflows.
🔍 Smarter RAG — Experiment with better chunking, reranking, embeddings, and retrieval strategies.
📊 Better Evaluation — Expand evaluation datasets and introduce more comprehensive metrics.
⚡ Performance Improvements — Improve response time and resource usage.
🛡️ Better Reliability — Improve error handling, retries, fallbacks, and failure recovery.
🌍 Multi-language Support — Add support for languages beyond English and Persian.
📝 Contributing

Found a bug or have an idea for improving the project?

Contributions are welcome!

Fork the repository.
Create a feature branch:
git checkout -b feature/your-feature
Make your changes.
Commit your changes:
git commit -m "Add your feature"
Push the branch:
git push origin feature/your-feature
Open a Pull Request.
⭐ Show Your Support

If you found this project interesting or useful, consider giving it a star on GitHub! ⭐

It really helps and is much appreciated. ❤️