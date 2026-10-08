from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import os 

def get_llm():
    if os.getenv("MISTRAL_API_KEY"):
        from langchain_mistralai import ChatMistralAI
        return ChatMistralAI(model="mistral-small-latest", mistral_api_key=os.getenv("MISTRAL_API_KEY"), temperature=0.3)
    elif os.getenv("GROQ_API_KEY"):
        from langchain_groq import ChatGroq
        model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        return ChatGroq(
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
        )
    elif os.getenv("OLLAMA_MODEL"):
        from langchain_community.chat_models import ChatOllama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL"),
            base_url=base_url,
            temperature=0.3,
        )
    raise ValueError("No LLM API key found. Please set MISTRAL_API_KEY or GROQ_API_KEY in environment/secrets.")


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 3000,
        chunk_overlap = 200
    )

    return splitter.split_text(transcript)

def summarize(transcript : str) -> str:
    llm = get_llm()

    # For short transcripts or YouTube Shorts, summarize directly in one clean pass
    if len(transcript.strip()) < 3000:
        single_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert video content summarizer. Provide a clear, "
                "professional bullet-point summary of the main points from the transcript. "
                "Do NOT include conversational meta-talk like 'I am ready' or 'Here is a summary'. "
                "Output ONLY the bullet points directly."
            ),
            ("human", "Transcript:\n{text}")
        ])
        chain = single_prompt | llm | StrOutputParser()
        return chain.invoke({"text": transcript.strip()})

    # For longer transcripts, use map-reduce
    map_prompt = ChatPromptTemplate.from_messages(
        [
        ("system", "Summarize this portion of a transcript concisely in bullet points."),
        ("human", "{text}"),
    ]
    )

    map_chain = map_prompt | llm | StrOutputParser()
    chunks = split_transcript(transcript)
    chunk_summaries = [map_chain.invoke({"text" : chunk}) for chunk in chunks]
    combined = "\n\n".join(chunk_summaries)

    combined_prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system",
            "You are an expert video content summarizer. Combine these partial summaries "
            "into one comprehensive, professional bullet-point summary. "
            "Do NOT include conversational filler like 'Here is the summary' or 'I am ready'. "
            "Output ONLY the final formatted bullet points directly.",
        ),
        ("human", "Partial Summaries:\n{text}"),
    ]
    )

    combined_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | combined_prompt | llm | StrOutputParser()
    )

    return combined_chain.invoke(combined)

def generate_title(transcipt : str) -> str:
    llm = get_llm()

    

    title_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | 
        ChatPromptTemplate.from_messages([
             (
                "system",
                "Based on the video transcript, generate a short professional video title "
                "(max 8 words). Only return the title, nothing else.",
            ),
            ("human", "{text}"),
        ])
        | llm
        |StrOutputParser()
    )

    return title_chain.invoke(transcipt[:2000])




