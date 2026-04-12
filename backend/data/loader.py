from __future__ import annotations

from typing import Dict, Iterable, List

from config.settings import Settings


class BloombergDataLoader:
    """Loads and normalizes a fixed-size Bloomberg subset for all pipelines."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cache: List[Dict] | None = None

    def _infer_text_column(self, sample: Dict) -> str:
        if "Article" in sample:
            return "Article"
        for key, value in sample.items():
            if isinstance(value, str):
                return key
        raise ValueError("No string article column found in dataset sample")

    def iter_articles(self, limit: int | None = None) -> Iterable[Dict]:
        from datasets import load_dataset

        max_items = limit or self.settings.dataset_subset_size
        stream = load_dataset(
            self.settings.dataset_name,
            split=self.settings.dataset_split,
            streaming=True,
        )
        iterator = iter(stream)
        first = next(iterator)
        text_col = self._infer_text_column(first)

        def _to_record(idx: int, row: Dict) -> Dict:
            return {
                "article_id": idx,
                "headline": str(row.get("Headline", "")),
                "text": str(row.get(text_col, "")),
                "date": str(row.get("Date", "")),
            }

        produced = 0
        first_record = _to_record(produced, first)
        if len(first_record["text"].strip()) > 30:
            yield first_record
            produced += 1

        for row in iterator:
            if produced >= max_items:
                break
            record = _to_record(produced, row)
            if len(record["text"].strip()) <= 30:
                continue
            yield record
            produced += 1

    def load_subset(self, force_refresh: bool = False) -> List[Dict]:
        if self._cache is not None and not force_refresh:
            return self._cache
        self._cache = list(self.iter_articles())
        return self._cache
