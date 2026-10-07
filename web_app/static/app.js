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

    // Continuous Learning Elements
    const selectFileBtn = document.getElementById('selectFileBtn');
    const refFileInput = document.getElementById('refFileInput');
    const selectedFileName = document.getElementById('selectedFileName');
    const uploadRefBtn = document.getElementById('uploadRefBtn');
    const retrainResultCard = document.getElementById('retrainResultCard');
    const retrainStatusTitle = document.getElementById('retrainStatusTitle');
    const retrainMetricsGrid = document.getElementById('retrainMetricsGrid');
    const retrainHistoryBody = document.getElementById('retrainHistoryBody');

    // System Settings Elements
    const settingsPrimaryModel = document.getElementById('settingsPrimaryModel');
    const settingsDefaultPartition = document.getElementById('settingsDefaultPartition');
    const settingsMaxPoints = document.getElementById('settingsMaxPoints');
    const settingsRefreshInterval = document.getElementById('settingsRefreshInterval');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    const settingsToast = document.getElementById('settingsToast');
    
    let activeRefreshInterval = 15000;
    let refreshTimerId = null;

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
    const appBody = document.querySelector('.app-body');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    function closeMobileSidebar() {
        if (appSidebar) appSidebar.classList.remove('mobile-open');
        if (sidebarBackdrop) sidebarBackdrop.classList.remove('active');
    }

    function toggleSidebar() {
        if (!appSidebar) return;
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            const isOpen = appSidebar.classList.toggle('mobile-open');
            if (sidebarBackdrop) {
                if (isOpen) sidebarBackdrop.classList.add('active');
                else sidebarBackdrop.classList.remove('active');
            }
        } else {
            const collapsed = appBody && appBody.classList.toggle('sidebar-collapsed');
            localStorage.setItem('sidebar_collapsed', collapsed ? 'true' : 'false');
        }
        window.dispatchEvent(new Event('resize'));
    }

    if (sidebarToggleBtn) sidebarToggleBtn.addEventListener('click', toggleSidebar);
    if (sidebarCollapseBtn) sidebarCollapseBtn.addEventListener('click', toggleSidebar);
    if (sidebarBackdrop) sidebarBackdrop.addEventListener('click', closeMobileSidebar);

    // Restore saved sidebar state (desktop only)
    if (localStorage.getItem('sidebar_collapsed') === 'true' && appBody && window.innerWidth > 768) {
        appBody.classList.add('sidebar-collapsed');
    }

    // Persistent Tab Switching
    function switchTab(targetTab) {
        if (!targetTab) return;
        closeMobileSidebar();
        
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

        // Lazy-load Tab Content on Demand (Fast Page Load)
        if (targetTab === 'tab-live') {
            fetchLiveTelemetry();
        } else if (targetTab === 'tab-explorer') {
            runInference();
        } else if (targetTab === 'tab-comparison') {
            runInferenceCompare();
        } else if (targetTab === 'tab-diagnostics') {
            runInference();
        } else if (targetTab === 'tab-rag') {
            loadChatSessions();
        } else if (targetTab === 'tab-retrain') {
            loadRetrainHistory();
        } else if (targetTab === 'tab-forecast') {
            loadForecastData();
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
        const tabToActivate = hash || savedTab || 'tab-live';
        
        if (document.getElementById(tabToActivate)) {
            switchTab(tabToActivate);
        } else {
            switchTab('tab-live');
        }
    }

    window.addEventListener('hashchange', restoreActiveTab);

    // Quick Launch Navigation Tiles (Homepage to Sub-pages)
    document.querySelectorAll('.quick-launch-tile').forEach(tile => {
        tile.addEventListener('click', () => {
            const jumpTab = tile.getAttribute('data-jump');
            if (jumpTab) switchTab(jumpTab);
        });
    });

    // Brand Logo Click returns to Live Homepage
    const brandLockup = document.querySelector('.brand-lockup');
    if (brandLockup) {
        brandLockup.style.cursor = 'pointer';
        brandLockup.addEventListener('click', () => {
            switchTab('tab-live');
        });
    }

    // Selector References for Dedicated Comparison Page
    const modelSelectCompare = document.getElementById('modelSelectCompare');
    const partitionSelectCompare = document.getElementById('partitionSelectCompare');

    // Active system settings state
    let systemSettings = {
        primary_model_key: localStorage.getItem('primary_model_key') || 'stacked_physics_meta_ensemble',
        default_partition: localStorage.getItem('default_partition') || 'holdout',
        max_points: parseInt(localStorage.getItem('max_points') || '500'),
        refresh_interval: parseInt(localStorage.getItem('refresh_interval') || '15')
    };

    async function fetchLiveTelemetry() {
        try {
            const activeModel = (settingsPrimaryModel && settingsPrimaryModel.value) || systemSettings.primary_model_key || 'stacked_physics_meta_ensemble';
            const res = await fetch(`/api/live_telemetry?model_key=${encodeURIComponent(activeModel)}`);
            const data = await res.json();
            if (data.status === 'success' && data.telemetry) {
                const t = data.telemetry;
                if (liveTimestamp) liveTimestamp.textContent = t.timestamp;
                if (liveTemp) liveTemp.textContent = `${t.temperature.toFixed(1)} °C`;
                if (liveRH) liveRH.textContent = `${t.humidity.toFixed(1)} %`;
                if (liveRawPM25) liveRawPM25.textContent = `${t.raw_pm25.toFixed(2)} µg/m³`;
                if (liveCalibratedPM25) liveCalibratedPM25.textContent = `${t.calibrated_pm25.toFixed(2)} µg/m³`;
                if (liveDelta) {
                    const deltaSign = t.delta > 0 ? '+' : '';
                    liveDelta.textContent = `${deltaSign}${t.delta.toFixed(2)} µg/m³`;
                    if (t.delta <= 0) {
                        liveDelta.style.color = '#34d399';
                        liveDelta.style.borderColor = 'rgba(52, 211, 153, 0.4)';
                        liveDelta.style.background = 'rgba(16, 185, 129, 0.2)';
                    } else {
                        liveDelta.style.color = '#f59e0b';
                        liveDelta.style.borderColor = 'rgba(245, 158, 11, 0.4)';
                        liveDelta.style.background = 'rgba(245, 158, 11, 0.15)';
                    }
                }
                if (livePctDelta) livePctDelta.textContent = `(${t.pct_delta > 0 ? '+' : ''}${t.pct_delta.toFixed(1)}%)`;

                const modelLabel = document.getElementById('live_model_label');
                if (modelLabel) modelLabel.textContent = t.model_name || '🏆 SPIME v4 Ensemble';

                if (t.us_epa_aqi) {
                    if (liveAqiScore) {
                        liveAqiScore.textContent = `AQI ${t.us_epa_aqi.score}`;
                        if (t.us_epa_aqi.color) {
                            liveAqiScore.style.background = t.us_epa_aqi.color;
                            liveAqiScore.style.boxShadow = `0 0 12px ${t.us_epa_aqi.color}66`;
                        }
                    }
                    if (liveAqiCategory) liveAqiCategory.textContent = t.us_epa_aqi.category;
                    if (liveAqiCard && t.us_epa_aqi.color) {
                        liveAqiCard.style.borderLeftColor = t.us_epa_aqi.color;
                    }

                    // Dynamic Health Advisory Text & Scale Highlighting
                    const liveHealthAdvisoryText = document.getElementById('liveHealthAdvisoryText');
                    if (liveHealthAdvisoryText) {
                        const score = t.us_epa_aqi.score;
                        let advice = `Live calibrated PM2.5 level is ${t.calibrated_pm25.toFixed(1)} µg/m³ (AQI ${score} - ${t.us_epa_aqi.category}). `;
                        if (score <= 50) {
                            advice += "Air quality is satisfactory and particulate pollution poses little or no risk to health.";
                        } else if (score <= 100) {
                            advice += "Air quality is acceptable for outdoor activity; unusually sensitive individuals should consider limiting prolonged outdoor exertion.";
                        } else if (score <= 150) {
                            advice += "Members of sensitive groups may experience health effects. The general public is less likely to be affected.";
                        } else {
                            advice += "Health alert: Everyone may begin to experience health effects; limit prolonged outdoor exposure.";
                        }
                        liveHealthAdvisoryText.textContent = advice;
                    }
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
            if (data.status === 'success' && data.models && data.models.length > 0) {
                const defaultKey = systemSettings.primary_model_key || 'stacked_physics_meta_ensemble';

                const populateSelect = (selectEl, defaultVal) => {
                    if (!selectEl) return;
                    selectEl.innerHTML = '';
                    data.models.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m.key;
                        opt.textContent = m.name;
                        selectEl.appendChild(opt);
                    });
                    if (defaultVal) selectEl.value = defaultVal;
                };

                populateSelect(modelSelect, defaultKey);
                populateSelect(settingsPrimaryModel, defaultKey);
                populateSelect(modelSelectCompare, 'stacked_physics_meta_ensemble');

                if (compareSelect) {
                    compareSelect.innerHTML = '<option value="none">-- None --</option><option value="quantaq_factory">QuantAQ Factory Uncalibrated Output</option>';
                    data.models.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m.key;
                        opt.textContent = m.name;
                        compareSelect.appendChild(opt);
                    });
                    compareSelect.value = 'none';
                }
            }
        } catch (e) {
            console.error('Load models error:', e);
        }
    }

    async function loadSystemSettings() {
        try {
            const res = await fetch('/api/settings');
            const data = await res.json();
            if (data.status === 'success' && data.settings) {
                systemSettings = { ...systemSettings, ...data.settings };
                if (settingsPrimaryModel && systemSettings.primary_model_key) {
                    settingsPrimaryModel.value = systemSettings.primary_model_key;
                }
                if (settingsDefaultPartition && systemSettings.default_partition) {
                    settingsDefaultPartition.value = systemSettings.default_partition;
                }
                if (settingsMaxPoints && systemSettings.max_points !== undefined) {
                    settingsMaxPoints.value = systemSettings.max_points.toString();
                }
                if (settingsRefreshInterval && systemSettings.refresh_interval) {
                    settingsRefreshInterval.value = systemSettings.refresh_interval.toString();
                }
            }
        } catch (e) {
            console.error('Load system settings error:', e);
        }
    }

    async function saveSystemSettings() {
        const primary_model_key = settingsPrimaryModel ? settingsPrimaryModel.value : 'random_forest_pm25_model_update2';
        const default_partition = settingsDefaultPartition ? settingsDefaultPartition.value : 'holdout';
        const max_points = settingsMaxPoints ? parseInt(settingsMaxPoints.value) : 500;
        const refresh_interval = settingsRefreshInterval ? parseInt(settingsRefreshInterval.value) : 15;

        try {
            const res = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ primary_model_key, default_partition, max_points, refresh_interval })
            });
            const data = await res.json();

            if (data.status === 'success') {
                systemSettings = { primary_model_key, default_partition, max_points, refresh_interval };
                localStorage.setItem('primary_model_key', primary_model_key);
                localStorage.setItem('default_partition', default_partition);
                localStorage.setItem('max_points', max_points.toString());
                localStorage.setItem('refresh_interval', refresh_interval.toString());

                if (modelSelect) modelSelect.value = primary_model_key;
                if (partitionSelect) partitionSelect.value = default_partition;

                if (settingsToast) {
                    settingsToast.style.display = 'block';
                    setTimeout(() => { settingsToast.style.display = 'none'; }, 3000);
                }

                fetchLiveTelemetry();
                runInference();
            }
        } catch (e) {
            console.error('Save settings error:', e);
        }
    }

    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSystemSettings);
    }

    // 2-Way Model Selection Synchronization & Real-time Update
    if (modelSelect) {
        modelSelect.addEventListener('change', () => {
            if (settingsPrimaryModel) settingsPrimaryModel.value = modelSelect.value;
            systemSettings.primary_model_key = modelSelect.value;
            localStorage.setItem('primary_model_key', modelSelect.value);
            runInference();
            fetchLiveTelemetry();
        });
    }

    if (settingsPrimaryModel) {
        settingsPrimaryModel.addEventListener('change', () => {
            if (modelSelect) modelSelect.value = settingsPrimaryModel.value;
            systemSettings.primary_model_key = settingsPrimaryModel.value;
            localStorage.setItem('primary_model_key', settingsPrimaryModel.value);
            saveSystemSettings();
        });
    }

    [compareSelect, partitionSelect].forEach(selectEl => {
        if (selectEl) {
            selectEl.addEventListener('change', () => {
                runInference();
            });
        }
    });

    [modelSelectCompare, partitionSelectCompare].forEach(selectEl => {
        if (selectEl) {
            selectEl.addEventListener('change', () => {
                runInferenceCompare();
            });
        }
    });

    async function runInference() {
        const modelKey = (modelSelect && modelSelect.value) ? modelSelect.value : 'stacked_physics_meta_ensemble';
        const compareKey = (compareSelect && compareSelect.value) ? compareSelect.value : 'none';
        const partition = (partitionSelect && partitionSelect.value) ? partitionSelect.value : 'holdout';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_key: modelKey, partition, compare_key: compareKey, max_points: 500 })
            });
            const data = await res.json();

            if (data.status === 'success') {
                if (metricR2) metricR2.textContent = data.metrics.r2.toFixed(4);
                if (metricMAE) metricMAE.textContent = `${data.metrics.mae.toFixed(2)} µg/m³`;
                if (metricRMSE) metricRMSE.textContent = `${data.metrics.rmse.toFixed(2)} µg/m³`;
                if (metricBias) metricBias.textContent = `${data.metrics.bias.toFixed(2)} µg/m³`;

                renderPlots(data);
            } else {
                console.error('Predict returned error status:', data.message);
            }
        } catch (e) {
            console.error('Run inference error:', e);
        }
    }

    async function runInferenceCompare() {
        const modelKey = modelSelectCompare ? modelSelectCompare.value : 'stacked_physics_meta_ensemble';
        const compareKey = compareSelect ? compareSelect.value : 'quantaq_factory';
        const partition = partitionSelectCompare ? partitionSelectCompare.value : 'holdout';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_key: modelKey, partition, compare_key: compareKey, max_points: 500 })
            });
            const data = await res.json();

            if (data.status === 'success') {
                renderComparePlot(data);
            }
        } catch (e) {
            console.error('Run comparison inference error:', e);
        }
    }

    let lastPlotData = null;
    let lastCompareData = null;

    function getPlotlyThemeColors() {
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        return {
            fontFamily: 'Host Grotesk, Inter, sans-serif',
            fontColor: isLight ? '#111812' : '#F1F5F2',
            gridColor: isLight ? 'rgba(17, 24, 18, 0.06)' : 'rgba(241, 245, 242, 0.06)',
            actualColor: isLight ? '#111812' : '#FFFFFF',       // Solid Obsidian Charcoal in light, Crisp White in dark (Reference Ground Truth)
            predColor: isLight ? '#2563eb' : '#38bdf8',         // Royal Cobalt in light, Radiant Sky in dark (Champion Calibrated SPIME v4)
            rawColor: isLight ? '#d97706' : '#f59e0b',          // Warm Amber (Raw OPC Input)
            compareColor: isLight ? '#7c3aed' : '#a78bfa'       // Vivid Amethyst Violet (Comparison Calibrator)
        };
    }

    function initThemeToggle() {
        const themeBtn = document.getElementById('themeToggleBtn');
        const savedTheme = localStorage.getItem('theme') || 'light';

        function applyTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            if (themeBtn) {
                themeBtn.innerHTML = theme === 'light' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
            }
            if (lastPlotData) renderPlots(lastPlotData);
            if (lastCompareData) renderComparePlot(lastCompareData);
        }

        applyTheme(savedTheme);

        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-theme') || 'dark';
                const next = current === 'dark' ? 'light' : 'dark';
                applyTheme(next);
            });
        }
    }

    function renderPlots(data) {
        lastPlotData = data;
        const colors = getPlotlyThemeColors();

        // Primary Time Series Plot
        const traceActual = {
            x: data.timestamps,
            y: data.actuals,
            mode: 'lines',
            name: 'Teledyne FEM Reference',
            line: { color: colors.actualColor, width: 2.5 }
        };

        const tracePred = {
            x: data.timestamps,
            y: data.predictions,
            mode: 'lines',
            name: data.model_name,
            line: { color: colors.predColor, width: 3 }
        };

        const traceRaw = {
            x: data.timestamps,
            y: data.raw_pm25,
            mode: 'lines',
            name: 'Raw OPC-N3 Input',
            line: { color: colors.rawColor, width: 1.5, dash: 'dot' }
        };

        const tsLayout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: colors.fontColor, family: colors.fontFamily },
            xaxis: { gridcolor: colors.gridColor },
            yaxis: { title: 'PM2.5 Concentration (µg/m³)', gridcolor: colors.gridColor },
            margin: { t: 20, b: 40, l: 50, r: 20 },
            legend: { orientation: 'h', y: 1.15 }
        };

        safePlotly('plotTimeSeries', [traceActual, tracePred, traceRaw], tsLayout, { responsive: true });

        // Diagnostic Scatter Plot
        if (document.getElementById('plotScatter')) {
            const minVal = Math.min(...data.actuals, ...data.predictions);
            const maxVal = Math.max(...data.actuals, ...data.predictions);

            const traceScatter = {
                x: data.actuals,
                y: data.predictions,
                mode: 'markers',
                name: 'Model Predictions',
                marker: { color: colors.predColor, size: 6, opacity: 0.6 }
            };

            const scatterTraces = [traceScatter, {
                x: [minVal, maxVal],
                y: [minVal, maxVal],
                mode: 'lines',
                name: '1:1 Ideal Line (R²=1.0)',
                line: { color: '#ef4444', dash: 'dash', width: 2 }
            }];

            const scatterLayout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: colors.fontColor, family: colors.fontFamily },
                xaxis: { title: 'Teledyne Reference PM2.5 (µg/m³)', gridcolor: colors.gridColor },
                yaxis: { title: 'Calibrated Prediction (µg/m³)', gridcolor: colors.gridColor },
                margin: { t: 20, b: 50, l: 50, r: 20 },
                legend: { orientation: 'h', y: 1.15 }
            };

            safePlotly('plotScatter', scatterTraces, scatterLayout, { responsive: true });
        }

        // Diagnostic Residuals Plot
        if (document.getElementById('plotResiduals')) {
            const residuals = data.predictions.map((pred, i) => pred - data.actuals[i]);
            const traceResiduals = {
                x: residuals,
                type: 'histogram',
                name: 'Error Distribution',
                marker: { color: colors.actualColor, opacity: 0.75, line: { color: colors.predColor, width: 1 } }
            };

            const residualsLayout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: colors.fontColor, family: colors.fontFamily },
                xaxis: { title: 'Calibration Error (Predicted - Actual) (µg/m³)', gridcolor: colors.gridColor },
                yaxis: { title: 'Sample Count', gridcolor: colors.gridColor },
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
    }

    function renderComparePlot(data) {
        if (!document.getElementById('plotTimeSeriesCompare')) return;
        lastCompareData = data;
        const colors = getPlotlyThemeColors();

        const traceActual = {
            x: data.timestamps,
            y: data.actuals,
            mode: 'lines',
            name: 'Teledyne Reference',
            line: { color: colors.actualColor, width: 2.5 }
        };

        const traceBase = {
            x: data.timestamps,
            y: data.predictions,
            mode: 'lines',
            name: `Baseline: ${data.model_name}`,
            line: { color: colors.predColor, width: 3 }
        };

        const traces = [traceActual, traceBase];

        if (data.compare_predictions && data.compare_predictions.length > 0) {
            traces.push({
                x: data.timestamps,
                y: data.compare_predictions,
                mode: 'lines',
                name: `Compare: ${data.compare_name}`,
                line: { color: colors.compareColor, width: 2.5, dash: 'dash' }
            });
        }

        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: colors.fontColor, family: colors.fontFamily },
            xaxis: { gridcolor: colors.gridColor },
            yaxis: { title: 'PM2.5 Concentration (µg/m³)', gridcolor: colors.gridColor },
            margin: { t: 20, b: 40, l: 50, r: 20 },
            legend: { orientation: 'h', y: 1.15 }
        };

        safePlotly('plotTimeSeriesCompare', traces, layout, { responsive: true });
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
                model_key: modelSelect ? modelSelect.value : 'stacked_physics_meta_ensemble',
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

    // Safe User Authentication Status Check
    async function checkCurrentUser() {
        try {
            const res = await fetch('/api/auth/me');
            if (res.ok) {
                const data = await res.json();
                if (data.status === 'success' && data.user) {
                    currentUser = data.user;
                    if (userNameLabel) userNameLabel.textContent = currentUser.username;
                    if (userAvatarIcon) userAvatarIcon.textContent = currentUser.username.charAt(0).toUpperCase();
                }
            }
        } catch (e) {
            console.warn('Auth status check skipped:', e);
        }
    }

    // ==========================================================================
    // FEATURE: 24-HOUR AIR QUALITY & AQI FORECASTING SYSTEM
    // ==========================================================================
    const refreshForecastBtn = document.getElementById('refreshForecastBtn');
    if (refreshForecastBtn) {
        refreshForecastBtn.addEventListener('click', () => {
            loadForecastData(true);
        });
    }

    let isForecastLoading = false;
    let cachedForecastData = null;

    async function loadForecastData(forceRefresh = false) {
        if (isForecastLoading) return;
        if (!forceRefresh && cachedForecastData) {
            renderForecastUI(cachedForecastData);
            return;
        }

        isForecastLoading = true;
        const chartContainer = document.getElementById('forecastPlotlyChart');
        if (chartContainer && !cachedForecastData) {
            chartContainer.innerHTML = '<div style="display:flex; justify-content:center; align-items:center; height:100%; color:var(--text-muted);"><i class="fa-solid fa-spinner fa-spin" style="margin-right:8px;"></i> Loading 24-Hour Forecast Trajectory...</div>';
        }

        try {
            const res = await fetch('/api/forecast');
            const data = await res.json();
            if (data.status === 'success') {
                cachedForecastData = data;
                renderForecastUI(data);
            } else {
                console.error('Forecast API error:', data.message);
                if (chartContainer) {
                    chartContainer.innerHTML = `<div style="display:flex; justify-content:center; align-items:center; height:100%; color:#ef4444;"><i class="fa-solid fa-triangle-exclamation" style="margin-right:8px;"></i> Failed to load forecast: ${data.message}</div>`;
                }
            }
        } catch (e) {
            console.error('Error fetching 24h forecast:', e);
            if (chartContainer) {
                chartContainer.innerHTML = '<div style="display:flex; justify-content:center; align-items:center; height:100%; color:#ef4444;"><i class="fa-solid fa-triangle-exclamation" style="margin-right:8px;"></i> Failed to connect to forecast endpoint.</div>';
            }
        } finally {
            isForecastLoading = false;
        }
    }

    function renderForecastUI(data) {
        const kpis = data.kpis;
        const history = data.history || [];
        const forecast = data.forecast || [];

        // 1. Update KPI Elements
        const curPm = document.getElementById('fc-current-pm');
        const curAqi = document.getElementById('fc-current-aqi');
        const peakPm = document.getElementById('fc-peak-pm');
        const peakMeta = document.getElementById('fc-peak-meta');
        const avgPm = document.getElementById('fc-avg-pm');
        const avgAqi = document.getElementById('fc-avg-aqi');
        const trendStatus = document.getElementById('fc-trend-status');

        if (curPm) curPm.textContent = `${kpis.current_pm25.toFixed(1)} µg/m³`;
        if (curAqi) {
            curAqi.innerHTML = `<span style="color:${kpis.current_color}; font-weight:700;">AQI ${kpis.current_aqi} (${kpis.current_category})</span>`;
        }
        if (peakPm) peakPm.textContent = `${kpis.peak_pm25.toFixed(1)} µg/m³`;
        if (peakMeta) {
            peakMeta.innerHTML = `Peak at <strong>${kpis.peak_hour}</strong> <span style="color:${kpis.peak_color}; font-weight:600;">(AQI ${kpis.peak_aqi})</span>`;
        }
        if (avgPm) avgPm.textContent = `${kpis.avg_pm25.toFixed(1)} µg/m³`;
        if (avgAqi) {
            avgAqi.innerHTML = `<span style="color:${kpis.avg_color}; font-weight:700;">Mean AQI ${kpis.avg_aqi} (${kpis.avg_category})</span>`;
        }
        if (trendStatus) {
            trendStatus.textContent = kpis.trend_status;
            trendStatus.style.color = kpis.trend_color;
        }

        // 2. Update Proactive Advisory Alert Box
        const advCard = document.getElementById('forecastAdvisoryCard');
        const advIcon = document.getElementById('forecastAdvisoryIcon');
        const advTitle = document.getElementById('forecastAdvisoryTitle');
        const advText = document.getElementById('forecastAdvisoryText');

        if (advCard && advTitle && advText) {
            advTitle.textContent = kpis.advisory_title;
            advText.textContent = kpis.advisory_text;

            let borderCol = '#38bdf8';
            let bgCol = 'rgba(56, 189, 248, 0.08)';
            let iconHtml = '<i class="fa-solid fa-shield-heart"></i>';

            if (kpis.advisory_level === 'danger') {
                borderCol = '#ef4444';
                bgCol = 'rgba(239, 68, 68, 0.12)';
                iconHtml = '<i class="fa-solid fa-triangle-exclamation"></i>';
            } else if (kpis.advisory_level === 'warning') {
                borderCol = '#f97316';
                bgCol = 'rgba(249, 115, 22, 0.12)';
                iconHtml = '<i class="fa-solid fa-circle-exclamation"></i>';
            } else if (kpis.advisory_level === 'success') {
                borderCol = '#34d399';
                bgCol = 'rgba(52, 211, 153, 0.12)';
                iconHtml = '<i class="fa-solid fa-circle-check"></i>';
            }

            advCard.style.borderLeftColor = borderCol;
            advCard.style.background = bgCol;
            if (advIcon) {
                advIcon.style.color = borderCol;
                advIcon.innerHTML = iconHtml;
            }
            advTitle.style.color = borderCol;
        }

        // 3. Render Interactive Plotly Chart
        renderForecastPlot(history, forecast);

        // 4. Populate Hourly Schedule Breakdown Table
        renderForecastTable(forecast);
    }

    function renderForecastPlot(history, forecast) {
        const chartEl = document.getElementById('forecastPlotlyChart');
        if (!chartEl) return;

        const colors = getPlotlyThemeColors();

        const histX = history.map(h => h.timestamp);
        const histY = history.map(h => h.pm25);

        const fcX = forecast.map(f => f.timestamp);
        const fcY = forecast.map(f => f.pm25);
        const fcUpper = forecast.map(f => f.upper_bound);
        const fcLower = forecast.map(f => f.lower_bound);

        // Connect history and forecast smoothly
        const connX = history.length > 0 ? [history[history.length - 1].timestamp, ...fcX] : fcX;
        const connY = history.length > 0 ? [history[history.length - 1].pm25, ...fcY] : fcY;

        // Trace 1: Historical Calibrated (Past 24h)
        const traceHistory = {
            x: histX,
            y: histY,
            mode: 'lines+markers',
            name: 'Observed Calibrated (Past 24h)',
            line: { color: colors.actualColor || '#38bdf8', width: 3 },
            marker: { size: 5, color: colors.actualColor || '#38bdf8' }
        };

        // Trace 2: Upper Bound (Envelope Top)
        const traceUpper = {
            x: fcX,
            y: fcUpper,
            mode: 'lines',
            line: { width: 0, color: 'transparent' },
            showlegend: false,
            hoverinfo: 'skip'
        };

        // Trace 3: Lower Bound with fill
        const traceLower = {
            x: fcX,
            y: fcLower,
            mode: 'lines',
            fill: 'tonexty',
            fillcolor: 'rgba(249, 115, 22, 0.16)',
            line: { width: 0, color: 'transparent' },
            name: '90% Confidence Uncertainty Envelope',
            hoverinfo: 'skip'
        };

        // Trace 4: 24h Ahead Forecast Trajectory
        const traceForecast = {
            x: connX,
            y: connY,
            mode: 'lines+markers',
            name: '24-Hour Horizon Forecast',
            line: { color: '#f97316', width: 3, dash: 'dash' },
            marker: { size: 6, color: '#f97316' }
        };

        const traces = [traceHistory, traceUpper, traceLower, traceForecast];

        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            margin: { t: 30, r: 25, b: 50, l: 55 },
            font: { family: colors.fontFamily, color: colors.fontColor, size: 12 },
            hovermode: 'x unified',
            legend: {
                orientation: 'h',
                yanchor: 'bottom',
                y: 1.02,
                xanchor: 'right',
                x: 1,
                font: { color: colors.fontColor, size: 11 }
            },
            xaxis: {
                title: { text: 'Timeline (Past 24 Hours → Next 24 Hours)', font: { size: 12 } },
                gridcolor: colors.gridColor,
                zeroline: false
            },
            yaxis: {
                title: { text: 'PM2.5 Concentration (µg/m³)', font: { size: 12 } },
                gridcolor: colors.gridColor,
                zeroline: false
            },
            shapes: [
                // US EPA Moderate threshold (12 µg/m³)
                {
                    type: 'line',
                    xref: 'paper', x0: 0, x1: 1,
                    yref: 'y', y0: 12.0, y1: 12.0,
                    line: { color: '#34d399', width: 1.5, dash: 'dot' }
                },
                // US EPA USG threshold (35.4 µg/m³)
                {
                    type: 'line',
                    xref: 'paper', x0: 0, x1: 1,
                    yref: 'y', y0: 35.4, y1: 35.4,
                    line: { color: '#f59e0b', width: 1.5, dash: 'dot' }
                },
                // US EPA Unhealthy threshold (55.4 µg/m³)
                {
                    type: 'line',
                    xref: 'paper', x0: 0, x1: 1,
                    yref: 'y', y0: 55.4, y1: 55.4,
                    line: { color: '#ef4444', width: 1.5, dash: 'dot' }
                }
            ],
            annotations: [
                {
                    xref: 'paper', x: 0.02, yref: 'y', y: 12.0,
                    text: 'EPA Moderate (12 µg/m³)',
                    showarrow: false,
                    font: { size: 10, color: '#34d399' },
                    yshift: 10
                },
                {
                    xref: 'paper', x: 0.02, yref: 'y', y: 35.4,
                    text: 'EPA Sensitive (35.4 µg/m³)',
                    showarrow: false,
                    font: { size: 10, color: '#f59e0b' },
                    yshift: 10
                }
            ]
        };

        const config = { responsive: true, displayModeBar: true, displaylogo: false };
        safePlotly('forecastPlotlyChart', traces, layout, config);
    }

    function renderForecastTable(forecast) {
        const tableBody = document.getElementById('forecastTableBody');
        if (!tableBody) return;

        let rowsHtml = '';
        forecast.forEach(item => {
            let riskBadge = `<span class="badge" style="background:${item.aqi_color}22; color:${item.aqi_color}; border:1px solid ${item.aqi_color}66; font-weight:700;">${item.aqi_category}</span>`;
            
            let actionText = 'Normal activities permitted';
            if (item.pm25 >= 55.5) {
                actionText = '<strong style="color:#ef4444;">Sensitive groups stay indoors; reduce outdoor exertion</strong>';
            } else if (item.pm25 >= 35.5) {
                actionText = '<span style="color:#f97316;">Sensitive individuals should reduce prolonged outdoor exertion</span>';
            } else if (item.pm25 >= 12.1) {
                actionText = '<span style="color:#fbbf24;">Acceptable quality; sensitive groups consider taking breaks</span>';
            } else {
                actionText = '<span style="color:#34d399;">Clean air; excellent for outdoor recreation</span>';
            }

            rowsHtml += `
                <tr>
                    <td style="font-weight:700; color:#38bdf8;">+${item.horizon}h Ahead</td>
                    <td><strong>${item.hour_label}</strong> <span style="font-size:11px; color:var(--text-muted);">(${item.timestamp.split(' ')[0]})</span></td>
                    <td style="font-weight:700; font-size:14px;">${item.pm25.toFixed(2)} µg/m³</td>
                    <td style="color:var(--text-secondary); font-size:12px;">${item.lower_bound.toFixed(1)} - ${item.upper_bound.toFixed(1)} µg/m³</td>
                    <td><strong>AQI ${item.aqi_score}</strong></td>
                    <td>${riskBadge}</td>
                    <td style="font-size:12px;">${actionText}</td>
                </tr>
            `;
        });

        tableBody.innerHTML = rowsHtml;
    }

    // ==========================================================================
    // FEATURE: AIRSENSE AI RAG CHAT STUDIO
    // ==========================================================================
    async function loadChatSessions() {
        if (!chatSessionsList) return;
        try {
            const res = await fetch('/api/chat/sessions');
            const data = await res.json();
            if (data.status === 'success' && Array.isArray(data.sessions) && data.sessions.length > 0) {
                chatSessionsList.innerHTML = data.sessions.map(s => `
                    <div class="chat-session-item ${s.session_id === activeSessionId ? 'active' : ''}" data-id="${s.session_id}">
                        <i class="fa-regular fa-message" style="margin-right:6px; font-size:11px;"></i>
                        <span>${s.title || 'Conversation'}</span>
                    </div>
                `).join('');

                chatSessionsList.querySelectorAll('.chat-session-item').forEach(item => {
                    item.addEventListener('click', () => {
                        const sid = item.getAttribute('data-id');
                        selectChatSession(sid);
                    });
                });
            } else {
                chatSessionsList.innerHTML = '<div style="font-size:11px; color:var(--kv-text-muted); padding:8px 4px;">No previous discussions</div>';
            }
        } catch (e) {
            console.warn('Error loading chat sessions:', e);
        }
    }

    async function selectChatSession(sessionId) {
        activeSessionId = sessionId;
        if (chatSessionsList) {
            chatSessionsList.querySelectorAll('.chat-session-item').forEach(item => {
                if (item.getAttribute('data-id') === sessionId) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }

        try {
            const res = await fetch(`/api/chat/history/${sessionId}`);
            const data = await res.json();
            if (data.status === 'success' && Array.isArray(data.messages)) {
                renderChatMessages(data.messages);
            }
        } catch (e) {
            console.error('Error fetching chat history:', e);
        }
    }

    function renderChatMessages(messages) {
        if (!chatMessagesContainer) return;
        if (!messages || messages.length === 0) {
            chatMessagesContainer.innerHTML = `
                <div class="chat-msg-assistant">
                    <div class="rag-text">
                        Hello! I am <strong>AirSense AI</strong>, your atmospheric intelligence analyst at the Department of Physics, University of Ghana, Legon.
                        Ask me anything regarding current particulate pollution levels, Köhler hygroscopic particle corrections, SPIME v4 calibrations, or Harmattan dust dynamics.
                    </div>
                </div>
            `;
            return;
        }

        chatMessagesContainer.innerHTML = messages.map(m => {
            if (m.role === 'user') {
                return `<div class="chat-msg-user">${m.content}</div>`;
            } else {
                return `
                    <div class="chat-msg-assistant">
                        <div class="rag-text">${safeRenderMarkdown(m.content)}</div>
                    </div>
                `;
            }
        }).join('');
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    async function sendChatMessage(customText = null) {
        const text = customText || (chatInputText ? chatInputText.value.trim() : '');
        if (!text) return;

        if (chatInputText) chatInputText.value = '';

        // Render user message immediately
        if (chatMessagesContainer) {
            const userMsgEl = document.createElement('div');
            userMsgEl.className = 'chat-msg-user';
            userMsgEl.textContent = text;
            chatMessagesContainer.appendChild(userMsgEl);

            const typingEl = document.createElement('div');
            typingEl.className = 'chat-msg-assistant';
            typingEl.id = 'chatTypingIndicator';
            typingEl.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing air quality physics and station data...';
            chatMessagesContainer.appendChild(typingEl);
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        }

        try {
            const activeModel = (settingsPrimaryModel && settingsPrimaryModel.value) || systemSettings.primary_model_key || 'stacked_physics_meta_ensemble';
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: text,
                    session_id: activeSessionId,
                    model_key: activeModel
                })
            });
            const data = await res.json();

            const typingEl = document.getElementById('chatTypingIndicator');
            if (typingEl) typingEl.remove();

            if (data.status === 'success') {
                if (data.session_id) activeSessionId = data.session_id;

                if (chatMessagesContainer) {
                    const botMsgEl = document.createElement('div');
                    botMsgEl.className = 'chat-msg-assistant';
                    botMsgEl.innerHTML = `<div class="rag-text">${safeRenderMarkdown(data.answer)}</div>`;
                    chatMessagesContainer.appendChild(botMsgEl);
                    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
                }
                loadChatSessions();
            } else {
                if (chatMessagesContainer) {
                    const errEl = document.createElement('div');
                    errEl.className = 'chat-msg-assistant';
                    errEl.style.borderColor = 'var(--kv-red)';
                    errEl.innerHTML = `<div class="rag-text" style="color:var(--kv-red);"><i class="fa-solid fa-triangle-exclamation"></i> ${data.message || 'Error communicating with AirSense AI'}</div>`;
                    chatMessagesContainer.appendChild(errEl);
                    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
                }
            }
        } catch (e) {
            console.error('Chat error:', e);
            const typingEl = document.getElementById('chatTypingIndicator');
            if (typingEl) typingEl.remove();
            if (chatMessagesContainer) {
                const errEl = document.createElement('div');
                errEl.className = 'chat-msg-assistant';
                errEl.style.borderColor = 'var(--kv-red)';
                errEl.innerHTML = `<div class="rag-text" style="color:var(--kv-red);"><i class="fa-solid fa-triangle-exclamation"></i> Network error connecting to AirSense AI.</div>`;
                chatMessagesContainer.appendChild(errEl);
                chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
            }
        }
    }

    if (sendChatBtn) {
        sendChatBtn.addEventListener('click', () => sendChatMessage());
    }

    if (chatInputText) {
        chatInputText.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }

    if (newChatBtn) {
        newChatBtn.addEventListener('click', async () => {
            activeSessionId = null;
            renderChatMessages([]);
            if (chatSessionsList) {
                chatSessionsList.querySelectorAll('.chat-session-item').forEach(i => i.classList.remove('active'));
            }
            try {
                const res = await fetch('/api/chat/new', { method: 'POST' });
                const data = await res.json();
                if (data.status === 'success' && data.session) {
                    activeSessionId = data.session.session_id;
                    loadChatSessions();
                }
            } catch (e) {
                console.warn('New chat error:', e);
            }
        });
    }

    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            renderChatMessages([]);
        });
    }

    // Quick suggestion prompt chips
    document.querySelectorAll('.chip-btn').forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            if (prompt) sendChatMessage(prompt);
        });
    });

    // ==========================================================================
    // CONTINUOUS LEARNING / RETRAINING PIPELINE
    // ==========================================================================
    if (selectFileBtn && refFileInput) {
        selectFileBtn.addEventListener('click', () => {
            refFileInput.click();
        });
        refFileInput.addEventListener('change', () => {
            if (refFileInput.files && refFileInput.files[0]) {
                if (selectedFileName) {
                    selectedFileName.textContent = `Selected: ${refFileInput.files[0].name} (${(refFileInput.files[0].size / 1024).toFixed(1)} KB)`;
                }
            } else if (selectedFileName) {
                selectedFileName.textContent = '';
            }
        });
    }

    if (uploadRefBtn && refFileInput) {
        uploadRefBtn.addEventListener('click', async () => {
            if (!refFileInput.files || !refFileInput.files[0]) {
                alert('Please select a reference CSV or Excel file first.');
                return;
            }

            const file = refFileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            uploadRefBtn.disabled = true;
            uploadRefBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing & Retraining...';

            try {
                const res = await fetch('/api/upload_reference', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                uploadRefBtn.disabled = false;
                uploadRefBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Upload & Retrain';

                if (retrainResultCard) {
                    retrainResultCard.style.display = 'block';
                    if (data.status === 'success') {
                        if (retrainStatusTitle) {
                            retrainStatusTitle.innerHTML = `<i class="fa-solid fa-circle-check" style="color:var(--color-success);"></i> ${data.message || 'Retraining completed successfully!'}`;
                        }
                        if (retrainMetricsGrid && data.retrain_metrics) {
                            const m = data.retrain_metrics;
                            retrainMetricsGrid.innerHTML = `
                                <div class="stat-item">
                                    <span class="stat-title">New R² Score</span>
                                    <div class="stat-value" style="color:var(--color-success);">${m.new_r2 != null ? Number(m.new_r2).toFixed(4) : '--'}</div>
                                    <span class="stat-sub">Prev: ${m.old_r2 != null ? Number(m.old_r2).toFixed(4) : '--'}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-title">New MAE</span>
                                    <div class="stat-value">${m.new_mae != null ? Number(m.new_mae).toFixed(2) + ' µg/m³' : '--'}</div>
                                    <span class="stat-sub">Prev: ${m.old_mae != null ? Number(m.old_mae).toFixed(2) : '--'}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-title">Aligned Samples</span>
                                    <div class="stat-value">${m.matched_samples != null ? m.matched_samples : '--'}</div>
                                    <span class="stat-sub">Matched timestamps</span>
                                </div>
                            `;
                        }
                    } else {
                        if (retrainStatusTitle) {
                            retrainStatusTitle.innerHTML = `<i class="fa-solid fa-circle-exclamation" style="color:var(--color-error);"></i> ${data.message || 'Retraining pipeline failed.'}`;
                        }
                    }
                }

                loadRetrainHistory();
            } catch (err) {
                uploadRefBtn.disabled = false;
                uploadRefBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Upload & Retrain';
                alert('Retraining request failed: ' + err.message);
            }
        });
    }

    async function loadRetrainHistory() {
        if (!retrainHistoryBody) return;
        try {
            const res = await fetch('/api/retrain/history');
            const data = await res.json();
            if (data.status === 'success' && Array.isArray(data.history) && data.history.length > 0) {
                retrainHistoryBody.innerHTML = data.history.map(item => `
                    <tr>
                        <td><strong>${item.model_key || 'SPIME Ensemble'}</strong><br><span style="font-size:11px; color:var(--color-text-dim);">${item.filename || 'Direct upload'}</span></td>
                        <td>${item.old_r2 != null ? Number(item.old_r2).toFixed(4) : '--'}</td>
                        <td><span class="badge badge-success">${item.new_r2 != null ? Number(item.new_r2).toFixed(4) : '--'}</span></td>
                        <td>${item.old_mae != null ? Number(item.old_mae).toFixed(2) + ' µg/m³' : '--'}</td>
                        <td>${item.new_mae != null ? Number(item.new_mae).toFixed(2) + ' µg/m³' : '--'}</td>
                        <td>${item.matched_samples != null ? item.matched_samples.toLocaleString() : '--'}</td>
                        <td><span class="badge badge-success"><i class="fa-solid fa-check"></i> ${item.status || 'Active'}</span></td>
                    </tr>
                `).join('');
            } else {
                retrainHistoryBody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align:center; color:var(--color-text-dim); padding:24px;">
                            <i class="fa-solid fa-clock-rotate-left" style="font-size:24px; margin-bottom:8px; display:block; opacity:0.4;"></i>
                            No retrain events recorded yet. Upload reference monitor data above to run continuous learning.
                        </td>
                    </tr>
                `;
            }
        } catch (e) {
            console.warn('Error loading retrain history:', e);
        }
    }

    // ==========================================================================
    // AUTH MODAL OPEN / CLOSE
    // ==========================================================================
    function openAuthModal() {
        if (authModal) authModal.classList.add('active');
    }
    function closeAuthModal() {
        if (authModal) authModal.classList.remove('active');
    }
    if (userAuthBtn) userAuthBtn.addEventListener('click', openAuthModal);
    if (closeAuthModalBtn) closeAuthModalBtn.addEventListener('click', closeAuthModal);
    if (authModal) {
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal) closeAuthModal();
        });
    }
    // Auth tabs
    if (authTabLogin) {
        authTabLogin.addEventListener('click', () => {
            authTabLogin.classList.add('active');
            if (authTabRegister) authTabRegister.classList.remove('active');
            if (loginForm) loginForm.style.display = '';
            if (registerForm) registerForm.style.display = 'none';
        });
    }
    if (authTabRegister) {
        authTabRegister.addEventListener('click', () => {
            authTabRegister.classList.add('active');
            if (authTabLogin) authTabLogin.classList.remove('active');
            if (loginForm) loginForm.style.display = 'none';
            if (registerForm) registerForm.style.display = '';
        });
    }
    // Login
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername')?.value || '';
            const password = document.getElementById('loginPassword')?.value || '';
            if (authErrorMsg) authErrorMsg.style.display = 'none';
            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                if (data.status === 'success' && data.user) {
                    currentUser = data.user;
                    if (userNameLabel) userNameLabel.textContent = currentUser.username;
                    if (userAvatarIcon) userAvatarIcon.textContent = currentUser.username.charAt(0).toUpperCase();
                    closeAuthModal();
                } else {
                    if (authErrorMsg) { authErrorMsg.textContent = data.message || 'Login failed.'; authErrorMsg.style.display = 'block'; }
                }
            } catch (err) {
                if (authErrorMsg) { authErrorMsg.textContent = 'Network error. Please try again.'; authErrorMsg.style.display = 'block'; }
            }
        });
    }
    // Register
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('regUsername')?.value || '';
            const email = document.getElementById('regEmail')?.value || '';
            const password = document.getElementById('regPassword')?.value || '';
            if (regErrorMsg) regErrorMsg.style.display = 'none';
            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    if (userNameLabel) userNameLabel.textContent = username;
                    if (userAvatarIcon) userAvatarIcon.textContent = username.charAt(0).toUpperCase();
                    closeAuthModal();
                } else {
                    if (regErrorMsg) { regErrorMsg.textContent = data.message || 'Registration failed.'; regErrorMsg.style.display = 'block'; }
                }
            } catch (err) {
                if (regErrorMsg) { regErrorMsg.textContent = 'Network error. Please try again.'; regErrorMsg.style.display = 'block'; }
            }
        });
    }

    // Defensive Fail-Safe Initializations
    (async () => {
        try {
            initThemeToggle();
        } catch (e) {
            console.warn('Theme toggle init note:', e);
        }

        try {
            await checkCurrentUser();
        } catch (e) {
            console.warn('Auth init note:', e);
        }

        try {
            await loadSystemSettings();
        } catch (e) {
            console.warn('System settings init note:', e);
        }

        try {
            await loadModelsRegistry();
        } catch (e) {
            console.warn('Models registry init note:', e);
        }

        try {
            fetchLiveTelemetry();
            if (refreshTimerId) clearInterval(refreshTimerId);
            refreshTimerId = setInterval(fetchLiveTelemetry, activeRefreshInterval);
            restoreActiveTab();
            runInference();
        } catch (e) {
            console.error('Core init error:', e);
        }
    })();
});
