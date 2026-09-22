import json
import os
import traceback

from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import Client

from backend.prompts import SYSTEM_PROMPT


 
# LOAD ENVIRONMENT
 

load_dotenv()


 
# OPENAI CLIENT
 

openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


 
# CONFIGURATION
 

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5"
)

MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "http://127.0.0.1:8001/mcp"
)


 
# MCP TOOL -> OPENAI TOOL
 

def convert_mcp_tool_to_openai(tool):

    schema = dict(tool.input_schema)

    # OpenAI strict mode requires this
    if schema.get("type") == "object":
        schema["additionalProperties"] = False

    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "MCP tool",
        "parameters": schema,
        "strict": True
    }

 
 

def extract_mcp_result(result):

    # Structured result
    structured = getattr(
        result,
        "structured_content",
        None
    )

    if structured:
        return structured

    # Text result
    content = getattr(
        result,
        "content",
        []
    )

    output = []

    for item in content:

        if hasattr(item, "text"):

            output.append(item.text)

    if output:

        return "\n".join(output)

    return str(result)


 
# UNWRAP EXCEPTION GROUP
 

def get_real_exception(error):

    """
    MCP/AnyIO can wrap the real exception inside
    ExceptionGroup / TaskGroup.

    This extracts the actual underlying error.
    """

    if isinstance(error, BaseExceptionGroup):

        if error.exceptions:

            return get_real_exception(
                error.exceptions[0]
            )

    return error


 
# MAIN AGENT
 

async def run_agent(user_message: str):

    print("\n" + "=" * 60)
    print("AGENT REQUEST")
    print("=" * 60)

    print("User:", user_message)

    print("\nConnecting to MCP:")
    print(MCP_SERVER_URL)

    try:

          
        # CONNECT MCP
          

        async with Client(
            MCP_SERVER_URL
        ) as mcp_client:

            print("\nMCP connected successfully.")

              
            # GET MCP TOOLS
              

            tool_result = await mcp_client.list_tools()

            mcp_tools = tool_result.tools

            print("\nMCP TOOLS:")

            for tool in mcp_tools:

                print(
                    f"- {tool.name}"
                )

              
            # CONVERT TO OPENAI TOOLS
              

            openai_tools = [
                convert_mcp_tool_to_openai(tool)
                for tool in mcp_tools
            ]

            print(
                f"\nConverted {len(openai_tools)} tools for OpenAI."
            )

              
            # FIRST OPENAI REQUEST
              

            print("\nCalling OpenAI...")

            response = await openai_client.responses.create(

                model=MODEL,

                instructions=SYSTEM_PROMPT,

                input=user_message,

                tools=openai_tools
            )

            print(
                "OpenAI response received."
            )

              
            # TOOL LOOP
              

            while True:

                function_calls = [

                    item

                    for item in response.output

                    if item.type == "function_call"

                ]

                  
                # NO TOOL CALL
                  

                if not function_calls:

                    print(
                        "\nNo tool call required."
                    )

                    return response.output_text

                print(
                    f"\nOpenAI requested {len(function_calls)} tool(s)."
                )

                tool_outputs = []

                  
                # EXECUTE MCP TOOLS
                  

                for function_call in function_calls:

                    tool_name = function_call.name

                    print(
                        f"\nCalling MCP tool: {tool_name}"
                    )

                    print(
                        "Arguments:",
                        function_call.arguments
                    )

                    try:

                        arguments = json.loads(
                            function_call.arguments
                        )

                    except Exception as error:

                        print(
                            "\nERROR parsing arguments:"
                        )

                        traceback.print_exc()

                        tool_result_data = {
                            "success": False,
                            "error": str(error)
                        }

                        tool_outputs.append({

                            "type":
                                "function_call_output",

                            "call_id":
                                function_call.call_id,

                            "output":
                                json.dumps(
                                    tool_result_data
                                )
                        })

                        continue

                      
                    # CALL MCP
                      

                    try:

                        result = await mcp_client.call_tool(

                            tool_name,

                            arguments

                        )

                        print(
                            "MCP tool returned."
                        )

                        print(
                            "MCP result:",
                            result
                        )

                 

                        if getattr(
                            result,
                            "is_error",
                            False
                        ):

                            tool_result_data = {

                                "success": False,

                                "error":
                                    extract_mcp_result(
                                        result
                                    )
                            }

                        else:

                            tool_result_data = (
                                extract_mcp_result(
                                    result
                                )
                            )

                    except Exception as error:

                        print(
                            "\nMCP TOOL ERROR:"
                        )

                        traceback.print_exc()

                        real_error = (
                            get_real_exception(
                                error
                            )
                        )

                        print(
                            "\nREAL ERROR:",
                            repr(real_error)
                        )

                        tool_result_data = {

                            "success": False,

                            "error":
                                str(real_error)
                        }

                      
                    # SEND TOOL RESULT TO OPENAI
                      

                    tool_outputs.append({

                        "type":
                            "function_call_output",

                        "call_id":
                            function_call.call_id,

                        "output":
                            json.dumps(
                                tool_result_data,
                                default=str
                            )
                    })

                  
                # SEND TOOL RESULT BACK TO OPENAI
                  

                print(
                    "\nSending tool result back to OpenAI..."
                )

                response = await openai_client.responses.create(

                    model=MODEL,

                    instructions=SYSTEM_PROMPT,

                    previous_response_id=response.id,

                    input=tool_outputs,

                    tools=openai_tools
                )

                print(
                    "OpenAI processed tool result."
                )

    except Exception as error:

        print("\n" + "=" * 60)
        print("AGENT ERROR")
        print("=" * 60)

        traceback.print_exc()

        real_error = get_real_exception(
            error
        )

        print(
            "\nREAL ERROR:",
            repr(real_error)
        )

        return (
            f"Agent error: {real_error}"
        )