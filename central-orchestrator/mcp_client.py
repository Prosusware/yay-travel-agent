import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    """
    Connects to a remote MCP server via mcp-remote
    and lists available tools.
    """
    server_url = "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", server_url],
        env=None
    )

    async with AsyncExitStack() as exit_stack:
        try:
            print("Connecting to MCP server via mcp-remote...")
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            
            print("Creating client session...")
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))

            print("Initializing session...")
            await session.initialize()

            print("Listing available tools...")
            response = await session.list_tools()
            tools = response.tools
            
            print("\n✅ Successfully connected to server!")
            print("Available tools:", [tool.name for tool in tools])
            
            if tools:
                print("\nTool details:")
                for tool in tools:
                    print(f"  - Name: {tool.name}")
                    print(f"    Description: {tool.description}")
                    print(f"    Input Schema: {tool.inputSchema}")


        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
        finally:
            print("\nClosing connection.")

if __name__ == "__main__":
    asyncio.run(main()) 