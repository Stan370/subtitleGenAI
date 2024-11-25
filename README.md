# subtitleGenAI
An accessibility-focused subtitle generation platform that uses AssemblyAI’s API to transcribe live audio streams into text and generate subtitles for local video content. It supports MP4, MKV, MOV formats and generates captions in SRT (with timelines), CC (closed captions), and TXT (plain text) formats.

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/c8mhq3hkx7juddwytefa.jpg)
```markdown

This project demonstrates how to resolve FFmpeg version conflicts when using MoviePy for video processing. The application allows video manipulation such as editing, adding subtitles, or exporting videos while ensuring compatibility with FFmpeg.

## Features
- Configures MoviePy to use either its built-in FFmpeg binary or a custom path.
- Provides troubleshooting steps for common FFmpeg-related errors.
- Includes a script for video processing tasks like cutting clips and adding effects.

## Prerequisites
- Python 3.7 or later
- FFmpeg installed and accessible in the system PATH (if not using MoviePy’s built-in FFmpeg)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/Stan370/subtitileGenAI.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify FFmpeg installation:
   ```bash
   ffmpeg -version
   ```
<img width="821" alt="image" src="https://github.com/user-attachments/assets/11a8332e-2407-4671-bb25-03dc100f35a5">
## Usage
### Setting FFmpeg Path
The script automatically configures FFmpeg. To specify a custom FFmpeg binary:
1. Update the path in `config.py`:
   ```python
   from moviepy.config import change_settings
   change_settings({"FFMPEG_BINARY": "/path/to/ffmpeg"})
   ```

2. Or set it programmatically:
   ```python
   from moviepy.config import change_settings
   change_settings({"FFMPEG_BINARY": "ffmpeg"})
   ```

### Running the Script
1. Run the main script for video processing:
   ```bash
   python process_video.py
   ```

2. Example task (cut a clip):
   ```python
   from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
   ffmpeg_extract_subclip("input.mp4", 0, 10, targetname="output.mp4")
   ```

## Troubleshooting
1. **Codec Errors**: Install a full version of FFmpeg with all codecs supported.
2. **Permission Issues**: Ensure FFmpeg binary is executable:
   ```bash
   chmod +x /path/to/ffmpeg
   ```
3. **FFmpeg Not Found**: Verify its location using:
   ```bash
   which ffmpeg
   ```

## Contribution
Contributions are welcome! If you encounter any issues or have feature requests, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

This `README` is structured to be informative for potential users and contributors, explaining the purpose, setup, usage, and troubleshooting of the project.
