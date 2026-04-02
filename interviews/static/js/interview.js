// AI Interview System - JavaScript Implementation
// Handles chat interface, API communication, and UI updates

let interviewStartTime = null;
let timerInterval = null;
let interviewMode = null;  // 'random' or 'single'
let selectedTopic = null;   // For single topic mode
let interviewStage = 'initial';  // Track current stage: initial, mode_selection, topic_selection, started

// Get CSRF token for Django security
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Start timer
function startTimer() {
    interviewStartTime = new Date();
    timerInterval = setInterval(updateTimer, 1000);
}

// Update timer display
function updateTimer() {
    if (!interviewStartTime) return;
    
    const now = new Date();
    const elapsed = Math.floor((now - interviewStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    
    document.getElementById('timer').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Add message to chat with typing effect
function addMessage(content, isUser = false, showButtons = false, buttonType = null) {
    const chatBox = document.getElementById('chatBox');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user-message' : 'ai-message'}`;
    
    if (isUser) {
        messageDiv.innerHTML = `
            <div class="avatar">👤</div>
            <div class="message-content">
                <p>${content.replace(/\n/g, '<br>')}</p>
            </div>
        `;
    } else {
        let messageHTML = `
            <div class="avatar">🤖</div>
            <div class="message-content">
                <p>${content.replace(/\n/g, '<br>')}</p>
            </div>
        `;
        messageDiv.innerHTML = messageHTML;
    }
    
    chatBox.appendChild(messageDiv);
    
    // Add option buttons if needed
    if (showButtons && buttonType) {
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = 'display: flex; gap: 10px; margin: 15px 0 15px 44px; flex-wrap: wrap;';
        
        if (buttonType === 'mode') {
            buttonContainer.innerHTML = `
                <button class="option-btn" onclick="selectMode('random')" style="padding: 12px 24px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.3s ease;">
                    📝 Random Topics
                </button>
                <button class="option-btn" onclick="selectMode('single')" style="padding: 12px 24px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.3s ease;">
                    🎯 Single Topic
                </button>
            `;
        } else if (buttonType === 'topic') {
            buttonContainer.innerHTML = `
                <button class="option-btn" onclick="selectTopic('SQL')" style="padding: 12px 24px; background: #8b5cf6; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.3s ease;">
                    💾 SQL
                </button>
                <button class="option-btn" onclick="selectTopic('Python')" style="padding: 12px 24px; background: #f59e0b; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.3s ease;">
                    🐍 Python
                </button>
            `;
        }
        
        chatBox.appendChild(buttonContainer);
    }
    
    chatBox.scrollTop = chatBox.scrollHeight;

    // Add a subtle animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';
    setTimeout(() => {
        messageDiv.style.transition = 'all 0.5s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 100);
}

// Handle mode selection
function selectMode(mode) {
    interviewMode = mode;
    interviewStage = 'mode_selected';
    
    // Remove all option buttons
    document.querySelectorAll('.option-btn').forEach(btn => btn.disabled = true);
    
    // Add user's selection as message
    const modeText = mode === 'random' ? '📝 Random Topics' : '🎯 Single Topic';
    addMessage(modeText, true);
    
    // Update PATH display
    document.getElementById('pathDisplay').textContent = (mode === 'random' ? 'RANDOM TOPICS' : 'SINGLE TOPIC');
    
    setTimeout(() => {
        if (mode === 'random') {
            // For random mode, ask for role and proceed with existing flow
            addMessage("Great! You've selected Random Topics mode. 🎲\n\nThis mode will ask you questions from various topics to test your overall knowledge.\n\nWhat role are you preparing for? (e.g., Software Engineer, Data Scientist, Full Stack Developer)");
            interviewStage = 'random_role_input';
        } else {
            // For single topic mode, show topic selection
            addMessage("Excellent! You've selected Single Topic mode. 🎯\n\nChoose a topic you want to focus on:", false, true, 'topic');
            interviewStage = 'topic_selection';
        }
    }, 1000);
}

// Handle topic selection
function selectTopic(topic) {
    selectedTopic = topic;
    interviewStage = 'topic_selected';
    
    // Remove all option buttons
    document.querySelectorAll('.option-btn').forEach(btn => btn.disabled = true);
    
    // Add user's selection as message
    const topicEmoji = topic === 'SQL' ? '💾' : '🐍';
    addMessage(`${topicEmoji} ${topic}`, true);
    
    setTimeout(() => {
        addMessage(`Perfect! Let's start your ${topic} interview! 🚀\n\nI'll ask you 5 questions focused on ${topic}. Take your time to answer each question thoroughly.\n\nLet me prepare your first question...`);
        
        // Update meta information - Single Topic mode doesn't need role
        document.getElementById('roleDisplay').textContent = 'N/A';
        document.getElementById('topicsDisplay').textContent = topic.toUpperCase();
        
        startTimer();
        interviewStage = 'interview_started';
        
        // Call backend to start interview and get first question
        startSingleTopicInterview(topic);
    }, 1000);
}

// Start Single Topic Interview
async function startSingleTopicInterview(topic) {
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch('/interview-api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ 
                message: 'START_SINGLE_TOPIC',
                mode: 'single',
                topic: topic,
                stage: 'interview_started'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Add first question from AI
        setTimeout(() => {
            addMessage(data.reply);
        }, 1000);

    } catch (error) {
        console.error('Error:', error);
        addMessage('❌ Sorry, there was an error starting the interview. Please refresh and try again.', false);
    }
}

// Send message to AI
async function sendMessage() {
    const answerInput = document.getElementById('answerInput');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    const message = answerInput.value.trim();
    if (!message) return;

    // Handle "go" command
    if (message.toLowerCase() === 'go' && interviewStage === 'initial') {
        addMessage(message, true);
        answerInput.value = '';
        
        setTimeout(() => {
            addMessage("Welcome! Let's get started with your interview preparation. 🎯\n\nChoose your interview mode:", false, true, 'mode');
            interviewStage = 'mode_selection';
        }, 500);
        return;
    }

    // Handle random mode role input
    if (interviewStage === 'random_role_input') {
        addMessage(message, true);
        answerInput.value = '';
        
        const role = message;
        document.getElementById('roleDisplay').textContent = role.toUpperCase();
        
        setTimeout(() => {
            addMessage(`Great! You're preparing for a ${role} position. 💼\n\nNow, which topics would you like to cover? (e.g., Python, JavaScript, DSA, System Design)`);
            interviewStage = 'random_topics_input';
        }, 1000);
        return;
    }

    // Handle random mode topics input
    if (interviewStage === 'random_topics_input') {
        addMessage(message, true);
        answerInput.value = '';
        
        const topics = message;
        document.getElementById('topicsDisplay').textContent = topics.toUpperCase();
        
        setTimeout(() => {
            addMessage(`Perfect! I'll prepare questions on ${topics}. 🎯\n\nLet's begin your interview!\n\n📌 Question 1: [Question will appear here based on your topics]`);
            startTimer();
            interviewStage = 'interview_started';
        }, 1000);
        return;
    }

    // Add user message to chat
    addMessage(message, true);
    answerInput.value = '';
    answerInput.style.height = 'auto'; // Reset height

    // Show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    loadingIndicator.style.display = 'flex';

    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch('/interview-api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ 
                message: message,
                mode: interviewMode,
                topic: selectedTopic,
                stage: interviewStage
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Add AI response to chat with delay for realism
        setTimeout(() => {
            addMessage(data.reply);
            updateInterviewState(message, data.reply);
        }, 1000);

    } catch (error) {
        console.error('Error:', error);
        addMessage('❌ Sorry, there was an error processing your request. Please check your connection and try again.', false);
    } finally {
        // Hide loading
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Send Message';
            loadingIndicator.style.display = 'none';
            answerInput.focus();
        }, 1000);
    }
}

// Update interview state based on responses
function updateInterviewState(userMessage, aiResponse) {
    const statusBadge = document.getElementById('statusBadge');

    // Check if interview started
    if (interviewStage === 'interview_started') {
        // Check if interview completed
        if (aiResponse.includes('Interview Completed')) {
            statusBadge.textContent = 'COMPLETED';
            statusBadge.style.background = '#e0e7ff';
            statusBadge.style.color = '#4f46e5';
            clearInterval(timerInterval);
            
            // Show completion panel with animation
            setTimeout(() => {
                const scorePanel = document.getElementById('scorePanel');
                const finalScore = document.getElementById('finalScore');
                
                // Extract final score from response
                const scoreMatch = aiResponse.match(/Final Score: ([\d.]+)\/10/);
                if (scoreMatch) {
                    finalScore.textContent = scoreMatch[1];
                }
                
                scorePanel.style.display = 'block';
                scorePanel.scrollIntoView({ behavior: 'smooth' });
            }, 1500);
        }
    }
}

// Restart interview
function restartInterview() {
    if (confirm('Are you sure you want to start a new interview? This will clear the current session.')) {
        location.reload();
    }
}

// Auto-resize textarea
function autoResize() {
    const textarea = document.getElementById('answerInput');
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Initialize interview interface
function initializeInterview() {
    const answerInput = document.getElementById('answerInput');
    const submitBtn = document.getElementById('submitBtn');

    // Event listeners
    submitBtn.addEventListener('click', sendMessage);
    
    answerInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    answerInput.addEventListener('input', autoResize);

    // Auto-focus on input and show welcome animation
    answerInput.focus();
    
    // Add initial animation to the first message
    const firstMessage = document.querySelector('.chat-message');
    if (firstMessage) {
        firstMessage.style.opacity = '0';
        firstMessage.style.transform = 'translateY(20px)';
        setTimeout(() => {
            firstMessage.style.transition = 'all 0.5s ease';
            firstMessage.style.opacity = '1';
            firstMessage.style.transform = 'translateY(0)';
        }, 500);
    }

    // Add some visual feedback for user experience
    answerInput.addEventListener('focus', function() {
        this.parentElement.style.transform = 'translateY(-2px)';
        this.parentElement.style.boxShadow = '0 4px 12px rgba(33, 150, 243, 0.2)';
    });

    answerInput.addEventListener('blur', function() {
        this.parentElement.style.transform = 'translateY(0)';
        this.parentElement.style.boxShadow = 'none';
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeInterview);