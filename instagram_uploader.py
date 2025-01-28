import os
import json
from instagrapi import Client
from time import sleep

class InstagramUploader:
    def __init__(self):
        self.client = Client()
        self._logged_in = False
        
    def login(self, username=None, password=None):
        """Login to Instagram"""
        # Try to get credentials from environment variables if not provided
        if not username:
            username = os.getenv('INSTAGRAM_USERNAME')
        if not password:
            password = os.getenv('INSTAGRAM_PASSWORD')
            
        if not username or not password:
            raise ValueError("Instagram credentials not found. Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env file")
        
        print("Logging into Instagram...")
        try:
            self.client.login(username, password)
            self._logged_in = True
            print("Successfully logged into Instagram")
        except Exception as e:
            print(f"Failed to login to Instagram: {str(e)}")
            self._logged_in = False
        
    def upload_reel(self, video_path, caption):
        """Upload a video as an Instagram Reel"""
        try:
            if not self._logged_in:
                self.login()
                
            print(f"Uploading video to Instagram: {os.path.basename(video_path)}")
            
            # Upload the video as a reel
            media = self.client.clip_upload(
                video_path,
                caption=caption,
                extra_data={
                    "custom_accessibility_caption": "",
                    "like_and_view_counts_disabled": False,
                    "disable_comments": False
                }
            )
            
            if media:
                print("Successfully uploaded to Instagram!")
                print(f"Post URL: https://www.instagram.com/p/{media.code}/")
                return True
            else:
                print("Failed to upload to Instagram")
                return False
                
        except Exception as e:
            print(f"Error uploading to Instagram: {str(e)}")
            return False
        
def upload_to_instagram(video_path, content_dir):
    """Helper function to upload a video using content from its directory"""
    
    # Load content.json for caption
    with open(os.path.join(content_dir, "content.json"), 'r') as f:
        content = json.load(f)
    
    # Load description
    with open(os.path.join(content_dir, "social_description.txt"), 'r') as f:
        description = f.read()

    # Initialize uploader and upload video
    uploader = InstagramUploader()
    try:
        success = uploader.upload_reel(
            video_path=video_path,
            caption=description
        )
        return success
    except Exception as e:
        print(f"Instagram upload failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    video_dir = "output_videos/20240321_143022"
    video_path = os.path.join(video_dir, "video_20240321_143022.mp4")
    upload_to_instagram(video_path, video_dir) 