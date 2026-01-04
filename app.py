"""
Speech-to-Text Transcription Tool with Streamlit UI
A user-friendly web interface for converting audio to text
"""

import streamlit as st
import speech_recognition as sr
import os
from pydub import AudioSegment
import tempfile
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Speech-to-Text",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern, clean design
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 0 3rem 0;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #8b8b8b;
        font-size: 1.1rem;
    }
    
    /* Upload section */
    .upload-section {
        background: #1e1e1e;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }
    
    /* Language selector */
    .stSelectbox {
        margin-bottom: 1.5rem;
    }
    
    .stSelectbox > div > div {
        background: #2d2d2d;
        border: 1px solid #404040;
        color: #ffffff;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #2d2d2d;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #505050;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: #363636;
    }
    
    [data-testid="stFileUploader"] section {
        border: none;
    }
    
    [data-testid="stFileUploader"] section > div {
        color: #ffffff;
    }
    
    [data-testid="stFileUploader"] small {
        color: #a0a0a0;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Audio player */
    audio {
        width: 100%;
        margin: 1rem 0;
        border-radius: 10px;
    }
    
    /* Results section */
    .result-box {
        background: #2d2d2d;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
    }
    
    /* Text area */
    .stTextArea textarea {
        background: #2d2d2d;
        color: #ffffff;
        border-radius: 12px;
        border: 2px solid #404040;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        background: #363636;
    }
    
    .stTextArea label {
        color: #ffffff;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    
    /* Download button */
    .stDownloadButton>button {
        background: white;
        color: #667eea;
        border: 2px solid #667eea;
        font-weight: 600;
    }
    
    .stDownloadButton>button:hover {
        background: #667eea;
        color: white;
    }
    
    /* Success/Error messages */
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)


def convert_to_wav(audio_bytes, file_extension):
    """Convert audio bytes to WAV format"""
    try:
        if file_extension == '.mp3':
            audio = AudioSegment.from_mp3(BytesIO(audio_bytes))
        elif file_extension == '.ogg':
            audio = AudioSegment.from_ogg(BytesIO(audio_bytes))
        elif file_extension == '.flac':
            audio = AudioSegment.from_file(BytesIO(audio_bytes), "flac")
        elif file_extension == '.m4a':
            audio = AudioSegment.from_file(BytesIO(audio_bytes), "m4a")
        elif file_extension == '.wav':
            return audio_bytes
        else:
            audio = AudioSegment.from_file(BytesIO(audio_bytes))
        
        wav_io = BytesIO()
        audio.export(wav_io, format='wav')
        wav_io.seek(0)
        return wav_io.read()
    except Exception as e:
        st.error(f"Error converting audio: {e}")
        return None


def transcribe_audio(audio_bytes, language='en-US'):
    """Transcribe audio bytes to text"""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        with sr.AudioFile(tmp_path) as source:
            audio_length = source.DURATION
            recognizer.adjust_for_ambient_noise(source, duration=min(1.0, audio_length))
            audio_data = recognizer.record(source)
            
            try:
                text = recognizer.recognize_google(audio_data, language=language)
                os.unlink(tmp_path)
                return {
                    'success': True,
                    'text': text,
                    'duration': audio_length,
                    'confidence': 'High'
                }
            except sr.UnknownValueError:
                try:
                    result = recognizer.recognize_google(audio_data, language=language, show_all=True)
                    os.unlink(tmp_path)
                    
                    if result and 'alternative' in result:
                        alternatives = result['alternative']
                        if alternatives:
                            return {
                                'success': True,
                                'text': alternatives[0].get('transcript', ''),
                                'duration': audio_length,
                                'confidence': 'Low'
                            }
                    
                    return {
                        'success': False,
                        'error': 'Could not understand audio',
                        'duration': audio_length
                    }
                except:
                    os.unlink(tmp_path)
                    return {
                        'success': False,
                        'error': 'Could not understand audio',
                        'duration': audio_length
                    }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {e}'
        }


def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🎤 Speech-to-Text</h1>
            <p>Convert your audio files to text in seconds</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Language selector
    st.markdown("### 🌐 Select Language")
    language_options = {
        "English (US)": "en-US",
        "English (UK)": "en-GB",
        "Spanish": "es-ES",
        "French": "fr-FR",
        "German": "de-DE",
        "Hindi": "hi-IN",
        "Chinese": "zh-CN",
        "Japanese": "ja-JP",
        "Korean": "ko-KR",
        "Portuguese": "pt-BR",
        "Russian": "ru-RU",
        "Italian": "it-IT"
    }
    
    selected_language = st.selectbox(
        "Choose the language of your audio",
        options=list(language_options.keys()),
        index=0,
        label_visibility="collapsed"
    )
    language_code = language_options[selected_language]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### 📁 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file (MP3, WAV, OGG, FLAC, M4A)",
        type=['mp3', 'wav', 'ogg', 'flac', 'm4a'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Display audio player
        st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
        
        # File info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name.split('.')[0][:15] + '...' if len(uploaded_file.name) > 18 else uploaded_file.name.split('.')[0])
        with col2:
            st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("Format", uploaded_file.name.split('.')[-1].upper())
        
        # Transcribe button
        if st.button("🎯 Transcribe Audio", type="primary"):
            with st.spinner("✨ Converting and transcribing your audio..."):
                # Get file extension
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                
                # Read file bytes
                audio_bytes = uploaded_file.read()
                
                # Convert to WAV if needed
                if file_extension != '.wav':
                    wav_bytes = convert_to_wav(audio_bytes, file_extension)
                else:
                    wav_bytes = audio_bytes
                
                if wav_bytes:
                    result = transcribe_audio(wav_bytes, language_code)
                    
                    # Display results
                    if result['success']:
                        st.markdown(f"""
                            <div class="success-message">
                                <strong>✅ Transcription Complete!</strong><br>
                                Duration: {result['duration']:.1f}s | Confidence: {result['confidence']} | Language: {selected_language}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Transcription result
                        st.markdown("### 📝 Transcription")
                        transcription_text = st.text_area(
                            "Edit if needed",
                            value=result['text'],
                            height=200,
                            label_visibility="collapsed"
                        )
                        
                        # Download button
                        st.download_button(
                            label="💾 Download as Text File",
                            data=transcription_text,
                            file_name="transcription.txt",
                            mime="text/plain"
                        )
                    else:
                        st.markdown(f"""
                            <div class="error-message">
                                <strong>❌ Transcription Failed</strong><br>
                                {result.get('error', 'Unknown error')}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if 'duration' in result:
                            st.info(f"📊 Audio duration: {result['duration']:.1f} seconds")
                        
                        with st.expander("💡 Troubleshooting Tips"):
                            st.markdown("""
                            **Common issues:**
                            - Audio contains no clear speech
                            - Wrong language selected
                            - Poor audio quality or background noise
                            - Audio file is corrupted
                            
                            **Try:**
                            - Using a different audio file
                            - Selecting the correct language
                            - Recording in a quieter environment
                            """)
    else:
        # Empty state
        st.info("👆 Upload an audio file to get started")
        
        with st.expander("ℹ️ Supported Formats & Tips"):
            st.markdown("""
            **Supported Audio Formats:**
            - MP3, WAV, OGG, FLAC, M4A
            
            **For Best Results:**
            - Use clear audio with minimal background noise
            - Ensure speakers speak clearly and at moderate pace
            - Keep file size under 200MB
            - Select the correct language before transcribing
            """)


if __name__ == "__main__":
    main()
