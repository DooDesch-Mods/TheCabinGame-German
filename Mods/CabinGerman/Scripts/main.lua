local directory = assert(debug.getinfo(1, "S").source:match("^@(.+[/\\])"))
package.path = directory .. "?.lua;" .. package.path
local translation = require("translate")
local radio = require("radio")
local fonts = require("fonts")
local catalog_count = 0
for _ in pairs(require("de")) do catalog_count = catalog_count + 1 end
local errors, applied = {}, {}
local busy = false
local changes = 0
local function log(level, message) print("[CabinGerman] " .. level .. ": " .. message .. "\n") end
local function report(operation, cause)
    local reason = tostring(cause)
    local prior = errors[operation]
    if not prior or prior.reason ~= reason then
        errors[operation] = {reason=reason, count=1}
        log("error", operation .. ": " .. reason)
    else prior.count = prior.count + 1 end
end
local function attempt(operation, callback)
    local ok, cause = xpcall(callback, debug.traceback)
    if not ok then report(operation, cause)
    elseif errors[operation] then
        log("info", operation .. " recovered; failures=" .. errors[operation].count)
        errors[operation] = nil
    end
    return ok
end
local function text(value)
    local library = StaticFindObject("/Script/Engine.Default__KismetTextLibrary")
    assert(library and library:IsValid(), "KismetTextLibrary unavailable")
    return library:Conv_StringToText(value)
end
local specs = {
    {class="TextBlock", property="Text", getter="GetText", setter="SetText"},
    {class="RichTextBlock", property="Text", getter="GetText", setter="SetText"},
    {class="EditableTextBox", property="HintText", setter="SetHintText", hint=true},
    {class="EditableText", property="HintText", setter="SetHintText", hint=true},
    {class="MultiLineEditableTextBox", property="HintText", setter="SetHintText", hint=true},
}
local function apply(object, spec)
    if not translation.allowed(object, spec.hint) then return end
    local current = spec.getter and object[spec.getter](object) or object[spec.property]
    local source = current:ToString()
    local target = translation.text(source)
    if (target or translation.is_target(source)) and not spec.hint then
        fonts.apply(object, target or source, spec.class == "RichTextBlock")
    end
    if not target then return end
    object[spec.setter](object, text(target))
    local readback = spec.getter and object[spec.getter](object) or object[spec.property]
    assert(readback:ToString() == target, "German text readback differs for " .. object:GetFullName())
    changes = changes + 1
    if not applied[source] then
        applied[source] = true
        log("info", "translated " .. source:gsub("[\r\n]", " "):sub(1, 120))
    end
end
for _, spec in ipairs(specs) do
    local path = "/Script/UMG." .. spec.class .. ":" .. spec.setter
    attempt("hook " .. path, function()
        RegisterHook(path, function(context, incoming)
            if busy then return end
            attempt("incoming " .. spec.class, function()
                local object = context:get()
                if not translation.allowed(object, spec.hint) then return end
                local target = translation.text(incoming:get():ToString())
                if target then incoming:set(text(target)) end
            end)
        end)
    end)
end
assert(type(LoopInGameThreadWithDelay) == "function", "UE4SS game-thread scheduler unavailable")
local ticks = 0
local handle = LoopInGameThreadWithDelay(250, function()
    if busy then return end
    busy = true
    for _, spec in ipairs(specs) do
        attempt("scan " .. spec.class, function()
            for _, object in ipairs(FindAllOf(spec.class) or {}) do
                attempt("apply " .. spec.class, function() apply(object, spec) end)
            end
        end)
    end
    busy = false
    attempt("radio subtitles", radio.tick)
    ticks = ticks + 1
    if ticks == 20 then log("info", "startup readbacks=" .. changes) end
end)
assert(handle and IsValidDelayedActionHandle(handle), "German scheduler registration failed")
log("info", "loaded 0.2.0; German catalog=" .. catalog_count .. "; game-thread interval=250ms")
