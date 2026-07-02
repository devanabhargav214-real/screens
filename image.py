import asyncio
import re
import streamlit as st
import edge_tts
import requests
import json

# వెబ్‌సైట్ టైటిల్ మరియు డిజైన్
st.set_page_config(page_title="Telugu AI Studio", page_icon="🎬", layout="wide")
st.title("🎬 తెలుగు AI ఆల్-ఇన్-వన్ స్టోరీ స్టూడియో")
st.write("ఇక్కడ మీరు స్టోరీ స్క్రిప్ట్ జనరేట్ చేయవచ్చు, వాయిస్ మార్చవచ్చు మరియు సీన్ ఇమేజ్స్ కూడా పొందవచ్చు.")

# మూడు ట్యాబ్స్ క్రియేట్ చేస్తున్నాం
tab1, tab2, tab3 = st.tabs([
    "📝 AI స్క్రిప్ట్ జనరేటర్ (New)", 
    "🎙️ AI వాయిస్ జనరేటర్", 
    "🎨 AI ఇమేజ్ జనరేటర్"
])

# --- ట్యాబ్ 1: AI స్క్రిప్ట్ జనరేటర్ (NEW FEATURE) ---
with tab1:
    st.write("### 📝 మీ ఐడియా నుండి స్టోరీ స్క్రిప్ట్ జనరేట్ చేయండి")
    st.write("మీకు కావాల్సిన కథ లైన్ లేదా ఐడియా ఇక్కడ టైప్ చేయండి, AI దాన్ని సీన్ బై సీన్ స్క్రిప్ట్ లాగా మారుస్తుంది.")
    
    story_idea = st.text_input(
        "మీ కథ ఐడియా (ఉదాహరణకు: ఒక అడవిలో సింహం మరియు ఎలుక స్నేహం లేదా దెయ్యం కథ):",
        placeholder="ఇక్కడ టైప్ చేయండి..."
    )
    
    if st.button("కథ & ఇమేజ్ ప్రాంప్ట్స్ జనరేట్ చేయి ✨"):
        if story_idea.strip() == "":
            st.warning("దయచేసి ఏదైనా ఒక ఐడియా ఇవ్వండి!")
        else:
            with st.spinner("AI మీ కథను మరియు సీన్లను తయారు చేస్తోంది..."):
                try:
                    # Pollinations text API ద్వారా ఉచితంగా స్క్రిప్ట్ జనరేట్ చేయడం
                    prompt = f"Create a short story about: '{story_idea}'. Give me the output in two sections. Section 1: The full story in Telugu text. Section 2: Break down the story into 3 to 5 separate scenes, and for each scene, provide a detailed English image prompt that describes that scene perfectly so I can generate pictures. Keep it clear."
                    
                    encoded_prompt = requests.utils.quote(prompt)
                    url = f"https://text.pollinations.ai/{encoded_prompt}?json=false"
                    
                    response = requests.get(url)
                    if response.status_code == 200:
                        ai_output = response.text
                        st.success("మీ స్క్రిప్ట్ మరియు సీన్స్ రెడీ అయ్యాయి! కింద చూడండి:")
                        
                        # స్క్రీన్ మీద చూపించడం
                        st.markdown("### 📖 జనరేట్ అయిన స్టోరీ & సీన్స్:")
                        st.text_area("AI అవుట్‌పుట్ (దీన్ని కాపీ చేసి పక్క ట్యాబ్స్‌లో వాడుకోండి):", value=ai_output, height=400)
                    else:
                        st.error("స్క్రిప్ట్ జనరేట్ చేయడం కుదరలేదు, మళ్లీ ప్రయత్నించండి.")
                except Exception as e:
                    st.error(f"చిన్న తప్పు జరిగింది: {e}")

# --- ట్యాబ్ 2: AI వాయిస్ జనరేటర్ ---
with tab2:
    voice_option = st.selectbox(
        "వాయిస్ ఎంచుకోండి (Voice):",
        ("మగవారి వాయిస్ (Mohan Neural)", "ఆడవారి వాయిస్ (Shruti Neural)"),
    )
    voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"

    st.write("### 🎛️ వాయిస్ సెట్టింగ్స్:")
    col1, col2 = st.columns(2)
    with col1:
        speed_slider = st.slider("వాయిస్ వేగం (Speed):", -50, 50, -5, 5, format="%d%%", key="sp_2")
        voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
    with col2:
        volume_slider = st.slider("వాల్యూమ్ స్థాయి (Volume):", -50, 50, 0, 5, format="%d%%", key="vl_2")
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

# --- ట్యాబ్ 3: AI ఇమేజ్ జనరేటర్ ---
with tab3:
    st.write("### 🎨 స్టోరీ సీన్ బై సీన్ ఇమేజ్ జనరేటర్")
    st.write("ఒక్కో లైన్‌లో ఒక్కో సీన్ ప్రాంప్ట్ (ఇంగ్లీష్‌లో) ఇవ్వండి. ఎన్ని లైన్లు ఇస్తే అన్ని ఇమేజ్‌లు వస్తాయి.")
    
    image_script = st.text_area(
        "ఇమేజ్ సీన్స్ ఇక్కడ ఇవ్వండి:",
        placeholder="An old wise king sitting on a throne\nA beautiful green forest with a river",
        height=200,
        key="image_script"
    )
    
    if st.button("సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨"):
        if image_script.strip() == "":
            st.warning("దయచేసి కనీసం ఒక సీన్ అయినా టైప్ చేయండి!")
        else:
            scenes = [line.strip() for line in image_script.split('\n') if line.strip()]
            st.success(f"మొత్తం {len(scenes)} సీన్లు కనుగొనబడ్డాయి. ఇమేజ్‌లు జనరేట్ అవుతున్నాయి...")
            
            for i, scene in enumerate(scenes):
                st.write(f"**సీన్ {i+1}:** {scene}")
                with st.spinner(f"సీన్ {i+1} ఇమేజ్ తయారవుతోంది..."):
                    try:
                        encoded_scene = requests.utils.quote(scene)
                        image_url = f"https://image.pollinations.ai/p/{encoded_scene}?width=1024&height=576&nologo=true"
                        
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            image_bytes = response.content
                            st.image(image_bytes, caption=f"Scene {i+1} Output", use_container_width=True)
                            st.download_button(
                                label=f"📥 సీన్ {i+1} ఇమేజ్ డౌన్‌లోడ్ చేసుకోండి",
                                data=image_bytes,
                                file_name=f"scene_{i+1}.jpg",
                                mime="image/jpeg",
                                key=f"download_{i}"
                            )
                            st.markdown("---")
                        else:
                            st.error(f"సీన్ {i+1} జనరేట్ చేయడం kuదరలేదు.")
                    except Exception as e:
                        st.error(f"తప్పు జరిగింది: {e}")
        
