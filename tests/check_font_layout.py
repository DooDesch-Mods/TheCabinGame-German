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
local fontObject={IsValid=function() return true end,GetAddress=function() return 10 end,
    GetFullName=function()return "Font /Engine/EngineFonts/Roboto.Roboto"end}
local loader={MakeSoftObjectPath=function(_,v) return v end,Conv_SoftObjPathToSoftObjRef=function(_,v) return v end,
    LoadAsset_Blocking=function() return fontObject end}
function StaticFindObject() return loader end
function FName(value) return value end
local fonts=require("fonts")
local serial=0
local function object(class,name,size,text)
    serial=serial+1;local id=serial
    local self={Font={Size=size,FontObject=fontObject,TypefaceFontName="Regular"},passes=0,sets=0,text=text,RenderTransform={Translation={X=0,Y=-49}}}
    function self:GetFullName() return "TextBlock "..class..".WidgetTree."..name end
    function self:GetAddress()return id end
    function self:GetFName() return {ToString=function() return name end} end
    function self:SetFont(font) self.Font=font;self.sets=self.sets+1 end
    function self:SetRenderTranslation(value) self.RenderTransform.Translation=value end
    self.parent={Slot={Padding={Left=0,Top=0,Right=0,Bottom=-85}}}
    function self:GetParent() return self.parent end
    function self.parent.Slot:IsValid() return true end
    function self.parent.Slot:GetClass() return {GetFName=function() return {ToString=function() return "ButtonSlot" end} end} end
    function self.parent.Slot:SetPadding(value) self.Padding=value end
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
    {"WBP_TheNeighbor_C","Intro_T",52,"Wenn du schon hier bist, kann ich dir vielleicht helfen.",24,1700},
    {"WBP_TheNeighbor_C","Intro_T",52,"W",24,1700},
}) do
    local o=object(case[1],case[2],case[3],case[4])
    fonts.apply(o,case[4],false)
    assert(o.Font.Size<=case[5] and o:GetDesiredSize().X<=case[6],"translated layout exceeds bounds")
    if case[1]=="WBP_Pause_Menu_C" and case[2]~="AreyouSure_T" then
        assert(o.RenderTransform.Translation.X==0 and o.RenderTransform.Translation.Y==0,"pause label remains outside its original button")
        assert(o.parent.Slot.Padding.Bottom==0,"confirmation label still inherits negative button padding")
    end
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
local original={IsValid=function() return true end,GetAddress=function() return 20 end,
    GetFullName=function()return "Font /Unknown/Font.Font"end}
unrelated.Font.FontObject=original
fonts.apply(unrelated,unrelated.text,false)
assert(unrelated.Font.FontObject==original,"ASCII text replaced the original font")
unrelated.text="Übersicht"
fonts.apply(unrelated,unrelated.text,false)
assert(unrelated.Font.FontObject==fontObject,"German glyph fallback missing")
unrelated.text="Kurzanleitung"
fonts.apply(unrelated,unrelated.text,false)
assert(unrelated.Font.FontObject==original,"original font was not restored after a missing-glyph fallback")
local function vanilla(path,id)
    return {IsValid=function()return true end,GetAddress=function()return id end,
        GetFullName=function()return "Font "..path end}
end
local pause=object("WBP_Pause_Menu_C","TextBlock",75,"Einstellungen")
local acha=vanilla("/Game/MenuContent/Widgets/Achafont_Font.Achafont_Font",30)
pause.Font.FontObject=acha;pause.Font.TypefaceFontName="Default"
fonts.apply(pause,pause.text,false)
assert(pause.Font.FontObject==acha and pause.Font.TypefaceFontName=="Default","ASCII pause text lost vanilla font/style")
pause.text="Größe ändern"
fonts.apply(pause,pause.text,false)
assert(pause.Font.FontObject==acha,"supported German glyphs lost vanilla pause font")
local neighbor=object("WBP_TheNeighbor_C","Intro_T",52,"Grüße für euch")
local expanded=vanilla("/Game/MenuContent/Widgets/Achafexp_Font.Achafexp_Font",31)
neighbor.Font.FontObject=expanded;neighbor.Font.TypefaceFontName="Default"
fonts.apply(neighbor,neighbor.text,false)
assert(neighbor.Font.FontObject==expanded and neighbor.Font.Size==24,"Neighbor font/style or size changed incorrectly")
local limited=object("WBP_ManualPage_Title_C","TextBlock",30,"Tür")
local typewriter=vanilla("/Game/CabinGameContent/BoardGameStuff/Cards/CardComponents/1942_Font.1942_Font",32)
limited.Font.FontObject=typewriter;limited.Font.TypefaceFontName="Default"
fonts.apply(limited,limited.text,false)
assert(limited.Font.FontObject==fontObject,"1942 lacks ü but fallback was skipped")
limited.text="Karte"
fonts.apply(limited,limited.text,false)
assert(limited.Font.FontObject==typewriter and limited.Font.TypefaceFontName=="Default","fallback permanently replaced the vanilla font/style")
local reused=object("WBP_Pause_Menu_C","TextBlock",75,"Einstellungen α")
reused.Font.FontObject=acha;reused.Font.TypefaceFontName="Default"
function reused:GetDesiredSize()return {X=self.Font.FontObject==acha and self.Font.Size*3 or utf8.len(self.text)*self.Font.Size*0.75}end
fonts.begin_pass();fonts.apply(reused,reused.text,false);fonts.end_pass()
assert(reused.Font.FontObject==fontObject)
local wrapper=object("WBP_Pause_Menu_C","TextBlock",reused.Font.Size,"Einstellungen")
function wrapper:GetAddress()return reused:GetAddress()end
wrapper.Font=reused.Font
wrapper.GetDesiredSize=reused.GetDesiredSize
fonts.begin_pass();fonts.apply(wrapper,wrapper.text,false);fonts.end_pass()
assert(wrapper.Font.FontObject==acha and wrapper.Font.TypefaceFontName=="Default"and wrapper.Font.Size==24,"new UObject wrapper lost vanilla font/style/size")
fonts.begin_pass();fonts.end_pass()
assert(not fonts.has_layout(unrelated),"destroyed/unobserved widget font state was retained")
local narrow=object("WBP_Pause_Menu_C","TextBlock",75,"Einstellungen")
function narrow:GetDesiredSize() return {X=self.Font.Size} end
fonts.apply(narrow,narrow.text,false)
assert(narrow.Font.Size==24,"pause label did not use the bounded German font")
local broken=object("WBP_Pause_Menu_C","TextBlock",75,"Einstellungen")
function broken:GetDesiredSize() return {X=10000} end
local ok,cause=pcall(fonts.apply,broken,broken.text,false)
assert(not ok and tostring(cause):find("still exceeds width",1,true),"failed layout must stay visible")
''')
print('PASS: pause/dialog/board width bounds, repeated-pass cache, unrelated typography and visible layout failures; engine rendering pending')
