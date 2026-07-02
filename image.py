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
    /* మెయిన్ బ్యాక్‌గ్రౌండ్ ఎల్లప్పుడూ ప్యూర్ వైట్ */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* క్లాసిక్ బ్లూ మెయిన్ హెడింగ్ */
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
    
    /* టాస్క్ బ్లూ హెడర్స్ */
    .task-header {
        background-color: #eff6ff;
        color: #1e3a8a !important;
        font-size: 18px;
        font-weight: bold;
        padding: 10px 15px;
        border-left: 5px solid #1e3a8a;
        border-radius: 4px;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    /* బ్లూ బటన్స్ డిజైన్ */
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
    
    /* గ్రీన్ డౌน์โหลด బటన్ */
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

    /* టెక్స్ట్ కలర్స్ స్పష్టత */
    p, label, span, div, .stRadio, p li {
        color: #1f2937 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# టాస్క్ పూర్తి కాగానే ప్లే అవ్వడానికి సక్సెస్ సౌండ్
def play_success_sound():
    sound_html = """
    <audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2019/2019-84.wav" type="audio/wav"></audio>
    """
    st.components.v1.html(sound_html, height=0, width=0)

# స్లైడర్ మార్చినప్పుడు వైబ్రేషన్
def trigger_vibration():
    vibrate_html = """
    <script>if (window.navigator && window.navigator.vibrate) { window.navigator.vibrate(30); }</script>
    """
    st.components.v1.html(vibrate_html, height=0, width=0)

st.markdown('<div class="main-heading">🎬 తెలుగు AI ఆటోమేటిక్ వీడియో స్టూడియో</div>', unsafe_allow_html=True)

# సెషన్ స్టేట్స్
if "story_text" not in st.session_state:
    st.session_state.story_text = ""
if "scenes_text" not in st.session_state:
    st.session_state.scenes_text = ""

# ==========================================
# STEP 1: స్టోరీ మరియు సీన్స్ జనరేషన్ (HIGH ACCURACY ROUTE)
# ==========================================
st.markdown('<div class="task-header">Step 1: 📝 కథ మరియు సీన్స్ సిద్ధం చేయండి</div>', unsafe_allow_html=True)
topic = st.text_input("మీ కథ టాపిక్ ఇక్కడ టైప్ చేయండి:", placeholder="ఉదాహరణకు: కాకి మరియు కుండ కథ...")

if st.button("1. కథ జనరేట్ చేయి 📖", key="gen_only_story"):
    if topic.strip() == "":
        st.warning("దయచేసి ఏదైనా ఒక టాపిక్ ఇవ్వండి!")
    else:
        with st.spinner("AI కథను వేగంగా తయారు చేస్తోంది..."):
            try:
                # సర్వర్ బిజీ సమస్యను నివారించడానికి టెక్స్ట్ మోడల్ రూట్‌ని మార్చాము
                prompt = f"Write a beautiful short story in clear Telugu language about the topic: '{topic}'."
                encoded_prompt = requests.utils.quote(prompt)
                
                # వేగవంతమైన బ్యాకప్ సర్వర్ లైన్
                url = f"https://text.pollinations.ai/{encoded_prompt}?model=searchgpt&json=false"
                response = requests.get(url)
                
                if response.status_code == 200 and response.text.strip() != "":
                    st.session_state.story_text = response.text.strip()
                    st.success("కథ సిద్ధమైంది! ఇప్పుడు కింద ఓపెన్ అయిన సీన్స్ బటన్ నొక్కండి.")
                    play_success_sound()
                else:
                    # ఒకవేళ ఫెయిల్ అయితే సెకండ్ బ్యాకప్ లైన్
                    fallback_url = f"https://text.pollinations.ai/{encoded_prompt}?json=false"
                    fb_res = requests.get(fallback_url)
                    if fb_res.status_code == 200:
                        st.session_state.story_text = fb_res.text.strip()
                        st.success("కథ సిద్ధమైంది!")
                        play_success_sound()
                    else:
                        st.error("సర్వర్ రెస్పాండ్ అవ్వడం లేదు. దయచేసి మరోసారి చిన్న టాపిక్ తో ట్రై చేయండి.")
            except Exception as e: 
                st.error(f"కనెక్షన్ లోపం: {e}")

# కథ ఉన్నప్పుడు మాత్రమే సీన్స్ బటన్ లాక్ ఓపెన్ అవుతుంది
if st.session_state.story_text.strip() != "":
    if st.button("2. కథ నుండి సీన్లను విడగొట్టు 🎬", key="gen_only_scenes"):
        with st.spinner("కథ నుండి విజువల్ సీన్లను వేరు చేస్తోంది..."):
            try:
                prompt = (
                    f"Read this Telugu story: '{st.session_state.story_text}'. "
                    f"Extract exactly 4 simple separate visual scenes from this story in Telugu. "
                    f"Write each scene on a new line clearly without using numbers or bullets."
                )
                encoded_prompt = requests.utils.quote(prompt)
                url = f"https://text.pollinations.ai/{encoded_prompt}?model=searchgpt&json=false"
                response = requests.get(url)
                
                if response.status_code == 200:
                    st.session_state.scenes_text = response.text.strip()
                    st.success("సీన్లు విజయవంతంగా విడిపోయాయి!")
                    play_success_sound()
                else:
                    st.error("సీన్స్ సర్వర్ బిజీగా ఉంది, మళ్లీ ట్రై చేయండి.")
            except Exception as e: st.error(f"లోపం: {e}")

colA, colB = st.columns(2)
with colA:
    edited_story = st.text_area("📖 పూర్తి కథ (వాయిస్ ఓవర్ కోసం):", value=st.session_state.story_text, height=220, key="story_area")
with colB:
    edited_scenes = st.text_area("🎬 ఇమేజ్ సీన్లు (లైన్ బై లైన్):", value=st.session_state.scenes_text, height=220, key="scenes_area")

st.session_state.story_text = edited_story
st.session_state.scenes_text = edited_scenes


# ==========================================
# STEP 2: వాయిస్ ఓవర్ జనరేషన్
# ==========================================
st.markdown('<div class="task-header">Step 2: 🎙️ కథను వాయిస్ లాగా మార్చండి</div>', unsafe_allow_html=True)

voice_option = st.selectbox("వాయిస్ మోడల్ ఎంచుకోండి (Voice):", ("మగవారి వాయిస్ (Mohan)", "ఆడవారి వాయిస్ (Shruti)"))
voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"

col1, col2, col3 = st.columns(3)
with col1:
    speed_slider = st.slider("వాయిస్ వేగం (Speed):", -50, 50, -4, 2, format="%d%%")
    voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
    if speed_slider: trigger_vibration()
with col2:
    volume_slider = st.slider("వాల్యూమ్ స్థాయి (Volume):", -50, 50, 8, 2, format="%d%%")
    voice_volume = f"{'' if volume_slider < 0 else '+'}{volume_slider}%"
    if volume_slider: trigger_vibration()
with col3:
    pitch_slider = st.slider("వాయిస్ పిచ్ (Pitch):", -20, 20, 0, 1, format="%dHz")
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
        st.warning("ముందుగా స్టెప్ 1 లో కథను జనరేట్ చేయండి!")
    else:
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
            except Exception as e: st.error(f"లోపం: {e}")


# ==========================================
# STEP 3: ఇమేజ్ జనరేషన్ (స్మార్ట్ టెక్స్ట్ ఆధారిత స్టైల్స్)
# ==========================================
st.markdown('<div class="task-header">Step 3: 🎨 సీన్స్ నుండి ఇమేజెస్ జనరేట్ చేయండి</div>', unsafe_allow_html=True)

user_style_input = st.text_input("ఇమేజ్ స్టైల్ టైప్ చేయండి (ఉదా: cartoon, cinematic, japanese cartoon):", placeholder="ఏమీ ఇవ్వకపోతే డిఫాల్ట్ 2D సౌత్ ఇండియన్ కార్టూన్ వస్తుంది...")

ratio_option = st.radio("వీడియో సైజ్ (Aspect Ratio):", ("16:9 (యూట్యూబ్)", "9:16 (షార్ట్స్)"))
img_width, img_height = (1024, 576) if "16:9" in ratio_option else (576, 1024)

style_keyword = user_style_input.lower().strip()

framing_rules = (
    ", established wide shot framing, no close-ups, show entire bodies and full characters from head to toe, "
    "completely visible clear background environment, crisp sharp facial features, highly detailed distinct eyes"
)

if "japanese cartoon" in style_keyword:
    style_prompt_addition = f"in beautiful vibrant Japanese anime studio Ghibli cartoon style, detailed backgrounds, hand-drawn aesthetic, rich anime coloring{framing_rules}"
elif "cartoon" in style_keyword:
    style_prompt_addition = f"in an amazing 2D cartoon illustration style, bright flat colors, clear outlines, playful comic look{framing_rules}"
elif "cinematic" in style_keyword:
    style_prompt_addition = f"8k resolution, photorealistic cinematic film style, dynamic real-life lighting, dramatic composition, highly detailed textures{framing_rules}"
elif "south indian" in style_keyword:
    style_prompt_addition = f"in beautiful traditional 2D South Indian village cartoon art style, cultural costumes, rich vibrant colors, clean vector lines{framing_rules}"
else:
    style_prompt_addition = f"in beautiful traditional Indian 2D cartoon book illustration style, South Indian character design, clean precise outlines, solid rich colors, no depth blur{framing_rules}"

if st.button("సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨", key="image_gen_trigger"):
    if st.session_state.scenes_text.strip() == "":
        st.warning("దయచేసి ముందుగా స్టెప్ 1 లో 'సీన్లను విడగొట్టు' బటన్ నొక్కండి!")
    else:
        telugu_scenes = [line.strip() for line in st.session_state.scenes_text.split('\n') if line.strip()]
        st.success(f"మొత్తం {len(telugu_scenes)} సీన్లకు ఇమేజెస్ సిద్ధమవుతున్నాయి...")
        
        for i, t_scene in enumerate(telugu_scenes):
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
                        encoded_scene
