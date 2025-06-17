# Model Context Protocol Documentation

This directory contains the scraped documentation from the Model Context Protocol (MCP) specification (version 2025-03-26).

## Structure

- **01_overview/** - Main specification overview and introduction
- **02_architecture/** - MCP architecture and design principles
- **03_base_protocol/** - Core protocol details including lifecycle, transports, and authorization
- **04_server_features/** - Server-side features: prompts, resources, and tools
- **05_client_features/** - Client-side features: roots and sampling

## About MCP

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. It provides a standardized way to connect LLMs with the context they need through:

- **Resources**: Context and data for the AI model to use
- **Prompts**: Templated messages and workflows
- **Tools**: Functions for the AI model to execute
- **Sampling**: Server-initiated LLM interactions

The protocol uses JSON-RPC 2.0 for communication and supports multiple transport mechanisms including stdio and HTTP.

For the latest documentation and implementation details, visit [modelcontextprotocol.io](https://modelcontextprotocol.io/).