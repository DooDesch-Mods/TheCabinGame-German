"""Exercise the translator with a mod that verifies text immediately after setting it."""
from pathlib import Path
import argparse
import sys

root = Path(__file__).resolve().parents[1]
vendor = root.parents[2] / 'Workspace/tools/german/vendor'
if vendor.exists():
    sys.path.insert(0, str(vendor))
from lupa.lua54 import LuaRuntime

vm = LuaRuntime(unpack_returned_tuples=True)
vm.globals().scripts = (root / 'Mods/CabinGerman/Scripts').as_posix()
entrypoint = root / 'Mods/CabinGerman/Scripts/main.lua'
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--main', type=Path, default=entrypoint)
    entrypoint = parser.parse_args().main
vm.globals().entrypoint = entrypoint.as_posix()
vm.execute(r'''
package.path=scripts.."/?.lua;"..package.path
local hooks,objects={},{}
local tick
local logs={}
print=function(message) logs[#logs+1]=message end
function FText(value) return {ToString=function() return value end} end
local menu={IsValid=function() return true end,
    GetClass=function() return {GetFName=function() return FText("MenuCardPlay_W_C") end} end,
    GetOuter=function() return nil end}
local function widget(class,name,value)
    local object={Text=FText(value),HintText=FText(value)}
    function object:IsValid() return true end
    function object:GetFName() return FText(name) end
    function object:GetFullName() return class.." MenuCardPlay_W_C."..name end
    function object:GetClass() return {GetFName=function() return FText(class) end} end
    function object:GetOuter() return menu end
    function object:GetText() return self.Text end
    function object:SetText(text)
        local hook=hooks["/Script/UMG."..class..":SetText"]
        if hook then hook({get=function() return self end},
            {get=function() return text end,set=function(_,changed) text=changed end}) end
        self.Text=text
    end
    function object:SetHintText(text) self.HintText=text end
    objects[class]=objects[class] or {}
    table.insert(objects[class],object)
    return object
end
function RegisterHook(path,callback) hooks[path]=callback end
function LoopInGameThreadWithDelay(delay,callback) assert(delay==250);tick=callback;return 1 end
function IsValidDelayedActionHandle(handle) return handle==1 end
function FindAllOf(class) return objects[class] or {} end
local library={IsValid=function() return true end,Conv_StringToText=function(_,value) return FText(value) end}
function StaticFindObject(path) assert(path=="/Script/Engine.Default__KismetTextLibrary");return library end
-- Font and radio rendering are unchanged; isolate their engine-dependent work.
package.loaded.fonts={apply=function() end}
package.loaded.radio={tick=function() end}
assert(loadfile(entrypoint))()
local label=widget("TextBlock","Single_T","Play")
label:SetText(FText("settings"))
assert(label:GetText():ToString()=="settings","mod's immediate SetText readback was changed")
assert(next(hooks)==nil,"translator must not rewrite another mod's setter arguments")
local rich=widget("RichTextBlock","Title","settings")
local player=widget("TextBlock","PlayerName_T","settings")
local hints={}
for _,class in ipairs({"EditableTextBox","EditableText","MultiLineEditableTextBox"}) do
    hints[#hints+1]=widget(class,"Hint","settings")
end
tick()
assert(label:GetText():ToString()=="Einstellungen","scheduled text translation missing")
assert(rich:GetText():ToString()=="Einstellungen","scheduled rich-text translation missing")
for _,hint in ipairs(hints) do assert(hint.HintText:ToString()=="Einstellungen") end
assert(player:GetText():ToString()=="settings","player name was translated")
label:SetText(FText("settings"))
assert(label:GetText():ToString()=="settings","later mod write readback changed")
tick()
assert(label:GetText():ToString()=="Einstellungen","later mod write was not translated")
label.SetText=function() end
label.Text=FText("settings")
tick()
local failure=false
for _,message in ipairs(logs) do
    if message:find("German text readback differs",1,true) then failure=true end
end
assert(failure,"translator's own failed write must still be reported")
''')
print('PASS: synchronous mod readback, deferred translation, all five widget types, user-text guard, repeated writes and visible failures')
