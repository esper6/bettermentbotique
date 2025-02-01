# BettermentBotique

An AI-powered app that generates educational social media videos. This tool helps create informative content by:
- Generating educational scripts
- Sourcing relevant images
- Creating voice-overs
- Assembling videos with dynamic effects
- Uploading to multiple social media platforms

## How It Works

1. Takes a simple idea/topic as input
2. Uses AI to generate an educational script
3. Sources appropriate images
4. Converts text to speech
5. Creates a video with Ken Burns effects
6. Can upload directly to YouTube and Instagram

## Transparency

All videos created with this tool are:
- AI-assisted in script generation
- Using AI-generated voice-overs
- Properly sourced images
- Clearly marked as AI-assisted content

## Social Media Channels

- YouTube: [Your Channel]
- Instagram: [Your Handle]
- TikTok: [Your Handle]

##How to run in different modes:

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

##Notes:
- For full mode and script-only mode, the --idea argument is required
- For video-only, image-only, and upload-only modes, the --folder argument should point to a timestamped directory
- Upload-only mode will automatically find the newest video file in the specified folder
- YouTube uploads will be private by default for review
- Instagram credentials must be set in .env file (INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD)
- The content.json file in each folder is used for video title, description, and tags

## Privacy & Terms

- [Privacy Policy](https://esper6.github.io/bettermentbotique.github.io/)
- [Terms of Service](https://esper6.github.io/bettermentbotique.github.io/terms) 