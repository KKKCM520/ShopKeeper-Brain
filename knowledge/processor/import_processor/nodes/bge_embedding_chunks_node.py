import json
from pathlib import Path
from typing import Any, Dict, List

from knowledge.processor.import_processor.base import BaseNode
from knowledge.processor.import_processor.exceptions import StateFieldError, EmbeddingError
from knowledge.processor.import_processor.state import ImportGraphState
from knowledge.utils.clients.ai_clients import AIClients
from knowledge.utils.clients.embedding_util import generate_bge_m3_hybrid_vectors


class BgeEmbeddingChunksNode(BaseNode):
    name = "bge_embedding_chunks_node"
    #node6:chunks向量化节点:将之前chunks中的内容进行向量化
    # 1.创建向量模型对象
    # 2.调用工具类的方法生成稠密向量和稀疏向量
    # 3.将稠密向量与稀疏向量设置到chunks的每一个chunk中
    def process(self,state: ImportGraphState) -> ImportGraphState:
        #1.参数校验
        chunks = self._validate(state)
        #2.每一个切都片嵌入成向量
        final_chunks = self.embedding_chunks(chunks)
        #3.将final_chunks更新到state中
        state["chunks"] = final_chunks
   #     print(json.dumps(final_chunks, indent=4, ensure_ascii=False))
        #4.将final_chunks备份成json文件(方便后续节点单独测试)
        self._backup_chunks(final_chunks, state)
        return state

    def _validate(self,state: ImportGraphState):
        #1.获取chunks
        chunks = state.get("chunks")
        #2.校验chunks
        if not chunks or not isinstance(chunks, list):
            self.logger.error("chunks is not a list")
            raise StateFieldError(node_name=self.name,field_name="chunks",expected_type=list)
        #3.校验每一个chunk的类型
        for chunk in chunks:
            if not isinstance(chunk, dict):
                self.logger.error("chunk is not a dictionary")
                raise StateFieldError(node_name=self.name,field_name="chunks",expected_type=list)
        #4.返回chunks
        return chunks

    def embedding_chunks(self,chunks:List[Dict[str,Any]]):
        #1.获取嵌入模型对象
        try:
            embedding_client = AIClients.get_bge_m3_client()
        except Exception as e:
            self.logger.error(f"获取嵌入模型对象失败:{e}")
            raise EmbeddingError(node_name=self.name,message=f"获取嵌入模型对象失败:{e}")

        #2.按批次进行批量嵌入
        #2.1获取batch_size
        embedding_batch_size = self.config.embedding_batch_size
        #2.2获取chunks的长度
        total_length = len(chunks)
        #2.3声明final_chunks用来存储向量化后的chunks
        final_chunks = []
        #2.4遍历chunks,步长应该是embedding_batch_size,这样就可以按批次进行向量化
        for i in range(0,total_length,embedding_batch_size):
            #2.4.1获取当前批次的chunk
            batch_chunks = chunks[i:i+embedding_batch_size]
            #2.4.2.1 将每一个chunk的item_name和content拼接成字符串
            document_list = [f"{chunk.get('item_name')}\n{chunk.get('content')}" for chunk in batch_chunks]
            #2.2.4.2 对document_list进行向量化
            try:
                embedding_result = generate_bge_m3_hybrid_vectors(embedding_client, document_list)
            except Exception as e:
                self.logger.error(f"嵌入向量失败{e}")
                raise EmbeddingError(node_name=self.name,message=f"嵌入向量失败{e}")
            #2.2.4.3从result 中获取稠密和稀疏向量
            dense_vector_list = embedding_result.get("dense")
            sparse_vector_list = embedding_result.get("sparse")

            #2.4.3遍历batch_chunks
            for i,chunk in enumerate(batch_chunks):
                #组装新的chunks,包括稠密和稀疏向量的chunks
                chunk["dense_vector"] = dense_vector_list[i]
                chunk["sparse_vector"] = sparse_vector_list[i]
                final_chunks.append(chunk)

        return final_chunks

    def _backup_chunks(self,final_chunks:List[Dict[str,Any]],state:ImportGraphState):
        md_path = state.get("md_path")
        md_path_obj = Path(md_path)
        file_dir = state.get("file_dir")
        file_dir_obj = Path(file_dir)
        backup_dir = file_dir_obj / md_path_obj.stem
        # 1.2 判断该目录是否真实存在，如果不存在则创建目录
        backup_dir.mkdir(parents=True, exist_ok=True)
        # 1.3 指定备份文件的路径
        backup_file_path = backup_dir / "chunks_vector.json"

        # 2. 将chunks写入到备份文件中
        try:
            with open(backup_file_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.warning(f"{md_path_obj.stem}文件备份成chunks_vector.json失败,但是不影响主流程")

if __name__ == '__main__':
    #1.获取chunks_item_name.json的内容
    json_path = r"E:\atguigu\demo\workspace_pycharm\ShopKeeper-Brain\knowledge\processor\import_processor\output_dir\万用表RS-12的使用\chunks_item_name.json"
    with open(json_path,"r",encoding="utf-8") as f:
        chunks = json.load(f)
    node = BgeEmbeddingChunksNode()
    state = {
        "chunks": chunks,
        "md_path": r"E:\atguigu\demo\workspace_pycharm\ShopKeeper-Brain\knowledge\processor\import_processor\output_dir\万用表RS-12的使用\万用表RS-12的使用.md",
        "file_dir": r"E:\atguigu\demo\workspace_pycharm\ShopKeeper-Brain\knowledge\processor\import_processor\output_dir"
    }
    node(state)
















