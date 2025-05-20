import 'dotenv/config'; // Ensure dotenv is configured at the very top
import express from 'express';
import {
  handleAssistantRequestLogic,
  handleCallStartLogic,
  handleCallEndLogic,
  handleFunctionCallLogic,
  handleSpeechUpdateLogic,
  handleStatusUpdateLogic,
  handleOtherEventsLogic,
} from './routes/vapiHandlers.js';

const app = express();
const port = process.env.PORT || 3000;

// Middleware to parse JSON request bodies
app.use(express.json());

// Simple root route for basic server check
app.get('/', (req, res) => {
  res.send('Server is running. Vapi webhook is at /vapi-webhook');
});

// Vapi Webhook Router
const vapiRouter = express.Router();

// Single POST endpoint for all Vapi events
vapiRouter.post('/', async (req, res) => {
  const { message } = req.body;

  // Log the entire payload to help understand its structure
  console.log("Received Vapi Webhook. Full Payload:", JSON.stringify(req.body, null, 2));

  if (!message || !message.type) {
    console.warn("Unknown payload structure or missing message.type:", req.body);
    // Vapi might expect a 200 OK even for errors if it's to avoid retries,
    // but sending a 400 is more standard for bad requests.
    // Adjust if Vapi's retry behavior is aggressive.
    return res.status(400).json({ error: "Unknown payload structure or missing message.type" });
  }

  console.log(`Processing Vapi message type: ${message.type}`);

  // Switch on message type
  // The actual Vapi message types might differ. These are based on common patterns and the provided examples.
  // Refer to Vapi documentation for the definitive list of server-side webhook event types.
  try {
    switch (message.type) {
      case 'assistant-request':
        await handleAssistantRequestLogic(message, res);
        break;
      case 'call-start': // This might be the first 'assistant-request' or a dedicated event.
        await handleCallStartLogic(message, res);
        break;
      case 'call-end': // Or 'hangup', 'end-of-call-report'
        await handleCallEndLogic(message, res);
        break;
      case 'function-call': // If Vapi can trigger function calls on your server
        await handleFunctionCallLogic(message, res);
        break;
      case 'speech-update': // For interim transcripts
        await handleSpeechUpdateLogic(message, res);
        break;
      case 'status-update': // e.g., ringing, answered, etc.
        await handleStatusUpdateLogic(message, res);
        break;
      // Add other cases as per Vapi documentation
      // e.g., 'user-interrupted', 'error', 'tool-calls-result' (if you send tool results to Vapi)
      default:
        console.warn(`Unhandled message type: ${message.type}`);
        await handleOtherEventsLogic(message, res); // Generic handler for unclassified types
    }
  } catch (error) {
    console.error(`Error processing message type ${message.type}:`, error);
    // It's crucial to still send a response to Vapi to acknowledge receipt,
    // even if an internal error occurred.
    res.status(500).json({ error: "Internal server error while processing event." });
  }
});

// Mount the router
app.use('/vapi-webhook', vapiRouter);

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
  console.log(`Vapi webhook endpoint: http://localhost:${port}/vapi-webhook`);
});

// Generic Express error handler middleware (should be the last piece of middleware)
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  console.error('[Unhandled Express Error] ===>', err.stack || err);
  
  // Check if headers have already been sent
  if (res.headersSent) {
    return next(err); // Delegate to default Express error handler
  }
  
  res.status(err.status || 500).json({ 
    error: {
      message: err.message || 'Internal Server Error',
      // Optionally include stack in development
      stack: process.env.NODE_ENV === 'development' && err.stack ? err.stack : undefined
    }
  });
});
