import streamlit as st
import os
import tempfile
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import assemblyai as aai
import time
from datetime import timedelta
from pysrt import SubRipFile

# Configure AssemblyAI
aai.settings.api_key = "YOUR_ASSEMBLY_AI_KEY"  # Replace with your API key

def generate_srt(transcript):
    """Generate SRT format from transcript"""
    srt_content = ""
    for i, utterance in enumerate(transcript.utterances, 1):
        start_time = str(timedelta(seconds=int(utterance.start/1000)))
        end_time = str(timedelta(seconds=int(utterance.end/1000)))
        srt_content += f"{i}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{utterance.text}\n\n"
    return srt_content

def merge_srt(video_path, srt_path):
    # Load the video
    video = VideoFileClip(video_path)

    # Load subtitles from SRT file
    subs = SubRipFile.open(srt_path)
    subtitle_clips = []

    for sub in subs:
        # Create a text clip for each subtitle
        start_time = sub.start.ordinal / 1000  # Convert to seconds
        end_time = sub.end.ordinal / 1000     # Convert to seconds
        text = sub.text.replace('\n', ' ')    # Replace newlines with spaces

        subtitle_clip = (TextClip(text, fontsize=24, color='white', bg_color='black', size=(video.size[0], None))
                         .set_start(start_time)
                         .set_duration(end_time - start_time)
                         .set_position(("center", "bottom")))

        subtitle_clips.append(subtitle_clip)

    # Combine the video and subtitles
    final_video = CompositeVideoClip([video] + subtitle_clips)

def main():
    st.title("AccessTranscribe")
    st.write("Generate subtitles from your videos easily!")

    uploaded_file = st.file_uploader("Upload your video", type=['mp4', 'mkv', 'mov'])
    
    if uploaded_file:
       
        with st.spinner("Processing video..."):
            # Extract audio
            transcript = aai.Transcriber().transcribe(uploaded_file)
            if transcript.status == aai.TranscriptStatus.error:
                st.warning(f"Transcription failed: {transcript.error}")
                
                if transcript:
                    # Generate different formats
                    srt_content = generate_srt(transcript)
                    txt_content = transcript.text
                    
                    # Preview section
                    st.subheader("Preview")
                    st.video(merge_srt(uploaded_file,srt_content))
                    st.text_area("Transcription", txt_content, height=200)
                    
                    # Download buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.download_button(
                            "Download SRT",
                            srt_content,
                            file_name="subtitles.srt",
                            mime="text/plain"
                        )
                    with col2:
                        st.download_button(
                            "Download TXT",
                            txt_content,
                            file_name="transcription.txt",
                            mime="text/plain"
                        )
                    with col3:
                        st.download_button(
                            "Download CC",
                            txt_content,
                            file_name="captions.cc",
                            mime="text/plain"
                        )
         
                    
if __name__ == "__main__":
    main()