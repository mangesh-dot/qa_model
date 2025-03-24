from transformers import pipeline

# Loading a free question-answering model bert-large-uncased-whole-word-masking-finetuned-squad
questionAnswering =pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

def ask_llm(query: str, context: str):
    """Generate an answer using a pre-trained Question Answering model."""
    try:
        if not context.strip(): 
            return "No relevant documents found."

        result = questionAnswering(question=query, context=context)

        print(f"Generated Answer: {result['answer']}, Confidence: {result['score']:.4f}")

        return result["answer"] if result["score"] > 0.3 else "I don't know."
    
    except Exception as e:
        return f"Error generating response: {e}"

