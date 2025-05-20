import OpenAI from 'openai';
import 'dotenv/config'; // Ensure dotenv is configured

/**
 * OpenAI API client.
 *
 * @type {OpenAI}
 */
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export default openai;
