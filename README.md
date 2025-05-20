# Vapi Voice Assistant Backend

## Description

This project is a Node.js backend application designed to power an intelligent voice assistant using Vapi.ai. It provides a robust server that handles voice interactions, manages conversation history, maintains long-term memory with a vector database (ChromaDB), analyzes user mood, and dynamically generates conversation starters. The assistant's core logic is powered by OpenAI models.

## Features

*   **Voice Interaction via Vapi.ai**: Seamlessly integrates with Vapi.ai for handling real-time voice input and output.
*   **OpenAI Powered**: Leverages OpenAI's models (e.g., GPT-4o, GPT-4o-mini) for natural language understanding, response generation, and other AI tasks.
*   **Long-Term Memory**: Utilizes ChromaDB as a vector store to remember key information from past conversations, enabling more personalized and context-aware interactions.
*   **Mood Analysis**: Analyzes the user's messages to infer their mood, allowing the assistant to adapt its responses.
*   **Dynamic Conversation Starters**: Generates engaging and context-relevant conversation starters based on time of day, past interactions, and mood.
*   **Session Management**: Maintains conversation history for each session, stored locally.
*   **Tool Usage with OpenAI**: Demonstrates the use of OpenAI's tool-calling feature (e.g., for saving memories explicitly).
*   **Configurable**: Key parameters like API keys, model names, and directory paths are configurable via environment variables.
*   **ES Modules & Async Operations**: Modern JavaScript syntax with asynchronous operations for efficient handling of I/O and API calls.

## Prerequisites

*   **Node.js**: v18.x or later recommended.
*   **npm**: Included with Node.js.
*   **OpenAI API Key**: Access to the OpenAI API.
*   **Vapi.ai Account**: Access to the Vapi.ai platform to create and configure your voice assistant.
*   **ChromaDB**: This project uses the `chromadb` client which runs an in-process version of ChromaDB, storing data locally. No separate ChromaDB server installation is required.

## Setup & Installation

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install Dependencies**:
    ```bash
    npm install
    ```

3.  **Set Up Environment Variables**:
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file and fill in the required values:
        *   `OPENAI_API_KEY`: Your API key for OpenAI.
        *   `VAPI_API_KEY`: Your Vapi API key. This key is typically used if the server needs to make authenticated calls *to* the Vapi API. For incoming webhooks from Vapi, Vapi might use a different mechanism to authenticate itself to your server (e.g., a secret token in headers), which you would verify in your webhook handler (this verification is not pre-implemented but is a common pattern).
        *   `CHROMA_DB_PATH`: Path to store ChromaDB data. Defaults to `./mem_store`.
        *   `SESSION_DIR`: Directory to store conversation session files. Defaults to `./sessions`.
        *   `MOOD_DIR`: Directory to store mood analysis files. Defaults to `./moods`.
        *   `PORT`: Port for the server to run on. Defaults to `3000`.
        *   `TIMEZONE`: Timezone for date/time operations. Defaults to `America/New_York`.
        *   `OPENAI_MODEL`: The primary OpenAI model for chat completions. Defaults to `gpt-4o`.
        *   `MEMORY_EXTRACTION_MODEL`: The OpenAI model for memory extraction at the end of calls. Defaults to `gpt-4o-mini`.

## Running the Application

1.  **Start the Server**:
    ```bash
    npm start
    ```
    The server will typically be accessible at `http://localhost:PORT` (e.g., `http://localhost:3000`).

## Vapi.ai Configuration

To connect your Vapi.ai assistant to this backend server, you need to configure it in your Vapi.ai dashboard:

1.  **Server URL / Webhook URL**:
    *   Vapi needs to send events (webhooks) to this server. You must provide Vapi with the publicly accessible URL where this Node.js server is running.
    *   The webhook endpoint in this application is `/vapi-webhook`.
    *   **Local Development**: If you are running this server locally, you'll need a tunneling service like `ngrok` to create a public URL.
        *   Install ngrok and run it: `ngrok http YOUR_LOCAL_PORT` (e.g., `ngrok http 3000`).
        *   Ngrok will provide a public URL (e.g., `https://your-unique-string.ngrok.io`).
        *   Your full Vapi Server URL will be: `https://your-unique-string.ngrok.io/vapi-webhook`.
    *   Enter this URL in the "Server URL" or "Webhook URL" field in your Vapi assistant's settings.

2.  **Authentication (Webhook Security)**:
    *   Vapi may allow you to specify a secret token or use other mechanisms to secure your webhook. This helps your server verify that incoming requests are genuinely from Vapi.
    *   While this backend doesn't currently have explicit Vapi webhook signature verification implemented, it's a good practice. If Vapi provides a secret token, you would typically add middleware to `src/index.js` to verify it.

3.  **Model Configuration (Vapi Dashboard)**:
    *   Ensure that your Vapi assistant is configured to use appropriate models for services Vapi provides directly (like STT - Speech-to-Text, and TTS - Text-to-Speech), if applicable.
    *   The OpenAI models configured in this server's `.env` file (`OPENAI_MODEL`, `MEMORY_EXTRACTION_MODEL`) are for server-side AI logic (chat completions, memory extraction).

4.  **Assistant Event Types**:
    *   Vapi allows you to subscribe to various event types. This server is structured to handle common events like `assistant-request`, `call-start`, `call-end`, `function-call`, `speech-update`, and `status-update`. Ensure your Vapi assistant is configured to send these relevant events to your webhook URL.

## Project Structure

```
.
├── .env                  # Local environment variables (ignored by Git)
├── .env.example          # Example environment variables
├── package.json          # Project dependencies and scripts
├── package-lock.json     # Lockfile for dependencies
├── README.md             # This file
├── VAPI_SETUP.md         # Notes on Vapi dashboard configuration
├── src/
│   ├── config/           # Configuration files (OpenAI/Chroma clients, prompts, tokenizer)
│   │   ├── chromaClient.js
│   │   ├── index.js
│   │   ├── openaiClient.js
│   │   ├── prompts.js
│   │   └── tokenizer.js
│   ├── routes/           # Webhook handlers for Vapi events
│   │   └── vapiHandlers.js
│   ├── utils/            # Utility functions (time, ChromaDB, session, mood)
│   │   ├── chromaUtils.js
│   │   ├── index.js
│   │   ├── moodUtils.js
│   │   ├── sessionUtils.js
│   │   └── timeUtils.js
│   └── index.js          # Main Express server setup and webhook router
├── sessions/             # Stores conversation history JSON files (created automatically)
├── moods/                # Stores mood analysis JSON files (created automatically)
└── mem_store/            # Default directory for ChromaDB data (created automatically)
```

## Troubleshooting

*   **API Key Issues**: Ensure `OPENAI_API_KEY` is correct and your OpenAI account has credits. Verify `VAPI_API_KEY` if used for server-to-Vapi calls.
*   **Ngrok Not Running**: If developing locally, make sure `ngrok` is running and correctly forwarding to your local server's port. The ngrok URL can change each time you restart it unless you have a paid account.
*   **Port Conflicts**: If `PORT 3000` is in use, change it in your `.env` file and restart the server (and update ngrok if necessary).
*   **ChromaDB Errors**: Check console logs for any errors related to ChromaDB initialization or operations. Ensure the `CHROMA_DB_PATH` is writable.
*   **Dependency Issues**: If you encounter issues after `npm install`, try removing `node_modules` and `package-lock.json`, then run `npm install` again.
*   **Check Server Logs**: The server logs detailed information, including errors, to the console. These are your first point of call for debugging.
*   **Vapi Dashboard Logs**: Check the Vapi.ai dashboard for logs related to your assistant and webhook events. This can show you what Vapi is sending and what responses it's receiving.
```
