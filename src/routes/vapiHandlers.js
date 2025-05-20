/**
 * @file Vapi webhook handler functions.
 * These functions contain the core logic for responding to Vapi events.
 */

import {
  loadSession,
  saveSession,
  generateSessionId, 
  analyzeMood,
  saveMood,
  getMoodTrend,
  getTimeContext,
  getDaysSinceLastChat,
  retrieveVectorMemories,
  saveVectorMemory,
  batchSaveMemories, // Added for memory extraction
} from '../utils/index.js';

import {
  openai,
  SYSTEM_PROMPT,
  CONVERSATION_STARTER_PROMPT,
  MEMORY_EXTRACTION_PROMPT,
} from '../config/index.js';
import path from 'path'; 

const OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-4o';
const MEMORY_EXTRACTION_MODEL = process.env.MEMORY_EXTRACTION_MODEL || 'gpt-4o-mini';
const SESSION_DIR = process.env.SESSION_DIR || './sessions';

/**
 * Tool definition for the AI to save memories.
 * @type {Array<object>}
 */
const tools = [{
    type: "function",
    function: {
        name: "save_memory",
        description: "Saves a significant piece of information, a user preference, or a key takeaway discussed during the conversation for future reference. Use this to remember important details that will enhance future interactions.",
        parameters: {
            type: "object",
            properties: {
                call_id: {
                    type: "string",
                    description: "The ID of the current call/session. This helps associate the memory with the correct conversation log."
                },
                memory_content: {
                    type: "string",
                    description: "The specific piece of information, preference, or key takeaway to remember. This should be a concise but descriptive summary of what needs to be recalled."
                }
            },
            required: ["call_id", "memory_content"]
        }
    }
}];

/**
 * Generates a conversation starter using AI or falls back to predefined starters.
 * @async
 * @param {string} sessionId - The ID of the current session.
 * @returns {Promise<string>} The generated conversation starter text.
 */
async function generate_conversation_starter(sessionId) {
  console.log(`[vapiHandlers.js] Generating conversation starter for session ${sessionId}`);
  try {
    const { timeOfDay, currentDate, currentTime } = getTimeContext();
    const { description: moodDescription, history: recentMoods } = await getMoodTrend(sessionId);
    const keyMemories = await retrieveVectorMemories("important personal information about the user", 5);

    let memoryString = "No specific memories retrieved for conversation starter.";
    if (keyMemories && keyMemories.length > 0) {
      memoryString = `Key memories that might be relevant:\n${keyMemories.map(mem => `- ${mem}`).join('\n')}`;
    }

    const starterPromptContext = CONVERSATION_STARTER_PROMPT
      .replace("{current_time}", `${currentDate} ${currentTime}`)
      .replace("{time_of_day}", timeOfDay)
      .replace("{mood_trend}", moodDescription || "No mood trend available.")
      .replace("{recent_moods}", recentMoods && recentMoods.length > 0 ? recentMoods.map(m => m.mood).join(', ') : "No recent moods.")
      .replace("{key_memories}", memoryString)
      .replace("{previous_interaction_summary}", "Summary of previous interaction not available yet."); // Placeholder

    const response = await openai.chat.completions.create({
      model: OPENAI_MODEL,
      messages: [{ role: "system", content: starterPromptContext }, {role: "user", content: "Please generate a conversation starter."}],
      temperature: 0.8,
      max_tokens: 100,
    });

    if (response.choices && response.choices[0] && response.choices[0].message.content) {
      return response.choices[0].message.content.trim();
    }
  } catch (error) {
    console.error("[vapiHandlers.js] Error generating conversation starter with OpenAI:", error);
  }

  const { timeOfDay } = getTimeContext();
  const starters = {
    morning: ["Good morning! What's on your mind today?", "Hello! How are you starting your day?", "Hi there! Ready to tackle the day?"],
    afternoon: ["Good afternoon! How's your day going?", "Hello! Anything interesting happening this afternoon?", "Hi! Hope you're having a productive day."],
    evening: ["Good evening! How was your day?", "Hello! Winding down or just getting started?", "Hi there! What are your plans for this evening?"],
    night: ["Hello! Burning the midnight oil or just a late-night chat?", "Good evening. Hope you had a good day.", "Hi! How are you doing this late?"],
  };
  const timeBasedStarters = starters[timeOfDay] || starters.evening;
  return timeBasedStarters[Math.floor(Math.random() * timeBasedStarters.length)];
}

/**
 * Prepares the message history context for a new or ongoing session.
 * Updates or prepends the system prompt.
 * @async
 * @param {string} sessionId - The ID of the current session.
 * @param {Array<object>} [currentMessages=[]] - The current array of messages for the session.
 * @returns {Promise<Array<object>>} The updated messages array with the system prompt.
 */
async function prepare_context_for_new_session(sessionId, currentMessages = []) {
  console.log(`[vapiHandlers.js] Preparing context for session ${sessionId}`);
  const { currentDate, currentTime, timeOfDay } = getTimeContext();
  const sessionFilePath = path.join(SESSION_DIR, `${sessionId}.json`);
  const daysSinceLast = getDaysSinceLastChat(sessionFilePath);
  const { description: moodTrend } = await getMoodTrend(sessionId); 
  
  const relevantMemoriesArray = await retrieveVectorMemories(`Overall user profile, preferences, and long-term discussion topics for ${sessionId}`, 5);
  let relevantMemoriesText = "No specific memories retrieved for this session's context.";
  if (relevantMemoriesArray && relevantMemoriesArray.length > 0) {
    relevantMemoriesText = relevantMemoriesArray.map(mem => `- ${mem}`).join('\n');
  }

  const formattedSystemPrompt = SYSTEM_PROMPT
    .replace("{current_time}", `${currentDate} ${currentTime} (${timeOfDay})`)
    .replace("{days_since_last_chat}", daysSinceLast)
    .replace("{mood_trend}", moodTrend || "No mood data available.")
    .replace("{relevant_memories}", relevantMemoriesText)
    .replace("{user_message}", ""); 

  let messages = [...currentMessages]; 

  if (messages.length > 0 && messages[0].role === "system") {
    messages[0].content = formattedSystemPrompt;
  } else {
    messages.unshift({ role: "system", content: formattedSystemPrompt });
  }
  return messages;
}

/**
 * Extracts key memories from a full conversation transcript and saves them.
 * @async
 * @param {string} sessionId - The ID of the session.
 * @param {string} fullConversationTranscript - The complete transcript of the conversation.
 * @returns {Promise<boolean>} True if memories were successfully extracted and attempts were made to save them, false otherwise.
 */
async function extract_memories_at_end(sessionId, fullConversationTranscript) {
  console.log(`[vapiHandlers.js] Starting memory extraction for session ${sessionId}. Transcript length: ${fullConversationTranscript.length}`);
  if (!fullConversationTranscript || typeof fullConversationTranscript !== 'string' || fullConversationTranscript.trim() === "") {
    console.log("[vapiHandlers.js] No transcript provided for memory extraction.");
    return false;
  }

  try {
    const extractionPrompt = MEMORY_EXTRACTION_PROMPT.replace("{user_message}", fullConversationTranscript);
    
    console.log(`[vapiHandlers.js] Calling OpenAI (${MEMORY_EXTRACTION_MODEL}) for memory extraction for session ${sessionId}.`);
    const response = await openai.chat.completions.create({
      model: MEMORY_EXTRACTION_MODEL,
      messages: [
        { role: "system", content: "You are an AI assistant tasked with extracting key pieces of information, user preferences, or significant events from the provided conversation transcript. List each item on a new line. If no specific information worth remembering is found, output 'NOTHING_TO_REMEMBER'." },
        { role: "user", content: extractionPrompt }
      ],
      temperature: 0.2, // Low temperature for factual extraction
      max_tokens: 800, // Increased max_tokens for potentially longer extractions
    });

    const extractedText = response.choices[0]?.message?.content?.trim();

    if (!extractedText || extractedText.toUpperCase() === "NOTHING_TO_REMEMBER" || extractedText.toUpperCase() === "NO SIGNIFICANT INFORMATION TO EXTRACT.") {
      console.log(`[vapiHandlers.js] No significant memories to extract for session ${sessionId} based on AI response.`);
      return false;
    }

    console.log(`[vapiHandlers.js] Raw extracted memories for ${sessionId}:\n${extractedText}`);

    const cleanedMemories = extractedText
      .split('\n') // Split by newline
      .map(line => line
        .replace(/^\s*\d+[\.\-\)]\s*/, '') // Remove leading numbers (e.g., "1. ", "2- ", "3) ")
        .replace(/^\s*[\-\•\*\+]+\s*/, '')    // Remove leading bullet points (e.g., "- ", "• ")
        .trim()                         // Trim whitespace
      )
      .filter(line => line && line.toUpperCase() !== "NOTHING_TO_REMEMBER" && line.toUpperCase() !== "NO SIGNIFICANT INFORMATION TO EXTRACT."); // Filter out empty strings and explicit "nothing"

    if (cleanedMemories.length === 0) {
      console.log(`[vapiHandlers.js] No valid memories left after cleaning for session ${sessionId}.`);
      return false;
    }

    console.log(`[vapiHandlers.js] Cleaned memories for ${sessionId} to be saved:`, cleanedMemories);
    
    const batchSaveSuccess = await batchSaveMemories(cleanedMemories, sessionId);
    if (batchSaveSuccess) {
      console.log(`[vapiHandlers.js] Successfully initiated batch save for ${cleanedMemories.length} memories for session ${sessionId}.`);
      return true;
    } else {
      console.warn(`[vapiHandlers.js] Batch save operation reported issues for session ${sessionId}. Check previous logs from chromaUtils.`);
      return false; // Batch save itself might have logged errors but returned false.
    }

  } catch (error) {
    console.error(`[vapiHandlers.js] Error during memory extraction or saving for session ${sessionId}:`, error);
    return false;
  }
}

/**
 * Handles the 'call-start' event logic.
 * @async
 * @param {object} vapiMessage - The Vapi message object (req.body.message).
 * @param {import('express').Response} res - Express response object.
 */
export async function handleCallStartLogic(vapiMessage, res) {
  const callId = vapiMessage.call?.id || vapiMessage.callId || generateSessionId(); 
  console.log(`[vapiHandlers.js] Handling call-start logic for callId: ${callId}`);

  try {
    const greeting = await generate_conversation_starter(callId);
    
    let messages = await loadSession(callId); 
    messages = await prepare_context_for_new_session(callId, messages); 
    messages.push({ role: "assistant", content: greeting, timestamp: new Date().toISOString() });
    await saveSession(callId, messages);

    res.json({ assistant: { type: "text", text: greeting } });
  } catch (error) {
    console.error(`[vapiHandlers.js] Error in handleCallStartLogic for callId ${callId}:`, error);
    res.status(500).json({ assistant: { type: "text", text: "I had a little trouble starting up. Could you try again?" } });
  }
}

/**
 * Handles the 'assistant-request' message from Vapi (user speaking).
 * @async
 * @param {object} vapiMessage - The Vapi message object (req.body.message).
 * @param {import('express').Response} res - Express response object.
 */
export async function handleAssistantRequestLogic(vapiMessage, res) {
  const callId = vapiMessage.call?.id || vapiMessage.callId;
  const userInput = vapiMessage.transcript; 

  if (!callId || typeof userInput !== 'string') {
    console.warn("[vapiHandlers.js] Missing callId or userInput in assistant-request:", vapiMessage);
    return res.status(400).json({ assistant: { type: "text", text: "I didn't get that. Could you please repeat?" } });
  }
  console.log(`[vapiHandlers.js] Handling assistant-request for callId: ${callId}, User input: "${userInput}"`);

  try {
    let messages = await loadSession(callId);
    messages = await prepare_context_for_new_session(callId, messages);

    const contextualMemories = await retrieveVectorMemories(userInput, 3);
    if (contextualMemories && contextualMemories.length > 0) {
      const memoryContextForLLM = "For your information, here's some potentially relevant context from past discussions related to the user's current message:\n" +
                                  contextualMemories.map(mem => `- ${mem}`).join("\n") +
                                  "\nBased on this, and our ongoing conversation, please respond to the user's last message.";
      messages.push({ role: "system", content: memoryContextForLLM, timestamp: new Date().toISOString() });
    }
    
    messages.push({ role: "user", content: userInput, timestamp: new Date().toISOString() });

    const moodData = await analyzeMood(userInput);
    if (moodData) { 
        await saveMood(callId, moodData);
    }
    
    console.log(`[vapiHandlers.js] Sending ${messages.length} messages to OpenAI for callId ${callId}. Last user message: "${userInput}"`);
    const response = await openai.chat.completions.create({
      model: OPENAI_MODEL,
      messages: messages,
      tools: tools,
      tool_choice: "auto",
      temperature: 0.7, 
    });

    const choice = response.choices[0].message; 

    if (choice.tool_calls && choice.tool_calls.length > 0) {
      console.log(`[vapiHandlers.js] OpenAI response includes tool calls for callId ${callId}.`);
      messages.push({ role: "assistant", tool_calls: choice.tool_calls, content: choice.content || null, timestamp: new Date().toISOString() });

      for (const toolCall of choice.tool_calls) {
        if (toolCall.function.name === "save_memory") {
          const args = JSON.parse(toolCall.function.arguments);
          console.log(`[vapiHandlers.js] Handling 'save_memory' tool for callId ${callId}:`, args);
          
          const memoryCallId = args.call_id || callId; 
          const memorySaved = await saveVectorMemory(args.memory_content, memoryCallId);
          
          messages.push({
            tool_call_id: toolCall.id,
            role: "tool",
            name: "save_memory",
            content: JSON.stringify({ success: memorySaved, message: memorySaved ? "Memory saved." : "Failed to save memory." }),
            timestamp: new Date().toISOString()
          });
        }
      }

      console.log(`[vapiHandlers.js] Making follow-up OpenAI call for callId ${callId} after tool execution.`);
      const followupResponse = await openai.chat.completions.create({
        model: OPENAI_MODEL,
        messages: messages,
        temperature: 0.7,
      });
      
      const followupReply = followupResponse.choices[0].message.content?.trim();
      if (followupReply) {
        messages.push({ role: "assistant", content: followupReply, timestamp: new Date().toISOString() });
        await saveSession(callId, messages);
        res.json({ assistant: { type: "text", text: followupReply } });
      } else {
        const ack = "Okay, I've noted that down.";
        messages.push({ role: "assistant", content: ack, timestamp: new Date().toISOString() });
        await saveSession(callId, messages);
        res.json({ assistant: { type: "text", text: ack } });
      }

    } else {
      const assistantReply = choice.content?.trim();
      if (assistantReply) {
        messages.push({ role: "assistant", content: assistantReply, timestamp: new Date().toISOString() });
        await saveSession(callId, messages);
        res.json({ assistant: { type: "text", text: assistantReply } });
      } else {
        console.warn(`[vapiHandlers.js] OpenAI response for callId ${callId} was empty or null.`);
        messages.push({ role: "assistant", content: "I'm not sure what to say to that.", timestamp: new Date().toISOString() });
        await saveSession(callId, messages);
        res.json({ assistant: { type: "text", text: "I'm not sure what to say to that." } });
      }
    }

  } catch (error) {
    console.error(`[vapiHandlers.js] Error in handleAssistantRequestLogic for callId ${callId}:`, error);
    res.status(500).json({ assistant: { type: "text", text: "I encountered an issue processing your request. Please try again in a moment." } });
  }
}

/**
 * Handles the 'call-end' event logic.
 * @async
 * @param {object} vapiMessage - The Vapi message object.
 * @param {import('express').Response} res - Express response object.
 */
export async function handleCallEndLogic(vapiMessage, res) {
  const callId = vapiMessage.call?.id || vapiMessage.callId || 'unknown_session_call_end';
  console.log(`[vapiHandlers.js] Handling call-end logic for callId: ${callId}.`);

  try {
    const sessionMessages = await loadSession(callId);
    let fullConversationTranscript = "";

    if (sessionMessages && sessionMessages.length > 0) {
      fullConversationTranscript = sessionMessages
        .filter(msg => msg.role === 'user' || msg.role === 'assistant') // Filter for user and assistant messages
        .map(msg => {
            let content = msg.content || "";
            if (msg.tool_calls) { // If assistant message has tool calls, it might not have direct content
                content += msg.tool_calls.map(tc => ` (Tool call: ${tc.function.name} with args ${tc.function.arguments})`).join('');
            }
            return `${msg.role.toUpperCase()}: ${content}`;
        })
        .join("\n");
    } else {
      console.log(`[vapiHandlers.js] No session messages found for callId ${callId} to build transcript for memory extraction.`);
      // Vapi might also send a full transcript directly in the 'call-end' payload.
      // Check for that as a fallback.
      const directTranscript = vapiMessage.fullTranscript || vapiMessage.transcript; // Or other potential paths
      if (directTranscript) {
          console.log(`[vapiHandlers.js] Using direct transcript from Vapi payload for callId ${callId}.`);
          fullConversationTranscript = directTranscript;
      } else {
          console.log(`[vapiHandlers.js] No transcript available from session or Vapi payload for callId ${callId}. Skipping memory extraction.`);
      }
    }
    
    if (fullConversationTranscript) {
      await extract_memories_at_end(callId, fullConversationTranscript);
    }
    
    console.log(`[vapiHandlers.js] Call ended processed for ${callId}.`);
    res.status(200).json({ message: "Call ended processed successfully by server." });
  } catch (error) {
    console.error(`[vapiHandlers.js] Error in handleCallEndLogic for callId ${callId}:`, error);
    res.status(500).json({ message: "Error processing call end on server." });
  }
}

/**
 * Handles function calls requested by Vapi (if Vapi itself makes function call requests to this server).
 * This is different from the AI model's tool_calls.
 * @async
 * @param {object} vapiMessage - The Vapi message object.
 * @param {import('express').Response} res - Express response object.
 */
export async function handleFunctionCallLogic(vapiMessage, res) {
    console.log("[vapiHandlers.js] Handling Vapi-initiated function-call logic:", JSON.stringify(vapiMessage, null, 2));
    const functionName = vapiMessage.functionCall?.name;
    const parameters = vapiMessage.functionCall?.parameters;

    try {
        let result = `Function ${functionName} called with params: ${JSON.stringify(parameters)} (placeholder server-side function result).`;
        // In a real scenario, the function execution itself might throw an error.
        // Example: if (functionName === "someRiskyFunction") throw new Error("Risky function failed");

        res.json({
            toolCallResult: {
                name: functionName,
                result: result
            }
        });
    } catch (error) {
        const callId = vapiMessage.call?.id || vapiMessage.callId || 'unknown_call_in_function_call_handler';
        console.error(`[vapiHandlers.js] Error in handleFunctionCallLogic for callId ${callId}, function ${functionName}:`, error);
        // Respond with an error message that Vapi can potentially speak or handle.
        // The exact format might depend on how Vapi expects errors from function calls.
        // This is a guess; consult Vapi docs.
        res.status(500).json({
            toolCallResult: {
                name: functionName,
                error: `Error executing function ${functionName}: ${error.message}`
            }
            // Alternatively, a more generic assistant response if this handler can generate speech:
            // assistant: { type: "text", text: `I encountered an error trying to use the function ${functionName}.` }
        });
    }
}

/**
 * Handles speech updates (interim transcripts).
 * @async
 * @param {object} vapiMessage - The Vapi message object.
 * @param {import('express').Response} res - Express response object.
 */
export async function handleSpeechUpdateLogic(vapiMessage, res) {
  res.status(200).send(); 
}

/**
 * Handles status updates from Vapi (e.g., ringing, answered).
 * @async
 * @param {object} vapiMessage - The Vapi message object.
 * @param {import('express').Response} res - Express response object.
 */
export async function handleStatusUpdateLogic(vapiMessage, res) {
  console.log("[vapiHandlers.js] Handling status-update:", vapiMessage.status, "Details:", JSON.stringify(vapiMessage, null, 2));
  res.status(200).send(); 
}

/**
 * Handles any other unclassified Vapi events.
 * @async
 * @param {object} vapiMessage - The Vapi message object.
 * @param {import('express').Response} res - Express response object.
 */
export async function handleOtherEventsLogic(vapiMessage, res) {
  console.warn("[vapiHandlers.js] Handling unclassified event type:", vapiMessage.type, "Payload:", JSON.stringify(vapiMessage, null, 2));
  res.status(200).json({ message: "Generic event received and acknowledged by server." });
}
