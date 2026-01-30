document.addEventListener('DOMContentLoaded', () => {
    
    // 1. CLOCK
    setInterval(() => {
        const now = new Date();
        document.getElementById('clock').innerText = now.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
    }, 1000);

    // 2. LIVE DASHBOARD UPDATER (Real Data)
    function updateMetrics() {
        fetch('/api/metrics')
            .then(response => response.json())
            .then(data => {
                // Update Bars
                document.querySelector('.metric-box:nth-child(1) .fill').style.width = data.focus + '%';
                document.querySelector('.metric-box:nth-child(2) .fill').style.width = data.stress + '%';
            });
    }
    setInterval(updateMetrics, 2000); // Refresh every 2 seconds

    // 3. CHAT SYSTEM (Connected to Python)
    window.sendMessage = function() {
        const input = document.getElementById('user-input');
        const history = document.getElementById('chat-history');
        const message = input.value.trim();
        
        if(message === "") return;

        // Show User Message
        history.innerHTML += `<div style="margin-bottom:8px; text-align:right; color:#ddd;">You: ${message}</div>`;
        input.value = ""; // Clear input

        // CALL PYTHON SERVER
        fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message})
        })
        .then(response => response.json())
        .then(data => {
            history.innerHTML += `<div style="margin-bottom:8px; text-align:left; color:#b388ff;">Etherea: ${data.response}</div>`;
            document.getElementById('ai-message').innerText = data.response;
            history.scrollTop = history.scrollHeight; // Auto-scroll
        });
    }
});
