const { loadReadings } = require("./readings-db");
const { buildForecastPayload } = require("./hourly");

const headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Cache-Control": "no-store"
};

exports.handler = async function (event) {
    if (event.httpMethod === "OPTIONS") {
        return { statusCode: 200, headers, body: "" };
    }
    if (event.httpMethod !== "GET") {
        return { statusCode: 405, headers, body: JSON.stringify({ status: "error", message: "Method Not Allowed" }) };
    }
    try {
        const readings = await loadReadings();
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(buildForecastPayload(readings))
        };
    } catch (error) {
        return {
            statusCode: 503,
            headers,
            body: JSON.stringify({ status: "error", message: "Reading database is unavailable" })
        };
    }
};
