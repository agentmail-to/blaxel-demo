from agents import Agent, Runner
from blaxel.openai import bl_model, bl_tools

from agentmail import AgentMail, Message
from markdown import markdown


async def agent(message: Message):
    tools = [
        tool
        for tool in await bl_tools(["agentmail", "context7"])
        if tool in ["get_thread", "resolve-library-id", "get-library-docs"]
    ]
    model = await bl_model("sandbox-openai")

    agent = Agent(
        name="docs-agent",
        model=model,
        tools=tools,
        instructions="""You are a helpful developer email assistant.
You will receive an email from a developer.
Your task is respond to the email in a friendly and helpful manner.

If the developer asks a technical question, use the context7 tools to retieve the relevant documentation.
First use the resolve-library-id tool to resolve the relevant library id.
Then use the get-library-docs tool to retrieve the relevant documentation.

Finally, respond to the developer as if you are writing an email.
In the email signature, refer to yourself as "AgentMail".

If the context of previous messages would be helpful for answering the developer's query, use the get_thread tool to retrieve the full email thread.

Generate markdown and include relevant hyperlinks to the documentation.
Do not specify the email subject, only the email body.
Do not include any other text in your response.

Analyze the documentation and generate a comprehensive response to the developer's query in one turn.
Do not plan to respond to the developer's query in multiple turns. Provide a single comprehensive response.
""",
    )

    result = await Runner.run(agent, message.model_dump_json())

    client = AgentMail()

    client.inboxes.messages.reply(
        inbox_id=message.inbox_id,
        message_id=message.message_id,
        html=markdown(result.final_output).replace("\n", ""),
    )

    return result.final_output
