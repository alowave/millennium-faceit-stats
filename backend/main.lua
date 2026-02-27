local logger = require("logger")
local millennium = require("millennium")
local http = require("http")
local json = require("json")
local fs = require("fs")
local utils = require("utils")

-- API Headers
local HEADERS = {
    ["Accept"] = "application/json",
    ["Authorization"] = "Bearer 8f9985f3-3cf5-43de-970c-dfe244a57fb0"
}

local HEADERS_LEETIFY = {
    ["Accept"] = "application/json"
}

-- ==========================================
-- FaceIt User & Stats Functions
-- ==========================================

-- Helper function to fetch stats (Equivalent to FaceItUser.get_user_stats)
local function get_user_stats(player_id)
    local url = string.format("https://open.faceit.com/data/v4/players/%s/stats/cs2", player_id)
    local res = http.get(url, { headers = HEADERS })
    
    if not res or res.status ~= 200 then
        logger:error("Failed to fetch FaceIt stats for ID: " .. tostring(player_id))
        return nil
    end

    local success, data = pcall(json.decode, res.body)
    if not success then return nil end

    local lifetime = data.lifetime or {}
    
    return {
        matches = tonumber(lifetime["Matches"]) or 0,
        avg_hs = tonumber(lifetime["Average Headshots %"]) or 0.0,
        avg_kd = tonumber(lifetime["Average K/D Ratio"]) or 0.0,
        adr = tonumber(lifetime["ADR"]) or 0.0,
        winrate = tonumber(lifetime["Win Rate %"]) or 0.0
    }
end

-- Globally exposed function so the frontend can call it
function get_user_by_steamId(steamId)
    local url = string.format("https://open.faceit.com/data/v4/players?game=cs2&game_player_id=%s", steamId)
    local res = http.get(url, { headers = HEADERS })
    
    if not res then
        logger:error("Error fetching FaceIt user data: Network request failed")
        return nil
    end
    
    if res.status == 404 then
        return nil
    elseif res.status ~= 200 then
        logger:error("Error fetching data: " .. tostring(res.status))
        return nil
    end
    
    local success, data = pcall(json.decode, res.body)
    if not success then return nil end

    local games_cs2 = (data.games and data.games.cs2) or {}

    local user = {
        id = data.player_id or "",
        nickname = data.nickname or "Unknown",
        country = data.country or "Unknown",
        avatar = data.avatar or "",
        cover_image_url = data.cover_image or "",
        faceit_elo = games_cs2.faceit_elo or 0,
        skill_level = games_cs2.skill_level or 0
    }

    -- Attach stats
    user.stats = get_user_stats(user.id)

    return json.encode(user)
end

-- Globally exposed function to fetch Leetify rating
function get_aim_rating(steamId)
    local url = string.format("https://api.cs-prod.leetify.com/api/profile/id/%s", steamId)
    local res = http.get(url, { headers = HEADERS_LEETIFY })
    
    if not res or res.status ~= 200 then
        logger:error("Failed to fetch aim rating")
        return nil
    end
    
    local success, data = pcall(json.decode, res.body)
    if not success then return nil end

    local aim_rating = 0.0
    if data.recentGameRatings and data.recentGameRatings.aim then
        aim_rating = data.recentGameRatings.aim
    end
    
    return utils.round(aim_rating)
end

-- ==========================================
-- File Management & Initialization 
-- ==========================================

-- Removed

-- ==========================================
-- Millennium Plugin Callbacks
-- ==========================================

local function on_load()
    logger:info("Bootstrapping FaceItStats, Millennium " .. millennium.version())
    
    millennium.ready()
end

local function on_unload()
    logger:info("Unloading FaceItStats")
end

local function on_frontend_loaded()
    logger:info("The front end has loaded!")
end

-- Return the standard Millennium plugin structure
return {
    on_load = on_load,
    on_unload = on_unload,
    on_frontend_loaded = on_frontend_loaded
}