const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('upload');
const loading = document.getElementById('loading');
const uploadContent = document.getElementById('uploadContent');
const resultsGrid = document.getElementById('resultsGrid');
const apiKeyInput = document.getElementById('apiKey');

let currentAnalysis = null;

fileInput.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const apiKey = apiKeyInput.value;
    if (!apiKey) {
        alert("Please enter your Gemini API Key first.");
        return;
    }

    loading.style.display = 'block';
    uploadContent.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`http://localhost:8000/analyze?api_key=${apiKey}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Analysis failed');

        const data = await response.json();
        displayResults(data);
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        loading.style.display = 'none';
        uploadContent.style.display = 'block';
    }
};

function displayResults(data) {
    currentAnalysis = data;
    resultsGrid.style.display = 'grid';

    // Themes
    const themesList = document.getElementById('themesList');
    themesList.innerHTML = data.themes.map(t => `<span class="theme-pill">${t}</span>`).join('');

    // Quotes
    const quotesList = document.getElementById('quotesList');
    quotesList.innerHTML = data.quotes.map(q => `<div class="quote-card">"${q}"</div>`).join('');

    // Actions
    const actionsList = document.getElementById('actionsList');
    actionsList.innerHTML = data.actions.map(a => `<li style="margin-bottom: 0.5rem;">• ${a}</li>`).join('');

    // Summary
    document.getElementById('summaryText').innerText = data.summary;

    // Scroll to results
    resultsGrid.scrollIntoView({ behavior: 'smooth' });
}

async function sendEmail() {
    if (!currentAnalysis) return;

    const recipientName = document.getElementById('recipientName').value || 'Team';
    const recipientEmail = document.getElementById('recipientEmail').value;

    if (!recipientEmail) {
        alert("Please enter a recipient email address.");
        return;
    }

    const emailBtn = document.getElementById('emailBtn');
    const originalText = emailBtn.innerText;
    emailBtn.innerText = "⏳ Sending...";
    emailBtn.disabled = true;

    try {
        const response = await fetch('http://localhost:8000/send-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: recipientName,
                email: recipientEmail,
                analysis: currentAnalysis
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send email');
        }

        alert("✅ Weekly pulse email sent successfully to " + recipientEmail);
    } catch (err) {
        alert("❌ Error: " + err.message + "\n\nMake sure your SMTP credentials are set in the .env file.");
    } finally {
        emailBtn.innerText = originalText;
        emailBtn.disabled = false;
    }
}

function exportReport() {
    if (!currentAnalysis) return;

    const md = `# Weekly Pulse: INDMoney Insights\n\n## Summary\n${currentAnalysis.summary}\n\n## Themes\n${currentAnalysis.themes.map(t => `- ${t}`).join('\n')}\n\n## Quotes\n${currentAnalysis.quotes.map(q => `> "${q}"`).join('\n\n')}\n\n## Actions\n${currentAnalysis.actions.map(a => `- ${a}`).join('\n')}`;

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `INDMoney_Weekly_Pulse_${new Date().toISOString().split('T')[0]}.md`;
    a.click();
    alert("One-pager report generated and downloaded!");
}
