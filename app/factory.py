from langgraph.graph import StateGraph, END
from app.nodes import (
    classify_intent, general_response, retrieve_schemas, 
    generate_sql, execute_sql, error_analyzer, update_history,
    AgentState
)

class AgentFactory:
    @staticmethod
    def create_nodes():
        return {
            "classify": classify_intent,
            "general": general_response,
            "retrieve": retrieve_schemas,
            "generate_sql": generate_sql,
            "execute": execute_sql,
            "error_analyzer": error_analyzer,
            "update_history": update_history
        }

    @staticmethod
    def build_graph_with_nodes():
        nodes = AgentFactory.create_nodes()
        graph = StateGraph(state_schema=AgentState)
        for node_name, node_func in nodes.items():
            graph.add_node(node_name, node_func)
        
        graph.set_entry_point("classify")
        graph.add_conditional_edges("classify", lambda s: s["intent"], {"greeting": "general", "general": "general", "data_query": "retrieve"})
        graph.add_edge("general", "update_history")
        graph.add_edge("retrieve", "generate_sql")
        graph.add_edge("generate_sql", "execute")
        graph.add_edge("execute", "error_analyzer")
        graph.add_conditional_edges(
            "error_analyzer",
            lambda s: s.get("analysis_action", "end"),
            {"retry": "generate_sql", "rephrase": "generate_sql", "fail": "update_history", "ask_user": "update_history", "end": "update_history"}
        )
        graph.add_edge("update_history", END)
        
        return graph.compile()