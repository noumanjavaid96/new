import { v4 as uuidv4 } from 'uuid';
import { openai, chroma, getOrCreateCollection } from '../config/index.js';

const DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002";
const EMBEDDING_DIMENSION = 1536; // For text-embedding-ada-002

/**
 * Generates an embedding for the given text using OpenAI's API.
 *
 * @async
 * @param {string} text - The text to embed.
 * @param {string} [model=DEFAULT_EMBEDDING_MODEL] - The embedding model to use.
 * @returns {Promise<number[] | null>} The embedding vector, or null if an error occurs.
 *                                      Returns a zero vector on critical errors.
 */
export async function getEmbedding(text, model = DEFAULT_EMBEDDING_MODEL) {
  if (!text || typeof text !== 'string') {
    console.warn("getEmbedding: Input text is invalid. Returning null.");
    return null;
  }
  try {
    const response = await openai.embeddings.create({
      model: model,
      input: text.replace(/\n/g, ' '), // API recommendation: replace newlines
    });
    if (response.data && response.data.length > 0 && response.data[0].embedding) {
      return response.data[0].embedding;
    }
    console.warn("getEmbedding: No embedding found in OpenAI response. Returning null.");
    return null;
  } catch (error) {
    console.error(`Error getting embedding from OpenAI (model: ${model}):`, error.message);
    // Fallback to a zero vector of the correct dimension
    console.error(`Error getting embedding from OpenAI (model: ${model}) for text (first 50 chars): "${text.substring(0,50)}..."`, error.message);
    // Fallback to a zero vector of the correct dimension
    return Array(EMBEDDING_DIMENSION).fill(0);
  }
}

/**
 * Saves a single memory vector to ChromaDB.
 *
 * @async
 * @param {string} memory - The memory text to save.
 * @param {string} discussionId - The ID of the discussion this memory belongs to.
 * @returns {Promise<boolean>} True if successful, false otherwise.
 */
export async function saveVectorMemory(memory, discussionId) {
  if (!memory || typeof memory !== 'string' || memory.trim() === "" || memory.trim().toUpperCase() === "NOTHING_TO_REMEMBER") {
    console.log("saveVectorMemory: No valid memory provided to save.");
    return false;
  }

  try {
    const collection = await getOrCreateCollection("memories");
    const embedding = await getEmbedding(memory);

    if (!embedding) {
      console.error("saveVectorMemory: Failed to generate embedding. Memory not saved.");
      return false;
    }

    const id = uuidv4();
    const timestamp = new Date().toISOString();

    await collection.add({
      ids: [id],
      embeddings: [embedding],
      metadatas: [{ discussionId, timestamp, type: "memory" }],
      documents: [memory],
    });
    console.log(`Memory saved with ID: ${id} to collection "memories".`);
    return true;
  } catch (error) {
    console.error(`Error saving vector memory for discussionId "${discussionId}" (memory snippet: "${memory.substring(0,50)}..."):`, error);
    return false;
  }
}

/**
 * Saves multiple memories in a batch to ChromaDB.
 *
 * @async
 * @param {string[]} memories - An array of memory texts to save.
 * @param {string} discussionId - The ID of the discussion these memories belong to.
 * @returns {Promise<boolean>} True if at least one memory was attempted to be saved (further check logs for individual successes/failures), false if no valid memories provided.
 */
export async function batchSaveMemories(memories, discussionId) {
  if (!memories || !Array.isArray(memories) || memories.length === 0) {
    console.log("batchSaveMemories: No memories provided to save.");
    return false;
  }

  const validMemories = memories.filter(
    (mem) => mem && typeof mem === 'string' && mem.trim() !== "" && mem.trim().toUpperCase() !== "NOTHING_TO_REMEMBER"
  );

  if (validMemories.length === 0) {
    console.log("batchSaveMemories: No valid memories after filtering.");
    return false;
  }

  try {
    const collection = await getOrCreateCollection("memories");
    const embeddings = await Promise.all(validMemories.map(mem => getEmbedding(mem)));

    const itemsToAdd = {
      ids: [],
      embeddings: [],
      metadatas: [],
      documents: [],
    };

    const timestamp = new Date().toISOString();
    for (let i = 0; i < validMemories.length; i++) {
      if (embeddings[i]) { // Only add if embedding was successful
        itemsToAdd.ids.push(uuidv4());
        itemsToAdd.embeddings.push(embeddings[i]);
        itemsToAdd.metadatas.push({ discussionId, timestamp, type: "memory_batch_item" });
        itemsToAdd.documents.push(validMemories[i]);
      } else {
        console.warn(`batchSaveMemories: Failed to generate embedding for memory: "${validMemories[i]}". It will be skipped.`);
      }
    }
    
    if (itemsToAdd.ids.length === 0) {
        console.log("batchSaveMemories: No memories could be processed after attempting embedding generation.");
        return false;
    }

    await collection.add(itemsToAdd);
    console.log(`Batch saved ${itemsToAdd.ids.length} memories to collection "memories".`);
    return true;
  } catch (error) {
    console.error(`Error batch saving memories for discussionId "${discussionId}":`, error);
    return false;
  }
}

/**
 * Retrieves relevant vector memories from ChromaDB based on a query.
 *
 * @async
 * @param {string} query - The query text to search for.
 * @param {number} [n=5] - The number of results to retrieve.
 * @returns {Promise<string[]>} An array of relevant memory documents, or an empty array if none found or an error occurs.
 */
export async function retrieveVectorMemories(query, n = 5) {
  if (!query || typeof query !== 'string') {
    console.warn("retrieveVectorMemories: Query is invalid. Returning empty array.");
    return [];
  }

  try {
    const collection = await getOrCreateCollection("memories");

    // Check if collection is empty or has few items
    const count = await collection.count();
    if (count === 0) {
      console.log("retrieveVectorMemories: Collection is empty. No memories to retrieve.");
      return [];
    }
    
    const queryEmbedding = await getEmbedding(query);
    if (!queryEmbedding) {
      console.error("retrieveVectorMemories: Failed to generate query embedding. Cannot retrieve memories.");
      return [];
    }

    const results = await collection.query({
      queryEmbeddings: [queryEmbedding],
      nResults: Math.min(n, count), // Ensure nResults is not greater than count
      // include: ["documents", "metadatas", "distances"] // Optional: include more data
    });

    // ChromaDB JS client returns results.documents as an array of arrays
    // Each inner array corresponds to a query embedding. We have only one.
    if (results.documents && results.documents.length > 0 && results.documents[0].length > 0) {
      // Filter out any null or undefined documents just in case
      return results.documents[0].filter(doc => doc != null);
    } else {
      console.log("retrieveVectorMemories: No relevant memories found for the query.");
      return [];
    }
  } catch (error) {
    console.error("Error retrieving vector memories:", error);
    return [];
  }
}
