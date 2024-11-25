from io import BytesIO
import streamlit as st
import os
import tempfile
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import get_setting
import assemblyai as aai
import time
from datetime import timedelta
from pysrt import SubRipFile
from dotenv import load_dotenv

load_dotenv()
# Configure AssemblyAI
aai.settings.api_key =  os.getenv('ASSEMBLYAI_API_KEY')  # Replace with your API key
print(get_setting("FFMPEG_BINARY")) 
config = aai.TranscriptionConfig(speaker_labels=True, language_detection=True )

def generate_srt(transcript):
    """Generate SRT format from transcript"""
    srt_content = ""
    for i, utterance in enumerate(transcript.utterances):
        start_time = str(timedelta(seconds=int(utterance.start/1000)))
        end_time = str(timedelta(seconds=int(utterance.end/1000)))
        srt_content += f"{i}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{utterance.text}\n\n"
    return srt_content

def merge_srt(video_file, srt_file):
    
    if video_file and srt_file:
        # Subtitle customization options
        st.sidebar.header("Subtitle Settings")
        font_size = st.sidebar.slider("Font Size", 12, 48, 24, key="font_Size")
        font_color = st.sidebar.color_picker("Font Color", "#FFFFFF", key="font_color")
        position = st.sidebar.selectbox("Position", 
                                    ["bottom", "top", "center"],
                                    index=0, key="position")
        try:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            if video_file:
                tfile.write(video_file.getvalue())
                video_path = tfile.name
            else:
                video_path = tfile._file_urls
            video = VideoFileClip(video_path)
            video2 = VideoFileClip(tfile)
            st.video(video)
            st.video(video2)
            subs = SubRipFile.open(srt_file.name)
            
            # Position mapping
            position_mapping = {
                "bottom": ('center', 'bottom'),
                "top": ('center', 'top'),
                "center": 'center'
            }
            subtitle_clips = []
            for sub in subs:
                start_time = sub.start
                end_time = sub.end
                duration = end_time - start_time
                
                subtitle_clip = (TextClip(sub.text, 
                                        font='Arial', 
                                        fontsize=font_size, 
                                        color=font_color,
                                        stroke_color='black')
                               .set_position(position_mapping[position])
                               .set_start(start_time)
                               .set_duration(duration))
                                
                
                subtitle_clips.append(subtitle_clip)
            
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='with_subs.mp4')
            
            # Merge video with subtitles
            final_video = CompositeVideoClip([video] + subtitle_clips)
            final_video.write_videofile(output_path.name)
            video.close()
            final_video.close()
            # Read the generated video file and return its binary content
            with open(output_path.name, 'rb') as f:
                return f.read()  # Return binary data instead of file path
                
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")

def main():
    st.title("Subtitle GenAI")
    st.write("Generate subtitles from your videos easily!")

    uploaded_file = st.file_uploader("Upload your video", type=['mp4', 'mkv', 'mov'])
    
    if uploaded_file:
       
        with st.spinner("Processing video..."):
            # Extract audio
            transcript = aai.Transcriber().transcribe(uploaded_file,config)
            
            if transcript.status == aai.TranscriptStatus.error:
                st.warning(f"Transcription failed: {transcript.error}")
                
            elif transcript.status == "completed":
                # Generate different formats
                for i, utterance in enumerate(transcript.utterances):
                    print(i,utterance,end='\n')
                srt_content = transcript.export_subtitles_srt()
                txt_content = transcript.text

                # Preview section
                st.subheader("Preview")
                st.video(uploaded_file)
                st.text_area("Transcription", txt_content, height=200)
                
                # Download buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        "Download VTT subtitles",
                        transcript.export_subtitles_vtt(),
                        file_name="subtitles.srt",
                        mime="text/plain"
                    )
                with col2:
                    st.download_button(
                        "Download SRT subtitles",
                        transcript.export_subtitles_srt(),
                        file_name="transcription.txt",
                        mime="text/plain"
                    )
                with col3:
                    # Get the merged video binary data
                    merged_video = merge_srt(uploaded_file, srt_content)
                    if merged_video:  # Check if merge was successful
                        st.download_button(
                            "Merge SRT into video",
                            merged_video,  # Pass binary data directly
                            file_name="video_with_subtitles.mp4",
                            mime="video/mp4"
                        )
         
                    
if __name__ == "__main__":
    main()