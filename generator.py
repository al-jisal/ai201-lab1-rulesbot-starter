from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_response(query, retrieved_chunks):
  """
  Generate a grounded answer from retrieved rule chunks.

  TODO — Milestone 3:

  `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
    - "text"     : the chunk text
    - "game"     : the game name
    - "distance" : similarity score (you can use this to filter weak matches)

  Before writing code, talk through these with your group:
    - How will you format the chunks into a context block for the prompt?
    - What instructions will stop the model from answering beyond what the
      rules say? (Grounding is the whole point — a confident wrong answer
      is worse than an honest "I don't know.")
    - How will you surface which game each answer comes from?

  Your response should:
    1. Answer using only the retrieved context — not the model's general knowledge
    2. Make clear which game the answer comes from
    3. Say so clearly when the answer isn't in the loaded rules

  Return the response as a plain string.
  """
  if not retrieved_chunks:
    return (
      "I couldn't find anything relevant in the loaded rule books. "
      "Try rephrasing your question — or check that your ingestion pipeline is working."
    )
  
  system_prompt = (
    "You're the go-to assistant at a game night when players are not sure about the game rules"
    "Answer the players' question using only the context provided below. If the answer is not in the text," 
    "say so clearly — do not guess or draw on outside knowledge."
  )
  
  context_text = "\n\n-------\n\n".join(
    f"Game: {chunk["game"]} | Distance: {chunk["distance"]} \n{chunk["text"]}"
    for chunk in retrieved_chunks
  )

  user_prompt = f"""
    Context:
    {context_text}

    Question:
    {query}

    Answer:
  """

  answer = _client.chat.completions.create(
    messages=[
      {
        "role" : "system",
        "content" : system_prompt
      },
      {
        "role" : "user",
        "content" : user_prompt
      },
    ],
    model=LLM_MODEL
  )

  return answer.choices[0].message.content.strip()
