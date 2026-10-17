from pathlib import Path
import json
import sys
root=Path(__file__).resolve().parents[1]
vendor=root.parents[2]/'Workspace/tools/german/vendor'
if vendor.exists(): sys.path.insert(0,str(vendor))
from lupa.lua54 import LuaRuntime
vm=LuaRuntime(unpack_returned_tuples=True)
scripts=root/'Mods/CabinGerman/Scripts'
compile_lua=vm.eval('function(source,name) return assert(load(source,name,"t",{})) end')
for path in scripts.glob('*.lua'): compile_lua(path.read_text(encoding='utf-8'),str(path))
vm.globals().directory=scripts.as_posix()
vm.execute('package.path=directory.."/?.lua;"..package.path; translate=require("translate")')
catalog=json.loads((root/'translations.de.json').read_text(encoding='utf-8'))
for source,target in catalog.items():
    expected=target if target!=source else None
    assert vm.globals().translate.text(source)==expected,(source,target)
    assert vm.globals().translate.text(source.replace('\r\n','\n'))==expected
assert vm.globals().translate.text('Deaths: 12')=='Tode: 12'
assert vm.globals().translate.text('Level: 27') is None
assert vm.globals().translate.text('Time: 12:04.5')=='Zeit: 12:04.5'
assert vm.globals().translate.text('my friend Play') is None
vm.execute('''
function object(name,class,outer)
 return {IsValid=function() return true end, GetFName=function() return {ToString=function() return name end} end,
 GetClass=function() return {GetFName=function() return {ToString=function() return class end} end} end,
 GetOuter=function() return outer end}
end
local menu=object("Menu","Menu_WBP_C")
assert(translate.allowed(object("Label","TextBlock",menu)))
assert(not translate.allowed(object("PlayerName_T","TextBlock",menu)))
assert(not translate.allowed(object("TextBlock_0","TextBlock",object("Chat","WBP_ChatText_C"))))
assert(not translate.allowed(object("Name_T","TextBlock",object("Slot","SessionSlot_WBP_C"))))
assert(not translate.allowed(object("Name_T","TextBlock",object("Slot","LobbyPlayerCard_WBP_C"))))
assert(translate.allowed(object("Hint","EditableTextBox",menu),true))
assert(not translate.allowed(object("Label","TextBlock",object("Other","UnknownMod_C"))))
''')
print(f'PASS: Lua syntax, {len(catalog)} exact translations, newline variants, numeric messages and user-text guards')
