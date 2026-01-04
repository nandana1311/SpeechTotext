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
    page_title="Speech-to-Text Transcription",
    page_icon="🎤",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)


def convert_to_wav(audio_bytes, file_extension):
    """
    Convert audio bytes to WAV format
    
    Args:
        audio_bytes: Audio file bytes
        file_extension: Original file extension
    
    Returns:
        WAV audio bytes
    """
    try:
        # Load audio from bytes
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
        
        # Export to WAV
        wav_io = BytesIO()
        audio.export(wav_io, format='wav')
        wav_io.seek(0)
        
        return wav_io.read()
        
    except Exception as e:
        st.error(f"Error converting audio: {e}")
        return None


def transcribe_audio(audio_bytes, language='en-US'):
    """
    Transcribe audio bytes to text
    
    Args:
        audio_bytes: Audio file bytes (WAV format)
        language: Language code
    
    Returns:
        Transcribed text and confidence info
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    
    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        # Load and transcribe
        with sr.AudioFile(tmp_path) as source:
            audio_length = source.DURATION
            
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=min(1.0, audio_length))
            
            # Record audio data
            audio_data = recognizer.record(source)
            
            # Try transcription
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
                # Try with show_all for alternatives
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
                    
    except sr.RequestError as e:
        return {
            'success': False,
            'error': f'API error: {e}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {e}'
        }


def main():
    # Header
    st.markdown('<h1 class="main-header">🎤 Speech-to-Text Transcription</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.subheader("Language Selection")
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
            "Select audio language:",
            options=list(language_options.keys()),
            index=0
        )
        language_code = language_options[selected_language]
        
        st.markdown("---")
        st.subheader("ℹ️ Information")
        st.info("""
        **Supported formats:**
        - MP3, WAV, OGG, FLAC, M4A
        
        **Tips for best results:**
        - Use clear audio with minimal background noise
        - Ensure speakers speak clearly
        - Select the correct language
        """)
        
        st.markdown("---")
        st.subheader("📋 About")
        st.write("This tool uses Google Speech Recognition API to convert speech to text.")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 Upload Audio File")
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'ogg', 'flac', 'm4a'],
            help="Upload an audio file to transcribe"
        )
        
        if uploaded_file is not None:
            st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
            
            col_a, col_b = st.columns([1, 1])
            
            with col_a:
                st.write(f"**Filename:** {uploaded_file.name}")
            with col_b:
                st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
            
            if st.button("🎯 Transcribe Audio", key="transcribe_btn"):
                with st.spinner("Processing audio..."):
                    # Get file extension
                    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                    
                    # Read file bytes
                    audio_bytes = uploaded_file.read()
                    
                    # Convert to WAV if needed
                    if file_extension != '.wav':
                        with st.spinner("Converting to WAV format..."):
                            wav_bytes = convert_to_wav(audio_bytes, file_extension)
                    else:
                        wav_bytes = audio_bytes
                    
                    if wav_bytes:
                        with st.spinner(f"Transcribing ({selected_language})..."):
                            result = transcribe_audio(wav_bytes, language_code)
                        
                        # Display results
                        st.markdown("---")
                        
                        if result['success']:
                            st.success("✅ Transcription Complete!")
                            
                            # Metadata
                            col_i, col_ii, col_iii = st.columns(3)
                            with col_i:
                                st.metric("Duration", f"{result['duration']:.2f}s")
                            with col_ii:
                                st.metric("Language", selected_language)
                            with col_iii:
                                st.metric("Confidence", result['confidence'])
                            
                            # Transcription result
                            st.subheader("📝 Transcription Result:")
                            st.text_area(
                                "Text Output",
                                value=result['text'],
                                height=200,
                                key="transcription_output"
                            )
                            
                            # Download button
                            st.download_button(
                                label="💾 Download Transcription",
                                data=result['text'],
                                file_name="transcription.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error("❌ Transcription Failed")
                            st.markdown(f'<div class="error-box">{result["error"]}</div>', unsafe_allow_html=True)
                            
                            if 'duration' in result:
                                st.info(f"Audio duration: {result['duration']:.2f} seconds")
                            
                            st.warning("""
                            **Possible reasons:**
                            - Audio contains no clear speech
                            - Wrong language selected
                            - Poor audio quality or too much background noise
                            - Audio is a sound effect or music only
                            """)
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        # Create sample statistics
        if uploaded_file:
            st.success("✅ File uploaded successfully")
            st.metric("Status", "Ready to transcribe")
        else:
            st.warning("⏳ Waiting for file upload")
            st.metric("Status", "No file uploaded")
        
        st.markdown("---")
        st.subheader("💡 Tips")
        st.markdown("""
        **For best results:**
        - Use clear audio with minimal background noise
        - Ensure speakers speak clearly
        - Select the correct language
        - Audio files should be under 200MB
        - Supported formats: MP3, WAV, OGG, FLAC, M4A
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Made with ❤️ using Streamlit | Powered by Google Speech Recognition</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
