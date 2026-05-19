import sys
import os
# 将项目根目录加入Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embedding.services.embedding_service import EmbeddingService


service = EmbeddingService()

vec = service.embed_query("苹果手机是什么")

print(len(vec))
print(vec[:10])
