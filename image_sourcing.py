from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
from moviepy.editor import ImageClip
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

def get_images(prompts, output_dir):
    # Load environment variables
    load_dotenv()
    client = OpenAI()
    
    image_paths = []
    
    # Create output directory for sources and images
    os.makedirs(output_dir, exist_ok=True)
    sources_path = os.path.join(output_dir, "image_sources.txt")
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    print("\nStarting image generation process...")
    
    with open(sources_path, "w") as f:
        f.write("Image Prompts and Sources:\n")
        f.write("=" * 50 + "\n\n")
        
        # Process each prompt
        for i, prompt in enumerate(prompts, 1):
            try:
                print(f"\nGenerating image {i} of {len(prompts)}...")
                print(f"Prompt: {prompt}")
                
                # Enhance prompt to specify vertical orientation
                enhanced_prompt = f"""Create a vertical portrait image in 9:16 aspect ratio. 
                The image should be optimized for vertical phone screens, with the main subject centered vertically. 
                Important: Must be in portrait orientation (taller than wide). {prompt}"""
                
                # Generate image using DALL-E
                print("Calling DALL-E API...")
                start_time = datetime.now()
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=enhanced_prompt,
                    size="1024x1792",  # Portrait mode ratio
                    quality="standard",
                    n=1,
                )
                
                # Get the image URL
                image_url = response.data[0].url
                print(f"Image generated in {(datetime.now() - start_time).total_seconds():.1f} seconds")
                
                # Download the image
                print("Downloading image...")
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                
                # Save the image temporarily
                temp_image_path = os.path.join(images_dir, f"temp_{i}.png")
                with open(temp_image_path, "wb") as img_file:
                    img_file.write(img_response.content)
                
                # Check orientation using moviepy
                clip = ImageClip(temp_image_path)
                width, height = clip.size
                
                # Final image path
                image_filename = f"image_{i}.png"
                image_path = os.path.join(images_dir, image_filename)
                
                # Write prompt and source to file
                f.write(f"Image {i}:\n")
                f.write(f"Original Prompt: {prompt}\n")
                f.write(f"Enhanced Prompt: {enhanced_prompt}\n")
                f.write(f"Saved as: {image_filename}\n")
                f.write(f"Dimensions: {width}x{height}\n\n")
                
                # Move temp file to final location
                os.rename(temp_image_path, image_path)
                image_paths.append(image_path)
                
                print(f"✓ Image saved to: {image_path}")
                print(f"Dimensions: {width}x{height}")
                
                # Log warning if image isn't in portrait mode
                if width > height:
                    print(f"⚠ Warning: Image {i} was generated in landscape orientation ({width}x{height})")
            
            except Exception as e:
                print(f"❌ Error generating image for prompt {i}: {e}")
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
    
    print(f"\nImage generation complete! Generated {len(image_paths)} images")
    print(f"Image sources saved to: {sources_path}")
    return image_paths, sources_path

# Example usage
if __name__ == "__main__":
    # Define your prompts here
    prompts = ["sunset beach", "mountain landscape", "cityscape at night"]
    output_dir = os.path.join("output_videos", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    images, sources_path = get_images(prompts, output_dir)
    print("Retrieved image paths:")
    for img_path in images:
        print(img_path)
    print("\nSources saved to:", sources_path)
