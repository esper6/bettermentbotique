from script_generation import generate_script
from image_sourcing import get_images
from video_creation import create_video
from text_to_speech import generate_audio
from datetime import datetime
import os
import json
import argparse
from youtube_uploader import upload_to_youtube
from instagram_uploader import upload_to_instagram

def create_output_directory():
    # Get the base directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create main output directory if it doesn't exist
    output_base = os.path.join(base_dir, "output_videos")
    os.makedirs(output_base, exist_ok=True)
    
    # Create timestamped subdirectory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_base, timestamp)
    os.makedirs(output_dir)
    
    return output_dir

def load_existing_content(folder_path):
    content_path = os.path.join(folder_path, "content.json")
    with open(content_path, 'r') as f:
        return json.load(f)

def get_newest_video(folder_path):
    """Find the newest video file in the specified folder"""
    video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.mov', '.avi'))]
    if not video_files:
        raise ValueError(f"No video files found in {folder_path}")
    
    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
    return os.path.join(folder_path, video_files[0])

def append_transparency_clause(description):
    """Add transparency clause to the end of the description"""
    transparency_clause = "\nThis video was created with AI assistance. Learn more about the process: https://github.com/esper6/bettermentbotique"
    return description + transparency_clause

def main():
    parser = argparse.ArgumentParser(description='Social Media Video Generator')
    parser.add_argument('--mode', 
                       choices=['full', 'video-only', 'script-only', 'image-only', 'upload-only'],
                       default='full',
                       help='full: generate everything, video-only: create new video from existing content, '
                            'script-only: generate script only, image-only: generate images from existing script, '
                            'upload-only: upload existing video from folder')
    parser.add_argument('--folder', help='Path to existing timestamped folder')
    parser.add_argument('--idea', help='Idea for the video (required for full and script-only mode)', default=None)
    parser.add_argument('--upload', action='store_true', 
                       help='Upload the video to YouTube after creation')
    parser.add_argument('--privacy', 
                       choices=['private', 'public', 'unlisted'],
                       default='private',
                       help='Privacy status for YouTube upload')
    parser.add_argument('--platform', 
                       choices=['youtube', 'instagram', 'all'],
                       default='youtube',
                       help='Platform to upload to (youtube, instagram, or all)')
    args = parser.parse_args()

    # Add upload-only mode
    if args.mode == 'upload-only':
        if not args.folder:
            raise ValueError("For upload-only mode, you must provide --folder")
        
        video_path = get_newest_video(args.folder)
        print(f"\nFound newest video: {video_path}")
        
        if args.platform in ['youtube', 'all']:
            video_id = upload_to_youtube(video_path, args.folder, privacy_status=args.privacy)
            if video_id:
                print(f"YouTube upload successful! Video ID: {video_id}")
        
        if args.platform in ['instagram', 'all']:
            if upload_to_instagram(video_path, args.folder):
                print("Instagram upload successful!")
        return

    if args.mode in ['full', 'script-only']:
        if not args.idea:
            raise ValueError("For full and script-only modes, --idea argument is required")
        
        print(f"\nGenerating content for idea: {args.idea}")
        output_dir = create_output_directory()
        
        # Generate script and content
        content = generate_script(args.idea)
        
        # Add transparency clause to description
        content['description'] = append_transparency_clause(content['description'])
        
        print("\nGenerated Content:")
        print(json.dumps(content, indent=2))
        
        # Save content to JSON
        with open(os.path.join(output_dir, "content.json"), "w") as f:
            json.dump(content, f, indent=4)
            
        # Save description separately for easy access
        with open(os.path.join(output_dir, "social_description.txt"), "w") as f:
            f.write(content['description'])
            
        if args.mode == 'script-only':
            print(f"\nScript generation complete! Files saved in: {output_dir}")
            return
        
        # Continue with full mode
        images, sources_path = get_images(content['image_prompts'], output_dir)
        
    elif args.mode == 'image-only':
        if not args.folder:
            raise ValueError("For image-only mode, you must provide --folder pointing to a timestamped directory")
        
        # Load existing content
        content = load_existing_content(args.folder)
        images, sources_path = get_images(content['image_prompts'], args.folder)
        return
        
    elif args.mode == 'video-only':
        if not args.folder:
            raise ValueError("For video-only mode, you must provide --folder pointing to a timestamped directory")
        
        # Load existing content
        content = load_existing_content(args.folder)
        output_dir = args.folder
        
        # Get list of existing images
        images_dir = os.path.join(args.folder, "images")
        images = [os.path.join(images_dir, f) for f in sorted(os.listdir(images_dir)) 
                 if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        print(f"Loaded {len(images)} images from {images_dir}")
    
    # Create video for full and video-only modes
    if args.mode in ['full', 'video-only']:
        video_path = create_video(
            images=images, 
            script_text=content['script'], 
            output_dir=output_dir,
            title=content['title']
        )
        print("\nVideo created successfully")
        print("Video saved to:", video_path)
        
        # Save social media description with more generic name
        description_path = os.path.join(output_dir, "social_description.txt")
        with open(description_path, "w") as f:
            f.write(content['description'])
        print("\nSocial media description saved to:", description_path)
        
        print(f"\nAll files saved in: {output_dir}")
        
        if args.upload:
            print("\nUploading to YouTube...")
            video_id = upload_to_youtube(video_path, output_dir)
            if video_id:
                print(f"Upload successful! Video ID: {video_id}")
    
    # Step 4 (Optional): Add audio
    # generate_audio(content['script'])

if __name__ == "__main__":
    main()
