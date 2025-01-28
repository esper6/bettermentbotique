from openai import OpenAI
import os

def generate_audio(script_text, output_dir):
    client = OpenAI()
    
    # Available voices: alloy, echo, fable, onyx, nova, shimmer
    audio_path = os.path.join(output_dir, "tts_audio.mp3")
    
    with open(audio_path, 'wb') as f:
        response = client.audio.speech.create(
            model="tts-1",  # or "tts-1-hd" for higher quality
            voice="nova",   # change this to try different voices
            input=script_text
        )
        for chunk in response.iter_bytes():
            f.write(chunk)
    
    return audio_path
