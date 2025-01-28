from openai import OpenAI
from dotenv import load_dotenv
import os
import json

def generate_script(idea):
    load_dotenv()
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "You are a creative YouTube Shorts content creator who specializes in creating viral, engaging, family-friendly content."},
            {"role": "user", "content": f"""Create a structured output for a YouTube Short based on this idea: {idea}
            Please provide:
            1. A short, catchy title (2-3 words maximum)
            2. A spoken narrative script (30-60 seconds, only spoken words). End the script with an open-ended question.
            3. Five specific image prompts for AI image generation that match the narrative. 
               Important guidelines for image prompts:
               - Keep all prompts family-friendly and safe for work
               - Avoid violence, weapons, or disturbing content
               - Avoid political or controversial subjects
               - Focus on nature, landscapes, abstract concepts, everyday objects
               - Avoid prompts involving specific people, faces, or human figures
               - Use positive, uplifting imagery
            4. A YouTube Shorts description including relevant hashtags. No emojis. No non-english characters.
            
            Format your response as a JSON object with these keys:
            - title: short catchy title
            - script: the spoken narrative. Only the spoken words. No emojis. No non-english characters. 
            - image_prompts: array of 5 specific image prompts
            - description: YouTube description with hashtags. No non-english characters. No emojis.
            
            Make the title attention-grabbing and relevant to the content.
            Make the image prompts very specific and detailed for best AI generation, no non-english characters. No emojis.
            Keep the script concise and engaging for short-form content.
            Include trending hashtags in the description along with good keywords for SEO optimization."""}
        ],
        max_tokens=1000,
        response_format={ "type": "json_object" }
    )
    
    # Parse the JSON response
    content = json.loads(response.choices[0].message.content)
    return content

if __name__ == "__main__":
    # Test the function
    idea = "A hopeful story about entropy"
    result = generate_script(idea)
    print(json.dumps(result, indent=2))