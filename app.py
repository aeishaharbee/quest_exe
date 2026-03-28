import streamlit as st
import json
import os
import random
import base64
import streamlit.components.v1 as components

# --- CONFIGURATION & DATABASE ---
st.set_page_config(page_title="QUEST.exe", layout="wide", initial_sidebar_state="collapsed")
DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE): 
        return {"users": {}}
    with open(DB_FILE, "r") as f: 
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: 
        json.dump(data, f)

# --- SESSION MANAGEMENT ---
for key, val in {
    "page": "auth", 
    "previous_page": "auth", 
    "username": None, 
    "newly_unlocked": []}.items():
    if key not in st.session_state: 
        st.session_state[key] = val

def navigate_to(page):
    st.session_state.previous_page = st.session_state.page
    st.session_state.page = page
    st.rerun()

def default_progress():
    return {
        "scene": 1, 
        "hp": 50,
        "inventory": [],
        "rps_player": 0, 
        "rps_bunny": 0
    }

def update_progress(updates):
    db = load_db()
    user = db["users"][st.session_state.username]
    for key, value in updates.items():
        user["progress"][key] = value
    if user["progress"]["hp"] <= 0 and user["progress"]["scene"] not in [100, 101]:
        user["progress"]["scene"] = 100 
    save_db(db)
    st.rerun()

def unlock_achievement(ach_name):
    db = load_db()
    user = db["users"][st.session_state.username]
    if ach_name not in user.get("achievements", []):
        user.setdefault("achievements", []).append(ach_name)
        st.session_state.newly_unlocked.append(ach_name)
        save_db(db)
        st.session_state.toast = f"🏆 Achievement Unlocked: {ach_name}!"

# --- IMAGE UTILITIES ---
def get_b64(filepath):
    if filepath and os.path.exists(filepath):
        with open(filepath, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

def get_image_html(item_name, image_path, size="50px"):
    img_b64 = get_b64(image_path)
    if img_b64:
        return f"<img src='data:image/png;base64,{img_b64}' title='{item_name}' style='height: {size}; margin: 0 5px; filter: drop-shadow(2px 2px 0px #000);' />"
    return item_name

def get_user_pfp(user_data):
    if user_data.get("profile_pic"): return user_data["profile_pic"]
    return get_b64(os.path.join("images", "elems", "profile.png"))

# --- AUDIO UTILITIES ---
def start_bgm(audio_path):
    if os.path.exists(audio_path):
        with open(audio_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            
        js_code = f"""
            <script>
            var parentDoc = window.parent.document;
            if (parentDoc.getElementById("game_music") === null) {{
                var audio = parentDoc.createElement("audio");
                audio.id = "game_music";
                audio.src = "data:audio/mp3;base64,{b64}";
                audio.loop = true;
                audio.volume = 0.4; 
                parentDoc.body.appendChild(audio);
                audio.play();
            }}
            </script>
        """
        components.html(js_code, height=0)

# --- GLOBAL STYLES ---
def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #22c55e;
        font-family: 'VT323', monospace;
    }

    /* maxed screen */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    
    /* text font */
    h1, h2, h3, p, span, div, label, input, button {
        font-family: 'VT323', monospace !important;
    }

    h1, .stButton > button[kind="primary"] p {
        text-shadow: 
            -2px -2px 0 #D30000, -2px 0 0 #D30000, -2px 2px 0 #D30000,
             0 -2px 0 #D30000,                      0 2px 0 #D30000,
             2px -2px 0 #D30000,  2px 0 0 #D30000,  2px 2px 0 #D30000 !important;
    }
                
    h2, h3, p, div, label, input, button {
        text-shadow: 
            -1px -1px 0 #000, -1px 0 0 #000, -1px 1px 0 #000,
             0 -1px 0 #000,                      0 1px 0 #000,
             1px -1px 0 #000,  1px 0 0 #000,  1px 1px 0 #000 !important;
    }
                
    .stProgress > div > div > div > div {
        background-color: #D30000 !important; 
    }

    
    /* buttons styling */
    .stButton > button {
        background-color: transparent !important;
        border: 1px solid #22c55e !important;
        color: #22c55e !important;
        border-radius: 0px !important;
        font-size: 1.2rem !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s !important;
        width: 100%;
        height: 100%;
        min-height: 60px;
    }
    
    .stButton > button:hover {
        background-color: #22c55e !important;
    }
                
    .stButton > button[kind="primary"] {
        width: fit-content !important;   
        padding: 0.5rem 2rem !important;  
        border-width: 3px !important;    
        border-color: #D30000 !important;
        margin: 0 auto !important;       
        display: block !important;
    }
    
    .stButton > button[kind="primary"] p {
        font-size: 2rem !important;
    }
    
    .st-key-logout_btn button p {
        color: #D30000 !important;
    }
    
    
    /* inputs styling */
    .stTextInput > div > div > input {
        background-color: #000000 !important;
        border: 1px solid #22c55e !important;
        color: #22c55e !important;
        border-radius: 0px !important;
    }
    
    /* hide header and footer */
    header {display: none !important;}
    footer {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

def set_dynamic_bg(bg_path):
    img_b64 = get_b64(bg_path)
    style = f"background-image: url('data:image/png;base64,{img_b64}'); background-size: cover; background-position: center; background-repeat: no-repeat;" if img_b64 else "background-color: #000;"
    
    st.markdown(f"""
    <style>
    .stApp {{ {style} }}
    .hp-text {{ color: #D30000 !important; }}
    </style>
    """, unsafe_allow_html=True)

def get_pfp_button_css(pfp_base64, size="70px", margin_top="0px"):
    return f"""
    <style>
    div.element-container:has(.pfp-anchor) {{
        display: none !important;
    }}
    
    div.element-container:has(.pfp-anchor) + div.element-container button {{
        background-image: url('data:image/png;base64,{pfp_base64}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 50% !important;
        width: {size} !important;
        height: {size} !important;
        min-height: {size} !important;
        border: 2px solid white !important;
        color: transparent !important;
        padding: 0 !important;
        margin-top: {margin_top} !important;
    }}
    div.element-container:has(.pfp-anchor) + div.element-container button p {{
        display: none !important;
    }}
    div.element-container:has(.pfp-anchor) + div.element-container button:hover {{
        border-color: #FFFFFF !important;
        filter: brightness(1.2);
    }}
    </style>
    <div class="pfp-anchor"></div>
    """

# --- PAGES ---

def auth_page():
    inject_global_css()
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-top: 10vh; margin-bottom: 2rem;'>QUEST.exe</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        db = load_db()
        with tab1:
            u = st.text_input("USERNAME", key="log_user")
            p = st.text_input("PASSWORD", type="password", key="log_pass")
            if st.button("LOGIN"):
                if u in db["users"] and db["users"][u]["password"] == p:
                    st.session_state.username = u
                    navigate_to("main_menu")
                else: st.error("Invalid credentials")
        with tab2:
            n, u, p = st.text_input("NAME"), st.text_input("USERNAME", key="reg_user"), st.text_input("PASSWORD", type="password", key="reg_pass")
            if st.button("REGISTER"):
                if u in db["users"]: st.error("Exists!")
                else:
                    db["users"][u] = {"name": n, "password": p, "profile_pic": None, "achievements": [], "progress": default_progress()}
                    save_db(db); st.success("Done!")

def main_menu():
    inject_global_css()
    set_dynamic_bg(os.path.join("images", "bgs", "screen", "screen1.png"))
    db = load_db()
    user_data = db["users"][st.session_state.username]
    
    _, s_col = st.columns([8, 1])
    with s_col:
        st.markdown(get_pfp_button_css(get_user_pfp(user_data), size="70px"), unsafe_allow_html=True)
        if st.button("PFP", key="main_pfp_btn"): navigate_to("settings")
    
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)

    _, c_col, _ = st.columns([1, 2, 1])
    with c_col:
        st.markdown("<h1 style='font-size: 6rem; letter-spacing: 0.2em; text-align: center; margin-bottom: 3rem;'>QUEST.exe</h1>", unsafe_allow_html=True)
        if st.button("START", type="primary", use_container_width=True): navigate_to("game")

    start_bgm(os.path.join("audio", "bgmusic.mp3"))

def settings_page():
    inject_global_css()
    set_dynamic_bg(os.path.join("images", "bgs", "settings.png"))
    db = load_db()
    user_data = db["users"][st.session_state.username]

    if st.button(f"← Back"): navigate_to(st.session_state.previous_page)

    col1, col2 = st.columns([1, 2])
    with col1:
        pfp_base64 = get_user_pfp(user_data) 
        img_html = f"<img src='data:image/png;base64,{pfp_base64}' style='width: 100%; height: 100%; object-fit: cover;'/>"
            
        st.markdown(f"""
        <div style='border: 2px solid #22c55e; width: 150px; height: 150px; display: flex; align-items: center; justify-content: center; overflow: hidden; margin-bottom: 1rem;'>
            {img_html}
        </div>
        """, unsafe_allow_html=True)
            
        uploaded_file = st.file_uploader("Upload New Picture", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if uploaded_file is not None:
            encoded_string = base64.b64encode(uploaded_file.read()).decode()
            user_data["profile_pic"] = encoded_string
            save_db(db)
            st.rerun()
            
        if user_data.get("profile_pic"):
            if st.button("Remove Picture"):
                user_data["profile_pic"] = None
                save_db(db)
                st.rerun()

    with col2:
        tab_ach, tab_edit = st.tabs(["ACHIEVEMENTS", "EDIT PROFILE"])
        
        with tab_edit:
            new_name = st.text_input("NAME", value=user_data["name"])
            new_username = st.text_input("USERNAME", value=st.session_state.username)
            new_password = st.text_input("PASSWORD", value=user_data["password"], type="password")
            
            if st.button("SAVE CHANGES"):
                if new_username != st.session_state.username:
                    if new_username in db["users"]:
                        st.error("That username is already taken!")
                    elif not new_username.strip():
                        st.error("Username cannot be empty!")
                    else:
                        db["users"][new_username] = db["users"].pop(st.session_state.username)
                        db["users"][new_username]["name"] = new_name
                        db["users"][new_username]["password"] = new_password
                        st.session_state.username = new_username
                        save_db(db)
                        st.success("Profile updated successfully!")
                else:
                    db["users"][st.session_state.username]["name"] = new_name
                    db["users"][st.session_state.username]["password"] = new_password
                    save_db(db)
                    st.success("Profile updated successfully!")
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("LOGOUT", key="logout_btn"):
                st.session_state.username = None
                navigate_to("auth")
                
        with tab_ach:
            achievements = user_data.get("achievements",[])
            
            if achievements:
                cols = st.columns(4)
                
                for i, ach in enumerate(achievements):
                    if i >= 4:
                        break
                        
                    with cols[i]:
                        # format name: "FIXER UPPER" -> "fixer_upper.png"
                        ach_filename = ach.lower().replace(" ", "_") + ".png"
                        ach_path = os.path.join("images", "emblem", ach_filename)
                        
                        if os.path.exists(ach_path):
                            with open(ach_path, "rb") as img_file:
                                encoded_img = base64.b64encode(img_file.read()).decode()
                            img_html = f"<img src='data:image/png;base64,{encoded_img}' style='width: 120px; height: 120px; object-fit: contain; margin-bottom: 10px; filter: drop-shadow(3px 3px 0px #000);'/>"
                        else:
                            img_html = "<div style='font-size: 80px; margin-bottom: 10px; text-shadow: 3px 3px 0px #000;'>🏆</div>"
                        
                        st.markdown(f"""
                        <div style='display: flex; flex-direction: column; align-items: center; text-align: center;'>
                            {img_html}
                            <div style='font-size: 1.3rem; font-weight: 800; line-height: 1.1; text-transform: uppercase;'>
                                {ach}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No achievements unlocked yet. Keep playing!")

# --- GAME ENGINE ---

def game_page():
    inject_global_css()

    if "toast" in st.session_state: 
        st.toast(st.session_state.toast); 
        del st.session_state.toast
    
    db = load_db(); 
    user_data = db["users"][st.session_state.username]
    prog = user_data["progress"]; 
    scene = prog["scene"]; 
    hp = prog["hp"]
    inventory = prog["inventory"]

    # Background Logic
    bg_map = {
        (1, 6): ("screen", f"screen{scene+1}.png"),
        (7, 7): ("screen", f"screen6.png"),
        (8, 8): ("level1", "level1_start.png"),
        (9, 11): ("level1", "level1_left.png"),
        (12, 13): ("level1", "level1_middle.png"),
        (14, 15): ("level1", "level1_right.png"),
        (16, 21): ("", "level2.png"),
        (22, 24): ("level3", "level3_glitched.png"),
        (25, 25): ("level3", "level3_fixed.png"),
        (26, 27): ("level3", "level3_defeat.png"),
        (29, 29): ("level3", "level3_sneak.png"),
        (30, 30): ("level3", "level3_caught.png"),
        (31, 31): ("level4", "level4_start.png"),
        (32, 32): ("level4", "level4_leap.png"),
        (33, 33): ("level4", "level4_other.png"),
        (34, 34): ("level4", "level4_fixed.png"),
        (35, 41): ("level5", "level5.png"),
        (42, 42): ("level5", "level5_sword.png"),
        (43, 43): ("level5", "level5_die.png"),
        (44, 46): ("level6", "level6.png"),
        (47, 47): ("level6", "level6_woke.png"),
        (48, 48): ("level6", "level6_egg.png"),
        (49, 49): ("level6", "level6_princess.png"),
        (50, 50): ("level6", "level6_sacrifice.png"),
        (100, 100): ("", "game_over.png"),
        (101, 101): ("screen", "screen1.png")
    }
    
    bg_path = os.path.join("images", "bgs", "screen1.png")
    for (low, high), (sub, name) in bg_map.items():
        if low <= scene <= high:
            bg_path = os.path.join("images", "bgs", sub, name) if sub else os.path.join("images", "bgs", name)
            break
    set_dynamic_bg(bg_path)

    # Assets & CSS
    dialogue_b64 = get_b64(os.path.join("images", "elems", "dialogue.png"))
    dialogue_thin_b64 = get_b64(os.path.join("images", "elems", "dialogue_thin.png"))
    btn_b64 = get_b64(os.path.join("images", "elems", "choice.png"))
    spoon_btn_b64 = get_b64(os.path.join("images", "items", "spoon_glitched.png"))
    sword_btn_b64 = get_b64(os.path.join("images", "items", "sword_glitched.png"))
    bread_btn_b64 = get_b64(os.path.join("images", "items", "bread.png"))
    rock_btn_b64 = get_b64(os.path.join("images", "elems", "rock.png"))
    paper_btn_b64 = get_b64(os.path.join("images", "elems", "paper.png"))
    scissors_btn_b64 = get_b64(os.path.join("images", "elems", "scissor.png"))
    
    st.markdown(f"""
    <style>
    /* White Text */          
    .stApp {{
        color: white !important;
    }}

    /* Dialogue Boxes */
    .dialogue-wrapper {{
        position: fixed;
        top: 115px; 
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 1000px;
        z-index: 100;
    }}
    .dialogue-box {{
        background-image: url('data:image/png;base64,{dialogue_b64}');
        background-size: 100% 100%;
        background-repeat: no-repeat;
        width: 100%;
        min-height: 160px;
        padding: 20px 40px;
        font-size: 1.8rem;
        color: black !important;
        text-shadow: 2px 2px 0 #fff !important;
        line-height: 1.4;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}
    .dialogue-box-thin {{
        background-image: url('data:image/png;base64,{dialogue_thin_b64}');
        background-size: 100% 100%;
        background-repeat: no-repeat;
        width: 100%;
        min-height: 120px;
        padding: 10px 20px;
        font-size: 1.8rem;
        color: black !important;
        text-shadow: 2px 2px 0 #fff !important;
        line-height: 1.4;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}
    
    /* Foreground Images */
    .fg-wrapper {{
        position: fixed;
        top: 55%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 50;
    }}
    .fg-wrapper img {{
        max-height: 250px;
        max-width: 100%;
        object-fit: contain;
        filter: drop-shadow(5px 5px 0px #000);
    }}

    /* Choice Buttons with Images */
    div[class*="st-key-game_spoon"] button,
    div[class*="st-key-game_sword"] button,
    div[class*="st-key-game_bread"] button,
    div[class*="st-key-game_rock"] button,
    div[class*="st-key-game_paper"] button,
    div[class*="st-key-game_scissors"] button {{
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }}
    div[class*="st-key-game_spoon"] button {{ background-image: url('data:image/png;base64,{spoon_btn_b64}') !important; }}
    div[class*="st-key-game_sword"] button {{ background-image: url('data:image/png;base64,{sword_btn_b64}') !important; }}
    div[class*="st-key-game_bread"] button {{ background-image: url('data:image/png;base64,{bread_btn_b64}') !important; }}
    div[class*="st-key-game_rock"] button {{ background-image: url('data:image/png;base64,{rock_btn_b64}') !important; }}
    div[class*="st-key-game_paper"] button {{ background-image: url('data:image/png;base64,{paper_btn_b64}') !important; }}
    div[class*="st-key-game_scissors"] button {{ background-image: url('data:image/png;base64,{scissors_btn_b64}') !important; }}

    div[class*="st-key-game_spoon"] button p,
    div[class*="st-key-game_sword"] button p,
    div[class*="st-key-game_bread"] button p,
    div[class*="st-key-game_rock"] button p,
    div[class*="st-key-game_paper"] button p,
    div[class*="st-key-game_scissors"] button p {{
        color: transparent !important;
        font-size: 0px !important;
        text-shadow: none !important;
    }}

    .stButton > button {{
        border: 1px solid white !important;
        color: #22c55e !important;
    }}
    
    .stButton > button:hover {{
        background-color: white !important;
    }}

    .stButton > button p {{
        color: white !important;
    }}
    
    /* Choice Column */
    div[data-testid="column"]:has(.choice-col-marker),
    div[data-testid="stColumn"]:has(.choice-col-marker) {{
        position: fixed !important;
        bottom: 130px !important; 
        left: 50% !important;
        width: 100% !important;
        max-width: 90% !important;
        transform: translateX(-50%) !important;
        z-index: 9999 !important;
        background: transparent !important;
        padding: 0 !important;
    }}

    div[data-testid="column"]:has(.choice-col-marker) > div,
    div[data-testid="stColumn"]:has(.choice-col-marker) > div {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 15px !important;
        flex-wrap: wrap !important;
    }}

    div[data-testid="column"]:has(.choice-col-marker) div[data-testid="stElementContainer"],
    div[data-testid="stColumn"]:has(.choice-col-marker) div[data-testid="stElementContainer"] {{
        width: auto !important;
    }}

    div[data-testid="column"]:has(.choice-col-marker) button,
    div[data-testid="stColumn"]:has(.choice-col-marker) button {{
        min-width: 140px !important;
        width: auto !important;
        margin: 0 !important;
    }}

    /* Choice Buttons Styling */
    div[data-testid="stElementContainer"][class*="st-key-game_choice_"] button,
    div[data-testid="stElementContainer"] [class*="st-key-game_choice_"] button {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        background-image: url('data:image/png;base64,{btn_b64}') !important;
        background-size: 100% 100% !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        border: none !important;
        min-height: 65px !important;
        height: auto !important;
        width: 100% !important; /* This makes it fill the column */
        padding: 10px 20px !important;
        margin-bottom: 8px !important;
    }}

    div[data-testid="stElementContainer"][class*="st-key-game_choice_"] button p,
    div[data-testid="stElementContainer"] [class*="st-key-game_choice_"] button p {{
        color: black !important;
        font-size: 1.5rem !important;
        text-shadow: 2px 2px 0 #fff !important;
        white-space: normal !important; 
        line-height: 1.2 !important;
    }}
    div[data-testid="stElementContainer"][class*="st-key-game_choice_"] button:hover,
    div[data-testid="stElementContainer"] [class*="st-key-game_choice_"] button:hover {{
        filter: brightness(1.2) !important;
        border-color: #22c55e !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Header
    h1, h2, h3, h4 = st.columns([1, 2, 6, 1])
    with h1: 
        if st.button("← Menu"): navigate_to("main_menu")
    with h2:
        st.markdown(f"<div style='text-align: right; font-size: 1.2rem;' class='hp-text'><b>♥ {hp}/100</b></div>", unsafe_allow_html=True)
        st.progress(min(max(hp, 0), 100) / 100.0)
    with h3:
        st.markdown(f"<div style='text-align: right; font-size: 1.5rem; margin-top: 5px; display: flex; justify-content: flex-end; align-items: center;'><b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
    with h4:
        pfp_base64 = get_user_pfp(user_data)
        st.markdown(get_pfp_button_css(pfp_base64, size="50px"), unsafe_allow_html=True)
        if st.button("PFP", key="game_pfp_btn"): navigate_to("settings")

    # Content Area
    text, fg_img = "", None
    
    if scene >= 100:
        _, center_col, _ = st.columns([1, 1, 1]) 
        with center_col:
            if scene == 100: # DEATH SCREEN
                st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
                st.markdown("<h1 style='font-size: 6rem; text-align: center; color: #7c0a02;'>YOU DIED</h1>", unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: center;'>Your journey ends here.</h3><br><br>", unsafe_allow_html=True)
                if st.button("Restart Game", key="game_choice_restart", use_container_width=True): 
                    update_progress(default_progress())

            elif scene == 101: # WIN SCREEN 
                st.markdown("<div style='height: 3vh;'></div>", unsafe_allow_html=True)
                st.markdown("<h1 style='font-size: 5rem; text-align: center; color: #eab308;'>GAME COMPLETED</h1>", unsafe_allow_html=True)
                new_achs = st.session_state.get("newly_unlocked", [])
                if new_achs:
                    cols = st.columns([1] * len(new_achs) if len(new_achs) <= 4 else 4)
                    for idx, ach in enumerate(new_achs):
                        with cols[idx % 4]:
                            # format filename: "FIXER UPPER" -> "fixer_upper.png"
                            ach_filename = ach.lower().replace(" ", "_") + ".png"
                            ach_path = os.path.join("images", "emblem", ach_filename)
                            
                            if os.path.exists(ach_path):
                                with open(ach_path, "rb") as img_file:
                                    encoded_img = base64.b64encode(img_file.read()).decode()
                                img_html = f"<img src='data:image/png;base64,{encoded_img}' style='width: 200px; height: 200px; object-fit: contain; filter: drop-shadow(3px 3px 0px #000);'/>"
                            else:
                                img_html = "<div style='font-size: 60px;'>🏆</div>"
                            
                            st.markdown(f"""
                            <div style='display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 20px;'>
                                {img_html}
                                <div style='font-size: 1.2rem; font-weight: bold; margin-top: 5px; color: white !important;'>{ach}</div>
                            </div>
                            """, unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: center; color: white !important;'>Check your Profile to see all your unlocked achievements!</h3><br><br>", unsafe_allow_html=True)
                
                if st.button("Play Again", key="game_choice_playagain", use_container_width=True):
                    st.session_state.newly_unlocked = []
                    update_progress(default_progress())
    else:
        _, right_col = st.columns([3, 1])
        
        with right_col:
            st.markdown("<div class='choice-col-marker'></div>", unsafe_allow_html=True)
            
            # Scene Logic
            if scene == 1:
                text = "A boy sits in his room, deep in a game called QUESt.exe..."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 2})
            elif scene == 2:
                text = "His phone battery dies mid-session."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 3})
            elif scene == 3:
                text = "He plugs it in and waits... eyes heavy... until..."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 4})
            elif scene == 4:
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 5})
            elif scene == 5:
                text = "You open your eyes. You are wearing a peasant's tunic.<br>'Wait... this looks like... QUESt.exe?!'<br>'How did I get inside the game?'<br>You spot a wooden sign along the path."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 6})
            elif scene == 6:
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 7})
            elif scene == 7:
                text = "'Okay... I need to be careful.'"
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 8})

            # Level #1
            elif scene == 8:
                text = "Three paths stretch ahead of you.<br>'The left path glitters with little blue berries. The middle path has clusters of dark, plump black berries. The right path is plain — no bushes at all.'"
                if st.button("Left Path", key="game_choice_1"): update_progress({"scene": 9})
                if st.button("Middle Path", key="game_choice_2"): update_progress({"scene": 12})
                if st.button("Right Path", key="game_choice_3"): update_progress({"scene": 15})
            elif scene == 9:
                fg_img = "items/blueberries.png"
                text = "You walk down the left path. Blue berries hang from every bush.<br>They look sweet... but something feels off.<br>Do you eat the blue berries?"
                if st.button("Eat", key="game_choice_1"): update_progress({"scene": 10, "hp": hp - 10})
                if st.button("Don't Eat", key="game_choice_2"): update_progress({"scene": 11})
            elif scene == 10:
                fg_img = "items/blueberries.png"
                text = "You pop a few in your mouth. They taste bitter. Your stomach churns."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 16})
            elif scene == 11:
                text = "You resist the temptation and walk on."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 16})
            elif scene == 12:
                fg_img = "items/blackberries.png"
                text = "You walk down the middle path. Plump black berries weigh down the branches.<br>They smell incredible. Do you eat them?"
                if st.button("Eat", key="game_choice_1"): update_progress({"scene": 13, "hp": min(hp + 20, 100)})
                if st.button("Don't Eat", key="game_choice_2"): update_progress({"scene": 14})
            elif scene == 13:
                fg_img = "items/blackberries.png"
                text = "Delicious! A warm energy surges through you."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 16})
            elif scene == 14:
                text = "You resist and continue down the path."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 16})
            elif scene == 15:
                text = "You walk the plain right path. No berries.<br>Nothing to see here. Just a quiet road."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 16})

            # Level #2
            elif scene == 16:
                fg_img = "items/chest_closed.png"
                text = "A crooked iron chest sits in the middle of the road"
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 16.5})
            elif scene == 16.5:
                fg_img = "items/chest_opened.png"
                text = "Its lid is cracked open. Inside you see three items.<br>'Should I take something? But which one...'"
                if st.button("Steel Spoon", key="game_spoon"): update_progress({"inventory": inventory + ["Steel Spoon"], "scene": 17})
                if st.button("Wooden Sword", key="game_sword"): update_progress({"inventory": inventory + ["Wooden Sword"], "scene": 18})
                if st.button("Bread", key="game_bread"): update_progress({"scene": 19})
            elif scene == 17:
                fg_img = "items/spoon_glitched.png"
                text = "You pocket the steel spoon. Odd choice, but something tells you it'll be useful."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 22})
            elif scene == 18:
                fg_img = "items/sword_glitched.png"
                text = "You grab the wooden sword. It's flimsy, but better than nothing."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 22})
            elif scene == 19:
                fg_img = "items/bread.png"
                text = "You take the bread. It smells fresh. Your stomach growls in appreciation. Will you eat it?"
                if st.button("Eat", key="game_choice_1"): update_progress({"scene": 20, "hp": min(hp + 30, 100)})
                if st.button("Store", key="game_choice_2"): update_progress({"inventory": inventory + ["Bread"], "scene": 21})
            elif scene == 20:
                text = "Your energy increases."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 22})
            elif scene == 21:
                fg_img = "items/bread.png"
                text = "You store the bread for later."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 22})

            # Level #3
            elif scene == 22:
                text = "A gurgling noise fills the path ahead.<br>You freeze. Standing before you is a glitchy, green blob...<br>...wearing a shiny steel bucket as a helmet."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 23})
            elif scene == 23:
                text = "Slime Knight: 'ERR0R... ERR0R... INTRUDER DETECTED—'"
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 24})
            elif scene == 24:
                text = "'He's... glitching? He looks like he's in pain.'"
                if "Steel Spoon" in inventory:
                    if st.button("System Patch", key="game_choice_patch"): 
                        inv = inventory.copy()
                        inv.remove("Steel Spoon")
                        update_progress({"inventory": inv, "scene": 25})
                if st.button("Challenge Duel", key="game_choice_duel"):
                    if "Wooden Sword" in inventory: 
                        inv = inventory.copy()
                        inv.remove("Wooden Sword")
                        update_progress({"inventory": inv, "scene": 26})
                    else: update_progress({"scene": 27, "hp": hp - 20})
                if st.button("Sneak Pass", key="game_choice_sneak"):
                    if random.random() > 0.5: update_progress({"scene": 29})
                    else: update_progress({"scene": 30, "hp": hp - 20})
            elif scene == 25:
                text = "You hold out the steel spoon. The Slime Knight's glitching slows...<br>'SYS_FIX... PATCH ACCEPTED... I am... grateful.'"
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 31})
            elif scene == 26:
                text = "You raise your wooden sword. The Slime Knight charges.<br>You deflect his blows and strike true. He dissolves.<br>The wooden sword splinters on impact — it's now unusable."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 31})
            elif scene == 27:
                text = "You charge barehanded! It's a tough fight.<br>You barely defeat the Slime Knight, bruised and battered."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 31})
            elif scene == 29:
                text = "The Slime Knight doesn't notice. You slip past safely."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 31})
            elif scene == 30:
                text = "Your foot snaps a twig. The Slime Knight spins around!<br>'INTRUDER!'<br>He swats you, hard.<br>You scramble past, wounded."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 31})

            # Level #4
            elif scene == 31:
                text = "A rickety bridge stretches over a dark ravine.<br>Half the planks are missing. It groans in the wind.<br>'There's no way that can hold my weight...'"
                if st.button("Leap Over", key="game_choice_1"): update_progress({"scene": 32, "hp": hp - 20})
                if st.button("Find Other Ways", key="game_choice_2"): update_progress({"scene": 33})
                if "Steel Spoon" in inventory:
                    if st.button("Fix Crossing", key="game_choice_3"):
                        unlock_achievement("FIXER UPPER")
                        inv = inventory.copy()
                        inv.remove("Steel Spoon")
                        update_progress({"inventory": inv, "scene": 34})
            elif scene == 32:
                text = "You take a running jump! You make it — but land hard.<br>Your ankle twists on impact."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 35})
            elif scene == 33:
                text = "You scout along the ravine and discover a narrow rock ledge.<br>It takes longer, but you cross safely."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 35})
            elif scene == 34:
                text = "You use the steel spoon to pry the loose boards back into place.<br>The bridge holds firm. You cross without a scratch."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 35})

            # Level #5
            elif scene == 35:
                text = "A mob of scowling rabbits blocks the path.<br>Their leader — a hulking bunny — steps forward."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 36})
            elif scene == 36:
                text = "Bunny Chief: 'You dare trespass? Then face us in a game of AWESOME!'"
                if "Bread" in inventory:
                    if st.button("Give Bread", key="game_bread"):  
                        inv = inventory.copy()
                        inv.remove("Bread")
                        update_progress({"inventory": inv, "scene": 37})
                if st.button("Play AWESOME", key="game_choice_play"): update_progress({"scene": 38})
                if st.button("Give Up", key="game_choice_giveup"): update_progress({"scene": 41})
            elif scene == 37:
                text = "You hold out the bread with a smile.<br>The Bunny Chief's nose twitches. He snatches it.<br>'...We let you pass. THIS TIME.'"
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 44})

            elif scene == 38:
                text = f"Player: {prog['rps_player']} &nbsp;&nbsp;|&nbsp;&nbsp; Bunny Chief: {prog['rps_bunny']}"
                
                def play_rps(choice):
                    bunny_choice = random.choice(["ROCK", "PAPER", "SCISSOR"])
                    p_wins, b_wins = prog["rps_player"], prog["rps_bunny"]
                    
                    if choice == bunny_choice:
                        result_text = "It's a DRAW!"
                    elif (choice == "ROCK" and bunny_choice == "SCISSOR") or \
                        (choice == "PAPER" and bunny_choice == "ROCK") or \
                        (choice == "SCISSOR" and bunny_choice == "PAPER"):
                        result_text = "You WON this round!"
                        p_wins += 1
                    else:
                        result_text = "You LOST this round!"
                        b_wins += 1
                        
                    # set a toast message to show the result of the round and bunny's choice
                    st.session_state.toast = f"Bunny chose {bunny_choice}! {result_text}"
                        
                    if p_wins >= 3:
                        update_progress({"scene": 39, "rps_player": 0, "rps_bunny": 0})
                    elif b_wins >= 3:
                        update_progress({"scene": 40, "hp": hp - 10, "rps_player": 0, "rps_bunny": 0})
                    else:
                        update_progress({"rps_player": p_wins, "rps_bunny": b_wins})
                        
                if st.button("ROCK", key="game_rock"): play_rps("ROCK")
                if st.button("PAPER", key="game_paper"): play_rps("PAPER")
                if st.button("SCISSOR", key="game_scissors"): play_rps("SCISSOR")

            elif scene == 39:
                text = "YOU WIN! The bunnies cheer reluctantly.<br>The Bunny Chief grumbles and hands you a small flag of allegiance."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 44})
            elif scene == 40:
                text = "CHIEF WINS! The bunnies jeer.<br>The Bunny Chief: 'Pathetic. Play again or face the consequences.'"
                if st.button("Play Again", key="game_choice_play"): update_progress({"scene": 38})
                if st.button("Face Consequences", key="game_choice_giveup"): update_progress({"scene": 41})
            elif scene == 41:
                text = "You raise your hands. 'I give up.'<br>Bunny Chief: 'Then you DUEL ME, coward!'"
                if st.button("Next", key="game_choice_next"):
                    if "Wooden Sword" in inventory: update_progress({"scene": 42})
                    else: update_progress({"scene": 43})
            elif scene == 42:
                text = "You draw your wooden sword. The Chief backs down, impressed.<br>'Tch... Go then.'<br>You pass without harm. The sword survives — barely."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 44})
            elif scene == 43:
                text = "You have nothing to fight with.<br>The Bunny Tribe swarms you.<br>Everything goes dark."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 100})

            # Level #6
            elif scene == 44:
                text = "You push open a great stone door. Inside, a dungeon glows red.<br>Chained to the far wall, a young woman in emerald robes."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 45})
            elif scene == 45:
                text = "Emerald Princess: 'YOU! Please, help me! That beast took me from my kingdom!'"
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 46})
            elif scene == 46:
                text = "In the corner, a massive nest holds a gleaming ruby-red egg.<br>Then; a low, thunderous rumble..."
                if st.button("Next", key="game_choice_next"): update_progress({"scene": 47})
            elif scene == 47:
                text = "RUBY DRAGON: 'WHO DARES WAKE ME...'<br>The dragon opens one enormous eye. It locks onto you.<br>Dragon: 'Hmm. A peasant. How... disappointing. What do you want here?'<br>You: 'I... I just want to finish my journey.'<br>Dragon: 'Then you must choose. And choose wisely.'"
                if st.button("Steal egg, abandon princess", key="game_choice_1"): update_progress({"scene": 48})
                if st.button("Save princess, abandon egg", key="game_choice_2"): update_progress({"scene": 49})
                if st.button("Sacrifice yourself, princess escapes", key="game_choice_3"): update_progress({"scene": 50})
            elif scene == 48:
                text = "You dart past the dragon, grab the egg, and bolt for the exit.<br>The princess screams. The dragon roars.<br>But you're already gone; gold in hand, conscience left behind."
                if st.button("Next", key="game_choice_next"):
                    unlock_achievement("THE GREED")
                    update_progress({"scene": 101})
            elif scene == 49:
                text = "You ignore the glittering egg.<br>You sprint to the princess, break her chains, and pull her toward the door.<br>The dragon bellows but does not give chase — it returns to guard its egg.<br>Outside, the princess thanks you with tears in her eyes."
                if st.button("Next", key="game_choice_next"): 
                    unlock_achievement("THE HEROISM")
                    update_progress({"scene": 101})
            elif scene == 50:
                text = "You turn to the Princess.<br>You: 'Take the egg. Go. Now. End the dragon's line.'<br>She hesitates, then runs. You face the Ruby Dragon alone.<br>Dragon: 'You would die for her? A stranger?'<br>You: 'Someone has to.'<br>The dragon lunges. Everything goes white."
                if st.button("Next", key="game_choice_next"):
                    unlock_achievement("THE LEGENDARY SACRIFICE")
                    update_progress({"scene": 101})

        # Render Visuals
        if fg_img:
            fg_b64 = get_b64(os.path.join("images", fg_img))
            if fg_b64:
                st.markdown(f"<div class='fg-wrapper'><img src='data:image/png;base64,{fg_b64}' /></div>", unsafe_allow_html=True)
        if text:
            if scene <= 7:
                st.markdown(f"<div class='dialogue-wrapper'><div class='dialogue-box-thin'>{text}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='dialogue-wrapper'><div class='dialogue-box'>{text}</div></div>", unsafe_allow_html=True)

    # Inventory Footer
    if 7 < scene < 100:
        inv_html = "".join([get_image_html(i, os.path.join("images", "items", f"{i.lower().split()[-1]}.png")) for i in prog["inventory"]])
        st.markdown(f"""
        <div style='position: fixed; bottom: 0; left: 0; width: 100%; border-top: 1px solid #FFFFFF40; background-color: rgba(0,0,0,0.8); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 999;'>
            <div style='font-size: 1.1rem; display: flex; align-items: center; color: white;'><span style='opacity: 0.5; margin-right: 10px;'>INVENTORY:</span> <div style='display: flex; align-items: center;'>{inv_html}</div></div>
        </div>
        """, unsafe_allow_html=True)

        inv_html=""
        if inventory:
            inv_html = "".join([get_image_html(i, os.path.join("images", "items", f"{i.lower().split()[-1]}.png")) for i in inventory])
        else: 
            inv_html = "<span style='opacity: 0.5;'>Empty</span>"

        st.markdown(f"""
        <div style='position: fixed; bottom: 0; left: 0; width: 100%; border-top: 1px solid #FFFFFF40; background-color: rgba(0,0,0,0.8); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 999;'>
            <div style='font-size: 1.1rem; display: flex; align-items: center; color: white;'><span style='opacity: 0.5; margin-right: 10px;'>INVENTORY:</span> <div style='display: flex; align-items: center;'>{inv_html}</div></div>
        </div>
        """, unsafe_allow_html=True)

# --- ROUTING ---
if st.session_state.page == "auth":
    auth_page()
elif st.session_state.page == "main_menu":
    main_menu()
elif st.session_state.page == "settings":
    settings_page()
elif st.session_state.page == "game":
    game_page()