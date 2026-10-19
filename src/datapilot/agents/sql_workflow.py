
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from datapilot.agents.sql_generator import (
    SQLGeneration,
    generate_sql,
)
from datapilot.connectors.base import DatabaseAdapter
from datapilot.connectors.models import (
    DatabaseMetadata,
    QueryResult,
    QuerySpec,
)


class SQLWorkflowState(TypedDict, total=False):
    """Data passed between LangGraph nodes."""

    question: str
    metadata: DatabaseMetadata
    sql_statement: str
    explanation: str
    result: QueryResult


def build_sql_workflow(adapter: DatabaseAdapter):
    """Build the natural-language-to-SQL execution graph."""

    def load_schema(state: SQLWorkflowState) -> dict:
        # Discover the schema instead of asking the LLM to guess it.
        return {"metadata": adapter.get_metadata()}

    def generate_query(state: SQLWorkflowState) -> dict:
        generated: SQLGeneration = generate_sql(
            question=state["question"],
            metadata=state["metadata"],
        )

        return {
            "sql_statement": generated.sql_statement,
            "explanation": generated.explanation,
        }

    def execute_query(state: SQLWorkflowState) -> dict:
        # The adapter validates SQL again before execution.
        query = QuerySpec(
            language="sql",
            payload={"statement": state["sql_statement"]},
            limit=100,
        )

        result = adapter.execute_readonly(query)
        return {"result": result}

    graph = StateGraph(SQLWorkflowState)

    graph.add_node("load_schema", load_schema)
    graph.add_node("generate_query", generate_query)
    graph.add_node("execute_query", execute_query)

    graph.add_edge(START, "load_schema")
    graph.add_edge("load_schema", "generate_query")
    graph.add_edge("generate_query", "execute_query")
    graph.add_edge("execute_query", END)

    return graph.compile()
