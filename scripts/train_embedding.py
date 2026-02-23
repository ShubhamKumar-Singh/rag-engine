"""Training skeleton for fine-tuning sentence-transformers embeddings.

This is a minimal script showing how to fine-tune a model on pairs/triplets.
It is intentionally small; adapt for real training with proper datasets and evaluation.
"""
from sentence_transformers import SentenceTransformer, losses, InputExample, models
from torch.utils.data import DataLoader
import json
from pathlib import Path


def load_pairs(path: Path):
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            q = obj.get("query")
            pos = obj.get("positive_text") or obj.get("positive_id")
            # For demo, we'll treat positive_id as text placeholder
            pairs.append(InputExample(texts=[q, str(pos)]))
    return pairs


def train(data_path: Path = Path("data/train_pairs.jsonl"), base_model: str = "all-MiniLM-L6-v2", out_dir: str = "models/emb-ft"):
    train_examples = load_pairs(data_path)
    if not train_examples:
        print("No training data found; run scripts/prepare_training_data.py first")
        return

    model = SentenceTransformer(base_model)
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
    train_loss = losses.CosineSimilarityLoss(model)

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=1,
        warmup_steps=10,
        output_path=out_dir
    )
    print(f"Saved fine-tuned model to {out_dir}")


if __name__ == "__main__":
    train()
