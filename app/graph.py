"""
Graph builder module - Creates the workflow graph
"""

from app.factory import AgentFactory

def build_graph():
    """Build and return the compiled workflow graph"""
    return AgentFactory.build_graph_with_nodes()