document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialization
    const VAPI_ASSISTANT_ID = '8d123243-302b-4eaa-8d62-a1c6afebb5e3';
    const VAPI_PUBLIC_API_KEY = 'a397b258-4036-4063-829f-6800f42c70b6';

    // This assumes Vapi class is globally available.
    // In a real-world scenario with a bundler, you'd use: import Vapi from '@vapi-ai/web';
    if (typeof Vapi === 'undefined') {
        console.error("Vapi SDK is not loaded. Please ensure it's included in your project.");
        alert("Vapi SDK not found. The app cannot function.");
        return;
    }
    const vapi = new Vapi(VAPI_PUBLIC_API_KEY);

    // 2. DOM Element References
    const toggleCallButton = document.getElementById('toggleCallButton');
    const callStatus = document.getElementById('callStatus');
    const interimSpeech = document.getElementById('interimSpeech');
    const transcriptArea = document.getElementById('transcriptArea');

    // 3. State Variable
    let isCallActive = false;

    // 4. Helper Functions
    function updateStatus(text) {
        callStatus.textContent = "Status: " + text;
    }

    function updateInterimSpeech(text) {
        interimSpeech.textContent = text ? "Listening: " + text : "";
    }

    function appendToTranscript(speaker, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('transcript-message');
        messageDiv.classList.add(speaker.toLowerCase() === 'you' || speaker.toLowerCase() === 'user' ? 'user' : 'assistant');
        if (speaker.toLowerCase() === 'system') {
             messageDiv.classList.add('system'); // Could add specific system styling
        }


        const speakerLabel = document.createElement('span');
        speakerLabel.classList.add('speaker');
        speakerLabel.textContent = speaker + ":";

        const messageText = document.createElement('span');
        messageText.textContent = text;

        messageDiv.appendChild(speakerLabel);
        messageDiv.appendChild(messageText);
        transcriptArea.appendChild(messageDiv);

        transcriptArea.scrollTop = transcriptArea.scrollHeight;
    }

    // 5. Vapi SDK Event Handlers
    vapi.on('call-start', () => {
        console.log("Vapi: call-start event received");
        isCallActive = true;
        updateStatus("Call active");
        toggleCallButton.textContent = "End Call";
        toggleCallButton.classList.add('active');
        appendToTranscript("System", "Call started.");
    });

    vapi.on('call-end', () => {
        console.log("Vapi: call-end event received");
        isCallActive = false;
        updateStatus("Call ended");
        toggleCallButton.textContent = "Start Call";
        toggleCallButton.classList.remove('active');
        updateInterimSpeech("");
        appendToTranscript("System", "Call ended.");
    });

    vapi.on('message', (message) => {
        console.log("Vapi message received:", JSON.stringify(message, null, 2));

        if (message.type === 'transcript' && message.transcriptType === 'final' && message.role === 'user') {
            appendToTranscript("You", message.transcript);
        } else if (message.type === 'message' && message.role === 'assistant') {
            // Assuming assistant's text is in message.message for older SDK versions or a simple text message
            // For newer SDKs, it might be message.content or structured within message.message
            let assistantText = "";
            if (typeof message.message === 'string') {
                assistantText = message.message;
            } else if (typeof message.message === 'object' && message.message.type === 'text') { // Common structure
                assistantText = message.message.text;
            } else if (message.content && typeof message.content === 'string') { // Another possible structure
                 assistantText = message.content;
            } else if (message.message && message.message.payload && typeof message.message.payload === 'string') { // Vapi server format
                 assistantText = message.message.payload;
            } else {
                 console.warn("Received assistant message with unknown structure:", message);
                 assistantText = JSON.stringify(message.message || message); // Fallback
            }
            appendToTranscript("Assistant", assistantText);
        } else if (message.type === 'function-call') {
            // Optional: Display that a function is being called
            appendToTranscript("System", `Function call initiated: ${message.functionCall?.name || 'unknown function'}`);
            console.log("Function call details:", message.functionCall);
        }
        updateInterimSpeech(""); // Clear interim speech on final message from user or assistant
    });

    vapi.on('speech-update', (payload) => {
        // console.log("Vapi: speech-update payload:", payload); // Can be very verbose
        if (payload.transcriptType === 'interim' && payload.transcript) {
            updateInterimSpeech(payload.transcript);
        }
    });

    vapi.on('error', (error) => {
        console.error("Vapi Error:", error);
        const errorMessage = error.message || (typeof error === 'object' ? JSON.stringify(error) : String(error));
        updateStatus("Error: " + errorMessage);
        appendToTranscript("System", "Error: " + errorMessage);

        if (isCallActive) {
            isCallActive = false;
            toggleCallButton.textContent = "Start Call";
            toggleCallButton.classList.remove('active');
        }
    });

    vapi.on('volume-level', (level) => {
        // Optional: can be used for mic activity visualization
        // console.log("Volume level:", level);
    });

    // 6. Button Event Listener
    toggleCallButton.addEventListener('click', () => {
        if (isCallActive) {
            vapi.stop();
        } else {
            transcriptArea.innerHTML = ""; // Clear previous transcript
            updateInterimSpeech("");
            updateStatus("Connecting...");
            vapi.start({
                assistant: VAPI_ASSISTANT_ID,
                // Other Vapi start options can be added here if needed, e.g.:
                // voice: "...", 
                // firstMessage: "Hello there!",
                // serverUrl: "your_custom_webhook_url_if_not_set_on_assistant_level"
            });
        }
    });

    // 7. Initial UI State
    updateStatus("Idle");
    updateInterimSpeech("");

    // Initial log to confirm script loaded
    console.log("Vapi Assistant UI script loaded and initialized.");
});
