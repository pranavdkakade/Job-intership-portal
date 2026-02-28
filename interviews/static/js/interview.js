// AI Interview System - JavaScript Implementation
// Handles chat interface, API communication, and UI updates

let interviewStartTime = null;
let timerInterval = null;

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
function addMessage(content, isUser = false) {
    const chatBox = document.getElementById('chatBox');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user-message' : 'ai-message'}`;
    
    if (isUser) {
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-label">CANDIDATE</span>
                <span class="candidate-badge">ME</span>
            </div>
            <div class="message-content">
                <p>${content.replace(/\n/g, '<br>')}</p>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="avatar">R</div>
                <span class="message-label">INTERVIEWER</span>
            </div>
            <div class="message-content">
                <p>${content.replace(/\n/g, '<br>')}</p>
            </div>
        `;
    }
    
    chatBox.appendChild(messageDiv);
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

// Send message to AI
async function sendMessage() {
    const answerInput = document.getElementById('answerInput');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    const message = answerInput.value.trim();
    if (!message) return;

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
                'X-CSRFToken': csrftoken, // Django CSRF protection
            },
            body: JSON.stringify({ message: message })
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
            answerInput.focus(); // Refocus input
        }, 1000);
    }
}

// Update interview state based on responses
function updateInterviewState(userMessage, aiResponse) {
    const statusBadge = document.getElementById('statusBadge');
    const roleDisplay = document.getElementById('roleDisplay');
    const topicsDisplay = document.getElementById('topicsDisplay');

    // Check if interview started
    if (userMessage.toLowerCase() === 'go') {
        statusBadge.textContent = 'LIVE';
        statusBadge.style.background = '#d1fae5';
        statusBadge.style.color = '#10b981';
        startTimer();
    }

    // Check if role was provided
    if (aiResponse.includes('Which topics?')) {
        roleDisplay.textContent = userMessage.toUpperCase();
        statusBadge.textContent = 'LIVE';
        statusBadge.style.background = '#d1fae5';
        statusBadge.style.color = '#10b981';
    }

    // Check if topics provided and questions started
    if (aiResponse.includes('Question 1:') || aiResponse.includes('Question ')) {
        if (userMessage.toLowerCase() !== 'go' && !aiResponse.includes('Score:')) {
            topicsDisplay.textContent = userMessage.toUpperCase();
        }
        statusBadge.textContent = 'LIVE';
        statusBadge.style.background = '#d1fae5';
        statusBadge.style.color = '#10b981';
    }

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