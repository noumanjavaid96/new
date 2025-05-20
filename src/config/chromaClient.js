import { ChromaClient } from '@chroma/chromadb';
import 'dotenv/config';

/**
 * ChromaDB client instance.
 * @type {ChromaClient}
 */
const chromaPath = process.env.CHROMA_DB_PATH || './mem_store';
console.log(`[chromaClient] Initializing ChromaDB client with path: ${chromaPath}`);
const client = new ChromaClient({
  path: chromaPath,
});

/**
 * Retrieves an existing collection or creates a new one if it doesn't exist.
 *
 * @async
 * @param {string} [collectionName="memories"] - The name of the collection.
 * @param {object} [metadata={"hnsw:space":"cosine"}] - Metadata for the collection creation.
 * @returns {Promise<import('@chroma/chromadb').Collection>} The collection object.
 * @throws {Error} If there's an issue getting or creating the collection.
 */
export async function getOrCreateCollection(
  collectionName = "memories",
  metadata = { "hnsw:space": "cosine" }
) {
  try {
    const collection = await client.getOrCreateCollection({
      name: collectionName,
      metadata: metadata,
    });
    console.log(`Collection "${collectionName}" retrieved or created successfully.`);
    return collection;
  } catch (error) {
    console.error(`Error getting or creating collection "${collectionName}":`, error);
    throw new Error(`Failed to get or create collection: ${error.message}`);
  }
}

export default client;
