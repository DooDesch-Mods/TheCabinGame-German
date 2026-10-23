"""Check bounded translated layouts without changing unrelated font sizes."""
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
vendor=root.parents[2]/'Workspace/tools/german/vendor'
if vendor.exists(): sys.path.insert(0,str(vendor))
from lupa.lua54 import LuaRuntime
vm=LuaRuntime(unpack_returned_tuples=True)
vm.globals().scripts=(root/'Mods/CabinGerman/Scripts').as_posix()
vm.execute(r'''
package.path=scripts.."/?.lua;"..package.path
local fontObject={IsValid=function() return true end,GetAddress=function() return 10 end}
local loader={MakeSoftObjectPath=function(_,v) return v end,Conv_SoftObjPathToSoftObjRef=function(_,v) return v end,
    LoadAsset_Blocking=function() return fontObject end}
function StaticFindObject() return loader end
function FName(value) return value end
local fonts=require("fonts")
local function object(class,name,size,text)
    local self={Font={Size=size,FontObject=fontObject},passes=0,sets=0,text=text}
    function self:GetFullName() return "TextBlock "..class..".WidgetTree."..name end
    function self:GetFName() return {ToString=function() return name end} end
    function self:SetFont(font) self.Font=font;self.sets=self.sets+1 end
    function self:ForceLayoutPrepass() self.passes=self.passes+1 end
    function self:GetDesiredSize()
        local longest=0
        for line in (self.text.."\n"):gmatch("(.-)\n") do longest=math.max(longest,utf8.len(line)) end
        return {X=longest*self.Font.Size*0.75,Y=self.Font.Size}
    end
    return self
end
for _,case in ipairs({
    {"WBP_Pause_Menu_C","TextBlock",75,"Einstellungen",75,108},
    {"WBP_Pause_Menu_C","TextBlock_3",75,"Abbrechen",75,150},
    {"WBP_Pause_Menu_C","AreyouSure_T",60,"Bist du sicher?",60,360},
    {"WBP_Chalkboard_C","TextBlock_7",72,"Mit [M] kannst du jederzeit das Spielhandbuch öffnen.",54,1650},
    {"WBP_TempClueBoard_C","TextBlock_6",60,"Es gibt insgesamt 12 Räume. In nur 3 davon erscheint ein\nzufälliger Hinweis.",48,1700},
    {"PlayerCustomization_WBP_C","character_t",24,"Charakter wählen",18,160},
    {"PlayerCustomization_WBP_C","Background_T",24,"Hintergrund wählen",18,160},
    {"PlayerCustomization_WBP_C","Eyes_T",24,"Kontaktlinsen",24,120},
    {"PlayerCustomization_WBP_C","HairDye_T",24,"Haarfarbe",24,120},
}) do
    local o=object(case[1],case[2],case[3],case[4])
    fonts.apply(o,case[4],false)
    assert(o.Font.Size<=case[5] and o:GetDesiredSize().X<=case[6],"translated layout exceeds bounds")
    local passes,sets=o.passes,o.sets
    fonts.apply(o,case[4],false)
    assert(o.passes==passes and o.sets==sets,"unchanged text was laid out again")
end
local rasterized=object("PlayerCustomization_WBP_C","Background_T",24,"Hintergrund wählen")
function rasterized:GetDesiredSize()
    return {X=({[18]=169,[17]=162})[self.Font.Size] or self.Font.Size*9}
end
fonts.apply(rasterized,rasterized.text,false)
assert(rasterized:GetDesiredSize().X<=160 and rasterized.passes>=3,"rasterized font width was not remeasured to fit")
local unrelated=object("WBP_ManualPage_Title_C","TextBlock",30,"Kurzanleitung")
fonts.apply(unrelated,unrelated.text,false)
assert(unrelated.Font.Size==30 and unrelated.passes==0,"unrelated layout changed")
local original={IsValid=function() return true end,GetAddress=function() return 20 end}
unrelated.Font.FontObject=original
fonts.apply(unrelated,unrelated.text,false)
assert(unrelated.Font.FontObject==original,"ASCII text replaced the original font")
unrelated.text="Übersicht"
fonts.apply(unrelated,unrelated.text,false)
assert(unrelated.Font.FontObject==fontObject,"German glyph fallback missing")
local narrow=object("WBP_Pause_Menu_C","TextBlock",75,"Einstellungen")
function narrow:GetDesiredSize() return {X=self.Font.Size} end
fonts.apply(narrow,narrow.text,false)
assert(narrow.Font.Size==75,"narrow original font was unnecessarily reduced")
local broken=object("WBP_Pause_Menu_C","TextBlock",75,"Einstellungen")
function broken:GetDesiredSize() return {X=10000} end
local ok,cause=pcall(fonts.apply,broken,broken.text,false)
assert(not ok and tostring(cause):find("still exceeds width",1,true),"failed layout must stay visible")
''')
print('PASS: pause/dialog/board width bounds, repeated-pass cache, unrelated typography and visible layout failures; engine rendering pending')
