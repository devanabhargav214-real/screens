import asyncio
import re
import streamlit as st
import edge_tts
import requests

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Studio Pro", page_icon="🎬", layout="wide")
st.title("🎬 తెలుగు AI ఆల్-ఇన్-వన్ వీడియో క్రియేటర్ స్టూడియో")
st.write("ఇక్కడ మీరు కేవలం టాపిక్ ఇస్తే కథ జనరేట్ అవుతుంది, నాచురల్ వాయిస్ ఓవర్ పొందవచ్చు మరియు 2D కార్టూన్ లేదా నార్మల్ HD ఇమేజ్స్ (9:16 / 16:9) క్రియేట్ చేయవచ్చు.")

# మూడు ప్రధాన ట్యాబ్స్
tab1, tab2, tab3 = st.tabs([
    "📝 1. AI స్టోరీ జనరేటర్ (Topic)", 
    "🎙️ 2. నాచురల్ AI వాయిస్ ఓవర్", 
    "🎨 3. HD సీన్ ఇమేజ్ జనరేటర్ (2D Cartoon/Normal)"
])

# --- ట్యాబ్ 1: AI స్టోరీ జనరేటర్ ---
with tab1:
    st.write("### 📝 మీ టాపిక్ ఇవ్వండి - పూర్తి కథను పొందండి")
    st.write("మీకు కావాల్సిన కథాంశం లేదా ఒక చిన్న లైన్ ఇక్కడ టైప్ చేయండి, AI పూర్తి కథను మరియు ఇమేజ్ సీన్లను సృష్టిస్తుంది.")
    
    story_idea = st.text_input(
        "కథ టాపిక్ (ఉదాహరణకు: అనగనగా ఒక గ్రామంలో ఒక పేద రైతు మరియు ఒక మాయా పక్షి):",
        placeholder="ఇక్కడ మీ కథ టాపిక్ రాయండి..."
    )
    
    if st.button("AI పూర్తి కథను తయారు చేయి ✨"):
        if story_idea.strip() == "":
            st.warning("దయచేసి ఏదైనా ఒక టాపిక్ ఇవ్వండి!")
        else:
            with st.spinner("AI మీ కోసం అద్భుతమైన కథను మరియు సీన్లను డిజైన్ చేస్తోంది..."):
                try:
                    prompt = (
                        f"Write a beautiful short story about the topic: '{story_idea}' in pure Telugu language. "
                        f"After completing the story, create a separate section called 'SCENES FOR IMAGE GENERATION' "
                        f"and provide 3 to 5 separate scenes from the story on new lines. Each scene must be written in "
                        f"Telugu so the user can easily copy them for creating images. Make it highly engaging."
                    )
                    encoded_prompt = requests.utils.quote(prompt)
                    response = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?json=false")
                    
                    if response.status_code == 200:
                        st.success("మీ కథ మరియు సీన్స్ విజయవంతంగా జనరేట్ అయ్యాయి!")
                        st.markdown("#### 📖 జనరేట్ అయిన కథ & సీన్స్:")
                        st.text_area("ఇక్కడి నుండి టెక్స్ట్‌ని కాపీ చేసి పక్క ట్యాబ్స్‌లో వాడుకోండి:", value=response.text, height=450)
                    else:
                        st.error("కథను జనరేట్ చేయడం కుదరలేదు, దయచేసి మళ్లీ ట్రై చేయండి.")
                except Exception as e:
                    st.error(f"చిన్న లోపం వచ్చింది: {e}")

# --- ట్యాబ్ 2: నాచురల్ AI వాయిస్ ఓవర్ ---
with tab2:
    st.write("### 🎙️ క్లియర్ & నాచురల్ తెలుగు వాయిస్ కంట్రోల్స్")
    
    voice_option = st.selectbox(
        "వాయిస్ ఎంచుకోండి (Voice Model):",
        ("మగవారి వాయిస్ (Mohan Neural - క్లియర్ అండ్ బేస్)", "ఆడవారి వాయిస్ (Shruti Neural - సాఫ్ట్ అండ్ నాచురల్)"),
    )
    voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"
    
    st.write("#### 🎛️ వాయిస్ క్లారిటీ సెッティングస్ (Voice Fine-Tuning):")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        speed_slider = st.slider("వాయిస్ వేగం (Speed):", -50, 50, -5, 5, format="%d%%", key="sp_voice")
        voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
        
    with col2:
        volume_slider = st.slider("వాల్యూమ్ స్థాయి (Volume):", -50, 50, 5, 5, format="%d%%", key="vl_voice")
        voice_volume = f"{'' if volume_slider < 0 else '+'}{volume_slider}%"
        
    with col3:
        pitch_slider = st.slider("వాయిస్ పిచ్/బేస్ (Pitch):", -20, 20, 0, 1, format="%dHz", key="pt_voice")
        voice_pitch = f"{'' if pitch_slider < 0 else '+'}{pitch_slider}Hz"
    
    script_text = st.text_area("మీ కథ లేదా స్క్రిప్ట్‌ను ఇక్కడ పేస్ట్ చేయండి:", height=250, key="voice_script")

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

    if st.button("హై-क्వాలిటీ ఆడియో జనరేట్ చేయి 🚀"):
        if script_text.strip() == "":
            st.warning("దయచేసి స్క్రిప్ట్ బాక్స్‌లో టెక్స్ట్ పేస్ట్ చేయండి!")
        else:
            with st.spinner("స్పష్టమైన AI వాయిస్ జనరేట్ అవుతోంది..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    final_audio_bytes = loop.run_until_complete(
                        generate_audio(script_text, voice, voice_speed, voice_volume, voice_pitch)
                    )
                    st.audio(final_audio_bytes, format="audio/mp3")
                    st.download_button(label="📥 నాచురల్ ఆడియో ఫైల్ డౌน์โหลด", data=final_audio_bytes, file_name="telugu_natural_voice.mp3", mime="audio/mp3")
                    st.success("వాయిస్ విజయవంతంగా జనరేట్ అయింది!")
                except Exception as e:
                    st.error(f"లోపం: {e}")

# --- ట్యాబ్ 3: HD ఇమేజ్ జనరేటర్ ---
# --- ట్యాబ్ 3: HD ఇమేజ్ జనరేటర్ (NEWSPAPER & TELUGU CULTURE UPDATE) ---
with tab3:
    st.write("### 🎨 తెలుగు సీన్స్ బట్టి హై-క్వాలిటీ HD ఇమేజ్ జనరేటర్")
    
    col_ratio, col_style = st.columns(2)
    
    with col_ratio:
        st.write("#### 📐 ఇమేజ్ సైజ్/రేషియో ఎంచుకోండి:")
        ratio_option = st.radio(
            "వీడియో టైప్ (Aspect Ratio):",
            ("యూట్యూబ్ నార్మల్ వీడియో (16:9 - Landscape) [డిఫాల్ట్]", "షార్ట్స్/రీల్స్/టిక్‌టాక్ (9:16 - Portrait)"),
            index=0
        )
        
    with col_style:
        st.write("#### 🎭 ఇమేజ్ స్టైల్ ఎంచుకోండి:")
        style_option = st.radio(
            "ఫోటో రకం (Image Style):",
            (
                "తెలుగు 2D యానిమేషన్ (Telugu Animated 2D Indian Culture Style)", 
                "న్యూస్ పేపర్ స్టైల్ (Vintage Newspaper Print/Sketch Style)",
                "నార్మల్ రియలిస్టిక్ స్టైల్ (Photorealistic/Cinematic)"
            ),
            index=0
        )
    
    # రేషియో కాన్ఫిగరేషన్
    if "16:9" in ratio_option:
        img_width = 1024
        img_height = 576
    else:
        img_width = 576
        img_height = 1024

    # స్టైల్స్ మరియు ఫేస్ క్లారిటీ కాన్ఫిగరేషన్
    face_and_framing = ", full wide view shot, showing full body and surrounding environment clearly without zooming in, ultra-clear detailed faces, perfect sharp facial features, well-defined eyes and expressions, complete properties"

    if "తెలుగు 2D యానిమేషన్" in style_option:
        style_prompt_addition = f"in a beautiful traditional Telugu animated 2D Indian culture style, authentic South Indian clothing like saree and dhoti, beautiful cultural background, vibrant flat colors, clean neat outlines, cartoon illustration{face_and_framing}"
    elif "న్యూస్ పేపర్ స్టైల్" in style_option:
        style_prompt_addition = f"in a vintage old Indian newspaper print style, halftone dots pattern, monochrome black and white ink sketch, retro newspaper archive illustration, highly detailed lines{face_and_framing}"
    else:
        style_prompt_addition = f"photorealistic, 8k resolution, cinematic lighting, highly detailed masterpiece, real-life look{face_and_framing}"

    st.write("#### 📝 మీ తెలుగు సీన్స్ ఇక్కడ ఇవ్వండి (లైన్ బై లైన్):")
    telugu_script = st.text_area(
        "ఒక్కో లైన్‌లో ఒక్కో సీన్ ఇవ్వండి:",
        placeholder="ఒక పల్లెటూర్లో ఒక తెలుగు రైతు పొలంలో పని చేస్తున్నాడు\nఒక ముసలి తాత అరుగు మీద కూర్చుని పేపర్ చదువుతున్నాడు",
        height=200,
        key="telugu_script"
    )
    
    if st.button("HD సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨"):
        if telugu_script.strip() == "":
            st.warning("దయచేసి కనీసం ఒక తెలుగు సీన్ అయినా టైప్ చేయండి!")
        else:
            telugu_scenes = [line.strip() for line in telugu_script.split('\n') if line.strip()]
            st.success(f"మొత్తం {len(telugu_scenes)} సీన్లు కనుగొనబడ్డాయి. అద్భుతమైన ఇమేజెస్ తయారవుతున్నాయి...")
            
            for i, t_scene in enumerate(telugu_scenes):
                st.write(f"**సీన్ {i+1} (తెలుగు):** {t_scene}")
                
                with st.spinner(f"సీన్ {i+1} ఫోటో తయారవుతోంది... దయచేసి ఆగండి..."):
                    try:
                        translate_prompt = (
                            f"Convert this Telugu scene into a highly detailed English image generation prompt. "
                            f"The output image must be strictly {style_prompt_addition}. "
                            f"Give me only the detailed English description, no other text. "
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
                                st.image(img_response.content, caption=f"HD Scene {i+1} Output", use_container_width=True)
                                st.download_button(
                                    label=f"📥 సీన్ {i+1} HD ఇమేజ్ డౌน์โหลด",
                                    data=img_response.content,
                                    file_name=f"hd_scene_{i+1}.jpg",
                                    mime="image/jpeg",
                                    key=f"img_dl_{i}"
                                )
                                st.markdown("---")
                            else: st.error(f"సీన్ {i+1} ఇమేజ్ లోడ్ అవ్వలేదు.")
                        else: st.error(f"తెలుగు లైన్‌ను అర్థం చేసుకోవడంలో లోపం వచ్చింది.")
                    except Exception as e: st.error(f"తప్పు జరిగింది: {e}")
                        
