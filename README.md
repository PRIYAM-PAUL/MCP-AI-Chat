# Fonada AI Support Agent

An AI-powered customer support agent built using Python,
FastAPI, OpenAI LLMs and the Model Context Protocol
## start
cd mcp_server
py server.py
py -m uvicorn backend.main:app --reload
npm run dev
## Architecture
                         User
                           |
                           v
                    React Frontend
                           |
                           | HTTP
                           v
                     FastAPI Backend
                           |
                           v
                       AI Agent
                           |
                           v
                     OpenAI LLM
                           |
                           | Tool Calling
                           v
                       MCP Client
                           |
                           | HTTP
                           v
                       MCP Server
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
       search_customer  create_callback  list_callbacks
             |             |             |
             +-------------+-------------+
                           |
                           v
                    Google Sheets
                    Data Storage
## Technologies

- Python
- FastAPI
- OpenAI API
- MCP
- REST API
- JSON
- HTTP
- Pydantic
- Python async/await

