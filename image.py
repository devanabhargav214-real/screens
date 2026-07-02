import asyncio
import re
import streamlit as st
import edge_tts
import requests

# వెబ్‌సైట్ టైటిల్ మరియు డిజైన్
st.set_page_config(page_title="Telugu AI Studio", page_icon="🎬", layout="wide")
st.title("🎬 తెలుగు AI ఆల్-ఇన్-వన్ స్టోరీ స్టూడియో")
st.write("ఇక్కడ మీరు స్టోరీ స్క్రిప్ట్ జనరేట్ చేయవచ్చు, వాయిస్ మార్చవచ్చు మరియు తెలుగు స్క్రిప్ట్ బట్టి సీన్ ఇమేజ్స్ పొందవచ్చు.")

# మూడు ట్యాబ్స్ క్రియేట్ చేస్తున్నాం
tab1, tab2, tab3 = st.tabs([
    "📝 AI స్క్రిప్ట్ జనరేటర్", 
    "🎙️ AI వాయిస్ జనరేటర్", 
    "🎨 AI తెలుగు ఇమేజ్ జనరేటర్"
])

# --- ట్యాబ్ 1: AI స్క్రిప్ట్ జనరేటర్ ---
with tab1:
    st.write("### 📝 మీ ఐడియా నుండి స్టోరీ స్క్రిప్ట్ జనరేట్ చేయండి")
    story_idea = st.text_input("మీ కథ ఐడియా ఇవ్వండి:", placeholder="ఇక్కడ టైప్ చేయండి...")
    
    if st.button("కథ జనరేట్ చేయి ✨"):
        if story_idea.strip() == "": st.warning("దయచేసి ఐడియా ఇవ్వండి!")
        else:
            with st.spinner("AI కథను తయారు చేస్తోంది..."):
                try:
                    prompt = f"Create a short story about: '{story_idea}' in Telugu text. After that, list 3 simple scenes from the story in Telugu, each scene on a new line."
                    encoded_prompt = requests.utils.quote(prompt)
                    response = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?json=false")
                    if response.status_code == 200:
                        st.text_area("AI అవుట్‌పుట్:", value=response.text, height=400)
                except Exception as e: st.error(f"తప్పు జరిగింది: {e}")

# --- ట్యాబ్ 2: AI వాయిస్ జనరేటర్ ---
with tab2:
    voice_option = st.selectbox("వాయిస్ ఎంచుకోండి (Voice):", ("మగవారి వాయిస్ (Mohan)", "ఆడవారి వాయిస్ (Shruti)"))
    voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"
    
    col1, col2 = st.columns(2)
    with col1: speed_slider = st.slider("వాయిస్ వేగం (Speed):", -50, 50, -5, 5, format="%d%%", key="sp_2")
    with col2: volume_slider = st.slider("వాల్యూమ్ స్థాయి (Volume):", -50, 50, 0, 5, format="%d%%", key="vl_2")
    
    script_text = st.text_area("మీ వాయిస్ స్క్రిప్ట్ ఇక్కడ పేస్ట్ చేయండి:", height=200, key="voice_script")

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

    async def generate_audio(full_text, voice_model, speed, volume):
        chunks = split_text(full_text)
        audio_data = b""
        for chunk in chunks:
            communicate = edge_tts.Communicate(chunk, voice_model, rate=speed, volume=volume)
            async for chunk_data in communicate.stream():
                if chunk_data["type"] == "audio": audio_data += chunk_data["data"]
        return audio_data

    if st.button("AI వాయిస్ జనరేట్ చేయి 🚀"):
        if script_text.strip() == "": st.warning("దయచేసి స్క్రిప్ట్ ఇవ్వండి!")
        else:
            with st.spinner("AI వాయిస్ జనరేట్ అవుతోంది..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    final_audio_bytes = loop.run_until_complete(generate_audio(script_text, voice, f"{'' if speed_slider < 0 else '+'}{speed_slider}%", f"{'' if volume_slider < 0 else '+'}{volume_slider}%"))
                    st.audio(final_audio_bytes, format="audio/mp3")
                    st.download_button(label="📥 ఆడియో డౌน์โหลด", data=final_audio_bytes, file_name="voice.mp3", mime="audio/mp3")
                except Exception as e: st.error(f"లోపం: {e}")

# --- ట్యాబ్ 3: AI తెలుగు ఇమేజ్ జనరేటర్ (UPDATED) ---
with tab3:
    st.write("### 🎨 తెలుగు స్క్రిప్ట్ బట్టి సీన్ ఇమేజ్ జనరేటర్")
    st.write("మీ తెలుగు కథలోని సీన్లను ఒక్కో లైన్‌లో ఒక్కోటి చొప్పున తెలుగులోనే ఇవ్వండి. AI దాన్ని అర్థం చేసుకుని బొమ్మలు చేస్తుంది.")
    
    telugu_script = st.text_area(
        "తెలుగు సీన్స్ ఇక్కడ ఇవ్వండి (ఉదాహరణకు):\nఒక అడవిలో ఒక పెద్ద సింహం పడుకుని ఉంది\nఒక చిన్న ఎలుక సింహం మీద ఆడుకుంటోంది\nసింహం ఎలుకను చేతితో పట్టుకుంది",
        height=200,
        key="telugu_script"
    )
    
    if st.button("తెలుగు సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨"):
        if telugu_script.strip() == "":
            st.warning("దయచేసి కనీసం ఒక తెలుగు సీన్ అయినా టైప్ చేయండి!")
        else:
            # లైన్ బై లైన్ తెలుగు సీన్లను విడగొడుతుంది
            telugu_scenes = [line.strip() for line in telugu_script.split('\n') if line.strip()]
            st.success(f"మొత్తం {len(telugu_scenes)} తెలుగు సీన్లు కనుగొనబడ్డాయి. ప్రాసెస్ అవుతున్నాయి...")
            
            for i, t_scene in enumerate(telugu_scenes):
                st.write(f"**సీన్ {i+1} (తెలుగు):** {t_scene}")
                
                with st.spinner(f"సీన్ {i+1} ఇమేజ్ తయారవుతోంది..."):
                    try:
                        # ట్రిక్: తెలుగు సీన్ ని బ్యాక్‌గ్రౌండ్‌లో AI ద్వారా ఇంగ్లీష్ ప్రాంప్ట్ కింద మార్చడం
                        translate_prompt = f"Convert this Telugu scene into a highly detailed English image generation prompt for AI. Just give me the English description, nothing else. Telugu text: '{t_scene}'"
                        encoded_t_prompt = requests.utils.quote(translate_prompt)
                        
                        translate_response = requests.get(f"https://text.pollinations.ai/{encoded_t_prompt}?json=false")
                        
                        if translate_response.status_code == 200:
                            english_prompt = translate_response.text.strip()
                            
                            # ఇంగ్లీష్ ప్రాంప్ట్ తో ఇమేజ్ జనరేట్ చేయడం
                            encoded_scene = requests.utils.quote(english_prompt)
                            image_url = f"https://image.pollinations.ai/p/{encoded_scene}?width=1024&height=576&nologo=true"
                            
                            img_response = requests.get(image_url)
                            if img_response.status_code == 200:
                                st.image(img_response.content, caption=f"Scene {i+1} Output", use_container_width=True)
                                st.download_button(
                                    label=f"📥 సీన్ {i+1} ఇమేజ్ డౌน์โหลด",
                                    data=img_response.content,
                                    file_name=f"scene_{i+1}.jpg",
                                    mime="image/jpeg",
                                    key=f"img_dl_{i}"
                                )
                                st.markdown("---")
                            else: st.error(f"సీన్ {i+1} ఇమేజ్ రాలేదు.")
                        else: st.error(f"తెలుగు సీన్ అర్థం చేసుకోవడంలో లోపం వచ్చింది.")
                    except Exception as e: st.error(f"తప్పు జరిగింది: {e}")
