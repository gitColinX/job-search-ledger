"""Themes for Job Search Ledger.

Every color and font the app uses comes from one dict per theme. To add a theme, copy an
entry in THEMES, give it a new name, and change the values. Nothing else needs to change.

Keys
  base        "dark" or "light"; sets Streamlit's own widgets (tables, inputs, menus)
  bg, panel   page background and card / input background
  ink, muted  main text and secondary text
  rule        borders and grid lines
  accent      primary accent: key stat, active tab, target line, "not reported"
  accent2     second accent: section headers, links, "reported", main chart color
  on_accent2  text color drawn on top of an accent2 bar
  funnel      four colors for Applied, Viewed, Interview, Offer
  heat        four colors from "no applications" to "busiest day"
  pay_hit     bars whose top of range meets the target
  pay_miss    bars below target (also drawn hatched, so color is never the only cue)
  fonts       display (wordmark), body, mono (numbers); font_url loads them
  title_glow, key_glow   CSS shadows, use "none" to turn off
  radius      corner radius for cards
  header_rule CSS background for the line under the header
  emblem      CSS for the small logo square next to the title ("" to hide it)
  sec_prefix  text shown before section headers, for example "> "
  extra_css   anything else (bevels, textures); keep it small
"""

_GF = "https://fonts.googleapis.com/css2?family="

THEMES = {
    "80s Synth": dict(
        base="dark", bg="#18161D", panel="#201D27", ink="#ECE7F2", muted="#938BA3", rule="#2E2A38",
        accent="#FF4F8B", accent2="#4DE3F2", on_accent2="#18161D",
        funnel=["#4DE3F2", "#3AAFC0", "#2C7F8E", "#FF4F8B"],
        heat=["#201D27", "#1F3B45", "#2E9AAB", "#4DE3F2"],
        pay_hit="#4DE3F2", pay_miss="#4A4458",
        display="Audiowide", body="Inter", mono="JetBrains Mono",
        font_url=_GF + "Audiowide&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap",
        title_glow="0 0 18px rgba(255,79,139,.35)",
        key_glow="0 0 24px rgba(255,79,139,.12)",
        radius="6px",
        header_rule="linear-gradient(90deg, #FF4F8B 0%, #FF4F8B 18%, #4DE3F2 60%, transparent 100%)",
        emblem="border-radius:50%; background:linear-gradient(180deg,#FFB86B 0%,#FF4F8B 70%);"
               "-webkit-mask:linear-gradient(180deg,#000 0 24px,transparent 24px 26px,#000 26px 30px,transparent 30px 33px,"
               "#000 33px 36px,transparent 36px 40px,#000 40px);"
               "mask:linear-gradient(180deg,#000 0 24px,transparent 24px 26px,#000 26px 30px,transparent 30px 33px,"
               "#000 33px 36px,transparent 36px 40px,#000 40px);",
        sec_prefix="> ", extra_css="",
    ),
    "90s": dict(
        base="light", bg="#C3C7CB", panel="#D4D0C8", ink="#111111", muted="#4A4A4A", rule="#808080",
        accent="#6B2C91", accent2="#007C80", on_accent2="#FFFFFF",
        funnel=["#007C80", "#2E9A9E", "#6B2C91", "#A0307A"],
        heat=["#E4E2DC", "#A9D3D4", "#3E9A9D", "#00585B"],
        pay_hit="#007C80", pay_miss="#9A9A9A",
        display="Silkscreen", body="IBM Plex Sans", mono="IBM Plex Mono",
        font_url=_GF + "Silkscreen:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap",
        title_glow="none", key_glow="none", radius="0px",
        header_rule="linear-gradient(90deg, #000080, #1084D0)",
        emblem="background:conic-gradient(#007C80 0 25%, #6B2C91 0 50%, #E0B000 0 75%, #C0392B 0); border:2px solid #111;",
        sec_prefix="",
        extra_css="""
.stat { border-top:2px solid #FFFFFF !important; border-left:2px solid #FFFFFF !important;
        border-right:2px solid #404040 !important; border-bottom:2px solid #404040 !important; }
.sec { background:linear-gradient(90deg,#000080,#1084D0); color:#FFFFFF !important; padding:3px 8px !important; border:none !important; }
.mast h1 { text-transform:uppercase; }
""",
    ),
    "Y2K": dict(
        base="light", bg="#EEF3F8", panel="#FFFFFF", ink="#1B2633", muted="#5E6F82", rule="#CBD6E2",
        accent="#0A84D6", accent2="#18B5C9", on_accent2="#FFFFFF",
        funnel=["#18B5C9", "#3E9FE0", "#0A84D6", "#7A5CE0"],
        heat=["#F2F6FA", "#BFE6EE", "#5CC4D6", "#0A84D6"],
        pay_hit="#18B5C9", pay_miss="#B8C4D0",
        display="Michroma", body="Nunito Sans", mono="Space Mono",
        font_url=_GF + "Michroma&family=Nunito+Sans:wght@400;600;700&family=Space+Mono:wght@400;700&display=swap",
        title_glow="0 1px 0 #FFFFFF", key_glow="0 6px 18px rgba(10,132,214,.18)", radius="14px",
        header_rule="linear-gradient(90deg, #C9D3DD, #FFFFFF 30%, #9FB0C2 60%, #FFFFFF 85%, #C9D3DD)",
        emblem="border-radius:50%; background:radial-gradient(circle at 35% 30%, #FFFFFF 0 12%, #8FE3F0 30%, #18B5C9 60%, #0A6FA8 100%);"
               "box-shadow: inset 0 -3px 6px rgba(0,0,0,.2);",
        sec_prefix="",
        extra_css="""
.stat { background:linear-gradient(180deg,#FFFFFF 0%,#F1F5F9 55%,#E6ECF2 100%) !important; }
.stTabs [aria-selected="true"] { background:linear-gradient(180deg,#E8F7FB,#C6ECF4); border-radius:10px 10px 0 0; padding:6px 10px !important; }
""",
    ),
    "Dark": dict(
        base="dark", bg="#141518", panel="#1C1E22", ink="#E6E7E9", muted="#8D9199", rule="#2A2D33",
        accent="#E0A458", accent2="#7FA7D9", on_accent2="#141518",
        funnel=["#7FA7D9", "#6A8FBF", "#5677A3", "#E0A458"],
        heat=["#1C1E22", "#24344A", "#4D6F99", "#7FA7D9"],
        pay_hit="#7FA7D9", pay_miss="#3A3E46",
        display="Inter", body="Inter", mono="JetBrains Mono",
        font_url=_GF + "Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
        title_glow="none", key_glow="none", radius="6px",
        header_rule="#2A2D33", emblem="", sec_prefix="", extra_css=".mast h1 { font-weight:600; letter-spacing:-.01em; }",
    ),
    "Light": dict(
        base="light", bg="#FAFAF9", panel="#FFFFFF", ink="#1C1C1E", muted="#6E6E73", rule="#E4E4E7",
        accent="#D9480F", accent2="#1E5FAD", on_accent2="#FFFFFF",
        funnel=["#1E5FAD", "#3D7CC4", "#6E9DD6", "#D9480F"],
        heat=["#F1F1F2", "#CFE0F3", "#6E9DD6", "#1E5FAD"],
        pay_hit="#1E5FAD", pay_miss="#C9C9CE",
        display="Inter", body="Inter", mono="IBM Plex Mono",
        font_url=_GF + "Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap",
        title_glow="none", key_glow="none", radius="8px",
        header_rule="#1C1C1E", emblem="", sec_prefix="", extra_css=".mast h1 { font-weight:700; letter-spacing:-.02em; }",
    ),
    "High Contrast": dict(
        base="dark", bg="#000000", panel="#000000", ink="#FFFFFF", muted="#E0E0E0", rule="#FFFFFF",
        accent="#FFFF00", accent2="#00FFFF", on_accent2="#000000",
        funnel=["#FFFFFF", "#00FFFF", "#FFFF00", "#FF66FF"],
        heat=["#000000", "#5A5A5A", "#BDBDBD", "#FFFFFF"],
        pay_hit="#00FFFF", pay_miss="#FFFFFF",
        display="Atkinson Hyperlegible", body="Atkinson Hyperlegible", mono="IBM Plex Mono",
        font_url=_GF + "Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@500;700&display=swap",
        title_glow="none", key_glow="none", radius="0px",
        header_rule="#FFFFFF", emblem="", sec_prefix="",
        extra_css="""
.stat { border-width:2px !important; }
.stat .val { font-weight:700 !important; }
.stApp a { text-decoration:underline !important; }
.stApp, .stApp p, .stat .hint, .note { font-size:1.02em; }
""",
    ),
    "Colorblind Safe": dict(  # Okabe-Ito palette; blue vs orange, never red vs green
        base="dark", bg="#1A1B1F", panel="#23252B", ink="#EDEDED", muted="#A3A3A8", rule="#34363D",
        accent="#E69F00", accent2="#56B4E9", on_accent2="#1A1B1F",
        funnel=["#56B4E9", "#0072B2", "#CC79A7", "#E69F00"],
        heat=["#23252B", "#1B3F5C", "#0072B2", "#56B4E9"],
        pay_hit="#56B4E9", pay_miss="#E69F00",
        display="Inter", body="Inter", mono="JetBrains Mono",
        font_url=_GF + "Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
        title_glow="none", key_glow="none", radius="6px",
        header_rule="linear-gradient(90deg, #E69F00, #56B4E9)", emblem="", sec_prefix="",
        extra_css=".mast h1 { font-weight:600; }",
    ),
}

DEFAULT = "80s Synth"
