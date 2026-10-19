const { MongoClient } = require("mongodb");
const seed = require("./readings-seed.json");

const DB_NAME = process.env.MONGO_DB_NAME || "airsense_db";
let clientPromise = null;

function readingKey(doc) {
    const device = doc.device_sn || "MOD-PM-01068";
    return [
        String(doc.timestamp),
        Number(doc.raw_pm25),
        Number(doc.temperature),
        Number(doc.humidity),
        device
    ].join("|");
}

function getClient() {
    const uri = process.env.MONGO_URI;
    if (!uri) {
        throw new Error("MONGO_URI is not configured");
    }
    if (!clientPromise) {
        const client = new MongoClient(uri, { serverSelectionTimeoutMS: 8000 });
        clientPromise = client.connect();
    }
    return clientPromise;
}

async function readingsCollection() {
    const client = await getClient();
    const db = client.db(DB_NAME);
    const collection = db.collection("raw_telemetry_logs");
    await collection.createIndex(
        { reading_key: 1 },
        { unique: true, partialFilterExpression: { reading_key: { $type: "string" } } }
    );
    return collection;
}

async function ensureSeed(collection) {
    const count = await collection.countDocuments({ reading_key: { $type: "string" } });
    if (count >= seed.length) return count;
    const operations = seed.map((doc) => ({
        updateOne: {
            filter: { reading_key: doc.reading_key },
            update: { $setOnInsert: doc },
            upsert: true
        }
    }));
    for (let index = 0; index < operations.length; index += 400) {
        await collection.bulkWrite(operations.slice(index, index + 400), { ordered: false });
    }
    return collection.countDocuments();
}

function normalizeReading(body) {
    const timestamp = String(body.timestamp || "").trim();
    const rawPm = Number(body.raw_pm25);
    const temperature = Number(body.temperature);
    const humidity = Number(body.humidity);
    if (!timestamp || Number.isNaN(rawPm) || Number.isNaN(temperature) || Number.isNaN(humidity)) {
        return null;
    }
    const doc = {
        timestamp,
        raw_pm25: rawPm,
        temperature,
        humidity,
        device_sn: body.device_sn || "MOD-PM-01068",
        created_at: new Date().toISOString()
    };
    doc.reading_key = readingKey(doc);
    return doc;
}

async function storeReading(body) {
    const doc = normalizeReading(body);
    if (!doc) return { stored: false };
    const collection = await readingsCollection();
    await ensureSeed(collection);
    const result = await collection.updateOne(
        { reading_key: doc.reading_key },
        { $setOnInsert: doc },
        { upsert: true }
    );
    return { stored: result.upsertedCount === 1 || result.upsertedId != null, duplicate: result.matchedCount > 0 };
}

async function loadReadings() {
    const collection = await readingsCollection();
    await ensureSeed(collection);
    return collection.find(
        {},
        { projection: { _id: 0, timestamp: 1, raw_pm25: 1, temperature: 1, humidity: 1, device_sn: 1 } }
    ).toArray();
}

module.exports = { loadReadings, storeReading };
