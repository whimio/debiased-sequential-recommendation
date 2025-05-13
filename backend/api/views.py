from django.shortcuts import render
from rest_framework.views    import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
import torch
from .recommender import Recommender, DEFAULT_REC_ARGS
from recommender_core.utils import (
    recall_at_k, ndcg_k, coverage_at_k, apt_at_k, get_user_seqs
)
# 全局加载一次模型，改用 DEFAULT_REC_ARGS
rec = Recommender(
    model_path=settings.BASE_DIR / "TrainModel" / "SASRec-Tenrec-1-Exposure1.pt",
    args=DEFAULT_REC_ARGS,
    model_name="SASRec",
    device=torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
)

class PredictView(APIView):
    """
    原接口，接受 JSON：{"sequence":[...], "top_k":k}
    或者表单上传 .txt：file 字段 + 可选 top_k
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        # 优先看是否上传了文件
        upload = request.FILES.get("file")
        top_k = request.data.get("top_k", 20)
        try:
            top_k = int(top_k)
        except:
            return Response({"error": "top_k 必须是整数"}, status=status.HTTP_400_BAD_REQUEST)

        if upload:
            # 批量推荐
            recs = rec.recommend(upload, top_k=top_k)
            # 格式化返回：每行一个结果
            results = [
                {"line_index": idx, "recommendations": recs[idx]}
                for idx in range(len(recs))
            ]
            return Response({"batch_recommendations": results})

        # 否则按原来 JSON 单条推荐
        data = request.data
        seq = data.get("sequence", [])
        if not isinstance(seq, list) or not all(isinstance(i, int) for i in seq):
            return Response({"error": "sequence 必须是整数列表"},
                            status=status.HTTP_400_BAD_REQUEST)
        rec_list = rec.recommend(seq, top_k=top_k)
        return Response({"recommendations": rec_list})


class EvaluateView(APIView):
    """
    POST /api/evaluate/
    表单上传测试集 txt 文件（每行: item_id 空格分隔，最后一项为 ground-truth）。
    返回：两个模型在各 K 值下的 Recall、NDCG、Coverage、APT 指标。
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    parser_classes = [JSONParser, FormParser, MultiPartParser]  # 支持 JSON


    def post(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response({"error": "请上传测试集 txt 文件"}, status=status.HTTP_400_BAD_REQUEST)

        # 1）解析上传的 txt，每行转成 int 列表
        lines = upload.read().decode("utf-8").splitlines()
        all_seqs = []
        for ln in lines:
            if ln.strip():
                try:
                    seq = [int(tok) for tok in ln.strip().split()]
                    if len(seq) >= 2:
                        all_seqs.append(seq)
                except ValueError:
                    continue

        if not all_seqs:
            return Response({"error": "文件内容格式错误"}, status=status.HTTP_400_BAD_REQUEST)

        # 2）拆成 inputs + actuals
        inputs = [seq[:-1] for seq in all_seqs]
        actuals = [[seq[-1]] for seq in all_seqs]

        # 3）加载两个模型
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        path1 = settings.BASE_DIR / "TrainModel" / "SASRec-Tenrec-1-Exposure1.pt"  # 去偏
        path2 = settings.BASE_DIR / "TrainModel" / "SASRec-Tenrec-0-Exposure1.pt"  # 不去偏

        rec_debiased = Recommender(str(path1), DEFAULT_REC_ARGS, model_name="SASRec", device=device)  # :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
        rec_biased   = Recommender(str(path2), DEFAULT_REC_ARGS, model_name="SASRec", device=device)

        # 4）批量推荐（一次取最大的 K，然后在计算各 K 指标时截取前 K）
        MAX_K = 20
        preds_deb = [ rec_debiased.recommend(seq, top_k=MAX_K) for seq in inputs ]
        preds_b   = [ rec_biased.recommend(seq,   top_k=MAX_K) for seq in inputs ]

        # 5）计算各项指标
        ks = [5, 10, 20]
        metrics = {"debiased": {}, "biased": {}}
        for name, preds in [("debiased", preds_deb), ("biased", preds_b)]:
            for k in ks:
                r    = recall_at_k(actuals, preds, k)                         # :contentReference[oaicite:4]{index=4}:contentReference[oaicite:5]{index=5}
                n    = ndcg_k   (actuals, preds, k)                          # :contentReference[oaicite:6]{index=6}:contentReference[oaicite:7]{index=7}
                cov  = coverage_at_k(preds, k) / DEFAULT_REC_ARGS.item_size  # :contentReference[oaicite:8]{index=8}:contentReference[oaicite:9]{index=9}
                apt, aptp = apt_at_k(actuals, set(), preds, k)               # :contentReference[oaicite:10]{index=10}:contentReference[oaicite:11]{index=11}

                metrics[name][k] = {
                    "recall":    round(r,    4),
                    "ndcg":      round(n,    4),
                    "coverage":  round(cov,  4),
                    "apt":       round(apt,  4),
                    "apt_p":     round(aptp, 4),
                }

        return Response(metrics)