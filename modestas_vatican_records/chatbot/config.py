
#* For convenience purposes I have decided not to move this environmental variables configuration to .env file
#* The SEPARATORS list holds a newline character that is being read funky from .env file
#* And this config script would still be needed to read that .env file
#* and default values for os.getenv() would need to be indicated

#* I picked probably the most popular embedding sentence transformer
#* It's fast and it's effective.
#* Model card https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER = "cross-encoder/ms-marco-MiniLM-L-6-v2"

#* I picked Qwen2.5-3B as an LLM
#* I wanted a free, decently small LLM that could run with decent latency on my MacBook M3 Pro
#* At first I was using Ollama API interface with Qwen2.5-7B which worked truly well
#* But then I thought that it might be a bit more problematic to deploy this chatbot having an Ollama API dependency
#* Ollama Qwen2.5-7B is quantized with Q4_K_M quantization, HuggingFace Qwen2.5-7B-Instruct version is not
#* Therefore instead of searching of .gguf version of Qwen2.5-7B on HuggingFace, I decided to pick Qwen2.5-3B model
#* By now, as I'm writing this documentation, I would like to test Qwen2.5-7B-Instruct Q4 model from HuggingFace
#* But not I'm already late with initially self-placed deadline, therefore - I will stick with Qwen2.5-3B model for now
#* Why Qwen generally, from all the other free Ollama available models?
#* I have tested a several of them before, including 7B reasoning DeepSeek R1 on Named Entity Recognition task
#* And Qwen2.5-7B caught my eye as it rarely failed to correctly classify entities back then
#* and adhered to the prompt more strictly than other Ollama models I tested before
#* following prompt instructions, not hallucinating wrong entities 
#* and without providing additional undesired contexts, when asked not to
#* Therefore Qwen2.5-7B for now is my favorite local free LLM
#* DeepSeek R1 (7B reasoning), on the other hand, is an overkill for this task
#* The latency delay caused by it's reasoning abilities is more an obstacle, than a help
#* Therefore, reasoning models were not considered for this task
#* Qwen model card: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct
HF_LLM_MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"

#* I chose to use ChromaDB database to store the articles semantics
#* I like ChromaDB for it's convenient and easy use
#* And an option to pass a SentenceTransformer instance as embedding function
#* and avoid additional function development to embed user queries and articles before forming database or performing RAG
#* I use SentenceTransformer for their semantically rich, fixed-size output embeddings
#* without the need to manually pool token-level outputs, normalize the results and 
#* fine-tune the embeddings with contrastive objectives to ensure semantic consistency
#* which would be required with token-based transformers
CHROMA_DB_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "help_center_articles"

#* I think, 5 retrieved documents for this RAG task should be sufficient enough
NUM_RETRIEVE_DOCUMENTS = 5

#* I use newline character's and end of sentence character as separators for text chunks
#* To try to maintain the semantic consistency of the retrieved documents
#* The newline character is still used as a primary option to split chunk paragraph-wise
SEPARATORS = ["\n", "."]

#* At first text is split in chunks by characters
#* But there might be some resulting chunks that are too long token-wise
#* For the SentenceTransformer model - exceed it's context window
#* Then later these chunks are reworked and split token-wise, if some exceed pre-defined context window
#* The context window of "all-MiniLM-L6-v2" SentenceTransformer model is 256, therefore TOKENS_PER_CHUNK = 256
#* Exceeding tokens (if not processed by token-wise chunking) are truncated and not included into the Chroma DB
CHARACTER_SPLIT_CHUNK_SIZE = 500
TOKENS_PER_CHUNK = 256
CHUNK_OVERLAP = 100

#* 1024 tokens to generate should be sufficient for Qwen and this task
MAX_NEW_TOKENS = 1024

#* To not exceed the already high Qwen context window (128K tokens)
#* I have added a limit to conversation history (1000 messages)
#* If a message on average could have 50-100 tokens
#* Then a reserved space for conversation history (100 * 1000 = 100K tokens) should be enough
#* And remaining 28K tokens are more than enough for retrieved 5 documents from the database and user query
#* But I can hardly imagine this limit being reached on this task
#* As the latency of the system becomes pretty annoying after 5 messages...
CONVERSATION_HISTORY_LIMIT = 1000

#* Some system prompts for Qwen to operate on. RAG task has a dedicated separate, task-based system prompt
GENERAL_SYSTEM_PROMPT = "You are a helpful assistant."
RAG_SYSTEM_PROMPT = """You are a helpful expert help center assistant.
Your users are asking questions about information help center articles.
You will be shown the user's question, and the relevant information from the help center articles.
Answer the user's question using only this information."""
QUESTIONS_SYSTEM_PROMPT = """You are a helpful expert help center assistant. Your users are asking questions about help center articles.
Suggest up to five additional related questions to help them find the information they need, for the provided question.
Suggest only short questions without compound sentences. Suggest a variety of questions that cover different aspects of the topic.
Make sure they are complete questions, and that they are related to the original question.
Output one question per line. Do not number the questions."""
ANSWER_SYSTEM_PROMPT = """You are a helpful expert help center assistant.
Provide an example answer to the given question, that might be found in a network, vpn, security or other related systems provider help center articles."""

#* The path to the JSON file containing the help center articles
DATA_ARTICLES_PATH = "chatbot/data/"
ASSESSMENT_RESULTS_PATH = "results/assessment_result.txt"

HF_CACHE_DIR = ".hf_cache"