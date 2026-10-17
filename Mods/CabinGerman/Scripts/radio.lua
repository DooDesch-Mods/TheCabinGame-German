local M = {}
local fonts = require("fonts")
local enabled = true
local playback, caption, hud, displayed
local cues = {
    {0.00,1.68,"Seid gegrüßt, Spieler."},
    {1.98,7.10,"Inzwischen habt ihr sicher bemerkt,\ndass ihr in dieser Hütte gefangen seid."},
    {7.10,11.74,"Und der einzige Ausweg führt über ein Spiel.\nEin Kartenspiel."},
    {12.04,17.48,"Das Ziel des Spiels ist einfach:\nFindet heraus, in welchem Raum sich der Ausgang befindet."},
    {17.78,22.00,"In dieser Hütte sind drei Hinweise versteckt,\ndie ihr finden müsst."},
    {22.00,24.30,"Deckt sie auf, bevor das Spiel endet."},
    {24.30,27.40,"Denn sobald eure Spielfigur die Zwölf erreicht,"},
    {27.40,30.18,"müsst ihr in diesem Raum sein, um zu gewinnen."},
    {30.48,35.76,"Doch eine weitere Spielfigur ist euch auf den Fersen.\nSie gehört dem Besucher."},
    {36.06,41.42,"Lasst seine Spielfigur eure nicht einholen.\nSonst heißt es: Game Over."},
    {41.72,46.76,"Viel Glück. Und, Spieler ...\nwillkommen bei ... The Cabin Game."},
}
local function valid(o) return o and o:IsValid() end
local function clock(o)
    return StaticFindObject("/Script/Engine.Default__GameplayStatics"):GetAudioTimeSeconds(o)
end
local function is_intro(component)
    if not valid(component) then return false end
    local sound = component.Sound
    return valid(sound) and sound:GetClass():GetFName():ToString() == "SoundCue"
        and sound:GetFullName() == "SoundCue /Game/CabinGameContent/Event_BPs/Other_Event_Stuff/Intro/RadioVoiceIntro_Cue.RadioVoiceIntro_Cue"
end
local function hide()
    if valid(caption) then caption:SetVisibility(2) end
    displayed = nil
end
local function panel()
    if valid(caption) and valid(hud) and hud:IsInViewport() then return caption end
    for _, candidate in ipairs(FindAllOf("CabinHUD_W_C") or {}) do
        if valid(candidate) and candidate:IsInViewport() then
            local tree = candidate.WidgetTree
            assert(valid(tree) and valid(tree.RootWidget), "radio caption HUD tree unavailable")
            local widget = StaticConstructObject(StaticFindObject("/Script/UMG.TextBlock"), tree, FName("CabinGermanRadio"))
            assert(valid(widget), "radio caption creation failed")
            local slot = tree.RootWidget:AddChildToCanvas(widget)
            assert(valid(slot), "radio caption canvas slot unavailable")
            widget:SetFont(candidate.ReadyUp_T.Font)
            widget:SetJustification(1)
            widget:SetColorAndOpacity({SpecifiedColor={R=1,G=1,B=1,A=1},ColorUseRule=0})
            widget:SetShadowColorAndOpacity({R=0,G=0,B=0,A=1})
            widget:SetShadowOffset({X=2,Y=2})
            widget:SetVisibility(4)
            slot:SetAnchors({Minimum={X=0.5,Y=0.92},Maximum={X=0.5,Y=0.92}})
            slot:SetAlignment({X=0.5,Y=1})
            slot:SetPosition({X=0,Y=0})
            slot:SetAutoSize(true)
            slot:SetZOrder(1000)
            caption, hud = widget, candidate
            return caption
        end
    end
    error("no visible gameplay HUD for German radio subtitles")
end
function M.tick()
    if playback and (not valid(playback.component) or not playback.component:IsPlaying()) then
        playback = nil
    end
    if not playback then
        for _, component in ipairs(FindAllOf("AudioComponent") or {}) do
            if is_intro(component) and component:IsPlaying() then
                playback = {component=component, time=clock(component)}
                print("[CabinGerman] info: radio playback detected; German subtitles started\n")
                break
            end
        end
    end
    if not enabled or not playback then hide(); return end
    local elapsed = clock(playback.component) - playback.time
    local line
    for _, cue in ipairs(cues) do
        if elapsed >= cue[1] and elapsed < cue[2] then line=cue[3]; break end
    end
    if not line then hide(); return end
    local widget = panel()
    if displayed ~= line then
        fonts.apply(widget, line, false)
        widget:SetText(StaticFindObject("/Script/Engine.Default__KismetTextLibrary"):Conv_StringToText(line))
        assert(widget:GetText():ToString() == line, "radio subtitle readback differs")
        widget:SetVisibility(4)
        displayed = line
    end
end
if RegisterKeyBind and Key and Key.F8 then
    RegisterKeyBind(Key.F8, function()
        ExecuteInGameThread(function()
            enabled = not enabled
            print("[CabinGerman] info: German radio subtitles=" .. tostring(enabled) .. "\n")
            if not enabled then hide() end
        end)
    end)
end
return M
