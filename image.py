import asyncio
import re
import streamlit as st
import edge_tts
import requests
import io

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Studio Pro", page_icon="🎬", layout="wide")

# ==========================================
# SIMPLE WHITE & BLUE INTERFACE STYLING
# ==========================================
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff !important;
    }
    .main-heading {
        font-size: 28px;
        color: #ffffff !important;
        font-weight: bold;
        text-align: center;
        background-color: #1e3a8a;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    
    /* Tabs custom styling for Blue theme */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #1e3a8a !important;
    }
    button[aria-selected="true"] {
        border-bottom-color: #1e3a8a !important;
        color: #1e3a8a !important;
        background-color: #eff6ff !important;
    }

    div.stButton > button {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 8px 20px !important;
        width: 100%;
        margin-bottom: 10px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #2563eb !important;
    }
    div.stDownloadButton > button {
        background-color: #10b981 !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        width: 100%;
    }
    div.stDownloadButton > button:hover {
        background-color: #059669 !important;
    }
    p, label, span, div, .stRadio, p li {
        color: #1f2937 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

def play_success_sound():
    sound_html = """
    <audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2019/2019-84.wav" type="audio/wav"></audio>
    """
    st.components.v1.html(sound_html, height=0, width=0)

def trigger_vibration():
    vibrate_html = """
    <script>if (window.navigator && window.navigator.vibrate) { window.navigator.vibrate(30); }</script>
    """
    st.components.v1.html(vibrate_html, height=0, width=0)

st.markdown('<div class="main-heading">🎬 తెలుగు AI ఆటోమేటిక్ వీడియో స్టూడియో</div>', unsafe_allow_html=True)

# Session States initialization
if "story_text" not in st.session_state:
    st.session_state.story_text = ""
if "scenes_manual_text" not in st.session_state:
    st.session_state.scenes_manual_text = "ఆడవిలో ఒక కాకి ఉంది.\nకాకికి చాలా దాహం వేసింది.\nఅక్కడ ఒక కుండ కనిపించింది.\nకుండలో నీళ్లు చాలా కిందకి ఉన్నాయి."

# CREATE INDIVIDUAL TABS
tab1, tab2, tab3 = st.tabs(["📖 1. Story Generator", "🎙️ 2. Voice Over", "🎨 3. Image Generator"])

# ==========================================
# TAB 1: STORY GENERATOR
# ==========================================
with tab1:
    st.subheader("📝 కథను సిద్ధం చేయండి")
    topic = st.text_input("మీ కథ టాపిక్ ఇక్కడ టైప్ చేయండి:", placeholder="ఉదాహరణకు: కాకి మరియు కుండ కథ...")

    if st.button("కథ జనరేట్ చేయి 📖", key="gen_story_tab"):
        if topic.strip() == "":
            st.warning("దయచేసి ఏదైనా ఒక టాపిక్ ఇవ్వండి!")
        else:
            with st.spinner("AI కథను వేగంగా తయారు చేస్తోంది..."):
                try:
                    prompt = f"Write a beautiful short story in clear Telugu language about the topic: '{topic}'."
                    encoded_prompt = requests.utils.quote(prompt)
                    url = f"https://text.pollinations.ai/{encoded_prompt}?model=searchgpt&json=false"
                    response = requests.get(url)
                    
                    if response.status_code == 200 and response.text.strip() != "":
                        st.session_state.story_text = response.text.strip()
                        st.success("కథ సిద్ధమైంది! ఈ కథను వాయిస్ ఓవర్ లేదా ఇమేజ్ ట్యాబ్స్ లో వాడుకోవచ్చు.")
                        play_success_sound()
                    else:
                        st.error("సర్వర్ బిజీగా ఉంది. దయచేసి మరోసారి ట్రై చేయండి.")
                except Exception as e: 
                    st.error(f"కనెక్షన్ లోపం: {e}")

    edited_story = st.text_area("📖 ప్రస్తుత కథ (ఇక్కడ మీరు మార్పులు చేసుకోవచ్చు):", value=st.session_state.story_text, height=250, key="story_area")
    st.session_state.story_text = edited_story

# ==========================================
# TAB 2: VOICE OVER
# ==========================================
with tab2:
    st.subheader("🎙️ కథను ఆడియో లాగా మార్చండి")
    
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

    if st.button("కథను ఆడియోగా మార్చు 🚀", key="audio_gen_trigger"):
        if st.session_state.story_text.strip() == "":
            st.warning("ట్యాబ్ 1 లో కథ లేదు! దయచేసి ఇక్కడ డైరెక్ట్ గా కథను టైప్ చేయండి లేదా ట్యాబ్ 1 లో జనరేట్ చేయండి.")
        
        with st.spinner("ఆడియో రికార్డ్ అవుతోంది..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_audio_bytes = loop.run_until_complete(
                    generate_audio(st.session_state.story_text, voice, voice_speed, voice_volume, voice_pitch)
                )
                st.audio(final_audio_bytes, format="audio/mp3")
                st.download_button(label="📥 కథ ఆడియో ఫైల్ డౌน์โหลด చేయండి", data=final_audio_bytes, file_name="story_voice.mp3", mime="audio/mp3")
                play_success_sound()
            except Exception as e: 
                st.error(f"లోపం: {e}")

# ==========================================
# TAB 3: IMAGE GENERATOR (SCENE REMOVED - DIRECT)
# ==========================================
with tab3:
    st.subheader("🎨 ఇమేజెస్ జనరేట్ చేయండి")
    st.info("గమనిక: సీన్స్ జనరేషన్ తీసివేయబడింది. కింద ఉన్న బాక్సులో ఒక్కో లైన్ లో ఒక్కో సీన్ టైప్ చేయండి. ప్రతి లైన్ కి ఒక ఫోటో వస్తుంది.")
    
    edited_manual_scenes = st.text_area("🎬 ఇమేజ్ సీన్లు (లైన్ బై లైన్ టైప్ చేయండి):", value=st.session_state.scenes_manual_text, height=180, key="manual_scenes_area")
    st.session_state.scenes_manual_text = edited_manual_scenes

    user_style_input = st.text_input("ఇమేజ్ స్టైల్ (ఉదా: cartoon, cinematic, anime):", placeholder="ఏమీ ఇవ్వకపోతే డిఫాల్ట్ 2D ఇండియన్ కార్టూన్ వస్తుంది...", key="style_in")

    ratio_option = st.radio("వీడియో సైజ్ (Aspect Ratio):", ("16:9 (యూట్యూబ్)", "9:16 (షార్ట్స్)"), key="ratio_in")
    img_width, img_height = (1024, 576) if "16:9" in ratio_option else (576, 1024)

    style_keyword = user_style_input.lower().strip()
    framing_rules = (
        ", established wide shot framing, no close-ups, show entire bodies and full characters from head to toe, "
        "completely visible clear background environment, crisp sharp facial features, highly detailed distinct eyes"
    )

    if "anime" in style_keyword or "japanese" in style_keyword:
        style_prompt_addition = f"in beautiful vibrant Japanese anime studio Ghibli cartoon style, detailed backgrounds{framing_rules}"
    elif "cartoon" in style_keyword:
        style_prompt_addition = f"in an amazing 2D cartoon illustration style, bright flat colors, clear outlines{framing_rules}"
    elif "cinematic" in style_keyword:
        style_prompt_addition = f"8k resolution, photorealistic cinematic film style, dynamic real-life lighting{framing_rules}"
    else:
        style_prompt_addition = f"in beautiful traditional Indian 2D cartoon book illustration style, South Indian character design, clean precise outlines, solid rich colors{framing_rules}"

    if st.button("సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨", key="image_gen_trigger"):
        if st.session_state.scenes_manual_text.strip() == "":
            st.warning("దయచేసి బాక్సులో కనీసం ఒక లైన్ సీన్ అయినా రాయండి!")
        else:
            lines = [line.strip() for line in st.session_state.scenes_manual_text.split('\n') if line.strip()]
            st.success(f"మొత్తం {len(lines)} లైన్లకు ఇమేజెస్ సిద్ధమవుతున్నాయి...")
            
            for i, t_scene in enumerate(lines):
                st.write(f"**సీన్ {i+1}:** {t_scene}")
                with st.spinner(f"సీన్ {i+1} ఫోటో తయారవుతోంది..."):
                    try:
                        translate_prompt = (
                            f"Convert this Telugu story action into a highly descriptive English image prompt. "
                            f"The output visual asset must strictly look like {style_prompt_addition}. "
                            f"Provide only the detailed English text scene layout, nothing else. "
                            f"Telugu text: '{t_scene}'"
                        )
                        encoded_t_prompt = requests.utils.quote(translate_prompt)
                        translate_response = requests.get(f"https://text.pollinations.ai/{encoded_t_prompt}?json=false")
                        
                        if translate_response.status_code == 200:
                            english_prompt = translate_response.text.strip()
                            encoded_scene = requests.utils.quote(english_prompt)
                            image_url = f"https://image.pollinations.ai/p/{encoded_scene}?width={img_width}&height={img_height}&nologo=true&model=flux"
                            
                            img_response = requests.get(image_url)
                            if img_response.status_code == 200:
                                st.image(img_response.content, caption=f"Scene {i+1} Output", use_container_width=True)
                                st.download_button(
                                    label=f"📥 సీన్ {i+1} ఇమేజ్ డౌน์โหลด చేయండి", data=io.BytesIO(img_response.content),
                                    file_name=f"scene_{i+1}.jpg", mime="image/jpeg", key=f"dl_manual_img_{i}"
                                )
                                st.markdown("---")
                            else:
                                st.error(f"సీన్ {i+1} ఇమేజ్ లోడ్ అవ్వలేదు.")
                        else:
                            st.error("ట్రాన్స్‌లేషన్ సర్వర్ బిజీగా ఉంది.")
                    except Exception as e:
                        st.error(f"తప్పు జరిగింది: {e}")
            play_success_sound()
