/* ==========================================================================
    ChatGPT Interaction Logic
   ========================================================================== */
(() => {

    class Chat {
        constructor() {
            /* ───────────── DOM Elements ───────────── */
            this.sendBtn = document.getElementById('sendBtn');
            this.userMessageInput = document.getElementById('userMessage');
            this.chatMessages = document.getElementById('chatMessages');

            /* ───────────── Initialization ───────────── */
            this.setupEventListeners();
        }

        /* ====================================================================
           Event Listeners
           ==================================================================== */
        setupEventListeners() {

            // Send message when the send button is clicked
            this.sendBtn.addEventListener('click', () => this.sendMessage());

            // Send message when Enter key is pressed in the input box (if the button is not disabled)
            this.userMessageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !this.sendBtn.disabled) {
                    this.sendMessage();
                }
            });

             // Initial greeting message
            this.displayMessage('Hello! How can I assist you with Python today?');

        }


        /* ====================================================================
           Message Handling
           ==================================================================== */    
        async sendMessage() {
            const message = this.userMessageInput.value.trim();
            if (!message) return;

            // Display user message
            this.displayMessage(
                "You: " + message, 
                'user-message'
            );
            
            // Clear the input box and disable input and button (to prevent duplicate actions)
            this.userMessageInput.value = '';
            this.sendBtn.disabled = true;
            this.userMessageInput.disabled = true;

            // Show loading indicator
            this.showLoading();

            try {
                // Send request to the backend
                const response = await fetch('/chatgpt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });

                if (response.status === 429) {
                    throw new Error(`You have reached the daily usage limit!`);
                }

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }


                const result = await response.json();     

                if (result.status === 'success') {
                    this.displayMessage(result.reply, 'chatgpt-message', true);
                } else {
                    throw new Error(result.message || 'Unknown error occurred');
                }

            } catch (error) {
                console.error('Error:', error);
                this.displayMessage("Error: " + error.message, 'error-message');

            } finally {
                this.hideLoading();
                this.sendBtn.disabled = false;
                this.userMessageInput.disabled = false;
            }
        }


         /* ====================================================================
           UI Rendering Helpers
           ==================================================================== */
        /**
         * // Display message in the chat window
         * @param {string} message // Displayed text content
         * @param {string} className // Class name used to distinguish message types
         * @param {boolean} isHTML // Whether to insert the message as HTML
         */
        displayMessage(message, className, isHTML = false) {
            const msgElem = document.createElement('div');
            msgElem.className = className;

            if (isHTML) {
                msgElem.innerHTML = message;
            } else {
                msgElem.textContent = message;
            }

            this.chatMessages.appendChild(msgElem);
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }

        /**
         * Show "ChatGPT is thinking..." loading indicator
         */
        showLoading() {
            const loadingElem = document.createElement('div');
            loadingElem.id = 'loadingIndicator';
            loadingElem.textContent = "AI is thinking...";
            loadingElem.className = 'loading-message';

            this.chatMessages.appendChild(loadingElem);
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }

        /**
         * Hide loading indicator
         */
        hideLoading() {
            const loadingElem = document.getElementById('loadingIndicator');
            if (loadingElem) {
                loadingElem.remove();
            }
        }
    }

    /* =========================================================================
       App Bootstrap
       ========================================================================= */
    document.addEventListener('DOMContentLoaded', () => {
        new Chat();
    });
    
})();



