from django.shortcuts import render
from django.http import JsonResponse
import torch

from Recweb.settings import BASE_DIR
#from predictor.recmodel.model import ExposureModel
from predictor.recmodel.model import SASRec
from predictor.recmodel.utils import get_user_seqs, recall_at_k, ndcg_k
import os

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import numpy as np

#定义模型参数
class Args:
    hidden_size = 64
    max_length = 50
    item_size = 30827 + 2   #后续修改为正确的item
    nhead = 2
    nlayers = 2
    attention_probs_dropout_prob = 0.5
    initializer_range = 0.02
    exposure_model_name = 'mix'

args = Args()

#加载模型
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'recmodel','SASRec-ZhihuRec-1-Exposure1-2025-04-03-15_17_45.pt')  #后续替换成已经训练到最好的checkpoints

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = SASRec(args).to(device)  #  放到 GPU 上
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

#页面渲染
def index(request):
    return render(request, 'predictor/index.html')


#临时假数据
#后续接模型
@csrf_exempt
def predict(request):
    if request.method == "POST":
        seq_str = request.POST.get("sequence", "")
        try:
            input_seq = [int(i) for i in seq_str.split(',') if i.strip().isdigit()]
        except:
            return JsonResponse({'error': 'invalid input foramt'})

        #构造输入
        input_ids = input_seq[-args.max_length:]
        pad_len = args.max_length - len(input_ids)
        input_ids = input_ids + ([0] * pad_len)
        seq_pos = list(range(args.max_length))
        seq_len = len(input_seq)

        input_ids_tensor = torch.tensor([input_ids], dtype=torch.long)
        seq_pos_tensor = torch.tensor([seq_pos], dtype=torch.long)
        #seq_len_tensor = torch.tensor([seq_len], dtype=torch.long)

        with torch.no_grad():
            scores = model.predict(input_ids_tensor, seq_pos_tensor)
            prob_scores = torch.softmax(scores[0], dim=0)
            top_scores, top_indices = torch.topk(prob_scores, k=10)

            top_k = []
            for item_id_tensor,score_tensor in zip(top_indices, top_scores):
                item_id = int(item_id_tensor)
                score = float(score_tensor)
                top_k.append({
                    "item_id": item_id,
                    "score": round(score, 4)
                })


        return JsonResponse({'recommendations': top_k})

    return JsonResponse({'error': 'Only POST methods are allowed'})

#评估
@csrf_exempt
def evaluate_metrics(request):
    if request.method != "GET":
        return JsonResponse({'error': 'only GET is allowed'})

    #读验证集
    val_file = os.path.join(settings.BASE_DIR, 'data', 'zhihu1M', 'valid.txt')
    user_seqs, max_item, _ = get_user_seqs(val_file)

    actual = [[seq[-1] ]for seq in user_seqs]
    predicted = []

    for seq in user_seqs:
        input_ids = seq[:-1][-args.max_length:]
        pad_len = args.max_length - len(input_ids)
        input_ids = input_ids + ([0] * pad_len)
        seq_pos = list(range(args.max_length))

        input_ids_tensor = torch.tensor([input_ids], dtype=torch.long)
        seq_pos_tensor = torch.tensor([seq_pos], dtype=torch.long)

        with torch.no_grad():
            scores = model.predict(input_ids_tensor, seq_pos_tensor)
            topk_items = torch.topk(scores[0], k=10).indices.tolist()
            predicted.append(topk_items)

    recall = recall_at_k(actual, predicted, topk=10)
    ndcg = ndcg_k(actual, predicted, topk=10)

    return JsonResponse({
        'Recall@10': round(recall, 4),
        "NDCG@10": round(ndcg, 4),
    })

# Create your views here.
