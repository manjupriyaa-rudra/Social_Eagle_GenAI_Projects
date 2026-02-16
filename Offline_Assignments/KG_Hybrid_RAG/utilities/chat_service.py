from openai import OpenAI
from config.settings import settings
from utilities.result_logger import log_result


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ask_question(question, kg, hybrid):
    # KG query (sync)
    kg_result = kg.query(question)

    # Hybrid retrieval
    hybrid_result = hybrid.retrieve(question)

    # Merge context
    context = "\n".join(kg_result + hybrid_result)

    prompt = f"""
You are an architecture assistant.
Answer only using the context below.

Context:
{context}

Question:
{question}

Answer concisely.
"""

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    raw_answer = response.choices[0].message.content
    final_answer = raw_answer
    if kg_result:
        source = "KG"
    elif any(word in final_answer.lower() for word in ["import", "send", "create", "flow"]):
        source = "KG"
    else:
        source = "Hybrid"

    log_result({
        "question": question,
        "kg_results": kg_result,
        "hybrid_results": hybrid_result,        
        "llm_raw_answer": raw_answer,        
        "source": source
    })
    # "final_context": context,
    #"normalized_answer": final_answer,
    return final_answer
