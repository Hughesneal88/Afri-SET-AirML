const HIT_THRESHOLD = 2.0;

function parseTimestamp(value) {
    const match = String(value || "").match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})/);
    if (!match) return null;
    const [, year, month, day, hour, minute, second] = match.map(Number);
    return new Date(Date.UTC(year, month - 1, day, hour, minute, second));
}

function formatTimestamp(date) {
    const pad = (n) => String(n).padStart(2, "0");
    return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())}`;
}

function hourLabel(date, showDate) {
    const clock = `${String(date.getUTCHours()).padStart(2, "0")}:00`;
    if (!showDate) return clock;
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${date.getUTCDate()} ${months[date.getUTCMonth()]} ${clock}`;
}

function aqi(pm25) {
    let c = Math.max(0, Number(pm25) || 0);
    c = Math.floor(c * 10 + 1e-8) / 10;
    const breakpoints = [
        [0.0, 12.0, 0, 50, "Good", "#34d399"],
        [12.1, 35.4, 51, 100, "Moderate", "#fbbf24"],
        [35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups", "#f97316"],
        [55.5, 150.4, 151, 200, "Unhealthy", "#ef4444"],
        [150.5, 250.4, 201, 300, "Very Unhealthy", "#a855f7"],
        [250.5, 500.4, 301, 500, "Hazardous", "#78350f"]
    ];
    for (const [lo, hi, iLo, iHi, category, color] of breakpoints) {
        if (c >= lo && c <= hi) {
            const score = Math.round(((iHi - iLo) / (hi - lo)) * (c - lo) + iLo);
            return { aqi_score: score, category, color };
        }
    }
    if (c > 500.4) return { aqi_score: 500, category: "Hazardous (Extreme Dust)", color: "#451a03" };
    return { aqi_score: 50, category: "Good", color: "#34d399" };
}

function diurnal(hour) {
    return 4.2 * Math.sin((2 * Math.PI * (hour - 3)) / 24) + 1.8 * Math.cos((4 * Math.PI * (hour - 8)) / 24);
}

function round(value, digits) {
    const factor = 10 ** digits;
    return Math.round(value * factor) / factor;
}

function hourlyHistory(readings) {
    const buckets = new Map();
    readings.forEach((reading) => {
        const stamp = parseTimestamp(reading.timestamp);
        if (!stamp || Number.isNaN(Number(reading.raw_pm25))) return;
        const hour = new Date(Date.UTC(stamp.getUTCFullYear(), stamp.getUTCMonth(), stamp.getUTCDate(), stamp.getUTCHours()));
        const key = hour.getTime();
        const slot = buckets.get(key) || { hour, raw: [], temp: [], rh: [] };
        slot.raw.push(Number(reading.raw_pm25));
        slot.temp.push(Number(reading.temperature) || 0);
        slot.rh.push(Number(reading.humidity) || 0);
        buckets.set(key, slot);
    });
    const hours = [...buckets.values()].sort((a, b) => a.hour - b.hour);
    const showDate = hours.length > 1 && (hours[hours.length - 1].hour - hours[0].hour) > 26 * 3600000;
    return hours.map((slot) => {
        const mean = (values) => values.reduce((sum, value) => sum + value, 0) / values.length;
        const pm = round(mean(slot.raw), 2);
        const info = aqi(pm);
        return {
            timestamp: formatTimestamp(slot.hour),
            hour_label: hourLabel(slot.hour, showDate),
            pm25: pm,
            raw_pm25: pm,
            temp: round(mean(slot.temp), 1),
            rh: round(mean(slot.rh), 1),
            readings: slot.raw.length,
            aqi_score: info.aqi_score,
            aqi_category: info.category,
            aqi_color: info.color
        };
    });
}

function forwardForecast(history) {
    if (!history.length) return [];
    const last = history[history.length - 1];
    const anchor = parseTimestamp(last.timestamp);
    const ref = diurnal(anchor.getUTCHours());
    const points = [];
    for (let horizon = 1; horizon <= 24; horizon += 1) {
        const future = new Date(anchor.getTime() + horizon * 3600000);
        const pm = Math.max(1.5, last.pm25 + (diurnal(future.getUTCHours()) - ref));
        const info = aqi(pm);
        points.push({
            horizon,
            timestamp: formatTimestamp(future),
            hour_label: hourLabel(future, false),
            pm25: round(pm, 2),
            lower_bound: round(Math.max(0, pm - 4.5), 2),
            upper_bound: round(pm + 4.5, 2),
            aqi_score: info.aqi_score,
            aqi_category: info.category,
            aqi_color: info.color
        });
    }
    return points;
}

function scoreHours(history) {
    const points = [];
    history.forEach((hour, index) => {
        const stamp = parseTimestamp(hour.timestamp);
        let source = null;
        for (let earlier = index - 1; earlier >= 0; earlier -= 1) {
            const previous = parseTimestamp(history[earlier].timestamp);
            const gap = (stamp - previous) / 3600000;
            if (gap > 0 && gap <= 3) {
                source = history[earlier];
                break;
            }
            if (gap > 3) break;
        }
        if (!source) return;
        const sourceStamp = parseTimestamp(source.timestamp);
        const forecastPm = Math.max(1, round(source.pm25 + (diurnal(stamp.getUTCHours()) - diurnal(sourceStamp.getUTCHours())), 2));
        const error = round(forecastPm - hour.pm25, 2);
        const info = aqi(forecastPm);
        points.push({
            timestamp: hour.timestamp,
            hour_label: hour.hour_label,
            issued_at: source.timestamp,
            issued_label: source.hour_label,
            readings: hour.readings,
            actual_pm25: hour.pm25,
            forecast_pm25: forecastPm,
            pm25: hour.pm25,
            error,
            abs_error: round(Math.abs(error), 2),
            came_true: Math.abs(error) <= HIT_THRESHOLD,
            within_bounds: Math.abs(error) <= HIT_THRESHOLD,
            lower_bound: round(Math.max(0, forecastPm - HIT_THRESHOLD), 2),
            upper_bound: round(forecastPm + HIT_THRESHOLD, 2),
            actual_aqi: hour.aqi_score,
            actual_category: hour.aqi_category,
            actual_color: hour.aqi_color,
            forecast_aqi: info.aqi_score,
            forecast_category: info.category,
            forecast_color: info.color,
            aqi_score: hour.aqi_score,
            aqi_category: hour.aqi_category,
            aqi_color: hour.aqi_color
        });
    });
    if (!points.length) {
        return {
            points,
            kpis: {
                mae: null,
                mbe: null,
                hit_threshold: HIT_THRESHOLD,
                hit_count: 0,
                scored_count: 0,
                hit_rate: null,
                status_summary: "No later hour is available to score a forecast yet."
            }
        };
    }
    const errors = points.map((point) => point.error);
    const mae = errors.reduce((sum, value) => sum + Math.abs(value), 0) / errors.length;
    const mbe = errors.reduce((sum, value) => sum + value, 0) / errors.length;
    const hits = points.filter((point) => point.came_true).length;
    const sign = mbe >= 0 ? "+" : "";
    return {
        points,
        kpis: {
            mae: round(mae, 2),
            mbe: round(mbe, 2),
            hit_threshold: HIT_THRESHOLD,
            hit_count: hits,
            scored_count: points.length,
            hit_rate: round((100 * hits) / points.length, 1),
            status_summary: `MAE ${mae.toFixed(2)} µg/m³ · MBE ${sign}${mbe.toFixed(2)} µg/m³ · ${hits} of ${points.length} hourly forecasts came true`
        }
    };
}

function distinctReadings(readings) {
    const seen = new Set();
    const unique = [];
    readings.forEach((reading) => {
        const key = [
            reading.timestamp,
            Number(reading.raw_pm25),
            Number(reading.temperature),
            Number(reading.humidity)
        ].join("|");
        if (seen.has(key)) return;
        seen.add(key);
        unique.push(reading);
    });
    return unique;
}

function buildForecastPayload(readings) {
    const uniqueReadings = distinctReadings(readings);
    const history = hourlyHistory(uniqueReadings);
    const forecast = forwardForecast(history);
    const verification = scoreHours(history);
    const last = history[history.length - 1] || {};
    const peak = forecast.reduce((best, point) => (point.pm25 > (best?.pm25 || -1) ? point : best), null);
    return {
        status: "success",
        source: "mongodb",
        reading_count: uniqueReadings.length,
        model_name: "Hourly mean of stored Modulair-PM readings",
        history,
        forecast,
        verification,
        kpis: {
            current_pm25: last.pm25,
            current_aqi: last.aqi_score,
            current_category: last.aqi_category,
            peak_pm25: peak ? peak.pm25 : last.pm25,
            peak_hour: peak ? peak.hour_label : last.hour_label,
            peak_category: peak ? peak.aqi_category : last.aqi_category,
            peak_color: peak ? peak.aqi_color : last.aqi_color,
            reading_count: uniqueReadings.length,
            hour_count: history.length
        }
    };
}

module.exports = { buildForecastPayload };
