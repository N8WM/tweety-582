"""Utility functions for handling embeddings"""

import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def similarity_rankings(single, matrix, k=None):
    """
    Compute top-k cosine similarity between two sets of embeddings.

    Args:
    - `single` (`numpy.ndarray`): A single vector containing the embedding to
      compare.
    - `matrix` (`torch.Tensor`): Tensor containing the set of embeddings to
      compare.
    - `k` (`int`, optional): Number of top similarities to retrieve. If None, all
      similarities are returned.

    Returns:
    - `list[torch.Tensor], list[torch.Tensor]`: Tensors where each row
      corresponds to an embedding in single, and contains the indices of the
      top-k most similar embeddings in matrix, and tensors with cosine
      similarities corresponding to the indices.
    """
    single = single.unsqueeze(0)

    assert single.size(-1) == matrix.size(-1), (
        f"Dimensions of single ({single.size(-1)}) and matrix "
        + f"({matrix.size(-1)}) do not match."
    )

    cosine_similarity_matrix = F.cosine_similarity(
        single.unsqueeze(1), matrix.unsqueeze(0), dim=2
    )

    rankings = list(
        torch.argsort(cosine_similarity_matrix, dim=1, descending=True).squeeze(0)
    )
    rankings = rankings[:k] if k else rankings
    cosines = [cosine_similarity_matrix.squeeze(0)[i] for i in rankings]

    return rankings, cosines


def embed(text: str) -> torch.Tensor:
    """
    Embed a given text using the SentenceTransformer model.
    Args:
    - `text` (`str`): The text to embed.
    Returns:
    - `torch.Tensor`: A tensor containing the embedding of the given text.
    """
    return torch.tensor(embedding_model.encode(text))


def most_similar(query: str, queries: torch.Tensor) -> tuple[int, float]:
    """
    Find the index of the most similar query to the given query, and how
    similar.
    Args:
    - `query` (`str`): The query to compare.
    - `queries` (`list[str] | torch.Tensor`): A list of queries to compare
      against, or a tensor of embeddings of the queries.
    Returns:
    - `int, float`: The index of the most similar query in `queries`, and its
      similarity score.
    """
    qemb = embed(query)
    qembs = queries
    result = similarity_rankings(qemb, qembs, 1)
    return int(result[0][0]), float(result[1][0])


if __name__ == "__main__":
    # Test similarity_rankings
    s = torch.tensor([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    m = torch.tensor(
        [
            [0.1, 0.2, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8],
            [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
            [0.5, 0.1, 0.4, 0.9, 0.2, 0.5, 0.1, 0.0],
            [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2],
        ]
    )
    print(similarity_rankings(s, m, 3))

    # Test embed
    qs = [
        "What's the name of the song?",
        "What is the artist of the song?",
        "When is that song from?",
    ]
    q_emb = torch.stack([embed(q) for q in qs])
    u_query = input("Enter a query: ")
    u_emb = embed(u_query)
    sim = most_similar(u_query, q_emb)
    ph = qs[sim[0]]
    cs = sim[1]
    print(f"Most similar to: {ph}\nSimilarity: {cs}")
