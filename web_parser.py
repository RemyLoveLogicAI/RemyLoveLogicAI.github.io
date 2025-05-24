"""
This script defines a function to fetch and parse a website's content.

Note: This script requires the 'requests' and 'beautifulsoup4' libraries.
You can install them using pip:
  pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup

def fetch_and_parse_website(url: str) -> dict:
    """
    Fetches the HTML content of a given URL, parses it, and extracts text and links.

    Args:
        url: The URL of the website to parse.

    Returns:
        A dictionary containing:
            - "text": The extracted human-readable text content as a single string.
            - "links": A list of dictionaries, where each dictionary has "text" 
                       (anchor text) and "href" (the URL) for each link.
                       Returns None if an error occurs.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract human-readable text content
    # Attempt to get main content by looking for common tags,
    # this is a simple heuristic and might need refinement.
    text_parts = []
    for element in soup.find_all(['p', 'article', 'main', 'div']):
        # Avoid common boilerplate sections by checking class names or ids (very basic)
        if any(term in element.get('class', []) for term in ['header', 'footer', 'nav', 'menu', 'sidebar', 'advertisement', 'banner', 'popup']):
            continue
        if any(term in element.get('id', '') for term in ['header', 'footer', 'nav', 'menu', 'sidebar', 'advertisement', 'banner', 'popup']):
            continue
        
        text = element.get_text(separator=' ', strip=True)
        if text:
            text_parts.append(text)
    
    # A more robust way to get main content might involve looking for <main> tag first
    main_content = soup.find('main')
    if main_content:
        extracted_text = main_content.get_text(separator=' ', strip=True)
    elif text_parts: # Fallback to collected text parts if <main> is not found or empty
        extracted_text = " ".join(text_parts)
    else: # Further fallback if no specific main content or p/article/div text found
        # Try to remove script and style elements and then get text
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose() # Remove these tags
        extracted_text = soup.get_text(separator=' ', strip=True)


    # Extract all hyperlinks
    links = []
    youtube_videos = [] # Initialize list for YouTube videos

    for link in soup.find_all('a', href=True):
        anchor_text = link.get_text(strip=True)
        href = link['href']
        
        if href and (href.startswith('http://') or href.startswith('https://')):
            links.append({"text": anchor_text, "href": href})
            
            # Check for YouTube links
            if "youtube.com/watch?v=" in href or "youtu.be/" in href:
                youtube_videos.append({
                    "url": href,
                    "title": anchor_text, # Using anchor text as title for now
                    "retrieved_from_url": url 
                })

    return {
        "text": extracted_text,
        "links": links,
        "youtube_videos": youtube_videos, # Add YouTube videos to the output
        "soup": soup # Add the BeautifulSoup object itself
    }

if __name__ == '__main__':
    # Example usage:
    # test_url_simple = "http://example.com" 
    # test_url_google = "https://google.com" # Might be blocked by CAPTCHA or terms of service
    test_url_complex = "https://www.gnu.org/software/bash/manual/bash.html" # A page with many links
    # A page that is likely to have YouTube links (e.g., a blog post or a specific Wikipedia article)
    # Using a search results page for "python tutorial for beginners youtube" as an example.
    # This is for demonstration; actual content may vary and be less stable.
    # A better test would be a self-hosted page or a very stable known page with YouTube embeds.
    test_url_with_youtube = "https://www.youtube.com/results?search_query=python+tutorial+for+beginners" # Example, actual parsing might be complex
    # Let's try a simpler page that might embed a YouTube video or link to one.
    # For instance, many blogs or news articles do.
    # I will use a known page that is less likely to change dramatically for testing.
    # Example: A page from a blog that often embeds YouTube videos
    test_url_blog_with_video = "https://openai.com/blog/new-models-and-developer-products-announced-at-devday" # This page often has videos embedded or linked

    test_urls_to_check = [test_url_complex, test_url_blog_with_video]

    for test_url in test_urls_to_check:
        print(f"\n{'='*20} Fetching and parsing {test_url} {'='*20}")
        parsed_data = fetch_and_parse_website(test_url)

        if parsed_data:
            print("\n--- Extracted Text (Snippet) ---")
            print(parsed_data["text"][:300] + "..." if parsed_data["text"] else "No text found.")
            
            print("\n--- Extracted Links (First 3) ---")
            if parsed_data["links"]:
                for link_data in parsed_data["links"][:3]:
                    print(f"  Text: {link_data['text']}, Href: {link_data['href']}")
            else:
                print("No links found.")

            print("\n--- Extracted YouTube Videos ---")
            if parsed_data.get("youtube_videos"):
                if parsed_data["youtube_videos"]:
                    for video_data in parsed_data["youtube_videos"][:3]: # Print first 3 found
                        print(f"  Title: {video_data['title']}")
                        print(f"  URL: {video_data['url']}")
                        print(f"  Retrieved from: {video_data['retrieved_from_url']}\n")
                else:
                    print("No YouTube videos found on this page.")
            else:
                print("No 'youtube_videos' key in parsed data (this shouldn't happen if function is correct).")

            # Confirm presence of soup object
            if parsed_data.get("soup"):
                print("\n--- BeautifulSoup Object ---")
                print("Soup object successfully included in the output.")
            else:
                print("\n--- BeautifulSoup Object ---")
                print("Error: Soup object NOT found in the output.")
            
            # To verify, you might want to write to files:
            # with open(f"extracted_text_{test_url.split('/')[-1] or 'default'}.txt", "w", encoding="utf-8") as f:
            #     f.write(parsed_data["text"])
            # import json
            # with open(f"extracted_links_{test_url.split('/')[-1] or 'default'}.json", "w", encoding="utf-8") as f:
            #     json.dump(parsed_data, f, indent=2) # Save all parsed data
            # print(f"\nFull parsed data saved for {test_url}")

        else:
            print(f"Failed to retrieve or parse website: {test_url}")
