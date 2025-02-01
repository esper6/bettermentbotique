How to run in different modes:

1. Full Mode (Generate everything):
python main.py --mode full --idea "Your creative idea here"

Example:
python main.py --mode full --idea "The fascinating science behind why cats always land on their feet"

2. Video Only Mode (Create new video from existing content):
python main.py --mode video-only --folder output_videos/20240321_143022

3. Script Only Mode (Generate script without images):
python main.py --mode script-only --idea "Your creative idea here"

4. Image Only Mode (Generate images from existing script):
python main.py --mode image-only --folder output_videos/20240321_143022

5. Upload Only Mode (Upload existing video from folder):
python main.py --mode upload-only --folder output_videos/20240321_143022

Optional Parameters:
--upload    Add this flag to automatically upload the video after creation
            (Only works with full and video-only modes)
--privacy   Set the privacy status for YouTube upload
            Options: private (default), public, unlisted
--platform  Choose platform to upload to
            Options: youtube (default), instagram, all

Examples:
# Generate and upload in one go
python main.py --mode full --idea "Why superfoods are good for us" --upload

# Upload existing video from folder (uses newest video file)
python main.py --mode upload-only --folder output_videos/20240321_143022

# Upload as public video to YouTube
python main.py --mode upload-only --folder output_videos/20240321_143022 --privacy public

# Upload to Instagram only
python main.py --mode upload-only --folder output_videos/20240321_143022 --platform instagram

# Upload to both YouTube and Instagram
python main.py --mode upload-only --folder output_videos/20240321_143022 --platform all

Notes:
- For full mode and script-only mode, the --idea argument is required
- For video-only, image-only, and upload-only modes, the --folder argument should point to a timestamped directory
- Upload-only mode will automatically find the newest video file in the specified folder
- YouTube uploads will be private by default for review
- Instagram credentials must be set in .env file (INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD)
- The content.json file in each folder is used for video title, description, and tags

Copy/paste:
python main.py --mode full --idea ""
python main.py --mode video-only --folder output_videos/
python main.py --mode script-only --idea ""
python main.py --mode image-only --folder output_videos/
python main.py --mode upload-only --folder output_videos/ --privacy public
python main.py --mode upload-only --folder output_videos/ --platform instagram
python main.py --mode upload-only --folder output_videos/ --platform all

python main.py --mode script-only --idea "Sleep benefits"
python main.py --mode image-only --folder output_videos\20250131_034411
python main.py --mode video-only --folder output_videos\20250131_034411
python main.py --mode upload-only --folder output_videos\20250131_034411 --privacy public

Privacy and Terms:
https://esper6.github.io/bettermentbotique.github.io/
https://esper6.github.io/bettermentbotique.github.io/terms