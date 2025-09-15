import pandas as pd
from opsml.llm import Prompt, Score

user_queries = [
    "What makes Drug Church's sound unique in modern post hardcore?",
    "How does Speed's approach differ from traditional hardcore punk?",
    "What are Turnstile's most influential songs and albums?",
    "How has Touché Amoré evolved their sound over the years?",
    "What are some bands similar to Drug Church and Speed?",
    "How do modern post hardcore bands incorporate melody differently?",
    "What's the difference between Turnstile's hardcore and post hardcore elements?",
    "Which Touché Amoré album is best for newcomers to emotional hardcore?",
    "How do bands like Drug Church blend punk and alternative rock?",
    "What makes the current post hardcore revival different from the 2000s?",
]

# Reformulated queries with more specific context
reformulated_queries = [
    "Analyze Drug Church's blend of 90s alternative rock with hardcore punk on albums like 'Cheer' and 'OPIHI'",
    "Compare Speed's aggressive hardcore approach to classic bands like Black Flag and Minor Threat",
    "Examine Turnstile's crossover appeal through tracks like 'Mystery' and 'Blackout' from 'Glow On'",
    "Trace Touché Amoré's progression from screamo to melodic post hardcore across their discography",
    "Recommend contemporary bands combining Drug Church's melodic sensibilities with Speed's intensity",
    "Evaluate how bands like Turnstile and Drug Church incorporate clean vocals into hardcore frameworks",
    "Distinguish Turnstile's hardcore punk roots from their experimental post hardcore evolution",
    "Suggest starting with Touché Amoré's 'Lament' for accessible entry into emotional hardcore subgenre",
    "Analyze Drug Church's use of 90s grunge and indie rock influences within hardcore punk structures",
    "Compare 2020s post hardcore revival bands to iconic 2000s acts like Thrice and Thursday",
]


# combine user queries and reformulated queries into a DataFrame with ids
def get_reformulation_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "user_query": user_queries,
            "reformulated_query": reformulated_queries,
            "id": [f"query_{i + 1}" for i in range(len(user_queries))],
        }
    )
    return df


def reformulation_evaluation_prompt():
    """
    Builds a prompt for evaluating the quality of a reformulated query.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the reformulation.

    Example:
        >>> prompt = create_reformulation_evaluation_prompt()
    """
    return Prompt(
        message=(
            "You are an expert evaluator of search query reformulations. "
            "Given the original user query and its reformulated version, your task is to assess how well the reformulation improves the query. "
            "Consider the following criteria:\n"
            "- Does the reformulation make the query more explicit and comprehensive?\n"
            "- Are relevant synonyms, related concepts, or specific features added?\n"
            "- Is the original intent preserved without changing the meaning?\n"
            "- Is the reformulation clear and unambiguous?\n\n"
            "Provide your evaluation as a JSON object with the following attributes:\n"
            "- score: An integer from 1 (poor) to 5 (excellent) indicating the overall quality of the reformulation.\n"
            "- reason: A brief explanation for your score.\n\n"
            "Format your response as:\n"
            "{\n"
            '  "score": <integer 1-5>,\n'
            '  "reason": "<your explanation>"\n'
            "}\n\n"
            "Original Query:\n"
            "${user_query}\n\n"
            "Reformulated Query:\n"
            "${reformulated_query}\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite",
        provider="gemini",
        response_format=Score,
    )
