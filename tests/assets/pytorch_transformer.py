from typing import List, Optional, Union

import numpy as np
import torch
import torch.nn.functional as func
from numpy.typing import NDArray
from torch import Tensor, nn
from transformers import AutoModel
from transformers import AutoTokenizer


def cos_sim(
    a: Union[Tensor, List[float], NDArray[np.float64]], b: Union[Tensor, List[float], NDArray[np.float64]]
) -> Tensor:

    if not isinstance(a, torch.Tensor):
        a = torch.tensor(a)

    if not isinstance(b, torch.Tensor):
        b = torch.Tensor(b)

    if len(a.shape) == 1:
        a = a.unsqueeze(0)

    if len(b.shape) == 1:
        b = b.unsqueeze(0)

    a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
    b_norm = torch.nn.functional.normalize(b, p=2, dim=1)
    return torch.mm(a_norm, b_norm.transpose(0, 1))


class SiameseTransformer(nn.Module):
    def __init__(  # type: ignore
        self,
        model_name_or_path: str,
        dropout: float,
        output_size: int,
        scale: float = 20.0,
        similarity_fct=cos_sim,
    ) -> None:
        super(SiameseTransformer, self).__init__()
        self.output_size = output_size
        self.dropout = nn.Dropout(dropout)
        self.new_los_fun = nn.CrossEntropyLoss()

        self.bert_model_query = AutoModel.from_pretrained(model_name_or_path)  # type: ignore
        self.query_dense = nn.Linear(self.bert_model_query.config.hidden_size, output_size)  # type: ignore

        self.similarity_fct = similarity_fct
        self.scale = scale

    @staticmethod
    def mean_pooling(model_output, attention_mask) -> torch.Tensor:  # type: ignore

        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def forward(
        self, input_ids: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:

        last_hidden_states = self.bert_model_query(  # type: ignore
            input_ids=input_ids, attention_mask=attention_mask, return_dict=False
        )
        query_embedding = self.mean_pooling(last_hidden_states, attention_mask)
        query_embedding = self.query_dense((query_embedding))

        return func.normalize(query_embedding, p=2, dim=1)


tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", do_lower_case=True)


def _get_tokens(query: str):
    tokens = tokenizer(
        [str(query).lower()],
        return_tensors="pt",
        return_offsets_mapping=True,
        is_split_into_words=False,
        padding=True,
        truncation=True,
    )

    product_input_ids = tokens["input_ids"].to(torch.device("cpu"))
    product_attention_mask = tokens["attention_mask"].to(torch.device("cpu"))

    return product_input_ids, product_attention_mask
