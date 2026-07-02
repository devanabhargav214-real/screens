import asyncio
import re
import streamlit as st
import edge_tts
import requests

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Audio Studio", page_icon="🎙️", layout="wide")

# ==========================================
# SIMPLE HIGH-CONTRAST WHITE & BLUE STYLING
# ==========================================
st.markdown("""
    <style>
    /* మెయిన్ బ్యాbackground ఎల్లప్పుడూ ప్యూర్ వైట్ */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* క్లాసిక్ బ్లూ మెయిన్ టైటిల్ */
    .main-heading {
        font-size: 26px;
        color: #ffffff !important;
        font-weight: bold;
        text-align: center;
        background-color: #1e3a8a;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    
    /* ట్యాబ్స్ డిజైన్ */
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

    /* ప్రైమరీ బ్లూ బటన్స్ */
    div.stButton > button {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 10px 20px !important;
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

    /* డార్క్ మోడ్‌లో కూడా అక్షరాలు నల్లగా స్పష్టంగా కనిపించడానికి ఫోర్స్ రూల్ */
    p, label, span, div, p li, .stSelectbox label {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 15px !important;
    }
    
    /* టెక్స్ట్ ఏరియా లోపలి ఫాంట్ స్టైలింగ్ */
    textarea {
        color: #000000 !important;
        font-weight: normal !important;
    }
    </style>
    """, unsafe_allow_html=True)

# టాస్క్ పూర్తి కాగానే ప్లే అవ్వడానికి సక్సెస్ బెల్ సౌండ్
def play_success_sound():
    sound_html = """
    <audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2019/2019-84.wav" type="audio/wav"></audio>
    """
    st.components.v1.html(sound_html, height=0, width=0)

# స్లైడర్ మార్చినప్పుడు వైబ్రేషన్ రావడానికి జావాస్క్రిప్ట్
def trigger_vibration():
    vibrate_html = """
    <script>if (window.navigator && window.navigator.vibrate) { window.navigator.vibrate(25); }</script>
    """
    st.components.v1.html(vibrate_html, height=0, width=0)

# ప్రధాన టైటిల్
st.markdown('<div class="main-heading">🎬 తెలుగు AI ఆటోమేటిక్ స్టోరీ & వాయిస్ స్టూడియో</div>', unsafe_allow_html=True)

# సెషన్ స్టేట్ డేటా స్టోరేజ్
if "story_text" not in st.session_state:
    st.session_state.story_text = ""

# ఇరవై ఇండివిడ్యువల్ ట్యాబ్స్ (కథ మరియు వాయిస్ ఓవర్)
tab1, tab2 = st.tabs(["📖 1. Story Generator", "🎙️ 2. Voice Over"])

# ==========================================
# TAB 1: STORY GENERATOR (HIGH SPEED)
# ==========================================
with tab1:
    st.write("### 📝 మీ టాపిక్ నుండి కథను జనరేట్ చేయండి")
    topic = st.text_input("మీ కథ టాపిక్ ఇక్కడ టైప్ చేయండి:", placeholder="ఉదాహరణకు: పేద రైతు మరియు బంగారు హంస కథ...")

    if st.button("కథ జనరేట్ చేయి 📖", key="gen_story_tab"):
        if topic.strip() == "":
            st.warning("దయచేసి ఏదైనా ఒక టాపిక్ ఇవ్వండి!")
        else:
            with st.spinner("AI కథను వేగంగా తయారు చేస్తోంది..."):
                try:
                    # సర్వర్ బిజీ ఎర్రర్ రాకుండా ఉండటానికి 'searchgpt' మోడల్ ని లింక్ చేసాం
                    prompt = f"Write a beautiful short story in clear Telugu language about the topic: '{topic}'."
                    encoded_prompt = requests.utils.quote(prompt)
                    url = f"https://text.pollinations.ai/{encoded_prompt}?model=searchgpt&json=false"
                    response = requests.get(url)
                    
                    if response.status_code == 200 and response.text.strip() != "":
                        st.session_state.story_text = response.text.strip()
                        st.success("కథ విజయవంతంగా సిద్ధమైంది! దీన్ని పక్కన ఉన్న వాయిస్ ఓవర్ ట్యాబ్‌లో వాడుకోవచ్చు.")
                        play_success_sound()
                    else:
                        st.error("సర్వర్ బిజీగా ఉంది. దయచేసి మరోసారి చిన్న టాపిక్ తో ట్రై చేయండి.")
                except Exception as e: 
                    st.error(f"కనెక్షన్ లోపం: {e}")

    # జనరేట్ అయిన కథను ఇక్కడ చూపిస్తాం (యూజర్ కావాలంటే ఎడిట్ చేసుకోవచ్చు)
    edited_story = st.text_area("📖 ప్రస్తుత కథ (వాయిస్ కోసం):", value=st.session_state.story_text, height=300, key="story_area")
    st.session_state.story_text = edited_story

# ==========================================
# TAB 2: VOICE OVER
# ==========================================
with tab2:
    st.write("### 🎙️ కథను నాచురల్ ఆడియో లాగా మార్చండి")
    
    voice_option = st.selectbox("వాయిస్ మోడల్ ఎంచుకోండి (Voice):", ("మగవారి వాయిస్ (Mohan)", "ఆడవారి వాయిస్ (Shruti)"), key="voice_select")
    voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"

    st.write("#### 🎛️ వాయిస్ సెట్టింగ్స్ (మార్చుతున్నప్పుడు మొబైల్ వైబ్రేట్ అవుతుంది):")
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

    # పెద్ద టెక్స్ట్‌ని విడగొట్టే ఫంక్షన్ (ఎర్రర్స్ రాకుండా ఉండటానికి)
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
            st.warning("మొదటి ట్యాబ్‌లో కథ లేదు! దయచేసి కథను జనరేట్ చేయండి లేదా ఇక్కడే నేరుగా టైప్ చేయండి.")
        else:
            with st.spinner("స్పష్టమైన ఆడియో రికార్డ్ అవుతోంది..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    final_audio_bytes = loop.run_until_complete(
                        generate_audio(st.session_state.story_text, voice, voice_speed, voice_volume, voice_pitch)
                    )
                    st.audio(final_audio_bytes, format="audio/mp3")
                    st.download_button(label="📥 కథ ఆడియో ఫైల్ డౌน์โหลด చేయండి", data=final_audio_bytes, file_name="telugu_story_voice.mp3", mime="audio/mp3")
                    play_success_sound()
                except Exception as e: 
                    st.error(f"లోపం: {e}")
