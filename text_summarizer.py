"""
This script defines a function to summarize text using Hugging Face Transformers.

Note: This script requires the 'transformers' library and one of its
machine learning framework backends (PyTorch or TensorFlow).
You can install them using pip:
  pip install transformers
  # For PyTorch (recommended for many models):
  pip install torch
  # Or for TensorFlow:
  # pip install tensorflow
"""

from transformers import pipeline

# Initialize the summarization pipeline
# Using a smaller model like 't5-small' for quicker loading and inference,
# especially in environments with limited resources.
# For higher quality summaries, 'facebook/bart-large-cnn' or 't5-base' could be used,
# but they are larger and slower.
try:
    summarizer = pipeline("summarization", model="t5-small")
except Exception as e:
    print(f"Error initializing Hugging Face pipeline. This might be due to missing dependencies or model download issues: {e}")
    print("Please ensure 'torch' or 'tensorflow' is installed and you have internet access for model download.")
    summarizer = None

def summarize_text(text: str, max_length: int = 150, min_length: int = 30) -> str:
    """
    Summarizes the input text using a pre-trained Hugging Face model.

    Args:
        text: The text content to summarize.
        max_length: The maximum length of the summary.
        min_length: The minimum length of the summary.

    Returns:
        The summarized text as a string, or an error message if summarization fails.
    """
    if not summarizer:
        return "Summarization pipeline not initialized. Please check installation and logs."
    
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return "Input text is empty or invalid."

    # Add warning for short input text
    if len(text.split()) < min_length:
        print(f"Warning: Input text ({len(text.split())} words) is shorter than the specified min_length ({min_length} words) for summarization. Summary might be suboptimal or longer than original.")

    try:
        # Ensure text is not too short for the model, or too long to process effectively
        # (though pipeline handles truncation, very long texts can be slow/memory intensive)
        # t5-small has a max input sequence length of 512 tokens.
        # The pipeline should handle truncation, but we add a practical limit.
        # For very long texts, consider chunking strategies.
        if len(text.split()) > 1000: # Heuristic: limit input words to avoid excessive processing time
             print("Warning: Input text is very long. Summarization might take a while or be truncated.")

        summary_list = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary_list[0]['summary_text']
    except Exception as e:
        return f"Error during summarization: {e}"

if __name__ == '__main__':
    sample_text_short = (
        "Paris is the capital and most populous city of France, with an estimated population of "
        "2,165,423 residents as of 1 January 2023 in an area of more than 105 square kilometres (41 square miles). "
        "Since the 17th century, Paris has been one of the world's major centres of finance, diplomacy, commerce, "
        "fashion, gastronomy, science, and arts. The City of Paris is the centre and seat of government of the "
        "Île-de-France, or Paris Region, which has an estimated population of 12,271,794 residents, or about 19% "
        "of the population of France as of 2023."
    )

    sample_text_long = (
        "The James Webb Space Telescope (JWST) is a space telescope designed primarily to conduct infrared astronomy. "
        "As the largest optical telescope in space, its significantly improved infrared resolution and sensitivity "
        "allow it to view objects too old, distant, or faint for the Hubble Space Telescope. This is expected to "
        "enable a broad range of investigations across the fields of astronomy and cosmology, such as observation "
        "of the first stars and the formation of the first galaxies, and detailed atmospheric characterization of "
        "potentially habitable exoplanets. JWST was launched by an Ariane 5 rocket from Kourou, French Guiana, in "
        "December 2021 and entered orbit around the Sun at a Lagrange point (L2), about 1.5 million kilometers "
        "(930,000 mi) from Earth, in January 2022. The first image from JWST was released to the public via a press "
        "conference on 11 July 2022. The telescope is the successor to Hubble and is a collaboration between NASA, "
        "the European Space Agency (ESA), and the Canadian Space Agency (CSA). "
        "The development of JWST began in 1996 for a launch that was initially planned for 2007 with a US$500 million budget. "
        "The project experienced numerous delays and cost overruns, and passed through a major redesign in 2005. "
        "JWST's construction was completed in late 2016, after which it began an extensive testing phase. "
        "The total cost of the project is estimated to be around US$10 billion, which includes the spacecraft's design "
        "and development, its launch, and five years of operations. The telescope's primary mirror consists of 18 "
        "hexagonal gold-plated beryllium segments that combine to create a 6.5-meter (21 ft) diameter mirror. "
        "This large mirror, along with its advanced instruments, allows JWST to capture images of some of the most "
        "distant objects in the universe. Scientists hope that JWST will help answer fundamental questions about "
        "the universe, including how it began, how galaxies evolved, and whether life exists beyond Earth."
    )
    
    print("Attempting to summarize a short text:")
    summary1 = summarize_text(sample_text_short)
    print(f"\nOriginal Text:\n{sample_text_short}")
    print(f"\nSummary:\n{summary1}")

    print("\n" + "="*50 + "\n")

    print("Attempting to summarize a longer text:")
    # Using slightly different parameters for longer text if needed
    summary2 = summarize_text(sample_text_long, max_length=100, min_length=25)
    print(f"\nOriginal Text (Snippet):\n{sample_text_long[:200]}...")
    print(f"\nSummary:\n{summary2}")

    print("\n" + "="*50 + "\n")
    
    print("Testing with empty text:")
    summary_empty = summarize_text("")
    print(f"Summary for empty text: {summary_empty}")

    print("\n" + "="*50 + "\n")

    print("Testing with text shorter than min_length (default 30):")
    sample_text_too_short = "This is a very short text. It has only ten words."
    summary_too_short = summarize_text(sample_text_too_short)
    print(f"\nOriginal Text:\n{sample_text_too_short}")
    print(f"\nSummary for too short text:\n{summary_too_short}")
    
    print("\n" + "="*50 + "\n")

    # Example of how it might be used with web_parser (conceptual)
    # from web_parser import fetch_and_parse_website # Assuming web_parser.py is in the same directory
    # target_url = "https://www.example.com"
    # print(f"Fetching content from {target_url} to summarize...")
    # data = fetch_and_parse_website(target_url)
    # if data and data.get("text"):
    #     print(f"Summarizing content from {target_url}...")
    #     web_summary = summarize_text(data["text"], max_length=200, min_length=50)
    #     print(f"\nSummary of {target_url}:\n{web_summary}")
    # else:
    #     print(f"Could not fetch or no text found at {target_url} to summarize.")

    if not summarizer:
        print("\nNote: The summarization pipeline could not be initialized.")
        print("The example summaries above will show error messages.")
        print("Please check your Hugging Face Transformers installation and dependencies (torch/tensorflow).")
        print("You may need to run: pip install transformers torch (or tensorflow)")
        print("An internet connection is also required for the first run to download the model.")

