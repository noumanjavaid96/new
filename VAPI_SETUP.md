# Vapi.ai Assistant Setup Guide

This document outlines the necessary configuration steps on the Vapi.ai dashboard to integrate with this Node.js server.

## 1. Assistant Model

*   You will need to configure the AI model for your assistant within the Vapi dashboard.
*   This project is designed to work with OpenAI models. Specify the desired OpenAI model (e.g., `gpt-4o`, `gpt-3.5-turbo`, etc.) in your Vapi assistant settings.

## 2. Server URL (Webhook)

*   Vapi.ai needs to send events (webhooks) to this server to interact with your custom logic.
*   You must provide Vapi with the publicly accessible URL where this Node.js server is running.
*   The endpoint for Vapi webhooks in this application will likely be `/vapi-webhook` (this will be defined in the route handlers). So, the full URL will be something like: `https://your-server-domain.com/vapi-webhook`.
*   **For Local Development**: When running the server locally, you'll need a tool like [ngrok](https://ngrok.com/) to create a secure tunnel and get a public URL that forwards to your local machine.
    *   Example ngrok command (if your server runs on port 3000): `ngrok http 3000`
    *   ngrok will provide you with a public HTTPS URL (e.g., `https://random-string.ngrok.io`) which you can then use as the base for your Vapi Server URL: `https://random-string.ngrok.io/vapi-webhook`.

## 3. API Keys and Credentials

*   **Vapi API Key**: This Node.js application requires a Vapi API Key to initialize the Vapi SDK and make calls to the Vapi platform (if needed, depending on the SDK's specific authentication mechanism). Ensure you have your Vapi API Key and have set it in the `.env` file as `VAPI_API_KEY`.
*   **OpenAI API Key**: This application uses the OpenAI API directly for certain functionalities (e.g., interacting with ChromaDB for RAG). Ensure your `OPENAI_API_KEY` is correctly set in the `.env` file. This key will be used by the OpenAI SDK.

## 4. Other Configuration

*   Review other settings in the Vapi dashboard for your assistant, such as voice selection, transcription settings, and any other specific features you wish to enable or configure.

By correctly setting up these points, your Vapi assistant should be able to communicate effectively with this backend server.
