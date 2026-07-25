                         ┌──────────────────────┐
                         │        USER          │
                         │  پیام + Token/Auth   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API       │
                         │   API / Endpoints     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Authentication /      │
                         │ Authorization         │
                         │ JWT / User Identity   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Conversation       │
                         │   / User Context     │
                         │                      │
                         │ Redis + PostgreSQL   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      ROUTER          │
                         │                      │
                         │ Intent / LLM Router  │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │       RAG       │    │     TOOLS       │    │   DATABASE      │
    │                 │    │                 │    │                 │
    │ Retriever       │    │ Order Tool      │    │ PostgreSQL      │
    │ Embedding       │    │ Payment Tool    │    │                 │
    │ BM25            │    │ Ticket Tool     │    │ User Data       │
    │ Hybrid Search   │    │ Weather Tool    │    │ Orders          │
    │ RRF             │    │ Email Tool      │    │ Tickets         │
    │                 │    │                 │    │                 │
    │ Chroma          │    │ External APIs   │    │ SQLAlchemy ORM  │
    │ Vector DB       │    │                 │    │                 │
    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   CONTEXT BUILDER    │
                         │                      │
                         │ RAG Results          │
                         │ Tool Results         │
                         │ DB Results           │
                         │ Conversation History │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │         LLM          │
                         │   Response Generator │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Streaming Response │
                         │   FastAPI / SSE       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                                  USER