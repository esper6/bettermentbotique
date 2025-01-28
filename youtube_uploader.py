from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import os
import json

class YouTubeUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'
        self.CLIENT_SECRETS_FILE = "client_secrets.json"  # You'll need to create this
        self.credentials = None

    def authenticate(self):
        # Load existing credentials if available
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.credentials = pickle.load(token)

        # If no valid credentials available, let user log in
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_FILE, self.SCOPES)
                self.credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)

        return build(self.API_SERVICE_NAME, self.API_VERSION, credentials=self.credentials)

    def upload_video(self, video_path, title, description, tags=None, privacy_status="private"):
        youtube = self.authenticate()
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags if tags else ['#shorts'],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }

        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(
                video_path, 
                chunksize=-1, 
                resumable=True
            )
        )

        print(f"Uploading: {title}")
        response = insert_request.execute()
        video_id = response['id']
        print(f"Upload Complete! Video ID: {video_id}")
        print(f"Video URL: https://youtu.be/{video_id}")
        return video_id

def extract_hashtags(description):
    """Extract hashtags from description text"""
    # Find all words that start with #
    hashtags = [word.strip() for word in description.split() if word.startswith('#')]
    # Remove the # symbol for YouTube API
    tags = [tag[1:] for tag in hashtags]
    return tags

def upload_to_youtube(video_path, content_dir, privacy_status="private"):
    """Helper function to upload a video using content from its directory"""
    
    # Load content.json for title and description
    with open(os.path.join(content_dir, "content.json"), 'r') as f:
        content = json.load(f)
    
    # Load description and extract hashtags
    with open(os.path.join(content_dir, "social_description.txt"), 'r') as f:
        description = f.read()
    
    # Extract hashtags for tags
    tags = extract_hashtags(description)
    print(f"Using tags: {tags}")

    # Initialize uploader and upload video
    uploader = YouTubeUploader()
    try:
        video_id = uploader.upload_video(
            video_path=video_path,
            title=content['title'],
            description=description,
            tags=tags,
            privacy_status=privacy_status  # Use the provided privacy status
        )
        return video_id
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    video_dir = "output_videos/20240321_143022"
    video_path = os.path.join(video_dir, "video_20240321_143022.mp4")
    upload_to_youtube(video_path, video_dir) 