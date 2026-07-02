import asyncio
import re
import streamlit as st
import edge_tts
import requests
import io

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Cartoon Studio", page_icon="🎬", layout="wide")

# ==========================================
# CUSTOM CSS FOR COLORFUL ATTRACTIVE CARTOON UI
# ==========================================
st.markdown("""
    <style>
    /* మెయిన్ బ్యాక్‌గ్రౌండ్ కలర్ */
    .stApp {
        background-color: #f7f9fc;
    }
    
    /* మెయిన్ టైటిల్ స్టైలింగ్ */
    .main-title {
        font-size: 42px !important;
        color: #ff6f61 !important;
        font-weight: bold;
        text-align: center;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 18px;
        color: #4a5568;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* ప్రతి స్టెప్ కార్డ్ బాక్స్ (Cartoon Container) */
    .step-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.05);
        border: 3px solid #e2e8f0;
        margin-bottom: 30px;
    }
    
    /* హెడర్స్ రంగులు */
    h1, h2, h3 {
        color: #2b6cb0 !important;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    
    /* స్ట్రీమ్‌లిట్ బటన్స్ కార్టూన్ స్టైల్ లోకి మార్చడం */
    div.stButton > button {
        background-color: #ff8c00 !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: bold !important;
        border-radius: 25px !important;
        border: 2px solid #e28743 !important;
        padding: 10px 25px !important;
        box-shadow: 0px 4px 0px #d97706 !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        transform: translateY(2px);
        box-shadow: 0px 2px 0px #d97706 !important;
        background-color: #ffa500 !important;
    }
    div.stButton > button:active {
        transform: translateY(4px);
        box-shadow: none !important;
    }
    
    /* డౌన్‌లోడ్ బటన్ కి వేరే కలర్ (Green/Teal) */
    div.stDownloadButton > button {
        background-color: #2ec4b6 !important;
        color: white !important;
        border-radius: 25px !important;
        border: 2px solid #20a498 !important;
        box-shadow: 0px 4px 0px #0f7a70 !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #33d6c7 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# వెబ్‌సైట్ హెడర్
st.markdown('<div class="main-title">🎬 తెలుగు AI కార్టూన్ వీడియో స్టూడియో</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">మీ ఐడియా ఇవ్వండి - వాయిస్ ఓవర్ మరియు బొమ్మలతో కూడిన అద్భుతమైన కథను నిమిషాల్లో పొందండి!</div>', unsafe_allow_html=True)

# సెషన్ స్టేట్
if "story_text" not in st.session_state:
    st.session_state.story_text = ""
if "scenes_text" not in st.session_state:
    st.session_state.scenes_text = ""

# ==========================================
# STEP 1: స్టోరీ మరియు సీన్స్ ఆటోమేటిక్ జనరేషన్
# ==========================================
st.markdown('<div class="step-box">', unsafe_allow_html=True)
st.header("Step 1: 📝 కథ మరియు సీన్స్ సిద్ధం చేయండి")
topic = st.text_input("మీ కథ టాపిక్ ఇక్కడ ఇవ్వండి:", placeholder="ఉదాహరణకు: అడవిలో సింహం మరియు ఎలుక స్నేహం...")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("1. కథ జనరేట్ చేయి 📖", key="gen_only_story"):
        if topic.strip() == "":
            st.warning("దయచేసి ఏదైనా ఒక టాపిక్ ఇవ్వండి!")
        else:
            with st.spinner("AI మీ కోసం అద్భుతమైన కథను రాస్తోంది..."):
                try:
                    prompt = f"Write a highly engaging short story in pure Telugu language about the topic: '{topic}'."
                    encoded_prompt = requests.utils.quote(prompt)
                    response = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?json=false")
                    if response.status_code == 200:
                        st.session_state.story_text = response.text.strip()
                        st.success("కథ సిద్ధమైంది! ఇప్పుడు పక్కన ఉన్న సీన్స్ బటన్ నొక్కండి.")
                    else: st.error("సర్వర్ బిజీగా ఉంది, మళ్లీ ట్రై చేయండి.")
                except Exception as e: st.error(f"లోపం: {e}")

with col_btn2:
    if st.button("2. కథ నుండి సీన్లను విడగొట్టు 🎬", key="gen_only_scenes"):
        if st.session_state.story_text.strip() == "":
            st.warning("ముందుగా ఎడమవైపు బటన్ నొక్కి కథను జనరేట్ చేయండి!")
        else:
            with st.spinner("కథ నుండి విజువల్ సీన్లను వేరు చేస్తోంది..."):
                try:
                    prompt = (
                        f"Read this Telugu story: '{st.session_state.story_text}'. "
                        f"Break it down into 4 to 5 separate visual scenes in Telugu. "
                        f"Each scene must be strictly on a new line. Do not add numbers or symbols at the start, just action text."
                    )
                    encoded_prompt = requests.utils.quote(prompt)
                    response = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?json=false")
                    if response.status_code == 200:
                        st.session_state.scenes_text = response.text.strip()
                        st.success("సీన్లు విజయవంతంగా విడిపోయాయి!")
                    else: st.error("సర్వర్ బిజీగా ఉంది, మళ్లీ ట్రై చేయండి.")
                except Exception as e: st.error(f"లోపం: {e}")

colA, colB = st.columns(2)
with colA:
    edited_story = st.text_area("📖 మీ మెయిన్ కథ (వాయిస్ కోసం):", value=st.session_state.story_text, height=250)
with colB:
    edited_scenes = st.text_area("🎬 ఇమేజ్ సీన్లు (ఒక్కో లైన్‌లో ఒకటి):", value=st.session_state.scenes_text, height=250)

st.session_state.story_text = edited_story
st.session_state.scenes_text = edited_scenes
st.markdown('</div>', unsafe_allow_html=True) # Step 1 Box Close


# ==========================================
# STEP 2: కథను చదవడం (Voice Over Generation)
# ==========================================
st.markdown('<div class="step-box">', unsafe_allow_html=True)
st.header("Step 2: 🎙️ కథను వాయిస్ లాగా మార్చండి")

voice_option = st.selectbox("వాయిస్ ఎంచుకోండి:", ("మగవారి వాయిస్ (Mohan)", "ఆడవారి వాయిస్ (Shruti)"))
voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"

col1, col2, col3 = st.columns(3)
with col1:
    speed_slider = st.slider("వేగం (Speed):", -50, 50, -4, 2, format="%d%%")
    voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
with col2:
    volume_slider = st.slider("వాల్యూమ్ (Volume):", -50, 50, 8, 2, format="%d%%")
    voice_volume = f"{'' if volume_slider < 0 else '+'}{volume_slider}%"
with col3:
    pitch_slider = st.slider("పిచ్ (Pitch):", -20, 20, 0, 1, format="%dHz")
    voice_pitch = f"{'' if pitch_slider < 0 else '+'}{pitch_slider}Hz"

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

if st.button("కథను ఆడియోగా మార్చు 🚀"):
    if st.session_state.story_text.strip() == "":
        st.warning("ముందుగా స్టెప్ 1 లో కథను జనరేట్ చేయండి!")
    else:
        with st.spinner("కథ చదవడం రికార్డ్ అవుతోంది..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_audio_bytes = loop.run_until_complete(
                    generate_audio(st.session_state.story_text, voice, voice_speed, voice_volume, voice_pitch)
                )
                st.audio(final_audio_bytes, format="audio/mp3")
                st.download_button(label="📥 కథ ఆడియో డౌน์โหลด", data=final_audio_bytes, file_name="story_voice.mp3", mime="audio/mp3")
            except Exception as e: st.error(f"లోపం: {e}")
st.markdown('</div>', unsafe_allow_html=True) # Step 2 Box Close


# ==========================================
# STEP 3: ఇమేజ్ జనరేషన్ (Images for Scenes)
# ==========================================
st.markdown('<div class="step-box">', unsafe_allow_html=True)
st.header("Step 3: 🎨 సీన్స్ నుండి ఇమేజెస్ జనరేట్ చేయండి")

col_ratio, col_style = st.columns(2)
with col_ratio:
    ratio_option = st.radio("వీడియో ఫార్మాట్:", ("16:9 (యూట్యూబ్) [డిఫాల్ట్]", "9:16 (షార్ట్స్/రీల్స్)"))
with col_style:
    style_option = st.radio("ఫోటో రకం:", ("2D కామిక్ స్ట్రిప్ (Cartoon)", "సినిమాటిక్ రియలిస్టిక్ (Real Photo)"))

img_width, img_height = (1024, 576) if "16:9" in ratio_option else (576, 1024)

framing_rules = (
    ", established wide shot framing, no close-ups, no face zoom, show entire bodies and full characters from head to toe, "
    "completely visible clear background environment, crisp sharp facial features, highly detailed distinct eyes and expressions, "
    "all background properties and elements fully visible in frame"
)

if "2D కామిక్" in style_option:
    style_prompt_addition = f"in a beautiful traditional Indian 2D comic book graphic novel illustration style, clean precise outlines, solid rich flat colors, pure comic art style, no 3d rendering, no depth blur{framing_rules}"
else:
    style_prompt_addition = f"8k resolution, photorealistic cinematic film style, dynamic lighting, masterpiece quality, highly detailed textures, real-life composition{framing_rules}"

if st.button("సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨"):
    if st.session_state.scenes_text.strip() == "":
        st.warning("ముందుగా స్టెప్ 1 లో 'సీన్లను విడగొట్టు' బటన్ నొక్కండి!")
    else:
        telugu_scenes = [line.strip() for line in st.session_state.scenes_text.split('\n') if line.strip()]
        st.success(f"మొత్తం {len(telugu_scenes)} సీన్లకు ఇమేజెస్ తయారవుతున్నాయి...")
        
        for i, t_scene in enumerate(telugu_scenes):
            st.write(f"**సీన్ {i+1}:** {t_scene}")
            with st.spinner(f"సీన్ {i+1} ఇమేజ్ తయారవుతోంది..."):
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
                            image_bytes = img_response.content
                            st.image(image_bytes, caption=f"Scene {i+1} Output", use_container_width=True)
                            
                            img_buffer = io.BytesIO(image_bytes)
                            st.download_button(
                                label=f"📥 సీన్ {i+1} ఇమేజ్ డౌน์โหลด", data=img_buffer,
                                file_name=f"scene_{i+1}.jpg", mime="image/jpeg", key=f"dl_img_{i}"
                            )
                            st.markdown("---")
                        else: st.error(f"సీన్ {i+1} లోడ్ అవ్వలేదు.")
                    else: st.error("లైన్ ట్రాన్స్‌లేషన్‌లో లోపం వచ్చింది.")
                except Exception as e: st.error(f"లోపం: {e}")
st.markdown('</div>', unsafe_allow_html=True) # Step 3 Box Close
