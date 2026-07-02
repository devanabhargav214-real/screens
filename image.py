import asyncio
import re
import streamlit as st
import edge_tts
import requests
import io

# వెబ్‌సైట్ టైటిల్ మరియు డిజైన్
st.set_page_config(page_title="Telugu AI Voice & Story Board", page_icon="🎙️")
st.title("🎙️ తెలుగు AI వాయిస్ & సీన్ ఇమేజ్ జనరేటర్")
st.write("మీ స్క్రిప్ట్‌ను ఇక్కడ పేస్ట్ చేసి వాయిస్ మరియు సీన్ ఇమేజ్‌లను జనరేట్ చేసుకోండి.")

# ట్యాబ్స్ క్రియేట్ చేస్తున్నాం (వాయిస్ కి ఒకటి, ఇమేజ్ కి ఒకటి)
tab1, tab2 = st.tabs(["🎙️ AI వాయిస్ జనరేటర్", "🎨 AI ఇమేజ్ జనరేటర్ (Scenes)"])

# వాయిస్ సెట్టింగ్స్ కోసం పాత కోడ్ (Tab 1 లో ఉంటుంది)
with tab1:
    voice_option = st.selectbox(
        "వాయిస్ ఎంచుకోండి (Voice):",
        ("మగవారి వాయిస్ (Mohan Neural)", "ఆడవారి వాయిస్ (Shruti Neural)"),
    )
    voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"

    st.write("### 🎛️ వాయిస్ సెట్టింగ్స్:")
    col1, col2 = st.columns(2)
    with col1:
        speed_slider = st.slider("వాయిస్ వేగం (Speed):", -50, 50, -5, 5, format="%d%%")
        voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
    with col2:
        volume_slider = st.slider("వాల్యూమ్ స్థాయి (Volume):", -50, 50, 0, 5, format="%d%%")
        voice_volume = f"{'' if volume_slider < 0 else '+'}{volume_slider}%"

    script_text = st.text_area("మీ వాయిస్ స్క్రిప్ట్ ఇక్కడ పేస్ట్ చేయండి:", height=200, key="voice_script")

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

    async def generate_audio(full_text, voice_model, speed, volume):
        chunks = split_text(full_text)
        audio_data = b""
        for chunk in chunks:
            communicate = edge_tts.Communicate(chunk, voice_model, rate=speed, volume=volume)
            async for chunk_data in communicate.stream():
                if chunk_data["type"] == "audio":
                    audio_data += chunk_data["data"]
        return audio_data

    if st.button("AI వాయిస్ జనరేట్ చేయి 🚀"):
        if script_text.strip() == "":
            st.warning("దయచేసి స్క్రిప్ట్ టైప్ చేయండి!")
        else:
            with st.spinner("AI వాయిస్ జనరేట్ అవుతోంది..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    final_audio_bytes = loop.run_until_complete(generate_audio(script_text, voice, voice_speed, voice_volume))
                    st.audio(final_audio_bytes, format="audio/mp3")
                    st.download_button(label="📥 ఆడియో డౌన్‌లోడ్", data=final_audio_bytes, file_name="voice.mp3", mime="audio/mp3")
                except Exception as e:
                    st.error(f"లోపం: {e}")

# --- కొత్త ఫీచర్: ఇమేజ్ జనరేటర్ (Tab 2 లో ఉంటుంది) ---
with tab2:
    st.write("### 🎬 స్టోరీ సీన్ బై సీన్ ఇమేజ్ జనరేటర్")
    st.write("ఒక్కో లైన్‌లో ఒక్కో సీన్ ప్రాంప్ట్ (ఇంగ్లీష్‌లో) ఇవ్వండి. ఎన్ని లైన్లు ఇస్తే అన్ని ఇమేజ్‌లు వస్తాయి.")
    
    # యూజర్ ఇమేజ్ ప్రాంప్ట్స్ ఇచ్చే బాక్స్ (ప్రతి లైన్ ఒక ఇమేజ్ లా మారుతుంది)
    image_script = st.text_area(
        "ఇమేజ్ సీన్స్ ఇక్కడ ఇవ్వండి (ఉదాహరణకు):\nAn old wise king sitting on a throne\nA beautiful green forest with a river\nA small wooden house in village",
        height=200,
        key="image_script"
    )
    
    if st.button("సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨"):
        if image_script.strip() == "":
            st.warning("దయచేసి కనీసం ఒక సీన్ అయినా టైప్ చేయండి!")
        else:
            # లైన్ బై లైన్ విడగొడుతుంది (ఎన్ని లైన్లు ఉంటే అన్ని ఇమేజెస్)
            scenes = [line.strip() for line in image_script.split('\n') if line.strip()]
            
            st.success(f"మొత్తం {len(scenes)} సీన్లు కనుగొనబడ్డాయి. ఇమేజ్‌లు జనరేట్ అవుతున్నాయి...")
            
            # ఒక్కో సీన్ ని ప్రాసెస్ చేయడం
            for i, scene in enumerate(scenes):
                st.write(f"**సీన్ {i+1}:** {scene}")
                with st.spinner(f"సీన్ {i+1} ఇమేజ్ తయారవుతోంది..."):
                    try:
                        # Pollinations AI ద్వారా ఉచితంగా ఇమేజ్ తెచ్చుకోవడం
                        encoded_scene = requests.utils.quote(scene)
                        image_url = f"https://image.pollinations.ai/p/{encoded_scene}?width=1024&height=576&nologo=true"
                        
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            image_bytes = response.content
                            
                            # స్క్రీన్ మీద ఇమేజ్ చూపించడం
                            st.image(image_bytes, caption=f"Scene {i+1} Output", use_container_width=True)
                            
                            # ప్రతి ఇమేజ్ కి విడివిడిగా డౌన్‌లోడ్ బటన్
                            st.download_button(
                                label=f"📥 సీన్ {i+1} ఇమేజ్ డౌన్‌లోడ్ చేసుకోండి",
                                data=image_bytes,
                                file_name=f"scene_{i+1}.jpg",
                                mime="image/jpeg",
                                key=f"download_{i}"
                            )
                            st.markdown("---") # లైన్ బ్రేక్
                        else:
                            st.error(f"సీన్ {i+1} జనరేట్ చేయడం కుదరలేదు.")
                    except Exception as e:
                        st.error(f"తప్పు జరిగింది: {e}")
      
