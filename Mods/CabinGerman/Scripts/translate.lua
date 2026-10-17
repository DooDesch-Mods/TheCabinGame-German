local texts = require("de")
local widgets = require("widgets")
local M = {}
local function normalize(text) return text:gsub("\r\n", "\n") end
local normalized = {}
local targets = {}
for source, target in pairs(texts) do
    local key = normalize(source)
    assert(not normalized[key] or normalized[key] == target, "conflicting normalized German entry")
    normalized[key] = target
    targets[normalize(target)] = true
end
function M.is_target(source) return targets[normalize(source)] == true end
local numeric = {
    {"^Time: ([%d:%.]+)$", "Zeit: %1"},
    {"^Minutes Progressed: (%d+)$", "Minuten vorgerückt: %1"},
    {"^Deaths: (%d+)$", "Tode: %1"},
    {"^Events Drawn: (%d+)$", "Events gezogen: %1"},
    {"^Rooms Placed: (%d+)$", "Räume platziert: %1"},
    {"^Clues Uncovered: (%d+)$", "Hinweise aufgedeckt: %1"},
    {"^%.%.%.there are (%d+) doors%.$", "...es gibt %1 Türen."},
    {"^%.%.%.there are (%d+) rooms %(including The Cellar%)%.$", "...es gibt %1 Räume (einschließlich Keller)."},
    {"^you need at least (%d+) progress cards on the table%.$", "Du brauchst mindestens %1 Zeitkarten auf dem Tisch."},
}
function M.text(source)
    local target = normalized[normalize(source)]
    if target then return target ~= source and target or nil end
    for _, pair in ipairs(numeric) do
        local value, count = source:gsub(pair[1], pair[2])
        if count == 1 then return value end
    end
end
local protected = {username=true, nickname=true, playername=true, lobbyname=true, chatmessage=true, messagetext=true}
function M.allowed(object, hint)
    if not object or not object:IsValid() then return false end
    if not hint then
        local name = object:GetFName():ToString():lower():gsub("[^a-z]", "")
        for token in pairs(protected) do if name:find(token, 1, true) then return false end end
    end
    local owner = object
    local recognized = false
    for _ = 1, 16 do
        if not owner or not owner:IsValid() then break end
        local class = owner:GetClass():GetFName():ToString()
        if class == "WBP_ChatText_C" or class == "WBP_PlayerChat_C" or class == "SessionSlot_WBP_C" or class == "LobbyPlayerCard_WBP_C" then
            return hint == true
        end
        if widgets[class] then recognized = true end
        owner = owner:GetOuter()
    end
    return recognized
end
return M
