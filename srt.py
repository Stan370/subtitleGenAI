import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from pysrt import SubRipFile
import tempfile
import os
import ffmpeg
from pathlib import Path

def process_video(video_file, srt_file, font_size, font_color, position):
    video_path = None
    srt_path = None
    output_path = None
    temp_files = []
    
    try:
        # Create temporary files
        video_path = tempfile.mktemp(suffix='.mp4')
        srt_path = tempfile.mktemp(suffix='.srt')
        output_path = tempfile.mktemp(suffix='_with_subs.mp4')
        temp_files.extend([video_path, srt_path, output_path])

        # Write video file
        with open(video_path, 'wb') as f:
            f.write(video_file.getvalue())

        # Write SRT file
        with open(srt_path, 'w', encoding='utf-8') as f:
            if isinstance(srt_file, str):
                f.write(srt_file)
            else:
                f.write(srt_file.getvalue().decode('utf-8'))

        # Get video information using ffmpeg
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])

        # Load video using ffmpeg
        stream = ffmpeg.input(video_path)
        
        # Load subtitles
        subs = SubRipFile.open(srt_path)
        
        # Position mapping
        position_mapping = {
            "bottom": ('center', height - font_size - 20),
            "top": ('center', font_size + 20),
            "center": ('center', height // 2)
        }
        
        # Create subtitle filter complex
        filter_complex = []
        for i, sub in enumerate(subs):
            start_time = sub.start.total_seconds()
            end_time = sub.end.total_seconds()
            duration = end_time - start_time
            
            # Escape special characters in subtitle text
            text = sub.text.replace("'", "\\'").replace('"', '\\"')
            
            # Create drawtext filter for each subtitle
            x, y = position_mapping[position]
            if x == 'center':
                x = f"(w-text_w)/2"
            
            filter_complex.append(
                f"drawtext=text='{text}':fontfile=/path/to/arial.ttf:fontsize={font_size}:"
                f"fontcolor={font_color}:bordercolor=black:borderw=1:"
                f"x={x}:y={y}:enable='between(t,{start_time},{end_time})'"
            )

        # Combine all filters
        filter_str = ','.join(filter_complex)
        
        # Apply filters and save
        stream = ffmpeg.filter(stream, 'subtitles', srt_path)
        stream = ffmpeg.output(stream, output_path, acodec='copy', vcodec='libx264')
        
        # Run ffmpeg command
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        # Read the output file
        with open(output_path, 'rb') as f:
            return f.read()
            
    except ffmpeg.Error as e:
        st.error(f"FFmpeg error: {e.stderr.decode()}")
        return None
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return None
    finally:
        # Clean up temporary files
        for file_path in temp_files:
            if file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except Exception as e:
                    st.warning(f"Could not delete temporary file {file_path}: {str(e)}")

def srt():
    st.title("Video Subtitle Merger")
    
    # File uploaders
    video_file = st.file_uploader("Upload your video", type=['mp4', 'mkv', 'mov'])
    srt_file = st.file_uploader("Upload SRT subtitle file", type=['srt'])
    
    if video_file and srt_file:
        # Subtitle customization options
        st.sidebar.header("Subtitle Settings")
        font_size = st.sidebar.slider("Font Size", 12, 48, 24, key="font_size")
        font_color = st.sidebar.color_picker("Font Color", "#FFFFFF", key="font_color")
        position = st.sidebar.selectbox("Position", 
                                      ["bottom", "top", "center"],
                                      index=0, 
                                      key="position")
        
        if st.button("Merge Subtitles"):
            with st.spinner('Processing video with subtitles...'):
                output_bytes = process_video(
                    video_file, 
                    srt_file, 
                    font_size, 
                    font_color.lstrip('#'),  # Remove # from color code
                    position
                )
                
                if output_bytes:
                    st.success('Video processing completed!')
                    
                    st.download_button(
                        label="Download Video with Subtitles",
                        data=output_bytes,
                        file_name="video_with_subtitles.mp4",
                        mime="video/mp4"
                    )

if __name__ == "__main__":
    srt()