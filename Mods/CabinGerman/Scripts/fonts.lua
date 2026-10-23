local M = {}
local fallback
local fitted=setmetatable({}, {__mode="k"})
-- Widths follow the fixed buttons and board margins in the original widgets.
local layouts={
    WBP_Pause_Menu_C={
        AreyouSure_T={size=32,width=360}, TextBlock={size=24,width=108},
        TextBlock_1={size=24,width=142}, TextBlock_2={size=28,width=150},
        TextBlock_3={size=24,width=150}, TextBlock_4={size=24,width=108},
        TextBlock_5={size=24,width=138}, TextBlock_56={size=24,width=98},
    },
    WBP_Chalkboard_C={
        TextBlock_3={size=90,width=1750}, TextBlock_4={size=70,width=1700},
        TextBlock_5={size=48,width=1700}, TextBlock_7={size=54,width=1650},
        TextBlock_8={size=48,width=1700}, TextBlock_9={size=48,width=1450},
    },
    WBP_TempClueBoard_C={
        TextBlock_3={size=90,width=1700}, TextBlock_4={size=45,width=1700},
        TextBlock_6={size=48,width=1700}, TextBlock_7={size=48,width=1700},
    },
    PlayerCustomization_WBP_C={
        character_t={size=18,width=160}, Background_T={size=18,width=160},
        Eyes_T={size=18,width=120}, HairDye_T={size=18,width=120}, Hats_T={size=18,width=120},
        TextBlock_358={size=44,width=900}, Back_T={size=24,width=160}, Confirm_T={size=24,width=160},
    },
}
local function fit(object,value,font,fullName,name,unicode)
    local rule
    for class,entries in pairs(layouts) do
        if fullName:find(class,1,true) then rule=entries[name];break end
    end
    if not rule then return end
    local previous=fitted[object]
    if previous and previous.text==value and previous.size==font.Size then return end
    if unicode and font.Size>rule.size then font.Size=rule.size;object:SetFont(font) end
    object:ForceLayoutPrepass()
    local width=object:GetDesiredSize().X
    assert(type(width)=="number" and width==width and width>=0 and width<math.huge,"German layout width invalid: "..fullName)
    if width==0 then return end
    -- Rasterized font metrics do not scale exactly with point size. Remeasure
    -- each smaller integer size; the decreasing size bounds this loop.
    while width>rule.width and font.Size>1 do
        font.Size=math.max(1,math.min(font.Size-1,math.floor(font.Size*rule.width/width)))
        object:SetFont(font)
        object:ForceLayoutPrepass()
        width=object:GetDesiredSize().X
        assert(type(width)=="number" and width==width and width>=0 and width<math.huge,"German layout width invalid: "..fullName)
    end
    assert(width<=rule.width+1,"German layout still exceeds width: "..fullName.."; measured="..width.."; required="..rule.width)
    assert(object.Font.Size==font.Size,"German font size readback differs: "..fullName)
    fitted[object]={text=value,size=font.Size}
end
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
    local fullName=object:GetFullName()
    local decorative = fullName:find("MenuCard", 1, true) ~= nil
    local name = object:GetFName():ToString()
    local settings = object:GetFullName():find("SettingsMaster_WBP_C", 1, true)
        and (name == "TextBlock_56" or name == "TextBlock_6")
    if decorative and not unicode and not settings then return end
    local font = rich and object.DefaultTextStyle.Font or object.Font
    local changed = false
    -- Keep the game's font metrics when no German glyph fallback is needed.
    if unicode then
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
    if not rich then fit(object,value,font,fullName,name,unicode) end
end
return M
