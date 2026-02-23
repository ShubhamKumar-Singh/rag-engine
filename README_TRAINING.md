Training your own embedding model (overview)

1. Prepare data
- Use `scripts/prepare_training_data.py` to generate synthetic pairs, or collect real query→relevant product pairs.

2. Train
- Run `python scripts/train_embedding.py` to fine-tune a sentence-transformers model (adjust `data_path`, `base_model`, and training hyperparams`).

3. Deploy
- After training, update `src/config.py` `MODEL_VERSION` to a new tag (e.g., `emb-v2`) and place the trained model where `sentence-transformers` can load it (or set EMBEDDINGS_MODEL to the new path).
- Restart the app; the startup indexing will re-embed products where the `embedding_hash` no longer matches.

Notes
- Real-world training requires careful evaluation, proper positive/negative sampling, and GPU resources.
