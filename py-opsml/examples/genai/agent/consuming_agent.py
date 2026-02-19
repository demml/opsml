import asyncio
from uuid import uuid4
import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import SendMessageRequest, MessageSendParams

base_url = "http://localhost:8888"


async def main():
    async with httpx.AsyncClient(base_url=base_url) as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        agent_card = await resolver.get_agent_card()

        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card,
            url=base_url,
        )

        send_message_payload = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "how much is 10 USD in INR?"}],
                "messageId": uuid4().hex,
            },
        }

        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**send_message_payload))

        response = await client.send_message(request)
        print(response.model_dump(mode="json", exclude_none=True))


if __name__ == "__main__":
    asyncio.run(main())
