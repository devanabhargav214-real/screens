import asyncio
import re
import streamlit as st
import edge_tts
import requests
import io

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Studio Pro", page_icon="🎬", layout="wide")

# ==========================================
# CUSTOM CSS FOR STYLING & TEXT CONTRAST
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    .main-heading {
        font-size: 30px; color: #000000 !important; font-weight: bold; text-align: center;
        background-color: #ffd166; padding: 15px; border: 3px solid #000000;
        border-radius: 12px; margin-bottom: 25px; box-shadow: 4px 4px 0px #000000;
    }
    .task-header {
        background-color: #ffd166; color: #000000 !important; font-size: 20px; font-weight: bold;
        padding: 10px 15px; border: 3px solid #000000; border-radius: 8px;
        margin-top: 25px; margin-bottom: 15px; box-shadow: 3px 3px 0px #000000;
    }
    div.stButton > button {
        background-color: #ffd166 !important; color: #000000 !important; font-size: 16px !important;
        font-weight: bold !important; border-radius: 10px !important; border: 3px solid #000000 !important;
        padding: 8px 20px !important; box-shadow: 3px 3px 0px #000000 !important; width: 100%; margin-bottom: 10px;
    }
    div.stButton > button:hover { background-color: #ffc333 !important; }
    div.stDownloadButton > button {
        background-color: #06d6a0 !important; color: #000000 !important; font-size: 16px !important;
        font-weight: bold !important; border-radius: 10px !important; border: 3px solid #000000 !important;
        box-shadow: 3px 3px 0px #000000 !important; width: 100%;
    }
    p, label, span, div, .stRadio, p li { color: #000000 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# టాస్క్ పూర్తి కాగానే ప్లే అవ్వడానికి సక్సెస్ సౌండ్ ఫంక్షన్
def play_success_sound():
    sound_html = """
    <audio autoplay>
      <source src="https://assets.mixkit.co/active_storage/sfx/2019/2019-84.wav" type="audio/wav">
    </audio>
    """
    st.components.v1.html(sound_html, height=0, width=0)

# స్లైడర్ మార్చినప్పుడు వైబ్రేషన్ రావడానికి జావాస్క్రిప్ట్ ఫంక్షన్
def trigger_vibration():
    vibrate_html = """
    <script>
        if (window.navigator && window.navigator.vibrate) {
            window.navigator.vibrate(30);
        }
    </script>
    """
    st.components.v1.html(vibrate_html, height=0, width=0)

st.markdown('<div class="main-heading">🎬 తెలుగు AI ఆటోమేటిక్ వీడియో స్టూడియో</div>', unsafe_allow_html=True)

# సెషన్ స్టేట్స్
if "story_text" not in st.session_state:
    st.session_state.story_text = ""
if "scenes_text" not in st.session_state:
    st.session_state.scenes_text = ""

# ==========================================
# STEP 1: స్టోరీ మరియు సీన్స్ జనరేషన్
# ==========================================
st.markdown('<div class="task-header">Step 1: 📝 కథ మరియు సీన్స్ సిద్ధం చేయండి</div>', unsafe_allow_html=True)
topic = st.text_input("మీ కథ టాపిక్ ఇక్కడ టైప్ చేయండి:", placeholder="ఉదాహరణకు: అడవిలో సింహం...")

if st.button("1. కథ జనరేట్ చేయి 📖", key="gen_only_story"):
    if topic.strip() == "":
        st.warning("దయచేసి ఏదైనా ఒక టాపిక్ ఇవ్వండి!")
    else:
        with st.spinner("AI కథను రాస్తోంది..."):
            try:
                prompt = f"Write a highly engaging short story in pure Telugu language about the topic: '{topic}'."
                encoded_prompt = requests.utils.quote(prompt)
                response = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?json=false")
                if response.status_code == 200:
                    st.session_state.story_text = response.text.strip()
                    st.success("కథ సిద్ధమైంది! కింద సీన్స్ బటన్ ఓపెన్ అయింది చూడండి.")
                    play_success_sound()
                else: st.error("సర్వర్ బిజీగా ఉంది, మళ్లీ ట్రై చేయండి.")
            except Exception as e: st.error(f"లోపం: {e}")

# కథ జనరేట్ అయిన తర్వాతే ఈ సీన్స్ బటన్ కనిపిస్తుంది
if st.session_state.story_text.strip() != "":
    if st.button("2. కథ నుండి సీన్లను విడగొట్టు 🎬", key="gen_only_scenes"):
        with st.spinner("సీన్లను వేరు చేస్తోంది..."):
            try:
                prompt = (
                    f"Read this Telugu story: '{st.session_state.story_text}'. "
                    f"Break it down into 4 to 5 separate visual scenes in Telugu for making a video. "
                    f"Each scene must be strictly on a new line. Do not add numbers or symbols at the start."
                )
                encoded_prompt = requests.utils.quote(prompt)
                response = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?json=false")
                if response.status_code == 200:
                    st.session_state.scenes_text = response.text.strip()
                    st.success("సీన్లు విజయవంతంగా విడిపోయాయి!")
                    play_success_sound()
                else: st.error("సర్వర్ బిజీగా ఉంది, మళ్లీ ట్రై చేయండి.")
            except Exception as e: st.error(f"లోపం: {e}")

colA, colB = st.columns(2)
with colA:
    edited_story = st.text_area("📖 పూర్తి కథ (వాయిస్ ఓవర్ కోసం):", value=st.session_state.story_text, height=220, key="story_area")
with colB:
    edited_scenes = st.text_area("🎬 ఇమేజ్ సీన్లు (లైన్ బై లైన్):", value=st.session_state.scenes_text, height=220, key="scenes_area")

st.session_state.story_text = edited_story
st.session_state.scenes_text = edited_scenes


# ==========================================
# STEP 2: వాయిస్ ఓవర్ జనరేషన్ (స్లైడర్ వైబ్రేషన్ తో)
# ==========================================
st.markdown('<div class="task-header">Step 2: 🎙️ కథను వాయిస్ లాగా మార్చండి</div>', unsafe_allow_html=True)

voice_option = st.selectbox("వాయిస్ మోడల్ ఎంచుకోండి (Voice):", ("మగవారి వాయిస్ (Mohan)", "ఆడవారి వాయిస్ (Shruti)"))
voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"

col1, col2, col3 = st.columns(3)
with col1:
    speed_slider = st.slider("వాయిస్ వేగం (Speed):", -50, 50, -4, 2, format="%d%%")
    voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
    if speed_slider: trigger_vibration()  # వైబ్రేషన్ ట్రిగ్గర్
with col2:
    volume_slider = st.slider("వాల్యూమ్ స్థాయి (Volume):", -50, 50, 8, 2, format="%d%%")
    voice_volume = f"{'' if volume_slider < 0 else '+'}{volume_slider}%"
    if volume_slider: trigger_vibration() # వైబ్రేషన్ ట్రిగ్గర్
with col3:
    pitch_slider = st.slider("వాయిస్ పిచ్ (Pitch):", -20, 20, 0, 1, format="%dHz")
    voice_pitch = f"{'' if pitch_slider < 0 else '+'}{pitch_slider}Hz"
    if pitch_slider: trigger_vibration()  # వైబ్రేషన్ ట్రిగ్గర్

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

# కస్టమర్ టైప్ చేసే టెక్స్ట్ బాక్స్
user_style_input = st.text_input("ఇమేజ్ స్టైల్ టైప్ చేయండి (ఉదా: cartoon, cinematic, japanese cartoon):", placeholder="ఏమీ ఇవ్వకపోతే డిఫాల్ట్ 2D కార్టూన్ వస్తుంది...")

col_ratio = st.columns(1)[0]
ratio_option = st.radio("వీడియో సైజ్ (Aspect Ratio):", ("16:9 (యూట్యూబ్)", "9:16 (షార్ట్స్)"))
img_width, img_height = (1024, 576) if "16:9" in ratio_option else (576, 1024)

# టెక్స్ట్ ఇన్పుట్ ఆధారంగా స్టైల్ డిసిషన్ మేకింగ్
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
    # default emi type cheyakapothe వచ్చే డిఫాల్ట్ స్టైల్
    style_prompt_addition = f"in beautiful traditional Indian 2D cartoon book illustration style, South Indian character design, clean precise outlines, solid rich colors, no depth blur{framing_rules}"

if st.button("సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨", key="image_gen_trigger"):
    if st.session_state.scenes_text.strip() == "":
        st.warning("దయచేసి ముందుగా స్టెప్ 1 లో 'సీన్లను విడగొట్టు' బటన్ నొక్కండి!")
    else:
        telugu_scenes = [line.strip() for line in st.session_state.scenes_text.split('\n') if line.strip()]
        st.success(f"మొత్తం {len(telugu_scenes)} సీన్లకు ఇమేజెస్ సిద్ధమవుతున్నాయి...")
        
        for i, t_scene in enumerate(telugu_scenes):
            st.write(f"**シーన్ {i+1}:** {t_scene}")
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
                            image_bytes = img_response.content
                            st.image(image_bytes, caption=f"Scene {i+1} Output", use_container_width=True)
                            
                            img_buffer = io.BytesIO(image_bytes)
                            st.download_button(
                                label=f"📥 సీన్ {i+1} ఇమేజ్ డౌน์โหลด చేయండి", data=img_buffer,
                                file_name=f"scene_{i+1}.jpg", mime="image/jpeg", key=f"dl_img_{i}"
                            )
                            st.markdown("---")
                        else: st.error(f"సీన్ {i+1} ఇమేజ్ లోడ్ అవ్వలేదు.")
                    else: st.error("లైన్ ట్రాన్స్‌లేషన్‌లో లోపం వచ్చింది.")
                except Exception as e: st.error(f"లోపం: {e}")
        play_success_sound()
