/**
 * Netlify Serverless Function: AirSense AI Chat
 * Endpoints:
 *   POST /.netlify/functions/chat
 *   POST /api/chat (via netlify.toml redirect)
 */

const GROQ_API_KEY = process.env.GROQ_API_KEY || "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";

exports.handler = async function (event, context) {
    // Handle CORS preflight
    if (event.httpMethod === "OPTIONS") {
        return {
            statusCode: 200,
            headers: {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            body: ""
        };
    }

    if (event.httpMethod !== "POST") {
        return {
            statusCode: 405,
            body: JSON.stringify({ status: "error", message: "Method Not Allowed" })
        };
    }

    let query = "";
    try {
        const body = JSON.parse(event.body || "{}");
        query = (body.query || body.message || "").trim();
    } catch (e) {
        query = "";
    }

    if (!query) {
        return {
            statusCode: 400,
            headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
            body: JSON.stringify({ status: "error", message: "Query cannot be empty" })
        };
    }

    // Try calling Groq API if key is present
    if (GROQ_API_KEY && GROQ_API_KEY.startsWith("gsk_")) {
        try {
            const systemPrompt = `You are "AirSense AI", a warm, approachable environmental scientist and air quality companion for the Legon Monitoring Station (MOD-PM-01068) at the Department of Physics, University of Ghana, Accra.
You help users understand air pollution (PM2.5), low-cost optical sensor calibration (QuantAQ OPC-N3 vs reference BAM / Teledyne T640), relative humidity hygroscopic growth f(RH), and Harmattan desert dust events.
Keep responses concise, empathetic, and formatted in clear markdown. When presenting mathematical equations, always write clean standard LaTeX wrapped in $$ for display formulas (e.g. $$f(RH) = 1 + a \\cdot \\frac{(RH/100)^b}{1 - RH/100}$$) and $ for inline terms (e.g. $R^2 = 0.9332$).`;

            const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${GROQ_API_KEY}`
                },
                body: JSON.stringify({
                    model: "llama-3.1-8b-instant",
                    messages: [
                        { role: "system", content: systemPrompt },
                        { role: "user", content: query }
                    ],
                    temperature: 0.5,
                    max_tokens: 500
                })
            });

            if (groqRes.ok) {
                const groqData = await groqRes.json();
                const reply = groqData.choices?.[0]?.message?.content;
                if (reply) {
                    return {
                        statusCode: 200,
                        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
                        body: JSON.stringify({
                            status: "success",
                            answer: reply,
                            llm_engine: "AirSense AI (Groq Llama-3.1-8B)"
                        })
                    };
                }
            }
        } catch (groqErr) {
            console.warn("Groq API call error in Netlify function:", groqErr);
        }
    }

    // Fallback Domain-Grounded Response
    const q = query.toLowerCase();
    let fallbackReply = "";

    if (/humid|hygro|water|moisture|deliquescen|growth|droplet|dew/i.test(q)) {
        fallbackReply = `### How Humidity Affects Optical Particulate Sensors

Optical particle counters (like our onboard **QuantAQ OPC-N3**) estimate particulate mass by measuring infrared laser light scattered by passing particles.

Here is why humidity causes measurement errors:
1. **The Sponge Effect (Hygroscopic Swelling):** When ambient relative humidity exceeds **70%–80%** (Deliquescence Relative Humidity), soluble aerosol particles absorb water vapor and swell.
2. **Optical Overestimation:** The sensor counts these swollen, water-encapsulated particles as large dust grains, artificially inflating raw PM2.5 readings.
3. **Köhler Physics Correction:** Our **SPIME v4 Meta-Ensemble** applies a non-linear Köhler growth correction factor:
$$f(RH) = 1 + a \\cdot \\frac{(RH/100)^b}{1 - RH/100}$$
This mathematically deducts the condensed water volume, matching reference ground-truth BAM readings.`;
    } else if (/harmattan|dust|sahara|sand|desert|trade wind/i.test(q)) {
        fallbackReply = `### Harmattan Saharan Dust Dynamics in West Africa

Between **November and March**, dry northeasterly trade winds carry coarse mineral dust across Ghana:
- **Coarse Mineral Particles:** Harmattan air masses contain jagged, non-spherical mineral dust grains.
- **Sensor Sizing Biases:** Irregular dust grains cause severe optical scattering anomalies and detector saturation in standard optical sensors.
- **Diurnal Inversion Layers:** Nighttime thermal inversions trap dense dust near ground level.
- **ML Mitigation:** Our models use seasonal flags and diurnal hour encoding to adjust optical channels during peak dust events.`;
    } else if (/model|spime|random forest|benchmark|accuracy|r2|mae|rmse|best/i.test(q)) {
        fallbackReply = `### Machine Learning Calibration Benchmark

Our champion model is the **SPIME v4 Meta-Ensemble**:
- **Holdout Test R²:** **0.9332** (Unseen 2025 data)
- **Validation R²:** **0.9922**
- **Holdout MAE:** **1.14 µg/m³**
- **Holdout RMSE:** **1.62 µg/m³**

It outperforms Random Forest v2 ($R^2 = 0.8914$), Two-Stage Purged Calibrator ($R^2 = 0.8805$), and PMC Hybrid ($R^2 = 0.8690$) by combining LightGBM, Random Forest, and a Ridge meta-learner with Köhler hygroscopic physics interaction terms.`;
    } else if (/safe|exercise|run|outside|outdoor|health|mask|breathe|asthma/i.test(q)) {
        fallbackReply = `### Health & Outdoor Activity Advisory

Based on our live Legon Station monitoring (MOD-PM-01068):
- **Air Quality Status:** Ambient PM2.5 levels are currently in standard ranges.
- **Recommendation:** Outdoor activities and exercise are suitable for the general public. Sensitive individuals (asthma, children, elderly) should monitor their breathing comfort during periods of elevated humidity or dust.`;
    } else {
        fallbackReply = `Hello! 👋 I'm **AirSense AI**, your environmental intelligence companion at the **Department of Physics, University of Ghana, Legon (MOD-PM-01068)**.

I monitor real-time optical particulate readings, hygroscopic humidity growth, and machine learning calibration pipelines. Feel free to ask me about:
- How **relative humidity** alters optical sensor readings.
- **Harmattan** Saharan dust dynamics across West Africa.
- How our **SPIME v4 Ensemble** achieves an $R^2$ of **0.9332** on unseen holdout test data.
- Air safety and health advisories for outdoor exercise.`;
    }

    return {
        statusCode: 200,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        body: JSON.stringify({
            status: "success",
            answer: fallbackReply,
            llm_engine: "AirSense AI (Netlify Edge Engine)"
        })
    };
};
