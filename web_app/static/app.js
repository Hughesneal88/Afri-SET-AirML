document.addEventListener('DOMContentLoaded', () => {
    // State Variables
    let activeSessionId = null;
    let currentUser = null;
    let cachedModelsRegistry = {};

    // UI Selectors - Sidebar & Nav
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
    const appSidebar = document.getElementById('appSidebar');
    const navItemBtns = document.querySelectorAll('.nav-item-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // UI Selectors - User Auth
    const userAuthBtn = document.getElementById('userAuthBtn');
    const authModal = document.getElementById('authModal');
    const closeAuthModalBtn = document.getElementById('closeAuthModalBtn');
    const authTabLogin = document.getElementById('authTabLogin');
    const authTabRegister = document.getElementById('authTabRegister');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const authErrorMsg = document.getElementById('authErrorMsg');
    const regErrorMsg = document.getElementById('regErrorMsg');
    const userNameLabel = document.getElementById('userNameLabel');
    const userAvatarIcon = document.getElementById('userAvatarIcon');

    // UI Selectors - Controls & Telemetry
    const partitionSelect = document.getElementById('partitionSelect');
    const modelSelect = document.getElementById('modelSelect');
    const compareSelect = document.getElementById('compareSelect');
    
    // Live Telemetry Elements
    const liveTimestamp = document.getElementById('live_timestamp');
    const liveTemp = document.getElementById('live_temp');
    const liveRH = document.getElementById('live_rh');
    const liveRawPM25 = document.getElementById('live_raw_pm25');
    const liveCalibratedPM25 = document.getElementById('live_calibrated_pm25');
    const liveDelta = document.getElementById('live_delta');
    const livePctDelta = document.getElementById('live_pct_delta');
    const liveAqiScore = document.getElementById('live_aqi_score');
    const liveAqiCategory = document.getElementById('live_aqi_category');
    const liveAqiCard = document.getElementById('live_aqi_card');

    // Metrics Scorecard Elements
    const metricR2 = document.getElementById('metric-r2');
    const metricMAE = document.getElementById('metric-mae');
    const metricRMSE = document.getElementById('metric-rmse');
    const metricBias = document.getElementById('metric-bias');

    // Simulator Elements
    const simPM25 = document.getElementById('sim_pm25');
    const simTemp = document.getElementById('sim_temp');
    const simRH = document.getElementById('sim_rh');
    const simHour = document.getElementById('sim_hour');
    const simHarmattan = document.getElementById('sim_harmattan');
    const simPM25Val = document.getElementById('sim_pm25_val');
    const simTempVal = document.getElementById('sim_temp_val');
    const simRHVal = document.getElementById('sim_rh_val');
    const simHourVal = document.getElementById('sim_hour_val');
    const simPrediction = document.getElementById('sim_prediction');
    const simDelta = document.getElementById('sim_delta');

    // Dedicated Chat Studio Selectors
    const newChatBtn = document.getElementById('newChatBtn');
    const chatSessionsList = document.getElementById('chatSessionsList');
    const chatMessagesContainer = document.getElementById('chatMessagesContainer');
    const chatInputText = document.getElementById('chatInputText');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');

    // Safe Markdown Renderer
    function safeRenderMarkdown(text) {
        if (!text) return '';
        if (typeof marked !== 'undefined') {
            try {
                return marked.parse(text);
            } catch (e) {
                console.warn('Marked parse error:', e);
            }
        }
        return text
            .replace(/^### (.*$)/gim, '<h3 style="color:#38bdf8; font-size:15px; margin:12px 0 6px 0;">$1</h3>')
            .replace(/^#### (.*$)/gim, '<h4 style="color:#60a5fa; font-size:13.5px; margin:10px 0 4px 0;">$1</h4>')
            .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#f8fafc;">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    // Safe Plotly Renderer
    function safePlotly(elementId, data, layout, config) {
        if (typeof Plotly !== 'undefined' && Plotly.newPlot) {
            Plotly.newPlot(elementId, data, layout, config);
        } else {
            setTimeout(() => {
                if (typeof Plotly !== 'undefined' && Plotly.newPlot) {
                    Plotly.newPlot(elementId, data, layout, config);
                }
            }, 1000);
        }
    }

    // ==========================================================================
    // FEATURE 1: COLLAPSIBLE SIDEBAR & PERSISTENT TAB NAVIGATION
    // ==========================================================================
    function toggleSidebar() {
        if (appSidebar) {
            appSidebar.classList.toggle('collapsed');
            const isCollapsed = appSidebar.classList.contains('collapsed');
            localStorage.setItem('sidebar_collapsed', isCollapsed ? 'true' : 'false');
            window.dispatchEvent(new Event('resize'));
        }
    }

    if (sidebarToggleBtn) sidebarToggleBtn.addEventListener('click', toggleSidebar);
    if (sidebarCollapseBtn) sidebarCollapseBtn.addEventListener('click', toggleSidebar);

    // Restore saved sidebar state
    if (localStorage.getItem('sidebar_collapsed') === 'true' && appSidebar) {
        appSidebar.classList.add('collapsed');
    }

    // Persistent Tab Switching
    function switchTab(targetTab) {
        if (!targetTab) return;
        
        navItemBtns.forEach(b => {
            if (b.getAttribute('data-tab') === targetTab) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });

        tabContents.forEach(c => {
            if (c.id === targetTab) {
                c.classList.add('active');
            } else {
                c.classList.remove('active');
            }
        });

        localStorage.setItem('active_tab', targetTab);
        if (window.location.hash !== `#${targetTab}`) {
            history.replaceState(null, '', `#${targetTab}`);
        }

        if (targetTab === 'tab-rag') {
            loadChatSessions();
        }

        window.dispatchEvent(new Event('resize'));
    }

    navItemBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    // Restore Active Tab on Page Refresh (URL Hash or LocalStorage)
    function restoreActiveTab() {
        const hash = window.location.hash ? window.location.hash.replace('#', '') : null;
        const savedTab = localStorage.getItem('active_tab');
        const tabToActivate = hash || savedTab || 'tab-explorer';
        
        if (document.getElementById(tabToActivate)) {
            switchTab(tabToActivate);
        } else {
            switchTab('tab-explorer');
        }
    }

    window.addEventListener('hashchange', restoreActiveTab);

    // ==========================================================================
    // FEATURE 4: USER ACCOUNTS & AUTHENTICATION
    // ==========================================================================
    async function checkCurrentUser() {
        try {
            const res = await fetch('/api/me');
            const data = await res.json();
            if (data.status === 'success' && data.user) {
                currentUser = data.user;
                if (userNameLabel) userNameLabel.textContent = currentUser.username;
                if (userAvatarIcon) userAvatarIcon.textContent = currentUser.username.charAt(0).toUpperCase();
            } else {
                currentUser = null;
                if (userNameLabel) userNameLabel.textContent = 'Sign In / Register';
                if (userAvatarIcon) userAvatarIcon.textContent = '?';
            }
        } catch (e) {
            console.error('Check current user error:', e);
        }
    }

    if (userAuthBtn) {
        userAuthBtn.addEventListener('click', () => {
            if (currentUser) {
                if (confirm(`Logged in as ${currentUser.username}. Do you want to sign out?`)) {
                    logoutUser();
                }
            } else {
                if (authModal) authModal.classList.add('active');
            }
        });
    }

    if (closeAuthModalBtn) {
        closeAuthModalBtn.addEventListener('click', () => {
            if (authModal) authModal.classList.remove('active');
        });
    }

    if (authTabLogin) {
        authTabLogin.addEventListener('click', () => {
            authTabLogin.classList.add('active');
            authTabRegister.classList.remove('active');
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
        });
    }

    if (authTabRegister) {
        authTabRegister.addEventListener('click', () => {
            authTabRegister.classList.add('active');
            authTabLogin.classList.remove('active');
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    currentUser = data.user;
                    if (authModal) authModal.classList.remove('active');
                    checkCurrentUser();
                    loadChatSessions();
                } else {
                    if (authErrorMsg) {
                        authErrorMsg.textContent = data.message;
                        authErrorMsg.style.display = 'block';
                    }
                }
            } catch (err) {
                console.error('Login error:', err);
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;

            try {
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    currentUser = data.user;
                    if (authModal) authModal.classList.remove('active');
                    checkCurrentUser();
                    loadChatSessions();
                } else {
                    if (regErrorMsg) {
                        regErrorMsg.textContent = data.message;
                        regErrorMsg.style.display = 'block';
                    }
                }
            } catch (err) {
                console.error('Register error:', err);
            }
        });
    }

    async function logoutUser() {
        try {
            await fetch('/api/logout', { method: 'POST' });
            currentUser = null;
            checkCurrentUser();
            loadChatSessions();
        } catch (e) {
            console.error('Logout error:', e);
        }
    }

    // ==========================================================================
    // FEATURE 2 & 3: DEDICATED ACTUAL CHAT STUDIO & PERSISTENT CONTEXT
    // ==========================================================================
    async function loadChatSessions() {
        try {
            const res = await fetch('/api/chat/sessions');
            const data = await res.json();
            if (data.status === 'success' && chatSessionsList) {
                chatSessionsList.innerHTML = '';
                if (data.sessions.length === 0) {
                    chatSessionsList.innerHTML = '<div style="font-size:12px; color:var(--text-muted); padding:8px;">No saved chats yet.</div>';
                    return;
                }

                data.sessions.forEach(sess => {
                    const activeClass = sess.session_id === activeSessionId ? 'active' : '';
                    const item = document.createElement('div');
                    item.className = `session-item-btn ${activeClass}`;
                    item.innerHTML = `
                        <span class="session-title-text"><i class="fa-solid fa-message"></i> ${sess.title}</span>
                        <button class="session-del-btn" title="Delete Session" data-id="${sess.session_id}"><i class="fa-solid fa-xmark"></i></button>
                    `;

                    item.addEventListener('click', (e) => {
                        if (e.target.closest('.session-del-btn')) {
                            e.stopPropagation();
                            deleteChatSession(sess.session_id);
                            return;
                        }
                        switchChatSession(sess.session_id);
                    });

                    chatSessionsList.appendChild(item);
                });
            }
        } catch (e) {
            console.error('Load chat sessions error:', e);
        }
    }

    async function switchChatSession(sessionId) {
        activeSessionId = sessionId;
        try {
            const res = await fetch(`/api/chat/history/${sessionId}`);
            const data = await res.json();
            if (data.status === 'success') {
                renderMessagesStream(data.messages);
                loadChatSessions();
            }
        } catch (e) {
            console.error('Switch chat session error:', e);
        }
    }

    async function createNewChatSession() {
        try {
            const res = await fetch('/api/chat/new', { method: 'POST' });
            const data = await res.json();
            if (data.status === 'success') {
                activeSessionId = data.session.session_id;
                renderMessagesStream([]);
                loadChatSessions();
            }
        } catch (e) {
            console.error('Create new chat error:', e);
        }
    }

    async function deleteChatSession(sessionId) {
        if (!confirm('Are you sure you want to delete this chat conversation?')) return;
        try {
            await fetch(`/api/chat/session/${sessionId}`, { method: 'DELETE' });
            if (activeSessionId === sessionId) {
                activeSessionId = null;
                renderMessagesStream([]);
            }
            loadChatSessions();
        } catch (e) {
            console.error('Delete chat session error:', e);
        }
    }

    function renderMessagesStream(messages) {
        if (!chatMessagesContainer) return;
        chatMessagesContainer.innerHTML = '';

        if (!messages || messages.length === 0) {
            chatMessagesContainer.innerHTML = `
                <div class="chat-msg-assistant">
                    <div class="chat-assistant-meta">
                        <span class="chat-engine-label"><i class="fa-solid fa-shield-halved"></i> AirSense AI Analyst</span>
                        <span style="font-size:11px; color:var(--text-muted);">Legon Station Stream</span>
                    </div>
                    <div class="rag-text">
                        Hello! I am **AirSense AI**, your environmental air quality analyst at the Department of Physics, University of Ghana, Legon. 
                        Ask me anything about current air quality, relative humidity particle swelling, optical sensor calibration, or machine learning accuracy!
                    </div>
                </div>
            `;
            return;
        }

        messages.forEach(msg => {
            if (msg.role === 'user') {
                const bubble = document.createElement('div');
                bubble.className = 'chat-msg-user';
                bubble.textContent = msg.content;
                chatMessagesContainer.appendChild(bubble);
            } else {
                const card = document.createElement('div');
                card.className = 'chat-msg-assistant';
                
                let citationsHtml = '';
                if (msg.citations_json) {
                    try {
                        const docs = JSON.parse(msg.citations_json);
                        if (docs && docs.length > 0) {
                            citationsHtml = '<div style="margin-top:10px; border-top:1px solid rgba(255,255,255,0.1); padding-top:6px;"><strong style="color:#60a5fa; font-size:11.5px;">Retrieved Literature:</strong>';
                            docs.forEach(d => {
                                citationsHtml += `<div class="citation-card" style="margin-top:4px; padding:8px;"><span class="citation-source"><i class="fa-solid fa-book"></i> ${d.source}</span><p class="citation-text" style="font-size:11.5px;">${d.text}</p></div>`;
                            });
                            citationsHtml += '</div>';
                        }
                    } catch (e) {}
                }

                card.innerHTML = `
                    <div class="chat-assistant-meta">
                        <span class="chat-engine-label"><i class="fa-solid fa-robot"></i> ${msg.llm_engine || 'AirSense AI'}</span>
                        <span style="font-size:10.5px; color:var(--text-muted);">${msg.created_at || 'Just now'}</span>
                    </div>
                    <div class="rag-text">${safeRenderMarkdown(msg.content)}</div>
                    ${citationsHtml}
                `;
                chatMessagesContainer.appendChild(card);
            }
        });

        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    async function sendChatMessage(queryText) {
        const query = (queryText || (chatInputText ? chatInputText.value : '')).trim();
        if (!query) return;

        if (chatInputText) {
            chatInputText.value = '';
            chatInputText.disabled = true;
        }
        if (sendChatBtn) sendChatBtn.disabled = true;

        // Append user bubble to UI
        const userBubble = document.createElement('div');
        userBubble.className = 'chat-msg-user';
        userBubble.textContent = query;
        chatMessagesContainer.appendChild(userBubble);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

        // Append loading assistant card
        const loadingCard = document.createElement('div');
        loadingCard.className = 'chat-msg-assistant';
        loadingCard.innerHTML = `
            <div class="chat-assistant-meta">
                <span class="chat-engine-label"><i class="fa-solid fa-spinner fa-spin"></i> AirSense AI Thinking...</span>
            </div>
            <div class="rag-text" style="color:var(--text-secondary); font-style:italic;">Analyzing live sensor telemetry and literature knowledge base...</div>
        `;
        chatMessagesContainer.appendChild(loadingCard);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

        try {
            const modelKey = modelSelect ? modelSelect.value : 'random_forest_pm25_model_update2';
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    session_id: activeSessionId,
                    model_key: modelKey
                })
            });

            const data = await res.json();
            if (data.status === 'success') {
                activeSessionId = data.session_id;
                renderMessagesStream(data.messages);
                loadChatSessions();
            } else {
                loadingCard.querySelector('.rag-text').innerHTML = `<span style="color:#ef4444;">Error: ${data.message || 'Could not reach server.'}</span>`;
            }
        } catch (err) {
            console.error('Send chat message error:', err);
            loadingCard.querySelector('.rag-text').innerHTML = `<span style="color:#ef4444;">Connection error. Please try again.</span>`;
        } finally {
            if (chatInputText) {
                chatInputText.disabled = false;
                chatInputText.focus();
            }
            if (sendChatBtn) sendChatBtn.disabled = false;
        }
    }

    if (sendChatBtn) sendChatBtn.addEventListener('click', () => sendChatMessage());
    if (chatInputText) {
        chatInputText.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }

    if (newChatBtn) newChatBtn.addEventListener('click', createNewChatSession);
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            if (confirm('Clear the current message view?')) {
                if (chatMessagesContainer) chatMessagesContainer.innerHTML = '';
            }
        });
    }

    // Quick Chips Event Listeners
    document.querySelectorAll('.chip-btn').forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            if (prompt) sendChatMessage(prompt);
        });
    });

    // ==========================================================================
    // LIVE TELEMETRY & MODEL INFERENCE
    // ==========================================================================
    async function fetchLiveTelemetry() {
        try {
            const res = await fetch('/api/live_telemetry');
            const data = await res.json();
            if (data.status === 'success' && data.telemetry) {
                const t = data.telemetry;
                if (liveTimestamp) liveTimestamp.textContent = t.timestamp;
                if (liveTemp) liveTemp.textContent = `${t.temperature.toFixed(1)} °C`;
                if (liveRH) liveRH.textContent = `${t.humidity.toFixed(1)} %`;
                if (liveRawPM25) liveRawPM25.textContent = `${t.raw_pm25.toFixed(2)} µg/m³`;
                if (liveCalibratedPM25) liveCalibratedPM25.textContent = `${t.calibrated_pm25.toFixed(2)} µg/m³`;
                if (liveDelta) liveDelta.textContent = `${t.delta > 0 ? '+' : ''}${t.delta.toFixed(2)} µg/m³`;
                if (livePctDelta) livePctDelta.textContent = `(${t.pct_delta > 0 ? '+' : ''}${t.pct_delta.toFixed(1)}%)`;

                if (t.us_epa_aqi) {
                    if (liveAqiScore) liveAqiScore.textContent = `AQI ${t.us_epa_aqi.score}`;
                    if (liveAqiCategory) liveAqiCategory.textContent = t.us_epa_aqi.category;
                    if (liveAqiCard) liveAqiCard.style.borderColor = t.us_epa_aqi.color;
                }
            }
        } catch (e) {
            console.error('Fetch live telemetry error:', e);
        }
    }

    async function loadModelsRegistry() {
        try {
            const res = await fetch('/api/models');
            const data = await res.json();
            if (data.status === 'success' && data.models) {
                if (modelSelect) {
                    modelSelect.innerHTML = '';
                    data.models.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m.key;
                        opt.textContent = m.name;
                        modelSelect.appendChild(opt);
                    });
                }
            }
        } catch (e) {
            console.error('Load models error:', e);
        }
    }

    async function runInference() {
        const modelKey = modelSelect ? modelSelect.value : 'random_forest_pm25_model_update2';
        const partition = partitionSelect ? partitionSelect.value : 'holdout';
        const compareKey = compareSelect ? compareSelect.value : 'none';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_key: modelKey, partition, compare_key: compareKey })
            });
            const data = await res.json();

            if (data.status === 'success') {
                if (metricR2) metricR2.textContent = data.metrics.r2.toFixed(4);
                if (metricMAE) metricMAE.textContent = `${data.metrics.mae.toFixed(2)} µg/m³`;
                if (metricRMSE) metricRMSE.textContent = `${data.metrics.rmse.toFixed(2)} µg/m³`;
                if (metricBias) metricBias.textContent = `${data.metrics.bias.toFixed(2)} µg/m³`;

                renderPlots(data);
            }
        } catch (e) {
            console.error('Run inference error:', e);
        }
    }

    function renderPlots(data) {
        // 1. Time Series Plot
        const traceActual = {
            x: data.timestamps,
            y: data.actuals,
            mode: 'lines',
            name: 'Teledyne FEM Reference',
            line: { color: '#06b6d4', width: 2 }
        };

        const tracePred = {
            x: data.timestamps,
            y: data.predictions,
            mode: 'lines',
            name: data.model_name,
            line: { color: '#3b82f6', width: 2 }
        };

        const traceRaw = {
            x: data.timestamps,
            y: data.raw_pm25,
            mode: 'lines',
            name: 'Raw OPC-N3 Input',
            line: { color: '#94a3b8', width: 1, dash: 'dot' }
        };

        const tsLayout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#cbd5e1', family: 'Inter, sans-serif' },
            xaxis: { gridcolor: 'rgba(255,255,255,0.06)' },
            yaxis: { title: 'PM2.5 Concentration (µg/m³)', gridcolor: 'rgba(255,255,255,0.06)' },
            margin: { t: 20, b: 40, l: 50, r: 20 },
            legend: { orientation: 'h', y: 1.1 }
        };

        safePlotly('plotTimeSeries', [traceActual, tracePred, traceRaw], tsLayout, { responsive: true });

        // 2. Scatter Plot (Predicted vs Actual)
        const minVal = Math.min(...data.actuals, ...data.predictions);
        const maxVal = Math.max(...data.actuals, ...data.predictions);

        const traceScatter = {
            x: data.actuals,
            y: data.predictions,
            mode: 'markers',
            name: 'Model Predictions',
            marker: { color: '#3b82f6', size: 6, opacity: 0.6 }
        };

        const trace1to1 = {
            x: [minVal, maxVal],
            y: [minVal, maxVal],
            mode: 'lines',
            name: '1:1 Ideal Line (R²=1.0)',
            line: { color: '#ef4444', dash: 'dash', width: 2 }
        };

        const scatterLayout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#cbd5e1', family: 'Inter, sans-serif' },
            xaxis: { title: 'Teledyne Reference PM2.5 (µg/m³)', gridcolor: 'rgba(255,255,255,0.06)' },
            yaxis: { title: 'Calibrated Prediction (µg/m³)', gridcolor: 'rgba(255,255,255,0.06)' },
            margin: { t: 20, b: 50, l: 50, r: 20 },
            legend: { orientation: 'h', y: 1.15 }
        };

        safePlotly('plotScatter', [traceScatter, trace1to1], scatterLayout, { responsive: true });

        // 3. Residuals Distribution Histogram
        const residuals = data.predictions.map((pred, i) => pred - data.actuals[i]);

        const traceResiduals = {
            x: residuals,
            type: 'histogram',
            name: 'Model Error',
            marker: { color: '#06b6d4', opacity: 0.75, line: { color: '#0284c7', width: 1 } }
        };

        const residualsLayout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#cbd5e1', family: 'Inter, sans-serif' },
            xaxis: { title: 'Calibration Error (Predicted - Actual) (µg/m³)', gridcolor: 'rgba(255,255,255,0.06)' },
            yaxis: { title: 'Sample Count', gridcolor: 'rgba(255,255,255,0.06)' },
            margin: { t: 20, b: 50, l: 50, r: 20 },
            shapes: [{
                type: 'line',
                x0: 0, x1: 0,
                y0: 0, y1: 1,
                yref: 'paper',
                line: { color: '#ef4444', dash: 'dash', width: 2 }
            }],
            legend: { orientation: 'h', y: 1.15 }
        };

        safePlotly('plotResiduals', [traceResiduals], residualsLayout, { responsive: true });
    }

    // Simulation Slider Logic
    function updateSimulation() {
        if (!simPM25 || !simTemp || !simRH || !simHour) return;
        const pm25 = parseFloat(simPM25.value);
        const temp = parseFloat(simTemp.value);
        const rh = parseFloat(simRH.value);
        const hour = parseInt(simHour.value);
        const harmattan = simHarmattan && simHarmattan.checked ? 1 : 0;

        if (simPM25Val) simPM25Val.textContent = pm25.toFixed(1);
        if (simTempVal) simTempVal.textContent = temp.toFixed(1);
        if (simRHVal) simRHVal.textContent = rh.toFixed(1);
        if (simHourVal) simHourVal.textContent = `${hour.toString().padStart(2, '0')}:00`;

        fetch('/api/predict_single', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model_key: modelSelect ? modelSelect.value : 'random_forest_pm25_model_update2',
                pm25, sample_temp: temp, sample_rh: rh, hour_of_day: hour, is_harmattan: harmattan
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                const pred = data.prediction;
                const delta = pred - pm25;
                if (simPrediction) simPrediction.textContent = `${pred.toFixed(2)} µg/m³`;
                if (simDelta) simDelta.textContent = `Adjustment: ${delta > 0 ? '+' : ''}${delta.toFixed(2)} µg/m³ (${((delta/pm25)*100).toFixed(1)}%)`;
            }
        })
        .catch(e => console.error('Sim error:', e));
    }

    [simPM25, simTemp, simRH, simHour, simHarmattan].forEach(el => {
        if (el) el.addEventListener('input', updateSimulation);
    });

    // Initializations
    restoreActiveTab();
    checkCurrentUser();
    loadModelsRegistry().then(() => {
        runInference();
    });
    fetchLiveTelemetry();
    setInterval(fetchLiveTelemetry, 15000);
    loadChatSessions();
});
