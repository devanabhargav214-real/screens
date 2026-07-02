import asyncio
import re
import streamlit as st
import edge_tts
import google.generativeai as genai
import requests
import io

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Gemini Pro Studio", page_icon="🎬", layout="wide")

# ==========================================
# SIMPLE HIGH-CONTRAST WHITE & BLUE STYLING
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-heading {
        font-size: 26px; color: #ffffff !important; font-weight: bold; text-align: center;
        background-color: #1e3a8a; padding: 12px; border-radius: 8px; margin-bottom: 25px;
    }
    button[data-baseweb="tab"] { font-size: 16px !important; font-weight: bold !important; color: #1e3a8a !important; }
    button[aria-selected="true"] { border-bottom-color: #1e3a8a !important; color: #1e3a8a !important; background-color: #eff6ff !important; }
    div.stButton > button {
        background-color: #1e3a8a !important; color: #ffffff !important; font-size: 15px !important;
        font-weight: bold !important; border-radius: 6px !important; border: none !important;
        padding: 10px 20px !important; width: 100%; margin-bottom: 10px; transition: background-color 0.3s ease;
    }
    div.stButton > button:hover { background-color: #2563eb !important; }
    div.stDownloadButton > button { background-color: #10b981 !important; color: #ffffff !important; font-size: 15px !important; font-weight: bold !important; border-radius: 6px !important; border: none !important; width: 100%; }
    div.stDownloadButton > button:hover { background-color: #059669 !important; }
    p, label, span, div, p li, .stSelectbox label, .stRadio label { color: #000000 !important; font-weight: bold !important; font-size: 15px !important; }
    textarea { color: #000000 !important; font-weight: normal !important; }
    </style>
    """, unsafe_allow_html=True)

# Google Gemini API కాన్ఫిగరేషన్
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    model = None

def play_success_sound():
    sound_html = """<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2019/2019-84.wav" type="audio/wav"></audio>"""
    st.components.v1.html(sound_html, height=0, width=0)

def trigger_vibration():
    vibrate_html = """<script>if (window.navigator && window.navigator.vibrate) { window.navigator.vibrate(25); }</script>"""
    st.components.v1.html(vibrate_html, height=0, width=0)

st.markdown('<div class="main-heading">🎬 Gemini తెలుగు AI కంప్లీట్ వీడియో స్టూడియో</div>', unsafe_allow_html=True)

# Session States
if "content_text" not in st.session_state:
    st.session_state.content_text = ""
if "scenes_manual_text" not in st.session_state:
    st.session_state.scenes_manual_text = "అడవిలో ఒక కాకి ఉంది.\nకాకికి చాలా దాహం వేసింది.\nఅక్కడ ఒక కుండ కనిపించింది.\nకుండలో నీళ్లు చాలా కిందకి ఉన్నాయి."

tab1, tab2, tab3 = st.tabs(["📖 1. Gemini Story Generator", "🎙️ 2. Voice Over", "🎨 3. Gemini Image Generator"])

# ==========================================
# TAB 1: AI STORY GENERATOR
# ==========================================
with tab1:
    st.write("### 📝 మీ టాపిక్ ఇవ్వండి - గూగుల్ జెమిని కథను రాస్తుంది")
    user_topic = st.text_input("మీకు కావలసిన టాపిక్ ఇక్కడ టైప్ చేయండి:", placeholder="ఉదాహరణకు: తెలివైన కాకి కథ, చందమామ నీతి కథలు...")

    if st.button("కథ జనరేట్ చేయి ✨", key="gen_content_tab"):
        if user_topic.strip() == "":
            st.warning("దయచేసి ఏదైనా ఒక టాపిక్ టైప్ చేయండి!")
        elif model is None:
            st.error("Gemini API Key సెట్ చేయబడలేదు! దయచేసి Streamlit Secrets లో GEMINI_API_KEY యాడ్ చేయండి.")
        else:
            with st.spinner("గూగుల్ జెమిని సర్వర్ ద్వారా కథ సిద్ధమవుతోంది..."):
                try:
                    response = model.generate_content(
                        f"Write a beautiful, engaging short story in clear and pure Telugu language about the topic: '{user_topic}'. Ensure proper vocabulary and grammar."
                    )
                    if response.text:
                        st.session_state.content_text = response.text.strip()
                        st.success("కథ విజయవంతంగా సిద్ధమైంది!")
                        play_success_sound()
                except Exception as e:
                    st.error(f"Gemini API లోపం వచ్చింది: {e}")

    edited_content = st.text_area("📋 జనరేట్ అయిన కథ (ఇక్కడ మీరు మార్పులు చేసుకోవచ్చు):", value=st.session_state.content_text, height=250, key="content_area")
    st.session_state.content_text = edited_content

# ==========================================
# TAB 2: VOICE OVER
# ==========================================
with tab2:
    st.write("### 🎙️ టెక్స్ట్‌ను నాచురల్ ఆడియో లాగా మార్చండి")
    
    voice_option = st.selectbox("వాయిస్ మోడల్ ఎంచుకోండి (Voice):", ("మగవారి వాయిస్ (Mohan)", "ఆడవారి వాయిస్ (Shruti)"), key="voice_select")
    voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"

    col1, col2, col3 = st.columns(3)
    with col1:
        speed_slider = st.slider("వాయిస్ వేగం (Speed):", -50, 50, -4, 2, format="%d%%", key="speed_v")
        voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
        if speed_slider: trigger_vibration()
    with col2:
        volume_slider = st.slider("వాల్యూమ్ స్థాయి (Volume):", -50, 50, 8, 2, format="%d%%", key="vol_v")
        voice_volume = f"{'' if volume_slider < 0 else '+'}{volume_slider}%"
        if volume_slider: trigger_vibration()
    with col3:
        pitch_slider = st.slider("వాయిస్ పిచ్ (Pitch):", -20, 20, 0, 1, format="%dHz", key="pitch_v")
        voice_pitch = f"{'' if pitch_slider < 0 else '+'}{pitch_slider}Hz"
        if pitch_slider: trigger_vibration()

    def split_text(text, max_chars=1000):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_chars:
                current_chunk += " " + sentence if current_chunk else sentence
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
                if chunk_data["type"] == "audio":
                    audio_data += chunk_data["data"]
        return audio_data

    if st.button("టెక్స్ట్‌ను ఆడియోగా మార్చు 🚀", key="audio_gen_trigger"):
        if st.session_state.content_text.strip() == "":
            st.warning("మొదటి ట్యాబ్‌లో ఎలాంటి సమాచారం లేదు!")
        else:
            with st.spinner("స్పష్టమైన ఆడియో రికార్డ్ అవుతోంది..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    final_audio_bytes = loop.run_until_complete(
                        generate_audio(st.session_state.content_text, voice, voice_speed, voice_volume, voice_pitch)
                    )
                    st.audio(final_audio_bytes, format="audio/mp3")
                    st.download_button(label="📥 ఆడియో ఫైల్ డౌน์โหลด చేయండి", data=final_audio_bytes, file_name="telugu_gemini_voice.mp3", mime="audio/mp3")
                    play_success_sound()
                except Exception as e: 
                    st.error(f"ఆడియో లోపం: {e}")

# ==========================================
# TAB 3: GEMINI-POWERED IMAGE GENERATOR (FIXED STYLES)
# ==========================================
with tab3:
    st.write("### 🎨 ప్రతి తెలుగు లైన్ ని బట్టి ఇమేజెస్ జనరేట్ చేయండి")
    
    edited_manual_scenes = st.text_area("🎬 ఇమేజ్ సీన్లు (లైన్ బై లైన్ తెలుగులో టైప్ చేయండి):", value=st.session_state.scenes_manual_text, height=150, key="manual_scenes_area")
    st.session_state.scenes_manual_text = edited_manual_scenes

    # ఇమేజ్ స్టైల్స్ ఎంపిక
    selected_style = st.radio(
        "ఇమేజ్ స్టైల్ ఎంచుకోండి (Image Style):",
        ("2D Indian Cartoon Style (2D కార్టూన్)", "Real Life / Cinematic Style (నిజమైన ఫొటో లాగా)", "3D Disney Pixar Style (3D యానిమేషన్)"),
        key="style_radio"
    )

    ratio_option = st.radio("వీడియో సైజ్ (Aspect Ratio):", ("16:9 (యూట్యూబ్)", "9:16 (షార్ట్స్)"), key="ratio_in")
    img_width, img_height = (1024, 576) if "16:9" in ratio_option else (576, 1024)

    # వైడ్ షాట్ మరియు స్పష్టమైన ఫీచర్స్ కోసం ఫ్రేమింగ్ రూల్స్
    framing_rules = (
        ", wide-angle established master shot framing, no cropped elements, show full body details from head to toe, "
        "vivid colorful beautiful background, hyper-detailed sharp eyes, crisp clear facial features, 8k resolution"
    )

    # యూజర్ ఎంచుకున్న రేడియో బటన్ ని బట్టి స్టైల్ రూల్స్
    if "2D" in selected_style:
        style_prompt_addition = f"in traditional beautiful Indian 2D children's storybook cartoon illustration style, bright flat vector colors, clean black outlines{framing_rules}"
    elif "Real" in selected_style:
        style_prompt_addition = f"photorealistic real-life cinematic film style, highly authentic human lighting, real world environments, professional photography{framing_rules}"
    else:
        style_prompt_addition = f"in high-end 3D animation style, cute Disney Pixar character design, smooth rendered 3D textures, magical cinematic lighting{framing_rules}"

    if st.button("సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨", key="image_gen_trigger"):
        if st.session_state.scenes_manual_text.strip() == "":
            st.warning("దయచేసి బాక్సులో కనీసం ఒక లైన్ సీన్ అయినా రాయండి!")
        elif model is None:
            st.error("Gemini API Key సెట్ చేయబడలేదు! దయచేసి Streamlit Secrets లో GEMINI_API_KEY యాడ్ చేయండి.")
        else:
            lines = [line.strip() for line in st.session_state.scenes_manual_text.split('\n') if line.strip()]
            st.success(f"మొత్తం {len(lines)} లైన్లకు ఇమేజెస్ సిద్ధమవుతున్నాయి...")
            
            for i, t_scene in enumerate(lines):
                st.write(f"**సీన్ {i+1}:** {t_scene}")
                with st.spinner(f"Gemini మరియు Flux కలిసి సీన్ {i+1} ఫోటోని తయారుచేస్తున్నాయి..."):
                    try:
                        # జెమినికి తెలుగు ప్రాంప్ట్ పంపి దాన్ని పర్ఫెక్ట్ ఇంగ్లీష్ ఇమేజ్ ప్రాంప్ట్ గా మారుస్తున్నాం
                        gemini_prompt = (
                            f"You are an expert AI Image prompt generator. Convert this Telugu story scene description "
                            f"into a highly detailed, descriptive, visual English prompt for image generation. "
                            f"The output must strictly be styled in: {style_prompt_addition}. "
                            f"Do not write any introductory text like 'Here is the prompt', give ONLY the final detailed English prompt text."
                            f"Telugu Scene Text: '{t_scene}'"
                        )
                        
                        response = model.generate_content(gemini_prompt)
                        english_prompt = response.text.strip() if response.text else f"{t_scene}, {style_prompt_addition}"
                        
                        # ఇమేజ్ జనరేషన్ (Flux API ద్వారా)
                        encoded_scene = requests.utils.quote(english_prompt)
                        image_url = f"https://image.pollinations.ai/p/{encoded_scene}?width={img_width}&height={img_height}&nologo=true&model=flux"
                        
                        img_response = requests.get(image_url, timeout=40)
                        if img_response.status_code == 200:
                            st.image(img_response.content, caption=f"Scene {i+1} Output ({selected_style})", use_container_width=True)
                            st.download_button(
                                label=f"📥 సీన్ {i+1} ఇమేజ్ డౌน์โหลด చేయండి", data=io.BytesIO(img_response.content),
                                file_name=f"scene_{i+1}.jpg", mime="image/jpeg", key=f"dl_gemini_img_{i}"
                            )
                            st.markdown("---")
                        else:
                            st.error(f"సీన్ {i+1} ఇమేజ్ లోడ్ అవ్వలేదు.")
                    except Exception as e:
                        st.error(f"తప్పు జరిగింది: {e}")
            play_success_sound()
