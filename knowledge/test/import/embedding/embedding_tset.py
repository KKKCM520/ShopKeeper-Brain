from pymilvus.model.hybrid import BGEM3EmbeddingFunction

bge_m3 = BGEM3EmbeddingFunction(
    model_name="E:/atguigu/ai_models/bge-m3",
    device="cpu",
    use_fp16=False,
)


document_list = ["11111111"]


result = bge_m3.encode_documents(document_list)

print(result)