# AI Customer Support Agent

An AI-powered customer support system built with **FastAPI, LangGraph, LangChain, RAG, and PostgreSQL**.

The system is designed to automate common customer support workflows such as answering company-related questions, tracking orders, processing returns and refunds, and helping customers find suitable products.

It uses a **multi-agent architecture** where a Supervisor Agent analyzes each request and routes it to the appropriate specialized agent.

---

## Features

* 💬 Answer general customer questions
* 📦 Retrieve order information and shipping status
* 🔄 Handle product returns and refund workflows
* 🛍️ Help customers find suitable products
* 🔎 Hybrid RAG for company knowledge
* 🌐 Web search when internal information is insufficient
* 🤖 Multi-agent orchestration with LangGraph
* 🔐 JWT-based authentication
* ⚡ FastAPI backend
* 🐳 Docker support
* 🧪 Automated tests
* 📊 Evaluation for RAG retrieval, generation, and agent routing
* 🛡️ Rate limiting and application-level validation

---

## Architecture

The application follows a multi-agent architecture built with **LangGraph**.

A request is received through the chat API and passed to the Supervisor Agent. The Supervisor determines the user's intent and routes the request to the appropriate specialized agent.

The system currently contains the following agents:

* **Chat Agent**
* **Order Info Agent**
* **RAG Agent**
* **Refund Agent**
* **Shop Agent**

Each specialized agent can use its own tools and data sources when necessary.

---

# Agents

## Chat Agent

The Chat Agent handles conversational requests that do not require access to the company's knowledge base, database, or specialized workflows.

Examples:

* "Hello, how are you?"
* "Thanks!"
* "I'm just looking around."

The agent is designed to keep simple conversations separate from more expensive or unnecessary tool-based workflows.

---

## Order Info Agent

The Order Info Agent handles requests related to customer orders.

It uses the `get_order_info` tool to retrieve order information from the application database.

### Capabilities

* Check order status
* Retrieve order details
* Check shipping information
* Retrieve information about a specific order

### Example requests

```text
Where is my order?

What's the status of order 125?

Can you show me the details of my order?
```

---

## RAG Agent

The RAG Agent handles questions that can be answered using the company's internal knowledge base.

The knowledge base contains information such as:

* Return and refund policies
* Shipping information
* Warranty rules
* Company FAQs
* General product information

Instead of relying exclusively on the LLM's internal knowledge, the system retrieves relevant documents from the company's knowledge base and provides them as context to the LLM.

This helps ground the generated response in company-specific information.

### Example requests

```text
How long do I have to return a product?

What are the warranty conditions?

How long does shipping take?
```

---

# RAG System

The RAG pipeline uses a hybrid retrieval approach combining **semantic search** and **BM25 keyword search**.

### Semantic Retrieval

Semantic retrieval is used to identify documents that are conceptually related to the user's question, even when the exact words used by the customer do not appear in the documents.

### BM25

BM25 provides keyword-based retrieval and is useful when exact terms, product names, policy names, or specific phrases are important.

Combining both approaches allows the system to benefit from both semantic similarity and lexical matching.

### Vector Database

The semantic retrieval layer uses **Chroma** as the vector database.

The retrieved context is then passed to the LLM to generate the final answer.

---

# RAG Evaluation

The RAG pipeline was evaluated using a custom evaluation dataset from both retrieval and generation perspectives.

## Retrieval Metrics

| Metric      | Score |
| ----------- | ----: |
| Recall@3    |   70% |
| Precision@3 |   67% |
| F1@3        |   68% |

## Generation Metrics

| Metric              | Score |
| ------------------- | ----: |
| Average Correctness |  0.94 |
| Average Relevance   | 0.948 |

### Interpretation

The retrieval metrics measure how effectively the system retrieves relevant documents from the knowledge base.

The generation metrics evaluate the quality of the final answers produced using the retrieved context.

The results indicate that while the generation quality is strong, the retrieval pipeline still has room for improvement, particularly in recall and precision.

Potential improvements include:

* Better chunking strategies
* Improved embeddings
* Query rewriting
* Reranking
* Hybrid retrieval optimization
* Better retrieval evaluation datasets

---

# Refund Agent

The Refund Agent handles the return and refund workflow.

Unlike the RAG Agent, this workflow requires database operations and validation before a refund can be processed.

The agent uses three tools:

* `find_product`
* `check_rule`
* `save_refund`

## Tools

### `find_product`

Checks whether the requested product exists and whether it belongs to the customer.

### `check_rule`

Checks whether the product is eligible for return according to the company's return policy.

### `save_refund`

Stores the return or refund result in the database.

The workflow is intentionally tool-driven so that important business operations are validated before modifying application data.

---

# Shop Agent

The Shop Agent helps customers find suitable products based on their requirements, budget, and preferences.

Instead of simply searching for a product, the agent can ask follow-up questions when additional information is required.

For example:

```text
I need a keyboard for programming, preferably under $100.
```

The agent can identify the customer's requirements, search the product database, retrieve additional information about relevant products, and provide recommendations.

## Tools

The Shop Agent uses three tools:

### `shop_find_product`

Searches the product database based on the customer's requirements.

### `product_info_search`

Retrieves additional information about a selected product.

### `search_product`

Performs a web search when the available product information is insufficient.

This allows the Shop Agent to combine internal product data with external information when necessary.

---

# Supervisor Agent

The Supervisor Agent is responsible for determining the user's intent and routing the request to the appropriate specialized agent.

It uses structured output to extract information required for routing, such as:

* User intent
* Order ID when applicable
* Relevant request information

The Supervisor was evaluated using a custom routing dataset.

## Supervisor Evaluation

| Metric              | Result |
| ------------------- | -----: |
| Total samples       |     55 |
| Correct predictions |     54 |
| Accuracy            | 98.18% |

The evaluation indicates that the Supervisor can reliably distinguish between the major request categories in the current dataset.

---

# Technology Stack

| Technology      | Purpose                   |
| --------------- | ------------------------- |
| Python 3.13+    | Main programming language |
| FastAPI         | API framework             |
| LangChain       | LLM and RAG integration   |
| LangGraph       | Multi-agent orchestration |
| Chroma          | Vector database           |
| BM25            | Keyword-based retrieval   |
| Semantic Search | Meaning-based retrieval   |
| PostgreSQL      | Application database      |
| JWT             | Authentication            |
| OpenAI          | LLM services              |
| Tavily          | Web search                |
| Docker          | Containerization          |
| pytest          | Automated testing         |
| uv              | Dependency management     |

---

# Project Architecture

```text
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
```

---

# Getting Started

## Prerequisites

Make sure the following are installed:

* Python 3.13+
* uv
* PostgreSQL
* Docker (optional)

---

## 1. Clone the Repository

```bash
git clone https://github.com/AryaRabiee/AI_Customer_Support.git
cd AI_Customer_Support
```

---

## 2. Install Dependencies

This project uses `uv` for dependency management.

```bash
uv sync
```

Activate the virtual environment.

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

---

# Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=your_database_url
JWT_SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

Replace the example values with your own credentials.

> **Important:** Never commit `.env` files, API keys, database credentials, or other secrets to GitHub.


---

# Running the Application

Alternatively, run the application using Uvicorn:

```bash
python -m uvicorn app.main:app --reload
```

The application will be available at:

```text
http://localhost:8000
```

FastAPI automatically provides interactive API documentation at:

```text
http://localhost:8000/docs
```

The alternative OpenAPI documentation is available at:

```text
http://localhost:8000/redoc
```

---

# Running with Docker

Docker can be used to run the application in an isolated environment.

## Build the Image

```bash
docker build -t ai-customer-support .
```

## Run the Container

```bash
docker run -p 8000:8000 --env-file .env ai-customer-support
```

The application will be available at:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

# Testing

The project includes automated tests for important application components and agent behavior.

Run the complete test suite:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest app/tests/test_order_info_agent.py -v
```

Tests are used to verify important behaviors such as:

* Agent execution
* Agent routing
* Tool interaction
* Database-related workflows
* Application behavior

---

# Evaluation

The project includes evaluation pipelines for the main RAG system and Supervisor Agent.

## Supervisor

The Supervisor was evaluated on a custom intent-routing dataset.

| Metric   | Result |
| -------- | -----: |
| Total    |     55 |
| Correct  |     54 |
| Accuracy | 98.18% |

## RAG

The RAG pipeline was evaluated from both retrieval and generation perspectives.

| Metric              | Score |
| ------------------- | ----: |
| Recall@3            |   70% |
| Precision@3         |   67% |
| F1@3                |   68% |
| Average Correctness |  0.94 |
| Average Relevance   | 0.948 |

These evaluations provide a baseline for measuring future improvements to the system.

---

# Reliability

The application is designed with production-oriented concerns in mind, including:

* Input validation
* Authentication
* Rate limiting
* Structured agent outputs
* Tool-based workflows
* Error handling
* Automated testing
* Evaluation datasets

For workflows that modify application state, such as refunds, the system relies on explicit tools and business-rule validation rather than allowing the LLM to directly modify the database.

---

# Security Considerations

The following practices should be followed when deploying the project:

* Never commit `.env` files.
* Never expose API keys in source code.
* Use strong JWT secrets.
* Use environment variables for sensitive configuration.
* Validate user input before executing tools.
* Apply authentication to protected endpoints.
* Apply rate limiting to prevent abuse.
* Restrict database permissions according to application requirements.
* Validate all database operations performed by agents.
* Do not allow the LLM to directly execute arbitrary database queries.

---

# Future Improvements

The current implementation is **Version 1**. Several areas can be improved in future versions.

## Better Conversation Memory

Improve context retention across longer conversations and support more reliable multi-turn interactions.

## More Specialized Agents

Add additional agents for workflows such as:

* Customer account management
* Payment issues
* Shipping problems
* Product comparison
* Technical support

## Smarter RAG

Experiment with:

* Better chunking strategies
* Query rewriting
* Improved embeddings
* Hybrid retrieval optimization
* Reranking
* Context compression
* Metadata filtering

## Better Evaluation

Expand the evaluation datasets and introduce additional metrics for:

* Retrieval quality
* Answer faithfulness
* Answer relevance
* Tool selection
* Agent routing
* End-to-end task success

## Performance Improvements

Improve:

* Response latency
* Retrieval performance
* Database queries
* Resource consumption
* Concurrent request handling

## Reliability Improvements

Add more robust:

* Retry mechanisms
* Exponential backoff
* Timeout handling
* LLM fallbacks
* Tool failure recovery
* Observability
* Structured logging

## Multi-language Support

Expand support beyond English and Persian to provide multilingual customer support.

---

# Example Use Cases

### General Question

```text
Customer:
How long does shipping usually take?
```

The Supervisor routes the request to the RAG Agent, which retrieves the relevant shipping policy and generates the answer.

### Order Tracking

```text
Customer:
Where is order 125?
```

The Supervisor routes the request to the Order Info Agent, which uses `get_order_info` to retrieve the order status.

### Refund Request

```text
Customer:
I want to return the keyboard I bought last week.
```

The Supervisor routes the request to the Refund Agent.

The agent verifies the product, checks the return policy, and saves the result if the request is eligible.

### Product Recommendation

```text
Customer:
I need a keyboard for programming under $100.
```

The Supervisor routes the request to the Shop Agent.

The agent identifies the requirements, searches the product database, retrieves additional information when necessary, and recommends suitable products.

### External Information

```text
Customer:
Can you find more information about this product online?
```

If the available internal product information is insufficient, the Shop Agent can use `search_product` to search the web.

---

# Design Principles

The project follows several principles when building LLM-powered applications:

### Specialized Agents

Each agent has a focused responsibility instead of one large agent handling every possible task.

### Tool-Based Actions

Database operations and business workflows are performed through explicit tools.

### Retrieval-Grounded Answers

Company-specific questions are answered using retrieved internal knowledge instead of relying exclusively on the model's pretrained knowledge.

### Structured Outputs

Structured model outputs are used where predictable data is required, particularly for routing and intent extraction.

### Evaluation-Driven Development

The project includes evaluation datasets and metrics to measure system behavior instead of relying only on subjective testing.

---

# Contributing

Contributions are welcome.

## Fork the Repository

```bash
git clone https://github.com/AryaRabiee/AI_Customer_Support.git
cd AI_Customer_Support
```

Create a feature branch:

```bash
git checkout -b feature/your-feature
```

Make your changes and commit them:

```bash
git add .
git commit -m "Add your feature"
```

Push the branch:

```bash
git push origin feature/your-feature
```

Then open a Pull Request.

---

Built as a practical AI engineering project focused on:

* LLM applications
* RAG
* Multi-agent systems
* LangGraph
* LangChain
* FastAPI
* Tool calling
* Database-integrated AI workflows
* Evaluation
* Production-oriented backend engineering

---

## Support

If you find the project useful or interesting, consider giving the repository a ⭐ on GitHub.

Feedback, issues, and contributions are welcome.
