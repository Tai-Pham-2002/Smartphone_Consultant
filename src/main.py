# main.py
from langgraph.graph import StateGraph, START, END
from nodes import tavily_search_node, schema_mapping_node, product_comparison_node, youtube_review_node, display_node, send_email_node
from models import State

def build_workflow():
    """Build and return the LangGraph workflow."""
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("tavily_search", tavily_search_node)
    workflow.add_node("schema_mapping", schema_mapping_node)
    workflow.add_node("product_comparison", product_comparison_node)
    workflow.add_node("youtube_review", youtube_review_node)
    workflow.add_node("display", display_node)
    workflow.add_node("send_email", send_email_node)
    
    # Define edges
    workflow.add_edge(START, "tavily_search")
    workflow.add_edge("tavily_search", "schema_mapping")
    workflow.add_edge("schema_mapping", "product_comparison")
    workflow.add_edge("product_comparison", "youtube_review")
    workflow.add_edge("youtube_review", "display")
    workflow.add_edge("display", "send_email")
    workflow.add_edge("send_email", END)
    
    return workflow.compile()

def run_workflow(query: str, email: str):
    """Run the ShopGenie workflow with the given query and email."""
    workflow = build_workflow()
    initial_state = State(
        query=query,
        email=email,
        products=[],
        product_schema=[],
        blogs_content=[],
        best_product={},
        comparison=[],
        youtube_link=""
    )
    
    result = workflow.invoke(initial_state)
    return result

if __name__ == "__main__":
    # Example usage
    query = "best smartphones under $1000"
    email = "tantai6889@gmail.com"
    result = run_workflow(query, email)
    print(result)