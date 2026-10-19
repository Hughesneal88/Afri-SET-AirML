const { storeReading } = require("./readings-db");

const headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS"
};

exports.handler = async function (event) {
    if (event.httpMethod === "OPTIONS") {
        return { statusCode: 200, headers, body: "" };
    }
    if (event.httpMethod !== "POST") {
        return { statusCode: 405, headers, body: JSON.stringify({ status: "error", message: "Method Not Allowed" }) };
    }
    let body = {};
    try {
        body = JSON.parse(event.body || "{}");
    } catch (error) {
        body = {};
    }
    try {
        const result = await storeReading(body);
        const statusCode = result.stored || result.duplicate ? 200 : 400;
        return { statusCode, headers, body: JSON.stringify({ status: statusCode === 200 ? "success" : "error", ...result }) };
    } catch (error) {
        return {
            statusCode: 503,
            headers,
            body: JSON.stringify({ status: "error", message: "Reading database is unavailable" })
        };
    }
};
