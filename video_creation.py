import os
import re
from moviepy.config import change_settings
from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip, ColorClip, VideoClip
import numpy as np
from text_to_speech import generate_audio
from datetime import datetime
from image_sourcing import get_images
import random
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.volumex import volumex

# Add this after imports
if os.name == 'nt':  # for Windows
    change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def count_syllables(word):
    # A very basic syllable counting heuristic
    word = word.lower()
    syllables = len(re.findall(r'[aeiouy]+', word))  # Count vowel groups
    syllables -= len(re.findall(r'(?:[^laeiouy]|ed|es|[^laeiouy]e)$', word))  # Subtract silent e's and endings
    return max(1, syllables)  # Ensure at least one syllable

def split_script_by_syllables(script_text, syllables_per_chunk=10):
    words = script_text.split()
    chunks = []
    current_chunk = []
    current_syllable_count = 0

    for word in words:
        syllables = count_syllables(word)
        if current_syllable_count + syllables > syllables_per_chunk and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_syllable_count = syllables
        else:
            current_chunk.append(word)
            current_syllable_count += syllables

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def create_dynamic_image_clip(img_url, duration, width, height):
    """Create an image clip with random pan and zoom effects"""
    img_clip = ImageClip(img_url)
    
    # Calculate resize dimensions to maintain aspect ratio
    aspect_ratio = img_clip.w / img_clip.h
    if aspect_ratio > width/height:  # too wide
        new_h = height
        new_w = int(height * aspect_ratio)
    else:  # too tall
        new_w = width
        new_h = int(width / aspect_ratio)
        
    # Resize image larger than needed to allow for movement
    scale_factor = 1.5  # Scale up by 50% to allow room for movement
    img_clip = img_clip.resize((int(new_w * scale_factor), int(new_h * scale_factor)))
    
    # Randomly choose effect type
    effect_type = random.choice(['zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'pan_up', 'pan_down'])
    
    def get_frame(t):
        progress = t / duration  # 0 to 1
        
        if effect_type == 'zoom_in':
            zoom = 1 - (0.3 * progress)  # Start at 100%, end at 70%
            pos_x = (img_clip.w - width) // 2
            pos_y = (img_clip.h - height) // 2
            
        elif effect_type == 'zoom_out':
            zoom = 0.7 + (0.3 * progress)  # Start at 70%, end at 100%
            pos_x = (img_clip.w - width) // 2
            pos_y = (img_clip.h - height) // 2
            
        elif effect_type == 'pan_left':
            zoom = 1
            pos_x = int((img_clip.w - width) * (1 - progress))
            pos_y = (img_clip.h - height) // 2
            
        elif effect_type == 'pan_right':
            zoom = 1
            pos_x = int((img_clip.w - width) * progress)
            pos_y = (img_clip.h - height) // 2
            
        elif effect_type == 'pan_up':
            zoom = 1
            pos_x = (img_clip.w - width) // 2
            pos_y = int((img_clip.h - height) * (1 - progress))
            
        else:  # pan_down
            zoom = 1
            pos_x = (img_clip.w - width) // 2
            pos_y = int((img_clip.h - height) * progress)
        
        # Apply zoom
        zoomed = img_clip.resize(zoom)
        
        # Ensure we don't go out of bounds
        pos_x = max(0, min(pos_x, zoomed.w - width))
        pos_y = max(0, min(pos_y, zoomed.h - height))
        
        # Crop the frame
        frame = zoomed.crop(x1=pos_x, y1=pos_y, width=width, height=height)
        return frame.get_frame(t)
    
    return VideoClip(get_frame, duration=duration)

def create_video(images, script_text, output_dir, title):
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create filename with timestamp
    output_filename = f"video_{timestamp}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    # Generate audio using OpenAI TTS
    audio_filename = generate_audio(script_text, output_dir)
    voice_clip = AudioFileClip(audio_filename)
    tts_duration = voice_clip.duration

    # Get random background music
    songs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs")
    song_files = [f for f in os.listdir(songs_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
    
    if song_files:
        # Pick a random song
        chosen_song = random.choice(song_files)
        song_path = os.path.join(songs_dir, chosen_song)
        print(f"Using background music: {chosen_song}")
        
        # Load and adjust background music
        background_music = AudioFileClip(song_path)
        
        # Loop the background music if it's shorter than the video
        if background_music.duration < tts_duration:
            loops_needed = int(tts_duration / background_music.duration) + 1
            background_music = CompositeAudioClip([
                background_music.set_start(i * background_music.duration)
                for i in range(loops_needed)
            ])
        
        # Trim background music to video length
        background_music = background_music.set_duration(tts_duration)
        
        # Adjust volumes
        voice_clip = voice_clip.volumex(1.0)  # Keep voice at 100%
        background_music = background_music.volumex(0.1)  # Reduce background to 10%
        
        # Combine audio tracks
        final_audio = CompositeAudioClip([background_music, voice_clip])
    else:
        final_audio = voice_clip
        print("No background music files found in the songs directory.")

    image_duration = 10

    # Set dimensions for YouTube Shorts (9:16 aspect ratio)
    width = 1080
    height = 1920

    # Calculate how many images we need based on audio duration
    total_duration = tts_duration
    clips_needed = int(total_duration / (image_duration - 0.5)) + 1
    
    # Create a loop of images by repeating the list as needed
    looped_images = []
    while len(looped_images) < clips_needed:
        looped_images.extend(images)
    looped_images = looped_images[:clips_needed]  # Trim to exact number needed
    
    # Modify image clips to fit Shorts format with transitions and effects
    clips = []
    transition_duration = 0.5  # Half second transition
    
    for img_url in looped_images:
        # Create dynamic clip with pan/zoom effect
        img_clip = create_dynamic_image_clip(img_url, image_duration, width, height)
        
        # Add fade in and fade out
        img_clip = (img_clip
                   .crossfadein(transition_duration)
                   .crossfadeout(transition_duration))
        
        clips.append(img_clip)
    
    # Overlap the clips slightly to create smooth transitions
    final_clips = []
    for i, clip in enumerate(clips):
        if i > 0:  # Not the first clip
            clip = clip.set_start(i * (image_duration - transition_duration))
        else:  # First clip
            clip = clip.set_start(0)
        final_clips.append(clip)

    # Create base video with transitions
    video = CompositeVideoClip(final_clips, size=(width, height)).set_duration(tts_duration)
    
    # Split script into chunks by syllables
    chunks = split_script_by_syllables(script_text, syllables_per_chunk=10)
    total_chunks = len(chunks)
    chunk_duration = tts_duration / total_chunks  # More precise duration calculation

    # Format text for better visibility in vertical format
    # Break long lines into shorter ones (around 30 chars)
    def format_chunk(text, max_chars=30):
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        return '\n'.join(lines)

    def create_text_clip(chunk, start_time, chunk_duration):
        formatted_text = format_chunk(chunk)
        
        # Add a small delay to text appearance (e.g., 0.2 seconds)
        delayed_start = start_time + 0.2
        
        # Create high-res outline clip with wider canvas
        outline_clip = TextClip(
            formatted_text, 
            fontsize=200,
            color='black',
            font='Verdana-Bold',
            stroke_color='black',
            stroke_width=24,
            size=(width*3, height*2),
            method='caption',
            align='center'
        ).resize(0.27)
        
        # Create high-res text clip with turquoise color
        text_clip = TextClip(
            formatted_text, 
            fontsize=200,
            color='#40E0D0',  # Turquoise color
            font='Verdana-Bold',
            stroke_color='black',
            stroke_width=10,
            size=(width*3, height*2),
            method='caption',
            align='center'
        ).resize(0.27)
        
        # Combine and position
        combined_clip = CompositeVideoClip([outline_clip, text_clip])
        return combined_clip.set_position(('center', 900))\
                          .set_start(delayed_start)\
                          .set_duration(chunk_duration - 0.2)  # Adjust duration to account for delay

    # Create high-res title clips with turquoise color and bigger dimensions
    title_outline = TextClip(
        title,
        fontsize=400,
        color='black',
        font='Verdana-Bold',
        stroke_color='black',
        stroke_width=48,  # Increased outline thickness
        size=(width*3, height*2),
        method='caption',
        align='center'
    ).resize(0.3)  # Increased size from 0.225 to 0.3
    
    title_text = TextClip(
        title,
        fontsize=400,
        color='#40E0D0',  # Turquoise color
        font='Verdana-Bold',
        stroke_color='black',
        stroke_width=20,  # Slightly thicker inner stroke
        size=(width*3, height*2),
        method='caption',
        align='center'
    ).resize(0.3)  # Increased size to match outline
    
    # Combine and position title with fade in and bounce effect
    title_clip = CompositeVideoClip([title_outline, title_text])\
        .set_position(('center', -100))\
        .set_start(0)\
        .set_duration(5)\
        .fadein(0.5)\
        .fadeout(1)  # Fade out over 1 second

    # Optional: Add a semi-transparent black background behind the title
    title_bg = ColorClip(size=(width, 200), color=(0,0,0))\
        .set_opacity(0.3)\
        .set_position(('center', -100))\
        .set_start(0)\
        .set_duration(5)\
        .fadein(0.5)\
        .fadeout(1)

    # Create text clips with more precise timing
    text_clips = []
    for i, chunk in enumerate(chunks):
        start_time = i * chunk_duration
        text_clips.append(create_text_clip(chunk, start_time, chunk_duration))

    # Update final composition to include title background
    final_video = CompositeVideoClip(
        [video] + text_clips + [title_bg, title_clip],
        size=(width, height)
    )
    final_video = final_video.set_audio(final_audio)
    
    # Save with higher quality settings
    final_video.write_videofile(output_path, fps=30, codec='libx264', bitrate="4000k")
    
    # Clean up the audio file after video is created
    os.remove(audio_filename)
    return output_path

if __name__ == "__main__":
    from image_sourcing import get_images
    
    # Create test output directory
    output_dir = os.path.join("output_videos", datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(output_dir, exist_ok=True)
    
    # Get images using image_sourcing
    test_prompts = [
        "sunset beach",
        "mountain landscape", 
        "cityscape at night"
    ]
    images, _ = get_images(test_prompts, output_dir)
    
    script_text = "This is the video script text."
    create_video(images, script_text, output_dir, "Test Title")