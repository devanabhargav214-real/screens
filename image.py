import asyncio
import re
import streamlit as st
import edge_tts
import google.generativeai as genai
import requests
import io
import time

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Studio Pro", page_icon="🎬", layout="wide")

# ==========================================
# TOTAL WHITE BACKGROUND & BLACK TEXT FONT
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-heading {
        font-size: 26px; color: #ffffff !important; font-weight: bold; text-align: center;
        background-color: #1e3a8a; padding: 12px; border-radius: 8px; margin-bottom: 25px;
    }
    button[data-baseweb="tab"] { font-size: 15px !important; font-weight: bold !important; color: #1e3a8a !important; }
    button[aria-selected="true"] { border-bottom-color: #1e3a8a !important; color: #1e3a8a !important; background-color: #eff6ff !important; }
    div.stButton > button {
        background-color: #1e3a8a !important; color: #ffffff !important; font-size: 15px !important;
        font-weight: bold !important; border-radius: 6px !important; border: none !important;
        padding: 10px 20px !important; width: 100%; margin-bottom: 10px; transition: background-color 0.3s ease;
    }
    div.stButton > button:hover { background-color: #2563eb !important; }
    div.stDownloadButton > button { background-color: #10b981 !important; color: #ffffff !important; font-size: 15px !important; font-weight: bold !important; border-radius: 6px !important; border: none !important; width: 100%; }
    
    div[data-testid="stTextInput"] input, 
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #1e3a8a !important;
        border-radius: 6px !important;
        font-size: 16px !important;
    }
    ul[role="listbox"] li { background-color: #ffffff !important; color: #000000 !important; }
    p, label, span, div, p li, .stSelectbox label, .stRadio label { color: #000000 !important; font-weight: bold !important; font-size: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# Google Gemini API కాన్ఫిగరేషన్
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception:
    model = None

# =======================================================
# MASTER ULTRA-FALLBACK SERVER ENGINE (ఎప్పటికీ ఎర్రర్ రాదు)
# =======================================================
def fetch_high_quality_text(prompt_text):
    """
    ఈ ఫంక్షన్ 4 విభిన్న ఉచిత సర్వర్ రూట్లను వరుసగా ట్రై చేస్తుంది.
    ఒకటి ఫెయిల్ అయినా ఇంకొకటి వెంటనే డేటాను తెస్తుంది. ఎప్పటికీ ఎర్రర్ రాదు.
    """
    # రూట్ 1: గూగుల్ జెమిని క్లయింట్ (కీ వర్క్ అవుతుంటే)
    if model is not None:
        try:
            response = model.generate_content(prompt_text)
            if response.text and "quota" not in response.text.lower() and "exceeded" not in response.text.lower():
                return response.text.strip()
        except:
            pass # జెమిని కోటా అయిపోతే కింద ఉన్న ఫ్రీ సర్వర్స్ కి వెళ్తుంది

    # బ్యాకప్ మోడల్స్ లిస్ట్ (High-Quality Free AI Hub)
    backup_models = ["searchgpt", "openai", "qwen-2.5-72b", "mistral"]
    
    for current_model in backup_models:
        try:
            encoded_text = requests.utils.quote(prompt_text)
            url = f"https://text.pollinations.ai/{encoded_text}?model={current_model}&json=false"
            res = requests.get(url, timeout=15)
            if res.status_code == 200 and res.text.strip() and "busy" not in res.text.lower() and "quota" not in res.text.lower():
                return res.text.strip()
        except:
            continue # ఒక సర్వర్ బిజీగా ఉంటే ఆటోమేటిక్‌గా నెక్స్ట్ సర్వర్‌కి మారుతుంది
            
    return ""

def play_success_sound():
    st.components.v1.html("""<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2019/2019-84.wav" type="audio/wav"></audio>""", height=0, width=0)

def trigger_vibration():
    st.components.v1.html("""<script>if (window.navigator && window.navigator.vibrate) { window.navigator.vibrate(25); }</script>""", height=0, width=0)

st.markdown('<div class="main-heading">🎬 Gemini & Free-Backup తెలుగు AI వీడియో స్టూడియో</div>', unsafe_allow_html=True)

# సెషన్ స్టేట్ హోల్డర్స్
if "generated_story_holder" not in st.session_state: st.session_state.generated_story_holder = ""
if "generated_scenes_holder" not in st.session_state: st.session_state.generated_scenes_holder = ""

tab1, tab2, tab3, tab4 = st.tabs(["📖 1. Story Generator", "🎙️ 2. Voice Over", "🎬 3. Scenes Divider", "🎨 4. Image Generator"])

# ==========================================
# TAB 1: STORY GENERATOR
# ==========================================
with tab1:
    st.write("### 📝 1. కథను జనరేట్ చేయండి")
    user_topic = st.text_input("మీ కథ టాపిక్ ఇవ్వండి:", placeholder="ఉదాహరణకు: తెనాలి రామకృష్ణ కథలు...", key="t1_topic")
    
    if st.button("కథ జనరేట్ చేయి ✨", key="t1_btn"):
        if user_topic.strip() == "": 
            st.warning("దయచేసి టాపిక్ ఇవ్వండి!")
        else:
            with st.spinner(f"మీరు సెర్చ్ చేసిన '{user_topic}' జనరేట్ అవుతుంది..."):
                master_story_prompt = (
                    f"Write a comprehensive, beautiful, long and detailed short story in pure Telugu language about the topic: '{user_topic}'. "
                    f"The story must be very clear, interesting, structured with paragraphs, and must include a valuable moral (నీతి) at the end."
                )
                
                result_story = fetch_high_quality_text(master_story_prompt)
                
                if result_story:
                    st.session_state.generated_story_holder = result_story
                    st.success("కథ విజయవంతంగా సిద్ధమైంది! కింద బాక్స్ నుండి కాపీ చేసుకోండి.")
                    play_success_sound()
                else:
                    st.error("నెట్‌వర్క్ నెమ్మదిగా ఉంది. దయచేసి ఒకసారి బటన్ మళ్లీ నొక్కండి.")
                    
    st.text_area("📋 ఇక్కడ వచ్చిన కథను కాపీ చేసుకోండి:", value=st.session_state.generated_story_holder, height=350, key="t1_area")

# ==========================================
# TAB 2: VOICE OVER
# ==========================================
with tab2:
    st.write("### 🎙️ 2. కథను పేస్ట్ చేసి ఆడియోగా మార్చండి")
    input_voice_text = st.text_area("📋 మీరు వాయిస్ ఓవర్ చేయాలనుకుంటున్న కథను ఇక్కడ పేస్ట్ చేయండి:", height=200, key="t2_area")
    voice_option = st.selectbox("వాయిస్ ఎంచుకోండి:", ("మగవారి వాయిస్ (Mohan)", "ఆడవారి వాయిస్ (Shruti)"), key="t2_select")
    voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        speed_slider = st.slider("వేగం (Speed):", -50, 50, -4, 2, format="%d%%", key="t2_speed")
        voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
        if speed_slider: trigger_vibration()
    with col2:
        volume_slider = st.slider("వాల్యూమ్ (Volume):", -50, 50, 8, 2, format="%d%%", key="t2_vol")
        voice_volume = f"{'' if volume_slider < 0 else '+'}{volume_slider}%"
        if volume_slider: trigger_vibration()
    with col3:
        pitch_slider = st.slider("పిచ్ (Pitch):", -20, 20, 0, 1, format="%dHz", key="t2_pitch")
        voice_pitch = f"{'' if pitch_slider < 0 else '+'}{pitch_slider}Hz"
        if pitch_slider: trigger_vibration()

    def split_text(text, max_chars=1000):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_chars: current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk: chunks.append(current_chunk.strip())
                current_chunk = sentence
        if current_chunk: chunks.append(current_chunk.strip())
        return chunks

    async def generate_audio(full_text, voice_model, speed, volume, pitch):
        chunks = split_text(full_text)
        audio_data = b""
        for chunk in chunks:
            communicate = edge_tts.Communicate(chunk, voice_model, rate=speed, volume=volume, pitch=pitch)
            async for chunk_data in communicate.stream():
                if chunk_data["type"] == "audio": audio_data += chunk_data["data"]
        return audio_data

    if st.button("ఆడియోగా మార్చు 🚀", key="t2_btn"):
        if input_voice_text.strip() == "": st.warning("దయచేసి టెక్స్ట్ పేస్ట్ చేయండి!")
        else:
            with st.spinner("మీ ఆడియో రికార్డర్ అవుతుంది..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    final_audio_bytes = loop.run_until_complete(generate_audio(input_voice_text, voice, voice_speed, voice_volume, voice_pitch))
                    st.audio(final_audio_bytes, format="audio/mp3")
                    st.download_button(label="📥 ఆడియో డౌน์โหลด", data=final_audio_bytes, file_name="voice.mp3", mime="audio/mp3")
                    play_success_sound()
                except Exception as e: st.error(f"లోపం: {e}")

# ==========================================
# TAB 3: SCENES DIVIDER
# ==========================================
with tab3:
    st.write("### 🎬 3. కథను పేస్ట్ చేసి సీన్లుగా విడగొట్టండి")
    input_story_to_split = st.text_area("📋 విజువల్ సీన్లుగా మార్చాల్సిన కథను ఇక్కడ పేస్ట్ చేయండి:", height=200, key="t3_area")
    
    if st.button("సీన్లుగా విడగొట్టు 🎬", key="t3_btn"):
        if input_story_to_split.strip() == "": 
            st.warning("దయచేసి కథను పేస్ట్ చేయండి!")
        else:
            with st.spinner("కథను సీన్లుగా విడగొడుతోంది..."):
                master_divider_prompt = f"Read this Telugu story: '{input_story_to_split}'. Break it down into exactly 4 separate descriptive visual action scenes in Telugu. Write each scene on a strict new line. Do not use numbers, bullets, or symbols."
                
                result_scenes = fetch_high_quality_text(master_divider_prompt)
                
                if result_scenes:
                    st.session_state.generated_scenes_holder = result_scenes
                    st.success("సీన్లు సిద్ధమయ్యాయి! కింద బాక్స్ నుండి కాపీ చేసుకోండి.")
                    play_success_sound()
                else:
                    st.error("సర్వర్ బిజీగా ఉంది. దయచేసి ఒకసారి మళ్లీ ట్రై చేయండి.")
                        
    st.text_area("🎬 ఇక్కడ వచ్చిన సీన్లను కాపీ చేసుకోండి (లైన్ బై లైన్):", value=st.session_state.generated_scenes_holder, height=220, key="t3_out_area")

# ==========================================
# TAB 4: IMAGE GENERATOR
# ==========================================
with tab4:
    st.write("### 🎨 4. సీన్లను పేస్ట్ చేసి ఇమేజెస్ జనరేట్ చేయండి")
    input_scenes_to_draw = st.text_area("📋 సీన్లను ఇక్కడ పేస్ట్ చేయండి (లైన్ బై లైన్):", value="తెనాలి రామకృష్ణ రాజుగారి ఆస్థానంలో నిలబడ్డాడు.\nరాజుగారు సింహాసనంపై కూర్చున్నారు.", height=150, key="t4_area")
    selected_style = st.radio("స్టైల్ ఎంచుకోండి:", ("2D Indian Cartoon Style (2D కార్టూన్)", "Real Life / Cinematic Style (నిజమైన ఫొటో లాగా)", "3D Disney Pixar Style (3D యానిమేషన్)"), key="t4_style")
    ratio_option = st.radio("వీడియో సైజ్:", ("16:9 (యూట్యూబ్)", "9:16 (షార్ట్స్)"), key="t4_ratio")
    img_width, img_height = (1024, 576) if "16:9" in ratio_option else (576, 1024)

    framing_rules = ", wide-angle established master shot framing, full body details from head to toe, vivid colorful beautiful background, sharp clear facial features, 8k resolution"
    if "2D" in selected_style: style_prompt_addition = f"in traditional beautiful Indian 2D children's storybook cartoon illustration style, bright flat vector colors, clean black outlines{framing_rules}"
    elif "Real" in selected_style: style_prompt_addition = f"photorealistic real-life cinematic film style, highly authentic human lighting, real world environments{framing_rules}"
    else: style_prompt_addition = f"in high-end 3D animation style, cute Disney Pixar character design, smooth rendered 3D textures{framing_rules}"

    if st.button("బొమ్మలను తయారుచేయి 🎨", key="t4_btn"):
        if input_scenes_to_draw.strip() == "": st.warning("దయచేసి సీన్లను రాయండి!")
        else:
            lines = [line.strip() for line in input_scenes_to_draw.split('\n') if line.strip()]
            st.success(f"మొత్తం {len(lines)} చిత్రాలు సిద్ధమవుతున్నాయి...")
            
            for i, t_scene in enumerate(lines):
                st.write(f"**సీన్ {i+1}:** {t_scene}")
                with st.spinner("మీరు ఇచ్చిన సీన్ కి ఇమేజ్ వస్తుంది..."):
                    
                    # డిఫాల్ట్ ఇంగ్లీష్ ప్రాంప్ట్ సెటప్
                    english_prompt = f"{t_scene}, {style_prompt_addition}"
                    
                    gemini_prompt = f"Convert this Telugu story scene action layout into a descriptive English image generation prompt. Art style: {style_prompt_addition}. Give ONLY raw prompt text. Telugu text: '{t_scene}'"
                    
                    translated_out = fetch_high_quality_text(gemini_prompt)
                    if translated_out:
                        english_prompt = translated_out
                    
                    try:
                        encoded_scene = requests.utils.quote(english_prompt)
                        image_url = f"https://image.pollinations.ai/p/{encoded_scene}?width={img_width}&height={img_height}&nologo=true&model=flux"
                        
                        img_response = requests.get(image_url, timeout=45)
                        if img_response.status_code == 200:
                            st.image(img_response.content, caption=f"Scene {i+1}", use_container_width=True)
                            st.download_button(label="📥 ఫోటో డౌน์โหลด", data=io.BytesIO(img_response.content), file_name=f"scene_{i+1}.jpg", mime="image/jpeg", key=f"dl_{i}")
                            st.markdown("---")
                        else: st.error(f"సీన్ {i+1} ఇమేజ్ లోడ్ అవ్వలేదు.")
                    except Exception as e: st.error(f"లోపం: {e}")
                time.sleep(2) # కోటా కాపాడటానికి బ్రేక్
            play_success_sound()
