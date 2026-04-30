
const API_BASE = "/api";

/**
 * @param {string} endpoint
 * @param {"GET"|"POST"|"PUT"|"DELETE"} method
 * @param {object|null} body
 * @param {number} retries  
 */
export async function apiRequest(endpoint, method = "GET", body = null, retries = 1) {
    const options = {
        method,
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        mode: "cors",
    };
    if (body) options.body = JSON.stringify(body);

    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, options);

            // Try to parse JSON regardless of status
            let data;
            try { data = await response.json(); }
            catch { data = {}; }

            if (!response.ok) {
                const msg = data.error || data.message || `Server Error ${response.status}`;
                throw new Error(msg);
            }

            return data;
        } catch (err) {
            // On last attempt, re-throw with a clear message
            if (attempt === retries) {
                if (err.message === "Failed to fetch") {
                    throw new Error("Cannot reach server. Make sure the backend (server.py) is running on port 5000.");
                }
                throw err;
            }
            // Wait before retrying
            await new Promise(r => setTimeout(r, 800 * (attempt + 1)));
        }
    }
}
