local M = {}
local fallback
local function roboto()
    if fallback and fallback:IsValid() then return fallback end
    local loader = StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
    local path = loader:MakeSoftObjectPath("/Engine/EngineFonts/Roboto.Roboto")
    fallback = loader:LoadAsset_Blocking(loader:Conv_SoftObjPathToSoftObjRef(path))
    assert(fallback and fallback:IsValid(), "German glyph font unavailable")
    return fallback
end
function M.apply(object, value, rich)
    local unicode = value:find("[\128-\255]") ~= nil
    local decorative = object:GetFullName():find("MenuCard", 1, true) ~= nil
    local name = object:GetFName():ToString()
    local settings = object:GetFullName():find("SettingsMaster_WBP_C", 1, true)
        and (name == "TextBlock_56" or name == "TextBlock_6")
    if decorative and not unicode and not settings then return end
    local font = rich and object.DefaultTextStyle.Font or object.Font
    local changed = false
    if not decorative or unicode then
        local target = roboto()
        if not font.FontObject or not font.FontObject:IsValid() or font.FontObject:GetAddress() ~= target:GetAddress() then
            font.FontObject = target
            font.TypefaceFontName = FName("Regular")
            changed = true
        end
    end
    -- The original adjacent action labels need a smaller size for German words.
    if settings and font.Size ~= 20 then font.Size = 20; changed = true end
    if changed then
        if rich then object:SetDefaultFont(font) else object:SetFont(font) end
    end
end
return M
