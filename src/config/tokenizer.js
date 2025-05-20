import { get_encoding } from 'tiktoken';

/**
 * Tiktoken tokenizer instance.
 * Uses "cl100k_base" encoding, suitable for gpt-3.5-turbo and gpt-4 models.
 *
 * @type {import('tiktoken').Tiktoken}
 */
const tokenizer = get_encoding("cl100k_base");

export default tokenizer;
