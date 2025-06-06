import os
from typing import Any

import openai
from google.adk.memory.base import BaseMemoryService
from google.adk.sessions import Session  # for type hints
from qdrant_client import QdrantClient
from qdrant_client.http.models import (Distance, Payload, PointStruct,
                                       VectorParams)


# -----------------------------------------------------------------------------
# QdrantMemoryService: stores session messages as vectors in Qdrant.
# -----------------------------------------------------------------------------
class QdrantMemoryService(BaseMemoryService):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "adk_memory",
        embedding_model: str = "text-embedding-3-small",
        vector_size: int = 1024,  # adjust based on the embedder’s output
        distance: Distance = Distance.COSINE,
    ):
        """- host, port: Qdrant server location.
        - collection_name: name of the collection in Qdrant to hold memory points.
        - embedding_model: OpenAI embedding model (or your own).
        - vector_size: dimensionality of each embedding.
        - distance: which distance metric Qdrant uses for search.
        """
        super().__init__()
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.vector_size = vector_size

        # Initialize Qdrant client
        self.client = QdrantClient(url=f"http://{self.host}:{self.port}")

        # Create (or verify) collection on Qdrant
        if not self.client.collections_api.get_collection(collection_name).result:
            self.client.collections_api.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )

        # OpenAI API key must be available in env
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def _embed_text(self, text: str) -> list[float]:
        """Use OpenAI's embeddings endpoint to convert text → vector.
        You can swap this out for another embedder as needed.
        """
        resp = openai.Embedding.create(
            model=self.embedding_model,
            input=text,
        )
        return resp["data"][0]["embedding"]

    def add_session_to_memory(self, session: Session) -> None:
        """Called by ADK after a session finishes.
        Break the session into messages (or combine) and push embeddings+payload to Qdrant.
        """
        points: list[PointStruct] = []
        for message in session.messages:
            # message.text contains the user/assistant turn
            # we can filter: only store user messages, or both; here we store both.
            text = message.text.strip()
            if not text:
                continue

            vector = self._embed_text(text)

            payload: Payload = {
                "session_id": session.session_id,
                "sender": message.role,  # "user" or "assistant"
                "timestamp": message.timestamp.isoformat(),
                "text": text,
            }

            # Use message.id or incrementing ID as unique point ID
            point_id = f"{session.session_id}::{message.id}"

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        if points:
            self.client.points_api.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def search_memory(
        self, query: str, top_k: int = 5, min_score: float = 0.0
    ) -> list[dict[str, Any]]:
        """Called by ADK to retrieve relevant “memory” given a query string.
        Returns a list of payloads (or however you want to format it).
        """
        query_vector = self._embed_text(query)

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=min_score,
        )

        results = []
        for hit in search_result:
            results.append(
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                }
            )
        return results

    # (Optional) Implement delete or other methods if BaseMemoryService requires them.
