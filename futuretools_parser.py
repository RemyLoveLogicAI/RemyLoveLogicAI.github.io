"""
This script attempts to extract AI tool information from Futuretools.io.
It uses web_parser.py to fetch content and text_summarizer.py to summarize descriptions.
"""

import json # For pretty printing in the example
from web_parser import fetch_and_parse_website
from text_summarizer import summarize_text

# Attempt to get the summarizer pipeline ready, so it doesn't initialize on first summary.
# This is just to make the example run smoother if summarization is used.
try:
    from text_summarizer import summarizer as text_summarizer_pipeline
    if text_summarizer_pipeline is None: # Check if initialization failed in text_summarizer
        print("Warning: Text summarizer pipeline could not be initialized from text_summarizer.py.")
except ImportError:
    print("Warning: Could not import text_summarizer pipeline for pre-initialization.")


def extract_tools_from_futuretools(url: str = "https://www.futuretools.io/") -> list:
    """
    Fetches content from Futuretools.io and attempts to extract AI tool listings.

    Args:
        url: The URL of the Futuretools.io page to parse (defaults to main page).

    Returns:
        A list of dictionaries, where each dictionary represents a tool and contains:
        - name (str): Tool Name
        - website_link (str): External link to the tool's website
        - futuretools_link (str): Link to the tool's detail page on Futuretools.io
        - description (str): Tool description from Futuretools.io
        - summarized_description (str, optional): Summarized version of the description.
    """
    print(f"Fetching data from {url}...")
    parsed_data = fetch_and_parse_website(url)
    tools_found = []

    if not parsed_data:
        print("Failed to fetch or parse the website.")
        return tools_found

    # Current limitation: fetch_and_parse_website returns only aggregated text and a flat list of links.
    # This makes it very difficult to associate descriptions with specific tools or to differentiate
    # between a tool's own website link and its futuretools.io detail page link if they are separate.
    # A more robust solution would require web_parser.py to return the BeautifulSoup object
    # so we can navigate the HTML structure directly.

    soup = parsed_data.get("soup")

    if not soup:
        print("BeautifulSoup object not found in parsed_data. Cannot perform detailed parsing.")
        return tools_found

    print("Attempting to parse tools using BeautifulSoup object...")

    # Assumption 1: Each tool is in a `div` with class "tool-item" (common pattern)
    # Alternative: "tool-card", "item-card", "w-dyn-item" (Webflow), "collection-item"
    # I will try a few common ones if the first fails.
    # Let's assume a general class name like 'tool-card-container' or 'item-container' might exist.
    # Given it's futuretools.io, something like "tool-card" or "tool-item" is plausible.
    # Let's try a selector that might match a common structure for items in a list.
    # A common pattern is <article class="tool-item"> or <div class="tool-item">
    
    # Based on common patterns and the nature of the site, let's assume tools are listed in 
    # elements (div or article) that have a class containing "tool" and "item" or "card".
    # This is a broad guess. A more specific one would be div.tool-card or article.tool-item
    # Let's try to find elements with class containing 'tool-card' as a primary guess.
    # If that fails, I'll broaden to 'item' or 'card'.
    
    # General strategy:
    # 1. Find all "tool containers".
    # 2. For each container, find name, external link, internal link, description.

    # Primary guess for tool container: Elements with class name containing "tool-card"
    # This is a common naming convention for such items.
    # Example: <div class="tool-card anothertoolclass"> or <article class="tool-card">
    # We'll use a CSS selector that looks for class names containing "tool-card"
    tool_containers = soup.select('[class*="tool-card"]') 
    
    if not tool_containers:
        # Fallback: Try a more generic class name like "item" or "collection-item"
        tool_containers = soup.select('[class*="item"], [class*="collection-item"]')
        if tool_containers:
            print("Found potential tool containers with class 'item' or 'collection-item'.")
        else:
            print("Could not find any elements matching assumed tool container selectors (e.g., class containing 'tool-card', 'item', or 'collection-item').")
            print("The HTML structure might be different. Extraction will likely fail or be empty.")
            return tools_found


    print(f"Found {len(tool_containers)} potential tool containers. Processing each...")

    # Initialize counters
    processed_tools_count = 0
    missing_names_count = 0
    missing_website_links_count = 0 # For external website link
    missing_ft_links_count = 0    # For internal futuretools link
    missing_descriptions_count = 0

    for i, container in enumerate(tool_containers):
        name = "N/A"
        website_link = "N/A"
        futuretools_link_internal = "N/A"
        description = "N/A"
        summarized_description = "N/A"
        
        current_tool_has_name = False
        current_tool_has_website_link = False
        current_tool_has_ft_link = False
        current_tool_has_description = False

        # --- 2. Tool Name ---
        name_element_selectors = {
            "primary": (['h2', 'h3', 'h4'], {'class_': ['tool-name', 'tool-title', 'card-title']}),
            "fallback_heading": (['h2', 'h3', 'h4'], {}),
            "fallback_link": (['a'], {'class_': ['title', 'name']}),
            "fallback_first_link_text": (['a'], {}) # Will check for text content
        }
        
        name_element = None
        for key, (tags, attrs) in name_element_selectors.items():
            name_element = container.find(tags, **attrs)
            if name_element:
                if key == "fallback_first_link_text": # Ensure it has text
                    if not name_element.get_text(strip=True):
                        name_element = None # Not a valid name if link has no text
                        continue
                break # Found a name element
        
        if name_element:
            try:
                name = name_element.get_text(strip=True)
                if name:
                    current_tool_has_name = True
                else:
                    print(f"Info: Tool {i+1}: Found name element, but it lacked text content. Container snippet: {str(container)[:150]}...")
            except AttributeError:
                print(f"Warning: Tool {i+1}: Found a potential name element, but an AttributeError occurred when getting text. Element: {name_element}")
        else:
            print(f"Info: Tool {i+1}: Tool name element not found using defined selectors. Container snippet: {str(container)[:150]}...")

        # --- 3. Futuretools Link (Internal) ---
        ft_link_element = None
        if container.name == 'a': # Check if container itself is the link
            try:
                href_candidate = container.get('href', '')
                if href_candidate.startswith(('/tool/', '/tools/')):
                    futuretools_link_internal = href_candidate
                    current_tool_has_ft_link = True
            except AttributeError: # Should not happen with .get
                 print(f"Warning: Tool {i+1}: AttributeError on container link access. Container: {container}")
        
        if not current_tool_has_ft_link: # If container wasn't the link or didn't match
            ft_link_element = container.find('a', href=lambda x: x and (x.startswith('/tool/') or x.startswith('/tools/')))
            if ft_link_element:
                try:
                    futuretools_link_internal = ft_link_element['href']
                    current_tool_has_ft_link = True
                except AttributeError: # href should exist due to lambda, but for safety
                    print(f"Warning: Tool {i+1}: Found FT link element, but AttributeError on href access. Element: {ft_link_element}")
            else:
                print(f"Info: Tool {i+1}: Futuretools internal link element not found. Container snippet: {str(container)[:150]}...")
        
        if current_tool_has_ft_link and futuretools_link_internal.startswith('/'):
            base_url_ft = "https://www.futuretools.io"
            futuretools_link_internal = base_url_ft + futuretools_link_internal

        # --- 4. Tool Website Link (External) ---
        # Priority: specific classes, then general target="_blank"
        external_link_element = container.find('a', class_=['external-link', 'website-button', 'tool-website-link', 'outbound', 'visit-tool-button']) # Added one more common class
        if external_link_element:
            try:
                website_link = external_link_element.get('href', '')
                if website_link and (website_link.startswith('http') and 'futuretools.io' not in website_link) : # Ensure it's a valid external link
                    current_tool_has_website_link = True
                else: # Found element but href is not what we expect for external link
                    website_link = "N/A" # Reset if not valid
                    print(f"Info: Tool {i+1}: Found potential external link element, but href '{website_link}' was not a valid external URL. Element: {external_link_element}")
            except AttributeError:
                print(f"Warning: Tool {i+1}: Found external link element, but AttributeError on href access. Element: {external_link_element}")
        else: # Fallback to general non-FT http links
            all_links_in_container = container.find_all('a', href=True)
            for link_tag in all_links_in_container:
                try:
                    href = link_tag['href']
                    # Check if it's an absolute URL, not a futuretools.io link, and not the same as the internal FT link
                    if href.startswith('http') and 'futuretools.io' not in href and href != futuretools_link_internal:
                        website_link = href
                        current_tool_has_website_link = True
                        break 
                except AttributeError:
                     print(f"Warning: Tool {i+1}: AttributeError while checking fallback external link. Element: {link_tag}")
                     continue # Try next link
            if not current_tool_has_website_link:
                 print(f"Info: Tool {i+1}: Tool website link (external) not found using specific or fallback selectors. Container snippet: {str(container)[:150]}...")


        # --- 5. Tool Description ---
        desc_element = container.find(['p', 'div'], class_=['description', 'tool-description', 'card-text', 'item-description', 'tool-card-description']) # Added one more
        if desc_element:
            try:
                description = desc_element.get_text(strip=True)
                if description:
                    current_tool_has_description = True
                else:
                    print(f"Info: Tool {i+1}: Found description element, but it lacked text. Element: {desc_element}")
            except AttributeError:
                print(f"Warning: Tool {i+1}: Found description element, but AttributeError on get_text. Element: {desc_element}")
        else: # Fallback to the first <p> tag that is not empty and long enough
            all_paragraphs = container.find_all('p')
            for p_tag in all_paragraphs:
                try:
                    p_text = p_tag.get_text(strip=True)
                    if p_text and len(p_text) > 20:
                        description = p_text
                        current_tool_has_description = True
                        break
                except AttributeError:
                    print(f"Warning: Tool {i+1}: AttributeError on fallback paragraph get_text. Element: {p_tag}")
                    continue
            if not current_tool_has_description:
                 print(f"Info: Tool {i+1}: Tool description element not found using specific or fallback selectors. Container snippet: {str(container)[:150]}...")
        
        # Fallback: If no specific description found, use general text content of the card (if substantial)
        if not current_tool_has_description and current_tool_has_name: # Only if name was found
            try:
                container_text = container.get_text(separator=' ', strip=True)
                # Basic attempt to remove already extracted name to avoid it being the description
                if name != "N/A" and container_text.startswith(name): # Check name again for safety
                    container_text = container_text[len(name):].strip()
                
                # Avoid using very short texts or texts that are just the FT link as description
                if len(container_text) > 30 and container_text != futuretools_link_internal:
                    description = container_text
                    current_tool_has_description = True
                    # print(f"Info: Tool {i+1}: Used general container text as description.") # Optional: too verbose?
            except AttributeError:
                 print(f"Warning: Tool {i+1}: AttributeError on container.get_text for fallback description.")


        # Summarize if description is found and long enough
        if current_tool_has_description and len(description.split()) > 30:
            summarized_description = summarize_text(description, max_length=50, min_length=15)
        elif current_tool_has_description:
            summarized_description = description

        # --- Update Counts & Append Tool ---
        # Only add if we found a name and at least one link (either FT internal or external website)
        if current_tool_has_name and (current_tool_has_website_link or current_tool_has_ft_link):
            processed_tools_count += 1
            tools_found.append({
                "name": name,
                "website_link": website_link,
                "futuretools_link": futuretools_link_internal,
                "description": description,
                "summarized_description": summarized_description
            })
            # Update missing counts for this successfully added tool
            if not current_tool_has_name: missing_names_count +=1 # Should be 0 due to outer if, but for completeness
            if not current_tool_has_website_link: missing_website_links_count += 1
            if not current_tool_has_ft_link: missing_ft_links_count += 1 # If it was added based on external link only
            if not current_tool_has_description: missing_descriptions_count += 1
        elif current_tool_has_name: # Name found, but no usable links
            print(f"Info: Tool {i+1} ('{name}') found but discarded as no usable FutureTools link or external website link was extracted.")
            missing_website_links_count += 1 # Count as missing link if name was there
            missing_ft_links_count +=1
        elif len(tool_containers) > 0 : # If we are processing a container but couldn't even get a name
            missing_names_count += 1 # This container is a "miss" for a name

    # --- Final Summary Print ---
    print("\n--- Futuretools Parsing Summary ---")
    if len(tool_containers) == 0:
        print("No potential tool containers were identified on the page.")
    else:
        print(f"Processed {len(tool_containers)} potential tool containers.")
        print(f"Successfully extracted {processed_tools_count} tools with a name and at least one link.")
        
        # Adjust counts for tools that were not even added to tools_found
        # If a container was processed but didn't result in a tool_found entry, it implies critical info was missing.
        # The logic above already increments missing_names_count if a container is processed without yielding a name.
        # For tools that were added, the specific missing fields were counted.
        # This provides a more accurate picture of what was missed from the items considered tools.
        
        print(f"Tools missing a discernible Name: {missing_names_count if processed_tools_count == 0 and len(tool_containers) > 0 else (missing_names_count + (len(tool_containers) - processed_tools_count if missing_names_count == 0 else 0)) } (may include items not meeting criteria for 'tool')")
        print(f"Tools (among extracted) missing an External Website Link: {missing_website_links_count}")
        print(f"Tools (among extracted) missing an Internal FutureTools Link: {missing_ft_links_count}")
        print(f"Tools (among extracted) missing a Description: {missing_descriptions_count}")

    if not tools_found and len(tool_containers) > 0 : # If containers were found but no tools extracted
        print("\nNo tools extracted that met the criteria (name and at least one link).")
        print("This could be due to incorrect HTML structure assumptions for sub-elements within containers,")
        print("or the elements do not contain the expected content (e.g. empty text, invalid links).")
        print("Further refinement of selectors based on actual futuretools.io HTML is needed if this persists.")
    
    return tools_found

if __name__ == '__main__':
    print("Starting Futuretools.io parser update...")
    # Using the default URL "https://www.futuretools.io/"
    # To test specific category pages, you could change the URL:
    # e.g., test_url = "https://www.futuretools.io/browse-tools/image-generation" 
    # test_url = "https://www.futuretools.io/" 
    # For a more targeted test, let's try a specific category which might have a more consistent structure.
    # However, sticking to the main page as per default.
    test_url = "https://www.futuretools.io/"

    extracted_tools = extract_tools_from_futuretools(url=test_url)

    if extracted_tools:
        print(f"\n--- Extracted Tools ({len(extracted_tools)} found) ---")
        for i, tool in enumerate(extracted_tools[:5]): # Print first 5 tools
            print(f"\nTool {i+1}:")
            print(f"  Name: {tool.get('name')}")
            print(f"  Futuretools Link: {tool.get('futuretools_link')}")
            print(f"  Website Link: {tool.get('website_link')}")
            print(f"  Description: {tool.get('description')[:100] + '...' if tool.get('description') and len(tool.get('description')) > 100 else tool.get('description')}")
            print(f"  Summarized Desc: {tool.get('summarized_description')}")
    else:
        print("\nNo tools were extracted. The HTML structure assumptions might not match futuretools.io.")
        print("Or, the page structure is too dynamic or complex for the current generic selectors.")

    print("\nFuturetools.io parser update finished.")
```
