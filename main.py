from io import BytesIO
import streamlit as st
import os
import tempfile
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import assemblyai as aai
import time
from datetime import timedelta
from pysrt import SubRipFile
from dotenv import load_dotenv

load_dotenv()
# Configure AssemblyAI
aai.settings.api_key =  os.getenv('ASSEMBLYAI_API_KEY')  # Replace with your API key

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
    # Subtitle customization options
    st.sidebar.header("Subtitle Settings")
    font_size = st.sidebar.slider("Font Size", 12, 48, 24,key="1")
    font_color = st.sidebar.color_picker("Font Color", "#FFFFFF")
    position = st.sidebar.selectbox("Position", 
                                  ["bottom", "top", "center"],
                                  index=0)
    
    if video_file and srt_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as video_tmp:
            video_tmp.write(video_file.getvalue())

        try:
            # Load video
            video = VideoFileClip(video_tmp)
            
            # Load subtitles
            subs = SubRipFile.open(srt_file)
            subtitle_clips = []
            
            # Position mapping
            position_mapping = {
                "bottom": ('center', 'bottom'),
                "top": ('center', 'top'),
                "center": 'center'
            }
            
            for sub in subs:
                start_time = sub.start.total_seconds()
                end_time = sub.end.total_seconds()
                duration = end_time - start_time
                
                subtitle_clip = (TextClip(sub.text, 
                                        font='Arial', 
                                        fontsize=font_size, 
                                        color=font_color,
                                        stroke_color='black')
                               .set_position(position_mapping[position])
                               .set_duration(duration)
                               .set_start(start_time))
                
                subtitle_clips.append(subtitle_clip)
            
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='with_subs.mp4')
            
            # Merge video with subtitles
            final_video = CompositeVideoClip([video] + subtitle_clips)
            final_video.write_videofile(output_path)
            video.close()
            final_video.close()
            return output_path
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
        finally:
            try:
                os.unlink(output_path)
            except:
                pass
def main():
    st.title("Subtitile GenAI")
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
                st.video(merge_srt(uploaded_file.getvalue(),transcript.audio_url))
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
                    st.download_button(
                        "Merge SRT into video",
                        merge_srt(uploaded_file.getvalue(),srt_content),
                        file_name="captions.cc",
                        mime="text/plain"
                    )
         
                    
if __name__ == "__main__":
    main()