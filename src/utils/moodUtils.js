import fs from 'fs/promises';
import { existsSync, mkdirSync } from 'fs';
import path from 'path';
import { openai, MOOD_ANALYSIS_PROMPT } from '../config/index.js';
import { getTimeContext } from './timeUtils.js';
import 'dotenv/config';

const MOOD_DIR = process.env.MOOD_DIR || './moods';
const OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-4o'; // Or your preferred model

// Ensure MOOD_DIR exists
if (!existsSync(MOOD_DIR)) {
  mkdirSync(MOOD_DIR, { recursive: true });
  console.log(`Mood directory created at: ${MOOD_DIR}`);
}

/**
 * @typedef {object} MoodData
 * @property {string} mood - The perceived mood (e.g., "Happy", "Neutral").
 * @property {string} [reasoning] - Optional reasoning from the AI.
 * @property {string} timestamp - ISO string of when the mood was recorded.
 */

/**
 * Analyzes the user's mood based on their message using OpenAI.
 * @async
 * @param {string} userMessage - The user's message to analyze.
 * @returns {Promise<MoodData | { mood: string, reasoning: string, timestamp: string }>}
 *          The analyzed mood data, or a default "Uncertain" mood on failure.
 */
export async function analyzeMood(userMessage) {
  const { timestamp } = getTimeContext();
  if (!userMessage || typeof userMessage !== 'string' || userMessage.trim() === "") {
    console.warn("analyzeMood: No user message provided.");
    return { mood: "Uncertain", reasoning: "No message to analyze.", timestamp };
  }

  try {
    const moodPrompt = MOOD_ANALYSIS_PROMPT.replace("{user_message}", userMessage);

    const response = await openai.chat.completions.create({
      model: OPENAI_MODEL,
      messages: [{ role: "system", content: moodPrompt }],
      // Ensure the prompt guides the model to output structured JSON.
      // Forcing JSON mode might be an option if the model supports it well
      // and the prompt is designed for it.
      // response_format: { type: "json_object" }, // This requires careful prompt engineering.
      temperature: 0.5, // Lower temperature for more deterministic mood analysis
      max_tokens: 50,
    });

    let perceivedMood = "Uncertain";
    let reasoning = "Could not determine mood from AI response.";

    if (response.choices && response.choices[0] && response.choices[0].message) {
      const content = response.choices[0].message.content;
      // Attempt to parse the content if it's expected to be JSON
      // For now, assuming the prompt asks for a simple string like "Perceived Mood: Happy"
      const moodMatch = content.match(/Perceived Mood:\s*(\w+)/i);
      if (moodMatch && moodMatch[1]) {
        perceivedMood = moodMatch[1];
        reasoning = `AI perceived mood as ${perceivedMood}.`;
      } else {
         // If the direct match fails, try a simpler extraction if the model just returns the mood word.
        const lines = content.trim().split('\n');
        const lastLine = lines[lines.length - 1].trim();
        // Basic check if the last line is one of the expected moods
        const commonMoods = ["Neutral", "Happy", "Sad", "Anxious", "Excited", "Stressed", "Content", "Confused", "Frustrated", "Other"];
        if (commonMoods.includes(lastLine)) {
            perceivedMood = lastLine;
            reasoning = `AI perceived mood as ${perceivedMood}.`;
        } else {
            console.warn("analyzeMood: Could not parse mood from AI response:", content);
        }
      }
    }

    return { mood: perceivedMood, reasoning, timestamp };

  } catch (error) {
    console.error("Error analyzing mood with OpenAI:", error);
    console.error(`Error analyzing mood with OpenAI for userMessage (first 50 chars): "${userMessage.substring(0,50)}..."`, error);
    return { mood: "Uncertain", reasoning: `Error during analysis: ${error.message}`, timestamp };
  }
}

/**
 * Saves mood data for a session.
 * Appends the new mood data to a JSON file for the given session.
 * @async
 * @param {string} sessionId - The ID of the session.
 * @param {MoodData} moodData - The mood data to save.
 * @returns {Promise<boolean>} True if successful, false otherwise.
 */
export async function saveMood(sessionId, moodData) {
  if (!sessionId || typeof sessionId !== 'string' || sessionId.trim() === "") {
    console.warn("saveMood: Invalid sessionId provided. Mood not saved.");
    return false;
  }
  if (!moodData || typeof moodData.mood !== 'string') {
    console.warn("saveMood: Invalid moodData provided. Mood not saved.");
    return false;
  }

  const filePath = path.join(MOOD_DIR, `${sessionId}_moods.json`);
  let moods = [];

  try {
    // Try to load existing moods
    const fileData = await fs.readFile(filePath, 'utf8');
    moods = JSON.parse(fileData);
    if (!Array.isArray(moods)) moods = []; // Ensure it's an array
  } catch (error) {
    if (error.code === 'ENOENT') {
      // File doesn't exist, will create a new one
    } else if (error instanceof SyntaxError) {
      console.error(`Error parsing mood file ${filePath}. Will overwrite with new data.`, error);
      // Corrupted file, start fresh
       console.error(`Error parsing mood file ${filePath} for sessionId "${sessionId}". Will overwrite with new data.`, error);
    } else {
      console.error(`Error reading mood file ${filePath} for sessionId "${sessionId}":`, error);
      return false; // Other read error
    }
  }

  // Add new mood with a fresh timestamp (even if one was in moodData, this ensures consistency)
  const newMoodEntry = {
    ...moodData,
    timestamp: moodData.timestamp || new Date().toISOString(), // Use provided or generate new
  };
  moods.push(newMoodEntry);

  try {
    await fs.writeFile(filePath, JSON.stringify(moods, null, 2), 'utf8');
    // console.log(`Mood saved successfully to ${filePath}`);
    return true;
  } catch (error) {
    console.error(`Error saving mood file ${filePath} for sessionId "${sessionId}":`, error);
    return false;
  }
}

/**
 * Retrieves and analyzes the mood trend for a session.
 * @async
 * @param {string} sessionId - The ID of the session.
 * @returns {Promise<{ description: string, history: MoodData[] }>}
 *          An object containing a description of the mood trend and the recent mood history.
 */
export async function getMoodTrend(sessionId) {
  if (!sessionId || typeof sessionId !== 'string' || sessionId.trim() === "") {
    console.warn("getMoodTrend: Invalid sessionId provided.");
    return { description: "No session ID provided for mood history.", history: [] };
  }
  const filePath = path.join(MOOD_DIR, `${sessionId}_moods.json`);
  let moods = [];

  try {
    const fileData = await fs.readFile(filePath, 'utf8');
    moods = JSON.parse(fileData);
    if (!Array.isArray(moods)) moods = [];
  } catch (error) {
    if (error.code === 'ENOENT') {
      return { description: "No mood history available yet for this session.", history: [] };
    } else if (error instanceof SyntaxError) {
      console.error(`Error parsing mood file ${filePath} for trend analysis for sessionId "${sessionId}".`, error);
      return { description: "Could not parse mood history data.", history: [] };
    } else {
      console.error(`Error reading mood file ${filePath} for trend analysis for sessionId "${sessionId}":`, error);
      return { description: "Error reading mood history.", history: [] };
    }
  }

  if (moods.length === 0) {
    return { description: "No mood history recorded for this session.", history: [] };
  }

  const recentMoods = moods.slice(-5); // Get the last 5 moods
  const currentMood = recentMoods[recentMoods.length - 1];
  let description = `Current perceived mood is ${currentMood.mood}.`;

  if (recentMoods.length > 1) {
    const uniqueMoods = [...new Set(recentMoods.map(m => m.mood))];
    if (uniqueMoods.length === 1) {
      description = `Mood has been consistently perceived as ${currentMood.mood}.`;
    } else {
      const previousMood = recentMoods[recentMoods.length - 2];
      if (previousMood.mood !== currentMood.mood) {
        description = `Mood seems to have shifted from ${previousMood.mood} to ${currentMood.mood}.`;
      } else {
        // Find the earliest mood in the recent set that is different from the current
        let changedFrom = null;
        for (let i = recentMoods.length - 2; i >= 0; i--) {
          if (recentMoods[i].mood !== currentMood.mood) {
            changedFrom = recentMoods[i].mood;
            break;
          }
        }
        if (changedFrom) {
          description = `Recently, mood shifted from ${changedFrom} and is now ${currentMood.mood}.`;
        } else {
          description = `Perceived mood is ${currentMood.mood}. Recent history includes: ${recentMoods.map(m=>m.mood).join(', ')}.`;
        }
      }
    }
  }

  return { description, history: recentMoods };
}
