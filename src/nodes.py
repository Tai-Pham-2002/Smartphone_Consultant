# nodes.py
from typing import Dict
from models import State, ListOfSmartphoneReviews, ProductComparison, EmailRecommendation
from utils import load_blog_content
from config import load_config
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import json
import time


def tavily_search_node(state: State) -> Dict:
    """Search with Tavily and store content."""
    config = load_config()
    tavily_client = config["tavily_client"]
    try:
        query = state.get('query', '')
        response = tavily_client.search(query=query, max_results=1)
        if "results" not in response or not response["results"]:
            raise ValueError("No results found for the given query.")
        
        blogs_content = []
        for blog in response['results']:
            blog_url = blog.get("url", "")
            if blog_url:
                content = load_blog_content(blog_url)
                if content:
                    blogs_content.append({
                        "title": blog.get("title", ""),
                        "url": blog_url,
                        "content": content,
                        "score": blog.get("score", "")
                    })
        
        if blogs_content:
            print("Extracted Blogs Content:", blogs_content)
            return {"blogs_content": blogs_content}
        else:
            raise ValueError("No blogs content found.")
    
    except Exception as e:
        print(f"Error with Tavily API call: {e}")
        return {"blogs_content": []}

def schema_mapping_node(state: State) -> Dict:
    """Map web search results to a structured schema."""
    max_retries = 2
    wait_time = 60
    config = load_config()
    llm = config["llm"]
    
    if "blogs_content" not in state or not state["blogs_content"]:
        print("No blog content available or content is empty; schema extraction skipped.")
        return {"product_schema": []}
    
    blogs_content = state["blogs_content"]
    prompt_template = """
You are a professional assistant tasked with extracting structured information from a blogs.

### Instructions:

1. **Product Details**: For each product mentioned in the blog post, populate the `products` array with structured data for each item, including:
   - `title`: The product name.
   - `url`: Link to the blog post or relevant page.
   - `content`: A concise summary of the product's main features or purpose.
   - `pros`: A list of positive aspects or advantages of the product.if available other wise extract blog content.
   - `cons`: A list of negative aspects or disadvantages.if available other wise extract blog content.
   - `highlights`: A dictionary containing notable features or specifications.if available other wise extract blog content.
   - `score`: A numerical rating score if available; otherwise, use `0.0`.

### Blogs Contents: {blogs_content}

After extracting all information, just return the response in the JSON structure given below. Do not add any extracted information. The JSON should be in a valid structure with no extra characters inside, like Python’s \\n.

"""
    parser = JsonOutputParser(pydantic_object=ListOfSmartphoneReviews)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["blogs_content"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    for attempt in range(1, max_retries + 1):
        try:
            chain = prompt | llm | parser
            response = chain.invoke({"blogs_content": blogs_content})
            if response.get('products') and len(response['products']) > 1:
                return {"product_schema": response['products']}
            else:
                print(f"Attempt {attempt} failed: Product schema has one or fewer products.")
            if attempt < max_retries:
                time.sleep(wait_time)
        except Exception as retry_exception:
            print(f"Retry {attempt} error: {retry_exception}")
            if attempt < max_retries:
                time.sleep(wait_time)
    
    print("All retry attempts failed to create a valid product schema with more than one product.")
    return {"product_schema": []}

def product_comparison_node(state: State) -> Dict:
    """Compare products and select the best one."""
    config = load_config()
    llm = config["llm"]
    
    if "product_schema" not in state or not state["product_schema"]:
        print("No product schema available; product comparison skipped.")
        return state
    
    product_schema = state["product_schema"]
    prompt_template = """
1. **List of Products for Comparison (`comparisons`):**
   - Each product should include:
     - **Product Name**: The name of the product (e.g., "Smartphone A").
     - **Specs Comparison**:
       - **Processor**: Type and model of the processor (e.g., "Snapdragon 888").
       - **Battery**: Battery capacity and type (e.g., "4500mAh").
       - **Camera**: Camera specifications (e.g., "108MP primary").
       - **Display**: Display type, size, and refresh rate (e.g., "6.5 inch OLED, 120Hz").
       - **Storage**: Storage options and whether it is expandable (e.g., "128GB, expandable").
     - **Ratings Comparison**:
       - **Overall Rating**: Overall rating out of 5 (e.g., 4.5).
       - **Performance**: Rating for performance out of 5 (e.g., 4.7).
       - **Battery Life**: Rating for battery life out of 5 (e.g., 4.3).
       - **Camera Quality**: Rating for camera quality out of 5 (e.g., 4.6).
       - **Display Quality**: Rating for display quality out of 5 (e.g., 4.8).
     - **Reviews Summary**: Summary of key points from user reviews that highlight the strengths and weaknesses of this product.

2. **Best Product Selection (`best_product`):**
   - **Product Name**: Select the best product among the compared items.
   - **Justification**: Provide a brief explanation of why this product is considered the best choice. This should be based on factors such as balanced performance, high user ratings, advanced specifications, or unique features.

Here is the product data to analyze:\n\n{product_data}
"""
    parser = JsonOutputParser(pydantic_object=ProductComparison)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["product_data"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    try:
        chain = prompt | llm | parser
        response = chain.invoke({"product_data": json.dumps(state['product_schema'])})
        return {"comparison": response['comparisons'], "best_product": response['best_product']}
    except Exception as e:
        print(f"Error during product comparison: {e}")
        return {"best_product": {}, "comparison_report": "Comparison failed"}

def youtube_review_node(state: State) -> Dict:
    """Search for a YouTube review of the best product."""
    config = load_config()
    youtube = config["youtube"]
    
    best_product_name = state.get("best_product", {}).get("product_name")
    if not best_product_name:
        print("Skipping YouTube search: No best product found.")
        return {"youtube_link": None}
    
    try:
        search_response = youtube.search().list(
            q=f"{best_product_name} review",
            part="snippet",
            type="video",
            maxResults=1
        ).execute()
        
        video_items = search_response.get("items", [])
        if not video_items:
            print("No YouTube videos found for the best product.")
            return {"youtube_link": None}
        
        video_id = video_items[0]["id"]["videoId"]
        youtube_link = f"https://www.youtube.com/watch?v={video_id}"
        return {"youtube_link": youtube_link}
    except Exception as e:
        print(f"Error during YouTube search: {e}")
        return {"youtube_link": None}

def display_node(state: State) -> Dict:
    """Prepare data for UI display."""
    if "comparison" in state and state['comparison']:
        return {
            "products": state["product_schema"],
            "best_product": state["best_product"],
            "comparison": state["comparison"],
            "youtube_link": state["youtube_link"]
        }
    else:
        print("Comparison not available")
        return state

def send_email_node(state: State) -> Dict:
    """Send email with product recommendation."""
    from utils import send_email
    from prompts import email_template_prompt, email_html_template
    from config import load_config
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import PromptTemplate
    
    config = load_config()
    llm = config["llm"]
    
    if "best_product" not in state or not state['best_product']:
        print("No best product available; email sending skipped.")
        return {"send_email": None}
    
    user_query = state["query"]
    best_product_name = state["best_product"]["product_name"]
    justification = state["best_product"]["justification"]
    youtube_link = state.get("youtube_link", "")
    
    parser = JsonOutputParser(pydantic_object=EmailRecommendation)
    prompt = PromptTemplate(
        template=email_template_prompt,
        input_variables=["product_name", "justification_line", "user_query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    try:
        chain = prompt | llm | parser
        email_content = chain.invoke({
            "product_name": best_product_name,
            "justification_line": justification,
            "user_query": user_query
        })
        
        email_body = email_html_template.format(
            heading=email_content["heading"],
            product_name=best_product_name,
            justification=email_content["justification_line"],
            youtube_link=youtube_link
        )
        
        send_email(state["email"], email_content["subject"], email_body)
        return {"send_email": None}
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"send_email": None}