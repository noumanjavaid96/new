/**
 * @file Main export point for all configuration modules.
 * This allows for easy importing of clients, prompts, and utility functions
 * from the config directory.
 */

import OpenAI from 'openai'; // Re-exporting default from openaiClient
import { ChromaClient } from '@chroma/chromadb'; // Re-exporting default from chromaClient
import { get_encoding } from 'tiktoken'; // Re-exporting default from tokenizer

export { default as openai } from './openaiClient.js';
export { default as chroma } from './chromaClient.js';
export { getOrCreateCollection } from './chromaClient.js';
export { default as tokenizer } from './tokenizer.js';

export * from './prompts.js';
