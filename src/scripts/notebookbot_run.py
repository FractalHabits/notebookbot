import os
import sys

from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import BraveSearch

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from src.authentication.authentication_manager import AuthenticationManager

from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_community.document_loaders import ArxivLoader

def main():
    # Step 1: Set up or authenticate with existing credentials to access stored API keys
    env_file_path = '.env'  # This should be relative to the project root
    auth_manager = AuthenticationManager(env_file_path=env_file_path)
    #auth_manager.setup_or_authenticate()

    if auth_manager.is_authenticated:
        try:
            DECRYPT_OPENAI_API_KEY = auth_manager.api_interface.api_keys['OPENAI_API_KEY']
            DECRYPT_ANTHROPIC_API_KEY = auth_manager.api_interface.api_keys['ANTHROPIC_API_KEY']
        except ValueError as e:
            print(str(e))

    # Step 2: Create a LangGraph
    # Define the tools for the agent to use

    @tool
    def arxiv_search(query: str):
        """Call to search arxiv."""
        arxiv = ArxivAPIWrapper()
        return arxiv.run(query)
    
    tools = [arxiv_search]

    tool_node = ToolNode(tools)

    model = ChatAnthropic (api_key = DECRYPT_ANTHROPIC_API_KEY(), model="claude-3-5-sonnet-20240620", temperature=0).bind_tools(tools)

    # Define the function that determines whether to continue or not
    def should_continue(state: MessagesState) -> Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # Define the function that calls the model
    def call_model(state: MessagesState):
        messages = state['messages']
        response = model.invoke(messages)
        return {"messages": [response]}

    # Define a new graph
    workflow = StateGraph(MessagesState)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # Set the entrypoint as `agent`
    # This means that this node is the first one called
    workflow.add_edge(START, "agent")

    # We now add a conditional edge
    workflow.add_conditional_edges(
        # First, we define the start node. We use `agent`.
        # This means these are the edges taken after the `agent` node is called.
        "agent",
        # Next, we pass in the function that will determine which node is called next.
        should_continue,
    )

    # We now add a normal edge from `tools` to `agent`.
    # This means that after `tools` is called, `agent` node is called next.
    workflow.add_edge("tools", 'agent')

    # Initialize memory to persist state between graph runs
    checkpointer = MemorySaver()

    # Finally, we compile it!
    # This compiles it into a LangChain Runnable,
    # meaning you can use it as you would any other runnable.
    # Note that we're (optionally) passing the memory when compiling the graph
    app = workflow.compile(checkpointer=checkpointer)

    # Interact with the LangGraph
    while True:
        user_input = input("Enter your message (or 'quit' to exit): ")
        if user_input.lower() == 'quit' or user_input.lower() == 'exit':
            break

        final_state = app.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": 42}}
        )
        print("Assistant:", final_state["messages"][-1].content)


    # Use the Runnable
    final_state = app.invoke(
        {"messages": [HumanMessage(content="what is the weather in sf")]},
        config={"configurable": {"thread_id": 42}}
    )
    final_state["messages"][-1].content




if __name__ == "__main__":
    main()

