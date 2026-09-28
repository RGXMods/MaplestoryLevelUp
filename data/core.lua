--=====================================================================================
-- MSLU | MaplestoryLevelUp - core.lua
-- Version: 4.0.0
-- Author: DonnieDice
-- RGX Mods Collection - RealmGX Community Project
--=====================================================================================

local RGX = assert(_G.RGXFramework, "MSLU: RGX-Framework not loaded")

MSLU = MSLU or {}

local ADDON_VERSION = "4.0.2"
local ADDON_NAME = "MaplestoryLevelUp"
local PREFIX = "|Tinterface/addons/MaplestoryLevelUp/media/icon:16:16|t - |cffffffff[|r|cff2563EBMSLU|r|cffffffff]|r "
local TITLE = "|Tinterface/addons/MaplestoryLevelUp/media/icon:18:18|t [|cff2563EBM|r|cffffffffaplestory|r |cff2563EBL|r|cffffffffevel-|r|cff2563EBU|r|cff2563EB!|r]"

MSLU.version = ADDON_VERSION
MSLU.addonName = ADDON_NAME

local Sound = RGX:GetSound()

local handle = Sound:Register(ADDON_NAME, {
sounds = {
high = "Interface\\Addons\\MaplestoryLevelUp\\sounds\\maplestory_high.ogg",
medium = "Interface\\Addons\\MaplestoryLevelUp\\sounds\\maplestory_med.ogg",
low = "Interface\\Addons\\MaplestoryLevelUp\\sounds\\maplestory_low.ogg",
},
defaultSoundId = 569593,
savedVar = "MSLUSettings",
defaults = {
enabled = true,
soundVariant = "medium",
muteDefault = true,
showWelcome = true,
volume = "Master",
firstRun = true,
},
triggerEvent = "PLAYER_LEVEL_UP",
addonVersion = ADDON_VERSION,
})

MSLU.handle = handle

local L = MSLU.L or {}
local initialized = false

local function ShowHelp()
print(PREFIX .. " " .. (L["HELP_HEADER"] or ""))
print(PREFIX .. " " .. (L["HELP_TEST"] or ""))
print(PREFIX .. " " .. (L["HELP_ENABLE"] or ""))
print(PREFIX .. " " .. (L["HELP_DISABLE"] or ""))
print(PREFIX .. " " .. (L["HELP_HIGH"] or ""))
print(PREFIX .. " " .. (L["HELP_MED"] or ""))
print(PREFIX .. " " .. (L["HELP_LOW"] or ""))
end

local function HandleSlashCommand(args)
local command = string.lower(args or "")
if command == "" or command == "help" then
ShowHelp()
elseif command == "test" then
print(PREFIX .. " " .. (L["PLAYING_TEST"] or ""))
handle:Test()
elseif command == "enable" then
handle:Enable()
print(PREFIX .. " " .. (L["ADDON_ENABLED"] or ""))
elseif command == "disable" then
handle:Disable()
print(PREFIX .. " " .. (L["ADDON_DISABLED"] or ""))
elseif command == "high" then
handle:SetVariant("high")
print(PREFIX .. " " .. string.format(L["SOUND_VARIANT_SET"] or "%s", "high"))
elseif command == "med" or command == "medium" then
handle:SetVariant("medium")
print(PREFIX .. " " .. string.format(L["SOUND_VARIANT_SET"] or "%s", "medium"))
elseif command == "low" then
handle:SetVariant("low")
print(PREFIX .. " " .. string.format(L["SOUND_VARIANT_SET"] or "%s", "low"))
else
print(PREFIX .. " " .. (L["ERROR_PREFIX"] or "") .. " " .. (L["ERROR_UNKNOWN_COMMAND"] or ""))
end
end

RGX:RegisterEvent("ADDON_LOADED", function(event, addonName)
if addonName ~= ADDON_NAME then return end
handle:SetLocale(MSLU.L)
L = MSLU.L or {}
handle:Init()
initialized = true
end, "MSLU_ADDON_LOADED")

RGX:RegisterEvent("PLAYER_LEVEL_UP", function()
if initialized then
handle:Play()
end
end, "MSLU_PLAYER_LEVEL_UP")

RGX:RegisterEvent("PLAYER_LOGIN", function()
if not initialized then
handle:SetLocale(MSLU.L)
L = MSLU.L or {}
handle:Init()
initialized = true
end
handle:ShowWelcome(PREFIX, TITLE)
end, "MSLU_PLAYER_LOGIN")

RGX:RegisterEvent("PLAYER_LOGOUT", function()
handle:Logout()
end, "MSLU_PLAYER_LOGOUT")

RGX:RegisterSlashCommand("mslu", function(msg)
local ok, err = pcall(HandleSlashCommand, msg)
if not ok then
print(PREFIX .. " " .. (L["ERROR_PREFIX"] or "") .. " " .. tostring(err))
end
end, "MSLU_SLASH")
