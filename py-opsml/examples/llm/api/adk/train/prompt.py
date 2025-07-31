from opsml.llm import Prompt
from opsml.card import PromptCard
from opsml.scouter.drift import LLMDriftConfig
from opsml.scouter.alert import LLMAlertConfig
from opsml.scouter.types import CommonCrons
from .prompt_metrics import id_extraction, helpful_response

# take user input and reformulate it into a question for the LLM
extract_shipment_id_prompt = """
You are an expert assistant for supply chain operations. Your task is to extract the shipment ID from the user's query and return it in a structured JSON format.

Given the user's query, identify the shipment ID (an integer) and return a JSON object as follows:

{
  "id": <shipment_id>
}

If no shipment ID is found, return:

{
  "id": null
}

User query: ${user_query}

Return only the JSON object.
"""


# take a reformulated question and generate a response using the LLM
response_template = """
You are an expert in software development and debugging. Your task is to provide a detailed and informative response to the following question.
The question is based on user input that has been reformulated to be specific and focused. Your response should be clear, concise, and relevant to the context of the question.
Here are some examples of how to respond to questions:
1. Question: "How do I use the `map` function in Python?"
   Response: "The `map` function in Python applies a given function to all items in an iterable (like a list) and returns a map object (which is an iterator). You can convert it to a list using `list(map(function, iterable))`. For example, `list(map(lambda x: x * 2, [1, 2, 3]))` will return `[2, 4, 6]`."
2. Question: "What could be the reason for my code not working as expected?"
   Response: "There could be several reasons for your code not working as expected. Common issues include syntax errors, logical errors, or runtime exceptions. It would be helpful to see the specific error message or the part of the code that is causing the issue to provide a more accurate diagnosis."
3. Question: "What is recursion and how does it work in programming?"               
    Response: "Recursion is a programming technique where a function calls itself in order to solve a problem. It is often used to break down complex problems into simpler subproblems. A recursive function typically has a base case that stops the recursion and a recursive case that continues the recursion. For example, calculating the factorial of a number can be done using recursion."
4. Question: "What could be the cause of the error I am encountering when running my script?"
   Response: "The cause of the error when running your script could be due to various reasons such as missing dependencies, incorrect file paths, or syntax errors in the code. It would be helpful to see the specific error message you are encountering to provide a more accurate diagnosis."
5. Question: "What are some techniques to optimize code for better performance?"
   Response: "Some techniques to optimize code for better performance include using efficient algorithms and data structures, minimizing memory usage, avoiding unnecessary computations, and leveraging parallel processing when applicable. Profiling your code to identify bottlenecks can also help in optimizing performance."
Please provide a detailed and informative response to the following question:
${reformulated_query}
"""

prediction_response_prompt = """
You are an expert assistant for supply chain operations. Your task is to take a delivery time prediction and craft a clear, friendly, and informative response for the user.

Given the following information:
- Shipment ID: ${shipment_id}
- Predicted delivery time: ${predicted_delivery_time}
- Current shipment status: ${shipment_status}
- Destination: ${destination}

Generate a response that communicates the estimated delivery time and any relevant context (such as delays, current location, or other factors affecting delivery).

Return only the response message.

Examples:
1. "Your shipment #12345 is currently in Leipzig and is expected to arrive in Berlin by 3pm tomorrow, considering current traffic and weather conditions."
2. "Shipment #67890 is delayed due to severe weather and is now expected to arrive in Munich by 10am on Friday."

Information:
- Shipment ID: ${shipment_id}
- Predicted delivery time: ${predicted_delivery_time}
- Current shipment status: ${shipment_status}
- Destination: ${destination}
"""


def create_shipment_id_extraction_prompt():
    """
    Builds a prompt for extracting the shipment ID from a user's query.

    Returns:
        Prompt: A prompt that extracts the shipment ID in JSON format.
    """
    return Prompt(
        user_message=extract_shipment_id_prompt,
        model="gemini-2.5-flash",
        provider="gemini",
    )


def create_response_prompt():
    """
    Builds a prompt for generating a response to a reformulated question.

    Returns:
        Prompt: A prompt that generates a response based on the reformulated query.
    """
    return Prompt(
        user_message=response_template,
        model="gemini-2.5-flash",
        provider="gemini",
    )


def create_shipment_prompt_card() -> PromptCard:
    """
    Creates a response prompt card for extracting shipment IDs.

    Returns:
        PromptCard: A prompt card for extracting shipment IDs.
    """
    shipment_extraction_card = PromptCard(
        prompt=create_shipment_id_extraction_prompt(),
        space="opsml",
        name="shipment_id_extraction",
    )

    shipment_extraction_card.create_drift_profile(
        alias="shipment_id_extraction",
        config=LLMDriftConfig(
            sample_rate=1,
            alert_config=LLMAlertConfig(schedule=CommonCrons.Every6Hours),
        ),
        metrics=[id_extraction],
    )

    return shipment_extraction_card


def create_response_prompt_card() -> PromptCard:
    """
    Creates a response prompt card for generating responses to reformulated questions.

    Returns:
        PromptCard: A prompt card for generating responses based on reformulated queries.
    """
    response_card = PromptCard(
        prompt=create_response_prompt(),
        space="opsml",
        name="response_generation",
    )

    response_card.create_drift_profile(
        alias="response_generation",
        config=LLMDriftConfig(
            sample_rate=1,
            alert_config=LLMAlertConfig(schedule=CommonCrons.Every6Hours),
        ),
        metrics=[helpful_response],
    )

    return response_card
