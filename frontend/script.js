const form = document.getElementById('form');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const submitBtn = document.getElementById('submitBtn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const file = document.getElementById('resume').files[0];
    const jobText = document.getElementById('job_text').value;
    
    if (!file || !jobText) {
        alert('Please upload a resume and enter a job description');
        return;
    }
    
    // Show loading
    loading.classList.add('active');
    results.classList.remove('active');
    submitBtn.disabled = true;
    
    const fd = new FormData();
    fd.append('resume', file);
    fd.append('job_text', jobText);
    
    try {
        const res = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            body: fd
        });
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        displayResults(data);
    } catch (err) {
        results.innerHTML = `
            <div class="error">
                <h3>❌ Error</h3>
                <p>${err.message}</p>
                <p>Make sure the backend server is running on port 8000.</p>
            </div>
        `;
        results.classList.add('active');
    } finally {
        loading.classList.remove('active');
        submitBtn.disabled = false;
    }
});

function displayResults(data) {
    const matchPercent = Math.round(data.match.score * 100);
    
    let html = `
        <div class="score-card">
            <div class="score-label">Overall Match Score</div>
            <div class="score-number">${matchPercent}%</div>
            <p style="color: #666; margin-top: 10px;">
                Skills: ${Math.round(data.match.components.skills * 100)}% | 
                Responsibilities: ${Math.round(data.match.components.responsibilities * 100)}% | 
                Semantic: ${Math.round(data.match.components.semantic * 100)}%
            </p>
        </div>
    `;
    
    if (data.summary) {
        html += `
            <div class="summary">
                <h3 style="margin-bottom: 15px; color: #667eea;">📊 Summary</h3>
                <p>${data.summary}</p>
            </div>
        `;
    }
    
    // Skills section
    if (data.skills) {
        html += `<div class="skills-section">`;
        
        if (data.skills.resume && data.skills.resume.length > 0) {
            html += `
                <h3>✅ Your Skills</h3>
                <div>
                    ${data.skills.resume.map(skill => 
                        `<span class="skill-tag">${skill}</span>`
                    ).join('')}
                </div>
            `;
        }
        
        if (data.skills.missing && data.skills.missing.length > 0) {
            html += `
                <h3 style="margin-top: 20px; color: #d32f2f;">⚠️ Missing Skills</h3>
                <div>
                    ${data.skills.missing.map(skill => 
                        `<span class="skill-tag missing">${skill}</span>`
                    ).join('')}
                </div>
            `;
        }
        
        html += `</div>`;
    }
    
    // Improvements
    if (data.improvements && data.improvements.length > 0) {
        html += `
            <div class="improvements-section">
                <h3>💡 Top 3 Improvements</h3>
        `;
        
        data.improvements.forEach((imp, index) => {
            html += `
                <div class="improvement">
                    <h4>${index + 1}. ${imp.title}</h4>
                    <p><strong>Why:</strong> ${imp.reason}</p>
                    ${imp.example ? `<div class="example">💼 Example: ${imp.example}</div>` : ''}
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    results.innerHTML = html;
    results.classList.add('active');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
