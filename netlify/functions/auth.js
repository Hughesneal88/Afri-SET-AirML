const crypto = require("crypto");
const { MongoClient } = require("mongodb");

const headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
};

let clientPromise = null;

function getDb() {
    const uri = process.env.MONGO_URI;
    if (!uri) throw new Error("MONGO_URI is not configured");
    if (!clientPromise) {
        clientPromise = new MongoClient(uri, { serverSelectionTimeoutMS: 8000 }).connect();
    }
    return clientPromise.then((client) => client.db(process.env.MONGO_DB_NAME || "airsense_db"));
}

function generateKey() {
    const hex = crypto.randomBytes(4).toString("hex").toUpperCase();
    return `AIR-US-${hex.slice(0, 4)}-${hex.slice(4, 8)}`;
}

function publicUser(doc) {
    return {
        id: String(doc._id),
        username: doc.username,
        unique_key: doc.unique_key,
        email: doc.email
    };
}

async function usersCollection() {
    const db = await getDb();
    const users = db.collection("users");
    await users.createIndex({ unique_key: 1 }, { unique: true, sparse: true });
    return users;
}

async function createUser(username, customKey) {
    const users = await usersCollection();
    let uniqueKey = (customKey || generateKey()).trim().toUpperCase();
    if (!uniqueKey) uniqueKey = generateKey();
    const existingKey = await users.findOne({ unique_key: uniqueKey });
    if (existingKey) return { error: "That unique key already exists. Leave the field blank to generate a new one." };

    let name = (username || `Researcher-${uniqueKey.slice(-4)}`).trim();
    const sameName = await users.findOne({ username: name });
    if (sameName) name = `${name} (${uniqueKey.slice(-4)})`;

    const doc = {
        _id: crypto.randomUUID(),
        username: name,
        unique_key: uniqueKey,
        email: `${uniqueKey.toLowerCase()}@airsense.local`,
        created_at: new Date().toISOString()
    };
    await users.insertOne(doc);
    return { user: publicUser(doc) };
}

async function findByKey(uniqueKey) {
    const users = await usersCollection();
    const doc = await users.findOne({ unique_key: String(uniqueKey || "").trim().toUpperCase() });
    return doc ? publicUser(doc) : null;
}

function json(statusCode, body) {
    return { statusCode, headers, body: JSON.stringify(body) };
}

async function handleAuth(event, action) {
    if (event.httpMethod === "OPTIONS") return { statusCode: 200, headers, body: "" };

    let payload = {};
    if (event.body) {
        try {
            payload = JSON.parse(event.body);
        } catch (error) {
            payload = {};
        }
    }

    try {
        if (action === "generate" || action === "register") {
            if (event.httpMethod !== "POST") return json(405, { status: "error", message: "Method Not Allowed" });
            const created = await createUser(payload.username, payload.unique_key || payload.key);
            if (created.error) return json(400, { status: "error", message: created.error });
            return json(200, {
                status: "success",
                message: "Unique Access Key generated successfully!",
                user: created.user,
                unique_key: created.user.unique_key
            });
        }

        if (action === "login") {
            if (event.httpMethod !== "POST") return json(405, { status: "error", message: "Method Not Allowed" });
            const user = await findByKey(payload.unique_key || payload.key || payload.username);
            if (!user) {
                return json(401, {
                    status: "error",
                    message: "Invalid Unique Access Key. Please check the string and try again, or generate a new key."
                });
            }
            return json(200, {
                status: "success",
                message: `Welcome back, ${user.username}!`,
                user,
                unique_key: user.unique_key
            });
        }

        if (action === "me") {
            const key = (event.headers && (event.headers["x-unique-key"] || event.headers["X-Unique-Key"])) || "";
            const user = key ? await findByKey(key) : null;
            if (!user) return json(200, { status: "guest", authenticated: false, user: null });
            return json(200, { status: "success", authenticated: true, user, unique_key: user.unique_key });
        }

        if (action === "logout") {
            return json(200, { status: "success", message: "Logged out." });
        }

        return json(404, { status: "error", message: "Unknown auth action" });
    } catch (error) {
        return json(503, { status: "error", message: "Could not reach the account database. Please try again." });
    }
}

exports.handleAuth = handleAuth;

exports.handler = async function (event) {
    const action = (event.queryStringParameters && event.queryStringParameters.action) || "";
    return handleAuth(event, action);
};
