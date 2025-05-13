from argparse import Namespace
import torch

# —— 默认模型超参数 —— #
DEFAULT_REC_ARGS = Namespace(
    hidden_size=64,
    nhead=2,
    nlayers=2,
    attention_probs_dropout_prob=0.5,
    max_length=50,
    item_size=24655,
    initializer_range=0.02,
)

from recommender_core.models import SASRec, GRU4Rec
from recommender_core.utils import set_seed

class Recommender:
    def __init__(self,
                 model_path: str,
                 args: Namespace = DEFAULT_REC_ARGS,
                 model_name: str = "SASRec",
                 device: torch.device = None):
        set_seed(42)
        self.device     = device if device is not None else (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        self.model_name = model_name.lower()

        if self.model_name == "sasrec":
            self.model = SASRec(args).to(self.device)
        elif self.model_name == "gru4rec":
            self.model = GRU4Rec(args).to(self.device)
        else:
            raise ValueError(f"不支持的模型类型：{model_name}")

        state_dict = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.max_len = args.max_length

    def _single_recommend(self, seq: list[int], top_k: int) -> list[int]:
        # 原 recommend 的逻辑，输入一个列表，输出一个列表
        # 1. 截断 + padding
        seq_cut = seq[-self.max_len:]
        pad_len = self.max_len - len(seq_cut)
        seq_input = [0] * pad_len + seq_cut
        token_ids = torch.tensor([seq_input], dtype=torch.long, device=self.device)

        # 2. 分支模型
        if self.model_name == "sasrec":
            pos_ids = torch.arange(self.max_len, device=self.device).unsqueeze(0)
            with torch.no_grad():
                seq_out = self.model.predict(token_ids, pos_ids)
        else:  # GRU4Rec
            real_len = torch.tensor([min(len(seq), self.max_len)],
                                    dtype=torch.long,
                                    device=self.device)
            with torch.no_grad():
                seq_out = self.model.predict(token_ids, real_len)

        # 3. 打分 & 屏蔽
        scores = torch.matmul(seq_out,
                              self.model.token_emb.weight.t()).squeeze(0)
        scores[token_ids[0]] = -1e9

        # 4. Top-K
        return torch.topk(scores, top_k).indices.tolist()

    def recommend(self, data, top_k: int = 20):
        """
        支持两种输入：
        1) 列表：单条推荐 -> 返回 List[int]
        2) 文本文件（路径 str 或 file-like）：批量推荐 -> 返回 List[List[int]]
        """
        # 批量：file path or file-like
        if (isinstance(data, str) and data.endswith(".txt")) or hasattr(data, "read"):
            # 打开方式
            if isinstance(data, str):
                f = open(data, "r", encoding="utf-8")
                close_after = True
            else:
                f = data
                f.seek(0)
                close_after = False

            results = []
            for line in f:
                line = line.strip()
                if not line:
                    results.append([])  # 空行对应空结果
                    continue
                try:
                    seq = [int(tok) for tok in line.split()]
                except ValueError:
                    results.append([])  # 非法行也返回空
                    continue
                results.append(self._single_recommend(seq, top_k))

            if close_after:
                f.close()
            return results

        # 单条：按原逻辑
        if not isinstance(data, list) or not all(isinstance(i, int) for i in data):
            raise ValueError("单条推荐时，data 必须是 List[int]")
        return self._single_recommend(data, top_k)

