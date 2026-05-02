# Multi-Agent AI Ecosystem | Demon Slayer Edition

A concurrent, multi-agent AI simulation built with Python and `discord.py`. This project deploys five autonomous, persona-driven bots into a single Discord environment, allowing them to interact with users and each other in real-time. 

Powered by the Gemini API, the system features isolated memory management, dynamic context injection, and multimodal link parsing.

## 🚀 Key Features

* **Concurrent Multi-Agent Processing:** Utilizes `asyncio.gather` to run 5 independent bot clients simultaneously on a single event loop without blocking or race conditions.
* **Isolated State Management:** Each agent maintains an isolated, sliding-window chat history (capped at 20 messages) to optimize token usage while retaining short-term conversational memory.
* **Dynamic Context Injection:** Implements selective system prompting. When a URL is detected, the bots dynamically receive a temporary data protocol, allowing historical characters to process and react to modern internet metadata (scraped via Discord embeds) without breaking their core persona constraints.
* **String Formatting & Output Parsing:** Forces the LLM to output a specific formatted string (e.g., `[Emoji]|[Text]`). The backend intercepts this payload, splits the string, applies the emoji as a native Discord reaction, and sends the clean text to the chat.
* **REST API Integrations:** 
  * Integrates the **Gemini API** for generative language and decision-making.
  * Integrates the **Jikan REST API** via `aiohttp` for real-time data fetching.
* **Deployment Persistence:** Incorporates a Flask-based sidecar server to bypass PaaS inactivity limits (e.g., Render) and ensure persistent execution.

## 💻 Tech Stack

* **Language:** Python 3.x
* **Asynchronous I/O:** `asyncio`, `aiohttp`
* **APIs:** `discord.py`, Google Generative AI SDK, Jikan API
* **Web Server:** Flask (health-check/keep-alive routing)

## 🧠 System Architecture Overview

1. **The Event Listener:** The script listens for messages across all 5 clients. It safely ignores self-authored messages to prevent infinite feedback loops.
2. **Event & URL Interception:** Determines if a message contains a standard prompt, a specific command, or a URL. If a URL is present, it forces a sequential `asyncio.sleep` to allow Discord's servers to generate the preview embed, which is then scraped for hidden context.
3. **LLM Payload Construction:** Constructs a JSON payload containing the agent's system prompt directives, recent memory state, and conditional tech protocols.
4. **The Post-Processor:** Validates the API response, executes the output parsing logic for reactions, updates the isolated memory state, and dispatches the final response to the Discord channel.

## 🔮 Future Scope

* Migration from ephemeral RAM-based memory arrays to persistent database storage (PostgreSQL/MySQL) for long-term state retention across server restarts.
* Implementation of a true Multimodal Vision Pipeline via Base64 encoding for direct image attachments.
