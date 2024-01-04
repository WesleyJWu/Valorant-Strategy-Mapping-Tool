import pygame
pygame.init()

# Display dimenstions
DISPLAY_WIDTH = 1470
DISPLAY_HEIGHT = 800

# Common Text Fonts
TEXT_FONT_HEADER = pygame.font.SysFont("arial", 50)
TEXT_FONT_SUBHEADER = pygame.font.SysFont("arial", 30)
TEXT_FONT_MAP_BUTTON = pygame.font.SysFont("arial", 25)

# Colors
TAN = (210, 180, 140)
PALE_GREEN_3 = (124,205,124)
PALE_VIOLET_RED = (219,112,147)

# New File State's Width and Height
NEW_FILE_STATE_WIDTH = DISPLAY_WIDTH - 700
NEW_FILE_STATE_HEIGHT = DISPLAY_HEIGHT - 300

# Gameplay State Info
MAP_WIDTH = DISPLAY_HEIGHT
MAP_HEIGHT = MAP_WIDTH
TOOLBAR_WIDTH = DISPLAY_WIDTH - MAP_WIDTH
TOOLBAR_HEIGHT = MAP_HEIGHT

# Agent and Utility Info
AGENT_HEIGHT_WIDTH = 45 
AGENT_FIRST_ROW = 70
AGENT_SECOND_ROW = 118
UTILITY_HEIGHT_WIDTH = 36
UTILITY_FIRST_ROW = AGENT_SECOND_ROW + AGENT_HEIGHT_WIDTH + 5

AGENT_LIST = ["astra", "breach", "brimstone", "chamber", "cypher", "deadlock", "fade", "gekko", "harbor", "jett", "kayo", "killjoy", "neon", "omen", "phoenix", "raze", "reyna", "sage", "skye", "sova", "viper", "yoru"]
AGENT_TO_UTILITY_DICT = {
    "astra": ["astra_star", "astra_nova_pulse", "astra_nebula", "astra_gravity_well", "astra_cosmic_divide"],
    "breach": ["breach_aftershock", "breach_fault_line", "breach_flashpoint", "breach_rolling_thunder"],
    "brimstone": ["brimstone_incendiary", "brimstone_orbital_strike", "brimstone_smoke", "brimstone_stim_beacon"],
    "chamber": ["chamber_headhunter", "chamber_rendezvous", "chamber_tour_de_force", "chamber_trademark"],
    "cypher": ["cypher_cage", "cypher_neural_theft", "cypher_spycam", "cypher_trapwire"],
    "deadlock": ["deadlock_annihilation", "deadlock_barrier_mesh", "deadlock_gravnet", "deadlock_sonic_sensor"],
    "fade": ["fade_haunt", "fade_nightfall", "fade_prowler", "fade_seize"],
    "gekko": ["gekko_dizzy", "gekko_mosh_pit", "gekko_thrash", "gekko_wingman"],
    "harbor": ["harbor_cascade", "harbor_cove", "harbor_high_tide", "harbor_reckoning"],
    "jett": ["jett_blade_storm", "jett_cloudburst", "jett_tailwind", "jett_updraft"],
    "kayo": ["kayo_flash", "kayo_fragment", "kayo_nullcmd", "kayo_zeropoint"],
    "killjoy": ["killjoy_alarmbot", "killjoy_lockdown", "killjoy_nanoswarm", "killjoy_turret"],
    "neon": ["neon_fast_lane", "neon_high_gear", "neon_overdrive", "neon_relay_bolt"],
    "omen": ["omen_from_the_shadows", "omen_paranoia", "omen_shrouded_step", "omen_smoke"],
    "phoenix": ["phoenix_curveball", "phoenix_hot_hands", "phoenix_run_it_back", "phoenix_wall"],
    "raze": ["raze_blast_pack", "raze_boom_bot", "raze_paint_shells", "raze_showstopper"],
    "reyna": ["reyna_devour", "reyna_dismiss", "reyna_empress", "reyna_leer"],
    "sage": ["sage_healing_orb", "sage_resurrection", "sage_slow_orb", "sage_wall"],
    "skye": ["skye_regrowth", "skye_seekers", "skye_guiding_light", "skye_trailblazer"],
    "sova": ["sova_hunters_fury", "sova_owl_drone", "sova_recon_bolt", "sova_shock_bolt"],
    "viper": ["viper_pit", "viper_poison_cloud", "viper_snake_bite", "viper_wall"],
    "yoru": ["yoru_blindside", "yoru_clone", "yoru_dimensional_drift", "yoru_gatecrash"]
}
