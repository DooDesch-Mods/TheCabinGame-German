local M = {}
local fallback
local coverage=require("font_coverage")
local originals,fitted={},{}
local pass=0
local function address(value)return value and value:IsValid()and value:GetAddress()or 0 end
local function typeface_key(value)
    if type(value)=="string"then return value end
    return value and value:ToString()or ""
end
-- Widths follow the fixed buttons and board margins in the original widgets.
local layouts={
    WBP_Pause_Menu_C={
        AreyouSure_T={size=32,width=360,bounded=true}, TextBlock={size=24,width=108,bounded=true,center=true},
        TextBlock_1={size=24,width=142,bounded=true,center=true}, TextBlock_2={size=28,width=150,bounded=true,center=true},
        TextBlock_3={size=24,width=150,bounded=true,center=true}, TextBlock_4={size=24,width=108,bounded=true,center=true},
        TextBlock_5={size=24,width=138,bounded=true,center=true}, TextBlock_56={size=24,width=98,bounded=true,center=true},
    },
    WBP_TheNeighbor_C={
        Intro_T={size=24,width=1700,bounded=true},
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
local function layout(fullName,name)
    for class,entries in pairs(layouts) do
        if fullName:find(class,1,true) then return entries[name] end
    end
end
local function fit(object,value,font,fullName,name,unicode)
    local rule=layout(fullName,name)
    if not rule then return end
    -- The decorative pause font uses -49/-97 offsets inside centered button
    -- slots. Those offsets no longer align with the smaller German labels.
    if rule.center then
        local offset=object.RenderTransform.Translation
        if offset.X~=0 or offset.Y~=0 then object:SetRenderTranslation({X=0,Y=0}) end
        local overlay=object:GetParent()
        local slot=overlay and overlay.Slot
        if slot and slot:IsValid() and slot:GetClass():GetFName():ToString()=="ButtonSlot" then
            local padding=slot.Padding
            if padding.Left<0 or padding.Top<0 or padding.Right<0 or padding.Bottom<0 then
                slot:SetPadding({Left=0,Top=0,Right=0,Bottom=0})
            end
        end
    end
    local id=object:GetAddress()
    local previous=fitted[id]
    if previous and previous.text==value and previous.size==font.Size then return end
    if (unicode or rule.bounded) and font.Size>rule.size then font.Size=rule.size;object:SetFont(font) end
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
    fitted[id]={text=value,size=font.Size}
end
function M.has_layout(object)
    local name=object:GetFullName()
    local original=originals[object:GetAddress()]
    return layout(name,object:GetFName():ToString())~=nil or (original~=nil and original.name==name)
end
function M.begin_pass()pass=pass+1 end
function M.end_pass()
    for id,state in pairs(originals)do
        if state.seen~=pass then originals[id],fitted[id]=nil,nil end
    end
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
    local id=object:GetAddress()
    local original=originals[id]
    if not original or original.name~=fullName or (address(font.FontObject)~=original.selected and address(font.FontObject)~=address(original.font))then
        original={font=font.FontObject,typeface=typeface_key(font.TypefaceFontName),name=fullName,size=font.Size}
        originals[id]=original;fitted[id]=nil
    end
    original.seen=pass
    -- A widget can return from a missing-glyph fallback to its original typeface.
    if original.text~=value then
        original.supported=coverage.supports(original.font,value);original.text=value
    end
    local target,typeface
    if original.supported then target,typeface=original.font,FName(original.typeface)
    else target,typeface=roboto(),FName("Regular")end
    if address(font.FontObject)~=address(target)or typeface_key(font.TypefaceFontName)~=typeface_key(typeface)then
        font.FontObject,font.TypefaceFontName=target,typeface
        font.Size=original.size
        changed=true;fitted[id]=nil
    end
    original.selected=address(target)
    -- The original adjacent action labels need a smaller size for German words.
    if settings and font.Size ~= 20 then font.Size = 20; changed = true end
    if changed then
        if rich then object:SetDefaultFont(font) else object:SetFont(font) end
    end
    if not rich then fit(object,value,font,fullName,name,unicode) end
end
return M
