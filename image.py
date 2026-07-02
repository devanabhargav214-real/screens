import asyncio
import re
import streamlit as st
import edge_tts
import requests
import io

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Auto Studio", page_icon="🎬", layout="wide")
st.title("🎬 తెలుగు AI ఆటోమేటిక్ వీడియో స్టూడియో")
st.write("స్టెప్-బై-స్టెప్ ప్రాసెస్: ముందు కథ వస్తుంది, ఆపై సీన్లుగా విడిపోతుంది, తర్వాత వాయిస్ మరియు ఇమేజెస్ ఒకే ఫ్లోలో జనరేట్ అవుతాయి!")

# సెషన్ స్టేట్ (డేటాను ఆటోమేటిక్‌గా ట్రాన్స్‌ఫర్ చేయడానికి)
if "story_text" not in st.session_state:
    st.session_state.story_text = ""
if "scenes_text" not in st.session_state:
    st.session_state.scenes_text = ""

st.markdown("---")

# ==========================================
# STEP 1: స్టోరీ మరియు సీన్స్ ఆటోమేటిక్ జనరేషన్
# ==========================================
st.header("Step 1: 📝 కథ మరియు సీన్స్ జనరేట్ చేయండి")
topic = st.text_input("మీ కథ టాపిక్ ఇక్కడ ఇవ్వండి:", placeholder="ఉదాహరణకు: ఒక అడవిలో సింహం మరియు ఎలుక స్నేహం...")

if st.button("కథ & సీన్లను జనరేట్ చేయి ✨"):
    if topic.strip() == "":
        st.warning("దయచేసి ఏదైనా ఒక టాపిక్ ఇవ్వండి!")
    else:
        with st.spinner("AI మీ కథను రాసి, సీన్లను విడగొడుతోంది... దయచేసి ఆగండి..."):
            try:
                # కథ మరియు సీన్లను కచ్చితంగా విడగొట్టడానికి లాజిక్
                prompt = (
                    f"Write a highly engaging short story in Telugu about: '{topic}'. "
                    f"After completing the story, strictly write the exact word '===SCENES===' on a new line. "
                    f"Below that word, break down the story into 4 to 5 visual scenes in Telugu. "
                    f"Each scene must be on a new line."
                )
                encoded_prompt = requests.utils.quote(prompt)
                response = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?json=false")
                
                if response.status_code == 200:
                    full_output = response.text
                    
                    # ===SCENES=== అనే పదం దగ్గర కథను, సీన్లను రెండు ముక్కలుగా చేయడం
                    if "===SCENES===" in full_output:
                        parts = full_output.split("===SCENES===")
                        st.session_state.story_text = parts[0].strip()
                        st.session_state.scenes_text = parts[1].strip()
                    else:
                        st.session_state.story_text = full_output.strip()
                        st.session_state.scenes_text = "సీన్స్ సరిగ్గా విడిపోలేదు. దయచేసి మళ్ళీ జనరేట్ చేయండి."
                        
                    st.success("కథ మరియు సీన్లు విజయవంతంగా విడిపోయాయి! కింద చెక్ చేసుకోండి.")
                else:
                    st.error("సర్వర్ బిజీగా ఉంది, మళ్లీ ట్రై చేయండి.")
            except Exception as e:
                st.error(f"లోపం: {e}")

# జనరేట్ అయిన వాటిని బాక్సుల్లో చూపించడం (యూజర్ కావాలంటే ఇక్కడ మార్పులు చేసుకోవచ్చు)
colA, colB = st.columns(2)
with colA:
    edited_story = st.text_area("📖 మీ మెయిన్ కథ (వాయిస్ కోసం):", value=st.session_state.story_text, height=250)
with colB:
    edited_scenes = st.text_area("🎬 ఇమేజ్ సీన్లు (ఒక్కో లైన్‌లో ఒకటి):", value=st.session_state.scenes_text, height=250)

# బాక్సుల్లో ఏమైనా మారిస్తే అది సేవ్ అవ్వడానికి
st.session_state.story_text = edited_story
st.session_state.scenes_text = edited_scenes

st.markdown("---")

# ==========================================
# STEP 2: కథను చదవడం (Voice Over Generation)
# ==========================================
st.header("Step 2: 🎙️ కథను వాయిస్ లాగా మార్చండి")
st.write("స్టెప్ 1 లో వచ్చిన కథను ఆటోమేటిక్‌గా నాచురల్ వాయిస్‌తో చదివించండి.")

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
                st.download_button(label="📥 కథ ఆడియో డౌన్‌లోడ్", data=final_audio_bytes, file_name="story_voice.mp3", mime="audio/mp3")
            except Exception as e:
                st.error(f"లోపం: {e}")

st.markdown("---")

# ==========================================
# STEP 3: ఇమేజ్ జనరేషన్ (Images for Scenes)
# ==========================================
st.header("Step 3: 🎨 సీన్స్ నుండి ఇమేజెస్ జనరేట్ చేయండి")
st.write("స్టెప్ 1 లో విడిపోయిన సీన్లను పర్ఫెక్ట్ 2D/HD ఫొటోలుగా మార్చుకోండి.")

col_ratio, col_style = st.columns(2)
with col_ratio:
    ratio_option = st.radio("వీడియో ఫార్మాట్:", ("16:9 (యూట్యూబ్) [డిఫాల్ట్]", "9:16 (షార్ట్స్/రీల్స్)"))
with col_style:
    style_option = st.radio("ఫోటో రకం:", ("తెలుగు 2D కామిక్ స్ట్రిప్ (Cartoon)", "సినిమాటిక్ రియలిస్టిక్ (Real Photo)"))

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
        st.warning("ముందుగా స్టెప్ 1 లో సీన్స్ జనరేట్ చేయండి!")
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
