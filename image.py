import asyncio
import re
import streamlit as st
import edge_tts
import requests
import io

# వెబ్‌సైట్ కాన్ఫిగరేషన్
st.set_page_config(page_title="Telugu AI Pro Studio", page_icon="🎬", layout="wide")
st.title("🎬 తెలుగు AI ఆల్-ఇన్-వన్ వీడియో క్రియేటర్ స్టూడియో")
st.write("కథల టాపిక్ ఇస్తే చాలు - స్పష్టమైన 2D యానిమేషన్ సీన్లు మరియు ప్రొఫెషనల్ నాచురల్ వాయిస్‌ ఓవర్ లభిస్తాయి.")

# మూడు ప్రధాన ట్యాబ్స్
tab1, tab2, tab3 = st.tabs([
    "📝 1. AI స్టోరీ & సీన్స్ మేకర్", 
    "🎙️ 2. ప్రొఫెషనల్ వాయిస్ ఓవర్", 
    "🎨 3. HD 2D సీన్ ఇమేజ్ జనరేటర్"
])

# --- ట్యాబ్ 1: AI స్టోరీ జనరేటర్ ---
with tab1:
    st.write("### 📝 మీ టాపిక్ లేదా పూర్తి కథను ఇక్కడ ఇవ్వండి")
    st.write("మీరు కథ రాసినా లేదా ఒక చిన్న టాపిక్ ఇచ్చినా, AI దాన్ని ఇమేజ్ జనరేషన్ కోసం పర్ఫెక్ట్ సీన్లుగా మారుస్తుంది.")
    
    # యూజర్ ఇచ్చిన పెద్ద దెయ్యం కథ ఇక్కడ పేస్ట్ చేసుకోవచ్చు
    story_idea = st.text_area(
        "కథ లేదా టాపిక్ ఇక్కడ ఇవ్వండి:",
        placeholder="మీ కథను లేదా టాపిక్ ఇక్కడ పేస్ట్ చేయండి...",
        height=200,
        key="main_story_input"
    )
    
    if st.button("AI సీన్లను సిద్ధం చేయి ✨", key="gen_story_btn"):
        if story_idea.strip() == "":
            st.warning("దయచేసి కథను లేదా టాపిక్‌ను ఎంటర్ చేయండి!")
        else:
            with st.spinner("AI మీ కథ నుండి ఇమేజ్ సీన్లను వేరు చేస్తోంది..."):
                try:
                    # 1000167021.png లాంటి ప్యానెల్ సీన్లు రావడానికి ప్రాంప్ట్ ట్యూనింగ్
                    prompt = (
                        f"Analyze this story/topic: '{story_idea}'. "
                        f"First, present the complete running story in beautiful Telugu text. "
                        f"Next, create a section named 'IMAGE GENERATION SCENES' and break down the progression into 4 to 6 specific chronological scenes. "
                        f"Write each scene description clearly in Telugu on a separate line so that the user can easily copy-paste each line to generate precise visual assets."
                    )
                    encoded_prompt = requests.utils.quote(prompt)
                    response = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?json=false")
                    
                    if response.status_code == 200:
                        st.success("మీ కథ మరియు సీన్స్ రెడీ అయ్యాయి!")
                        st.text_area("జనరేట్ అయిన అవుట్‌పుట్ (కింది సీన్లను కాపీ చేసి 3వ ట్యాబ్‌లో వాడండి):", value=response.text, height=450, key="story_output_box")
                    else:
                        st.error("సర్వర్ బిజీగా ఉంది, మళ్లీ ట్రై చేయండి.")
                except Exception as e:
                    st.error(f"చిన్న లోపం వచ్చింది: {e}")

# --- ట్యాబ్ 2: నాచురల్ AI వాయిస్ ఓవర్ ---
with tab2:
    st.write("### 🎙️ క్లియర్ & నాచురల్ వాయిస్ కంట్రోల్స్")
    
    voice_option = st.selectbox(
        "వాయిస్ మోడల్ ఎంచుకోండి:",
        ("మగవారి వాయిస్ (Mohan Neural - క్లియర్ అండ్ బేస్)", "ఆడవారి వాయిస్ (Shruti Neural - సాఫ్ట్ అండ్ నాచురల్)"),
        key="voice_select_opt"
    )
    voice = "te-IN-MohanNeural" if "Mohan" in voice_option else "te-IN-ShrutiNeural"
    
    st.write("#### 🎛️ క్లారిటీ మరియు స్పష్టత సెట్టింగ్స్:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # వాయిస్ నత్తిగా రాకుండా, స్పష్టంగా వినపడటానికి డిఫాల్ట్ వేగం -4% కి సెట్ చేశాం
        speed_slider = st.slider("వాయిస్ వేగం (Speed):", -50, 50, -4, 2, format="%d%%", key="sp_voice")
        voice_speed = f"{'' if speed_slider < 0 else '+'}{speed_slider}%"
        
    with col2:
        # డీఫాల్ట్ వాల్యూమ్ బూస్ట్ 8% చేసాం క్లారిటీ కోసం
        volume_slider = st.slider("వాల్యూమ్ స్థాయి (Volume):", -50, 50, 8, 2, format="%d%%", key="vl_voice")
        voice_volume = f"{'' if volume_slider < 0 else '+'}{volume_slider}%"
        
    with col3:
        # బేస్ సహజంగా ఉండటానికి పిచ్ సెట్టింగ్
        pitch_slider = st.slider("వాయిస్ పిచ్ (Pitch):", -20, 20, 0, 1, format="%dHz", key="pt_voice")
        voice_pitch = f"{'' if pitch_slider < 0 else '+'}{pitch_slider}Hz"
    
    script_text = st.text_area("వాయిస్ ఓవర్ కావలసిన టెక్స్ట్‌ను ఇక్కడ పేస్ట్ చేయండి:", height=250, key="voice_script")

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

    if st.button("హై-క్వాలిటీ ఆడియో జనరేట్ చేయి 🚀", key="gen_audio_btn"):
        if script_text.strip() == "":
            st.warning("దయచేసి స్క్రిప్ట్ బాక్స్‌లో టెక్స్ట్ ఎంటర్ చేయండి!")
        else:
            with st.spinner("స్పష్టమైన AI వాయిస్ ఓవర్ తయారవుతోంది..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    final_audio_bytes = loop.run_until_complete(
                        generate_audio(script_text, voice, voice_speed, voice_volume, voice_pitch)
                    )
                    st.audio(final_audio_bytes, format="audio/mp3")
                    st.download_button(label="📥 నాచురల్ ఆడియో ఫైల్ డౌน์โหลด", data=final_audio_bytes, file_name="telugu_clear_voice.mp3", mime="audio/mp3", key="dl_audio_btn")
                    st.success("వాయిస్ ఓవర్ విజయవంతంగా పూర్తయింది!")
                except Exception as e:
                    st.error(f"లోపం: {e}")

# --- ట్యాబ్ 3: HD ఇమేజ్ జనరేటర్ ---
with tab3:
    st.write("### 🎨 HD సీన్ ఇమేజ్ జనరేటర్ (జూమ్ సమస్య పూర్తిగా పరిష్కరించబడింది)")
    
    col_ratio, col_style = st.columns(2)
    
    with col_ratio:
        st.write("#### 📐 ఇమేజ్ సైజ్/రేషియో ఎంచుకోండి:")
        ratio_option = st.radio(
            "వీడియో ఫార్మాట్:",
            ("యూట్యూబ్ నార్మల్ వీడియో (16:9 - Landscape) [డిఫాల్ట్]", "షార్ట్స్/రీల్స్ (9:16 - Portrait)"),
            index=0,
            key="ratio_choice"
        )
        
    with col_style:
        st.write("#### 🎭 ఇమేజ్ శైలి (Style):")
        style_option = st.radio(
            "ఫోటో రకం:",
            (
                "తెలుగు 2D కామిక్ స్ట్రిప్ (Traditional 2D Art Style like 1000167021.png)", 
                "న్యూస్ పేపర్ స్కెచ్ (Vintage Newspaper Print Style)",
                "సినిమాటిక్ రియలిస్టిక్ (Photorealistic Cinematic Style)"
            ),
            index=0,
            key="style_choice"
        )
    
    if "16:9" in ratio_option:
        img_width, img_height = 1024, 576
    else:
        img_width, img_height = 576, 1024

    # 1000167021.png లాగా జూమ్ అవ్వకుండా ఫుల్ బాడీ, బ్యాక్‌గ్రౌండ్, వస్తువులు అన్నీ స్పష్టంగా వచ్చేలా కఠినమైన నిబంధనలు పెట్టాం
    framing_rules = (
        ", established wide shot framing, no close-ups, no face zoom, show entire bodies and full characters from head to toe, "
        "completely visible clear background environment, crisp sharp facial features, highly detailed distinct eyes and expressions, "
        "all background properties and elements fully visible in frame"
    )

    if "2D కామిక్ స్ట్రిప్" in style_option:
        style_prompt_addition = f"in a beautiful traditional Indian 2D comic book graphic novel illustration style resembling file 1000167021.png, clean precise outlines, solid rich flat colors, detailed regional background, pure comic art style, no 3d rendering, no depth blur{framing_rules}"
    elif "న్యూస్ పేపర్" in style_option:
        style_prompt_addition = f"in an old classic vintage newspaper archive print style, sharp black and white ink sketch line-art, detailed engravings, halftone texture look{framing_rules}"
    else:
        style_prompt_addition = f"8k resolution, photorealistic cinematic film style, dynamic lighting, masterpiece quality, highly detailed textures, real-life composition{framing_rules}"

    st.write("#### 📝 మీ తెలుగు సీన్స్ ఇక్కడ ఇవ్వండి (లైన్ బై లైన్):")
    telugu_script = st.text_area(
        "ఒక్కో లైన్‌లో ఒక సీన్ చొప్పున పేస్ట్ చేయండి:",
        placeholder="మూడు స్నేహితులు ఒక దట్టమైన అడవిలో ఉన్న పాత చెక్క ఇంటిని చూస్తున్నారు\nఇంటి ప్రధాన తలుపుపై ఒక నల్లటి ఆకారం నిలబడి ఉంది",
        height=200,
        key="telugu_script_box"
    )
    
    if st.button("HD సీన్ ఇమేజెస్ జనరేట్ చేయి 🎨", key="gen_images_btn"):
        if telugu_script.strip() == "":
            st.warning("దయచేసి కనీసం ఒక సీన్ అయినా టైప్ చేయండి!")
        else:
            telugu_scenes = [line.strip() for line in telugu_script.split('\n') if line.strip()]
            st.success(f"మొత్తం {len(telugu_scenes)} సీన్లు లభించాయి. ఇమేజెస్ తయారవుతున్నాయి...")
            
            for i, t_scene in enumerate(telugu_scenes):
                st.write(f"**సీన్ {i+1} (తెలుగు):** {t_scene}")
                
                with st.spinner(f"సీన్ {i+1} ఫోటో తయారవుతోంది... దయచేసి ఆగండి..."):
                    try:
                        # తెలుగు నుండి ఇంగ్లీష్ ప్రాంప్ట్ బూస్టింగ్ కి మార్చడం
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
                                st.image(image_bytes, caption=f"HD Scene {i+1} Output", use_container_width=True)
                                
                                # డౌన్‌లోడ్ ఫిక్స్ బఫర్
                                img_buffer = io.BytesIO(image_bytes)
                                st.download_button(
                                    label=f"📥 సీన్ {i+1} HD ఇమేజ్ డౌน์โหลด",
                                    data=img_buffer,
                                    file_name=f"hd_scene_{i+1}.jpg",
                                    mime="image/jpeg",
                                    key=f"img_dl_fixed_{i}"
                                )
                                st.markdown("---")
                            else: st.error(f"సీన్ {i+1} సర్వర్ నుండి రాలేదు.")
                        else: st.error(f"లైన్ అర్థం చేసుకోవడంలో చిన్న లోపం వచ్చింది.")
                    except Exception as e: st.error(f"తప్పు జరిగింది: {e}")
