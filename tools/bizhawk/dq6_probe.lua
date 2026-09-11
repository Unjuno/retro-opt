-- Minimal read-only SFC DQ6 probe for BizHawk 2.11+.
--
-- This intentionally reads the explicit "WRAM" memory domain rather than
-- relying on BizHawk's current/default domain.  Addresses in the research
-- notes are SNES CPU addresses ($7Exxxx/$7Fxxxx), so cpu_to_wram() converts
-- them to zero-based offsets in the 128 KiB WRAM domain.
--
-- Output is change-driven TSV on the Lua console.  The permanent event block
-- is emitted in full only when its hash changes.

local DOMAIN = "WRAM"
local WRAM_CPU_START = 0x7E0000
local WRAM_CPU_END = 0x7FFFFF

local function has_domain(name)
    for _, value in pairs(memory.getmemorydomainlist()) do
        if value == name then
            return true
        end
    end
    return false
end

assert(has_domain(DOMAIN),
    "BizHawk SNES core does not expose a WRAM domain named 'WRAM'; inspect memory.getmemorydomainlist()")

local function cpu_to_wram(address)
    if address < WRAM_CPU_START or address > WRAM_CPU_END then
        error(string.format("not a direct SNES WRAM address: $%06X", address))
    end
    return address - WRAM_CPU_START
end

local function u8(address)
    return memory.read_u8(cpu_to_wram(address), DOMAIN)
end

local function u16le(address)
    return memory.read_u16_le(cpu_to_wram(address), DOMAIN)
end

local function bytes_hex(address, length)
    local data = memory.read_bytes_as_binary_string(cpu_to_wram(address), length, DOMAIN)
    local out = {}
    for index = 1, #data do
        out[index] = string.format("%02X", string.byte(data, index))
    end
    return table.concat(out)
end

local EVENT_START = 0x7E3D2A
local EVENT_LENGTH = 0xD6 -- inclusive through $7E3DFF

local last_signature = nil
local last_event_hash = nil

local function sample()
    local frame = emu.framecount()

    -- Map / encounter state.
    local map_no = u16le(0x7E5ED9)
    local encounter_no = u16le(0x7E5EC3)
    local encounter_counter_raw = u8(0x7E3B8F)

    -- Battle control state.  Keep bit-packed values raw here; decode them in
    -- the game adapter after cross-checking the public RAM documentation.
    local battle_flags = u8(0x7E2011)
    local battle_control = u8(0x7E2514)
    local turn = u8(0x7E2541)

    local event_hash = memory.hash_region(
        cpu_to_wram(EVENT_START), EVENT_LENGTH, DOMAIN)

    local signature = string.format(
        "%04X:%04X:%02X:%02X:%02X:%02X:%s",
        map_no,
        encounter_no,
        encounter_counter_raw,
        battle_flags,
        battle_control,
        turn,
        event_hash)

    if signature == last_signature then
        return
    end

    local event_hex = "-"
    if event_hash ~= last_event_hash then
        event_hex = bytes_hex(EVENT_START, EVENT_LENGTH)
        last_event_hash = event_hash
    end

    -- $7E2000-$7E200F: enemy group IDs/counts according to the public DQ6 RAM map.
    local battle_head_hex = bytes_hex(0x7E2000, 0x10)

    console.log(string.format(
        "DQ6PROBE\tframe=%d\tmap=%04X\tencounter=%04X\tencounter_counter_raw=%02X" ..
        "\tbattle_flags=%02X\tbattle_control_raw=%02X\tturn=%02X" ..
        "\tbattle_head=%s\tevent_hash=%s\tevent_hex=%s",
        frame,
        map_no,
        encounter_no,
        encounter_counter_raw,
        battle_flags,
        battle_control,
        turn,
        battle_head_hex,
        event_hash,
        event_hex))

    last_signature = signature
end

console.log("DQ6PROBE\tstatus=started\tdomain=" .. DOMAIN)

while true do
    emu.frameadvance()
    sample()
end
