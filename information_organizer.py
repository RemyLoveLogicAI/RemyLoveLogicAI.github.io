"""
This script organizes and presents structured data extracted by other parser scripts
in different text-based formats.
"""

from web_parser import fetch_and_parse_website
from futuretools_parser import extract_tools_from_futuretools
from text_summarizer import summarize_text, summarizer as text_summarizer_pipeline # For pre-initialization check

# Ensure summarizer is available, print warning if not
if text_summarizer_pipeline is None:
    print("Warning: Text summarizer pipeline from text_summarizer.py could not be initialized.")

def format_data_as_list(data: any, source_type: str) -> str:
    """
    Formats extracted data as a human-readable list.

    Args:
        data: The structured data from parsing functions.
              - If source_type is "futuretools", expects a list of tool dictionaries.
              - If source_type is "generic_website", expects a dictionary from fetch_and_parse_website.
        source_type: Either "futuretools" or "generic_website".

    Returns:
        A string containing the formatted list.
    """
    output_lines = []

    if source_type == "futuretools":
        output_lines.append("--- AI Tools (List Format) ---")
        if not data:
            output_lines.append("No tools data provided or tools list is empty.")
        else:
            for i, tool in enumerate(data):
                output_lines.append(f"\nTool {i+1}:")
                output_lines.append(f"  Name: {tool.get('name', 'N/A')}")
                output_lines.append(f"  Website: {tool.get('website_link', 'N/A')}")
        
        # Note: extract_tools_from_futuretools currently doesn't directly return youtube_videos.
        # This would require running fetch_and_parse_website on the FutureTools page itself
        # and then passing that *specific* data here if we want generic YouTube links from that page.
        # For now, this section will assume 'data' might have a 'youtube_videos' key if it were
        # from a direct fetch_and_parse_website call on a futuretools page.
        # However, the primary 'data' for "futuretools" source_type is the list of tool dicts.
        # This part is a bit ambiguous in the prompt if 'data' is *only* the output of extract_tools.
        # Assuming we check if 'data' is a dictionary and has 'youtube_videos' (less likely for futuretools type)
        if isinstance(data, dict) and "youtube_videos" in data:
            youtube_videos = data.get("youtube_videos", [])
            if youtube_videos:
                output_lines.append("\n--- YouTube Videos Found on Page ---")
                for video in youtube_videos:
                    output_lines.append(f"  Title: {video.get('title', 'N/A')}")
                    output_lines.append(f"  URL: {video.get('url', 'N/A')}")

    elif source_type == "generic_website":
        output_lines.append("--- Website Content (List Format) ---")
        if not data:
            output_lines.append("No website data provided.")
            return "\n".join(output_lines)

        links = data.get("links", [])
        if links:
            output_lines.append("\n--- Hyperlinks ---")
            for i, link in enumerate(links[:10]): # Display first 10 links
                output_lines.append(f"  {i+1}. Text: {link.get('text', 'N/A')}")
                output_lines.append(f"     Href: {link.get('href', 'N/A')}")
        else:
            output_lines.append("\nNo hyperlinks extracted.")

        youtube_videos = data.get("youtube_videos", [])
        if youtube_videos:
            output_lines.append("\n--- YouTube Videos ---")
            for i, video in enumerate(youtube_videos):
                output_lines.append(f"  {i+1}. Title: {video.get('title', 'N/A')}")
                output_lines.append(f"     URL: {video.get('url', 'N/A')}")
        else:
            output_lines.append("\nNo YouTube videos identified.")
            
    else:
        return "Invalid source_type provided. Use 'futuretools' or 'generic_website'."

    return "\n".join(output_lines)


def format_data_as_paragraphs(data: any, source_type: str) -> str:
    """
    Formats extracted data as human-readable paragraphs.

    Args:
        data: The structured data.
              - If source_type is "futuretools", expects a list of tool dictionaries.
              - If source_type is "generic_website", expects a dictionary from fetch_and_parse_website.
        source_type: Either "futuretools" or "generic_website".

    Returns:
        A string containing the formatted paragraphs.
    """
    output_paragraphs = []

    if source_type == "futuretools":
        output_paragraphs.append("--- AI Tools (Paragraph Format) ---")
        if not data:
            output_paragraphs.append("No tools data provided or tools list is empty.")
        else:
            for i, tool in enumerate(data):
                name = tool.get('name', 'N/A')
                desc = tool.get('summarized_description') or tool.get('description', 'No description available.')
                website = tool.get('website_link', 'N/A')
                ft_link = tool.get('futuretools_link', 'N/A')
                
                paragraph = f"Tool: {name}\n"
                paragraph += f"Description: {desc}\n"
                paragraph += f"Website: {website}\n"
                if ft_link != 'N/A':
                    paragraph += f"FutureTools Page: {ft_link}\n"
                output_paragraphs.append(paragraph)

    elif source_type == "generic_website":
        output_paragraphs.append("--- Website Content (Paragraph Format) ---")
        if not data:
            output_paragraphs.append("No website data provided.")
            return "\n\n".join(output_paragraphs)

        main_text = data.get("text", "")
        if main_text and text_summarizer_pipeline: # Check if summarizer is working
            summary = summarize_text(main_text, max_length=150, min_length=40)
            output_paragraphs.append(f"Website Summary:\n{summary}")
        elif main_text:
            output_paragraphs.append(f"Website Summary:\n(Summarizer not available or text too short). Full text snippet:\n{main_text[:500]}...")
        else:
            output_paragraphs.append("No main text content extracted to summarize.")

        links = data.get("links", [])
        if links:
            links_paragraph = "Key Hyperlinks Found:\n"
            for i, link in enumerate(links[:5]): # First 5 links
                links_paragraph += f"- {link.get('text', 'N/A')} ({link.get('href', 'N/A')})\n"
            if len(links) > 5:
                links_paragraph += f"...and {len(links)-5} more links."
            output_paragraphs.append(links_paragraph)
        
        youtube_videos = data.get("youtube_videos", [])
        if youtube_videos:
            yt_paragraph = "YouTube Videos Found:\n"
            for video in youtube_videos:
                yt_paragraph += f"- {video.get('title', 'N/A')} ({video.get('url', 'N/A')})\n"
            output_paragraphs.append(yt_paragraph)

    else:
        return "Invalid source_type provided. Use 'futuretools' or 'generic_website'."

    return "\n\n".join(output_paragraphs)


if __name__ == '__main__':
    print("Demonstrating Information Organizer Script...\n")

    # 1. Process data from Futuretools.io
    print("="*30)
    print("Fetching and processing from Futuretools.io...")
    print("="*30)
    # It's possible futuretools.io blocks requests or has complex JS, results might be empty.
    futuretools_data = extract_tools_from_futuretools() # Uses default URL

    if futuretools_data:
        print("\n--- Formatting Futuretools Data as List ---")
        list_output_ft = format_data_as_list(futuretools_data, "futuretools")
        print(list_output_ft)

        print("\n--- Formatting Futuretools Data as Paragraphs ---")
        paragraph_output_ft = format_data_as_paragraphs(futuretools_data, "futuretools")
        print(paragraph_output_ft)
    else:
        print("\nNo data extracted from Futuretools.io. Skipping formatting for it.")
        print("This might be due to website blocking, network issues, or HTML structure changes.")

    # 2. Process data from a generic website (e.g., a blog post)
    print("\n\n" + "="*30)
    print("Fetching and processing from a generic blog post...")
    print("="*30)
    # Using OpenAI blog post as an example - this URL can be changed if it becomes problematic
    generic_url = "https://openai.com/blog/new-models-and-developer-products-announced-at-devday"
    # Fallback if the primary URL fails
    generic_url_fallback = "https://www.gnu.org/philosophy/free-sw.html" 
    
    print(f"Attempting to fetch: {generic_url}")
    generic_website_data = fetch_and_parse_website(generic_url)

    if not generic_website_data:
        print(f"Failed to fetch primary generic URL. Trying fallback: {generic_url_fallback}")
        generic_website_data = fetch_and_parse_website(generic_url_fallback)

    if generic_website_data:
        print("\n--- Formatting Generic Website Data as List ---")
        list_output_generic = format_data_as_list(generic_website_data, "generic_website")
        print(list_output_generic)

        print("\n--- Formatting Generic Website Data as Paragraphs ---")
        paragraph_output_generic = format_data_as_paragraphs(generic_website_data, "generic_website")
        print(paragraph_output_generic)
    else:
        print(f"\nFailed to extract data from both primary and fallback generic URLs. Skipping formatting.")

    print("\n\nInformation Organizer Script demonstration finished.")
```
