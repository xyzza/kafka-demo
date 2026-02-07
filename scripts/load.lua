-- wrk load test script for PUT /publish

local hex = "0123456789abcdef"
local alpha = "abcdefghijklmnopqrstuvwxyz"
local extensions = { ".txt", ".csv", ".json", ".xml", ".log", ".pdf" }
local variant = { "8", "9", "a", "b" }

math.randomseed(os.time())

local function random_hex(n)
    local s = {}
    for i = 1, n do
        local idx = math.random(1, #hex)
        s[i] = hex:sub(idx, idx)
    end
    return table.concat(s)
end

local function random_uuid()
    return string.format(
        "%s-%s-4%s-%s%s-%s",
        random_hex(8),
        random_hex(4),
        random_hex(3),
        variant[math.random(1, 4)],
        random_hex(3),
        random_hex(12)
    )
end

local function random_filename()
    local len = math.random(3, 10)
    local name = {}
    for i = 1, len do
        local idx = math.random(1, #alpha)
        name[i] = alpha:sub(idx, idx)
    end
    return table.concat(name) .. extensions[math.random(1, #extensions)]
end

local function random_files()
    local count = math.random(1, 5)
    local files = {}
    for i = 1, count do
        files[i] = '"' .. random_filename() .. '"'
    end
    return "[" .. table.concat(files, ",") .. "]"
end

local function random_location()
    local lat = math.random() * 180 - 90
    local lon = math.random() * 360 - 180
    return string.format("[%.6f,%.6f]", lat, lon)
end

wrk.method = "PUT"
wrk.headers["Content-Type"] = "application/json"

request = function()
    local body = string.format(
        '{"session_id":"%s","files":%s,"location":%s}',
        random_uuid(),
        random_files(),
        random_location()
    )
    return wrk.format("PUT", "/publish", wrk.headers, body)
end
