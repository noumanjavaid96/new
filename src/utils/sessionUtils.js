import fs from 'fs/promises';
import { existsSync, mkdirSync } from 'fs';
import path from 'path';
import moment from 'moment-timezone';
import 'dotenv/config';

const SESSION_DIR = process.env.SESSION_DIR || './sessions';
const TIMEZONE = process.env.TIMEZONE || 'America/New_York';

// Ensure SESSION_DIR exists
if (!existsSync(SESSION_DIR)) {
  mkdirSync(SESSION_DIR, { recursive: true });
  console.log(`Session directory created at: ${SESSION_DIR}`);
}

/**
 * Generates a unique session ID.
 * Format: chat_YYYYMMDD_XXXX (XXXX is a random 4-letter string)
 * @returns {string} The generated session ID.
 */
export function generateSessionId() {
  const dateStr = moment().tz(TIMEZONE).format('YYYYMMDD');
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  let letters = '';
  for (let i = 0; i < 4; i++) {
    letters += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return `chat_${dateStr}_${letters}`;
}

/**
 * Loads a session's message history from a JSON file.
 * @async
 * @param {string} sessionId - The ID of the session to load.
 * @returns {Promise<Array<object>>} A promise that resolves to an array of messages,
 *                                    or an empty array if the session file doesn't exist or is invalid.
 */
export async function loadSession(sessionId) {
  if (!sessionId || typeof sessionId !== 'string' || sessionId.trim() === "") {
    console.warn("loadSession: Invalid sessionId provided.");
    return [];
  }
  const filePath = path.join(SESSION_DIR, `${sessionId}.json`);
  try {
    const data = await fs.readFile(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    if (error.code === 'ENOENT') {
      // File does not exist for sessionId, this is normal for a new session.
      // console.log(`No session file found for sessionId "${sessionId}", starting new session.`);
    } else if (error instanceof SyntaxError) {
      console.error(`Error parsing session file ${filePath} for sessionId "${sessionId}":`, error);
      // Corrupted JSON file
    } else {
      console.error(`Error reading session file ${filePath} for sessionId "${sessionId}":`, error);
    }
    return []; // Default structure for new or problematic sessions
  }
}

/**
 * Prepares a message object for serialization, ensuring tool_calls are plain objects.
 * This mirrors the Python script's handling of tool_calls.
 * @param {object} message - The message object.
 * @returns {object} The cleaned message object.
 */
function prepareMessageForSerialization(message) {
  if (message && message.tool_calls && Array.isArray(message.tool_calls)) {
    return {
      ...message,
      tool_calls: message.tool_calls.map(tc => {
        if (tc && typeof tc === 'object') {
          const newTc = { ...tc }; // Shallow copy
          if (newTc.function && typeof newTc.function === 'object') {
            newTc.function = { ...newTc.function }; // Shallow copy of function object
          }
          return newTc;
        }
        return tc; // Should not happen if structure is correct
      }),
    };
  }
  return message;
}


/**
 * Saves a session's message history to a JSON file.
 * @async
 * @param {string} sessionId - The ID of the session to save.
 * @param {Array<object>} messages - An array of message objects to save.
 * @returns {Promise<boolean>} True if successful, false otherwise.
 */
export async function saveSession(sessionId, messages) {
  if (!sessionId || typeof sessionId !== 'string' || sessionId.trim() === "") {
    console.warn("saveSession: Invalid sessionId provided. Session not saved.");
    return false;
  }
  if (!Array.isArray(messages)) {
    console.warn("saveSession: Messages must be an array. Session not saved.");
    return false;
  }

  const filePath = path.join(SESSION_DIR, `${sessionId}.json`);
  try {
    // Ensure tool_calls are properly structured before serialization
    const serializableMessages = messages.map(prepareMessageForSerialization);
    const jsonData = JSON.stringify(serializableMessages, null, 2); // Pretty print JSON
    await fs.writeFile(filePath, jsonData, 'utf8');
    // console.log(`Session saved successfully to ${filePath} for sessionId "${sessionId}"`);
    return true;
  } catch (error) {
    console.error(`Error saving session file ${filePath} for sessionId "${sessionId}":`, error);
    return false;
  }
}
