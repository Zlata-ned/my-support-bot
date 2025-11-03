import logging
from database import Database
logger = logging.getLogger(__name__)

class SimpleRAG:
    def __init__(self, db: Database):
        self.db = db

    def search_relevant_chunks(self, user_id, query, max_results=3):
        query_words = query.lower().split()
        docs = self.db.get_user_documents(user_id)
        if not docs:
            return []

        relevant_chunks = []

        for doc in docs:
            content = doc['content'].lower()
            matches = sum(1 for word in query_words if word in content)
            if matches > 0:
                for word in query_words:
                    pos = content.find(word)
                    if pos != -1:
                        start = max(0, pos - 100)
                        end = min(len(content), pos + len(word) + 100)
                        context = content[start:end]
                        break

                relevant_chunks.append({
                    'filename': doc['filename'],
                    'content': context,
                    'relevance': matches

                })
        relevant_chunks.sort(key=lambda x: x['relevance'], reverse=True)
        return relevant_chunks[:max_results]

    def generate_answer_with_context(self, ai_manager, query, context_chunks):
        if not context_chunks:
            return None

        if isinstance(context_chunks[0], str):
            context = "\n\n".join([
                f"Из документа:\n{chunk}"
                for chunk in context_chunks
            ])
        elif isinstance(context_chunks[0], dict):
            context = "\n\n".join([
                f"Из документа '{chunk['filename']}':\n{chunk['content']}"
                for chunk in context_chunks
            ])
        else:
            return None
        prompt = f"""На основе следующей информации из документов ответь на вопрос.

        ДОКУМЕНТЫ:
        {context}

        ВОПРОС: {query}
        
        Ответь на вопрос, используя только информацию из документов выше. Если в документах нет ответа на поставленный вопрос, скажи об этом пользователю"""

        response = ai_manager.get_response(prompt)
        return response

rag_service = SimpleRAG(None)

