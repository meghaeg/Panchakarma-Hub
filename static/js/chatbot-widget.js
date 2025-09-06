// Chatbot Widget JavaScript

class AyurvedaChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.isDragging = false;
        this.offset = { x: 0, y: 0 };
        this.init();
    }

    init() {
        // Create widget elements
        this.createWidgetElements();
        
        // Add event listeners
        this.addEventListeners();
        
        // Initialize with welcome message
        this.addMessage('assistant', 'Namaste! 🌿 Ask me anything about Ayurveda or Panchakarma therapies.');
    }

    createWidgetElements() {
        // Create main container
        this.widgetContainer = document.createElement('div');
        this.widgetContainer.className = 'ayurveda-chatbot-widget';
        document.body.appendChild(this.widgetContainer);

        // Create chat icon
        this.chatIcon = document.createElement('div');
        this.chatIcon.className = 'chat-icon';
        this.widgetContainer.appendChild(this.chatIcon);

        // Create chat window
        this.chatWindow = document.createElement('div');
        this.chatWindow.className = 'chat-window';
        this.chatWindow.style.display = 'none';
        this.widgetContainer.appendChild(this.chatWindow);

        // Create chat header
        const chatHeader = document.createElement('div');
        chatHeader.className = 'chat-header';
        chatHeader.innerHTML = `
            <h3><i class="fas fa-leaf"></i> Ayurveda Chatbot</h3>
            <button class="close-btn"><i class="fas fa-times"></i></button>
        `;
        this.chatWindow.appendChild(chatHeader);

        // Create messages container
        this.messagesContainer = document.createElement('div');
        this.messagesContainer.className = 'chat-messages';
        this.chatWindow.appendChild(this.messagesContainer);

        // Create input area
        const inputArea = document.createElement('div');
        inputArea.className = 'chat-input';
        inputArea.innerHTML = `
            <input type="text" placeholder="Type your message..." id="chat-input-field">
            <button class="send-btn"><i class="fas fa-paper-plane"></i></button>
        `;
        this.chatWindow.appendChild(inputArea);

        // Store input field reference
        this.inputField = inputArea.querySelector('#chat-input-field');
    }

    addEventListeners() {
        // Close chat window when close button is clicked
        this.chatWindow.querySelector('.close-btn').addEventListener('click', () => this.toggleChatWindow(false));

        // Send message when send button is clicked
        this.chatWindow.querySelector('.send-btn').addEventListener('click', () => this.sendMessage());

        // Send message when Enter key is pressed
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Make widget draggable
        this.setupDraggable();
    }
    
    setupDraggable() {
        // Make chat icon draggable
        this.chatIcon.addEventListener('mousedown', (e) => this.startDrag(e));
        document.addEventListener('mousemove', (e) => this.drag(e));
        document.addEventListener('mouseup', (e) => this.endDrag(e));
        
        // Touch support for mobile devices
        this.chatIcon.addEventListener('touchstart', (e) => this.startDrag(e.touches[0]));
        document.addEventListener('touchmove', (e) => this.drag(e.touches[0]));
        document.addEventListener('touchend', (e) => this.endDrag());
    }
    
    startDrag(e) {
        // Store the initial position to determine if this was a click or drag
        this.initialPosition = {
            x: e.clientX,
            y: e.clientY
        };
        
        this.isDragging = true;
        
        // Calculate the offset of the mouse pointer from the top-left corner of the widget
        const rect = this.widgetContainer.getBoundingClientRect();
        this.offset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        // Prevent default behavior to avoid text selection during drag
        e.preventDefault();
    }
    
    drag(e) {
        if (!this.isDragging) return;
        
        // Calculate new position
        const x = e.clientX - this.offset.x;
        const y = e.clientY - this.offset.y;
        
        // Apply new position with boundaries to keep widget on screen
        const maxX = window.innerWidth - this.widgetContainer.offsetWidth;
        const maxY = window.innerHeight - this.widgetContainer.offsetHeight;
        
        this.widgetContainer.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
        this.widgetContainer.style.bottom = 'auto';
        this.widgetContainer.style.right = 'auto';
        this.widgetContainer.style.top = `${Math.max(0, Math.min(y, maxY))}px`;
        
        // Prevent default to avoid text selection during drag
        e.preventDefault();
    }
    
    endDrag(e) {
        if (this.isDragging) {
            // If the mouse hasn't moved much, treat it as a click instead of a drag
            if (this.initialPosition) {
                const moveX = Math.abs(e?.clientX - this.initialPosition.x) || 0;
                const moveY = Math.abs(e?.clientY - this.initialPosition.y) || 0;
                
                // If movement was minimal, treat as a click on the chat icon
                if (moveX < 5 && moveY < 5 && e?.target === this.chatIcon) {
                    this.toggleChatWindow();
                }
            }
            
            this.isDragging = false;
            this.initialPosition = null;
        }
    }

    toggleChatWindow(forceState = null) {
        this.isOpen = forceState !== null ? forceState : !this.isOpen;
        this.chatWindow.style.display = this.isOpen ? 'flex' : 'none';
        
        if (this.isOpen) {
            this.inputField.focus();
        }
    }

    addMessage(role, content) {
        // Add message to state
        this.messages.push({ role, content });

        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${role}`;
        messageEl.innerHTML = `<div class="message-content">${content}</div>`;
        
        // Add to messages container
        this.messagesContainer.appendChild(messageEl);
        
        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;

        // Clear input field
        this.inputField.value = '';

        // Add user message to chat
        this.addMessage('user', message);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send message to backend via proxy
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: this.messages
                })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();

            // Add assistant response
            if (data.error) {
                this.addMessage('assistant', 'Sorry, I encountered an error. Please try again later.');
            } else {
                this.addMessage('assistant', data.reply);
            }
        } catch (error) {
            console.error('Error:', error);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add error message
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again later.');
        }
    }

    showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        
        const messageEl = document.createElement('div');
        messageEl.className = 'chat-message assistant';
        messageEl.appendChild(typingIndicator);
        messageEl.id = 'typing-indicator';
        
        this.messagesContainer.appendChild(messageEl);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Initialize the widget when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    new AyurvedaChatbotWidget();
});