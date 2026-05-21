import asyncio
from typing import Tuple

from knowledge.processor.query_processor.base import BaseNode, T
from knowledge.processor.query_processor.exceptions import StateFieldError
from knowledge.processor.query_processor.state import QueryGraphState


class WebSearchNode(BaseNode):
    def __init__(self, name:str, node:BaseNode):
        super().__init__(name)
        self.node = node
    def process(self, state: QueryGraphState) -> QueryGraphState:
        #1. 参数校验:都要校验什么参数呢?::
            # state+rewritten_query和item_names,这两个参数是在上一个节点产出的,要新定义方法才能拿到.
           # 这个节点要把它们作为起始值放在搜索方法里,再调用这两个参数,随后返回搜索后的结果.
          # 在_validate_state方法就是拿到这两个参数并校验的
        rewritten_query,item_names = self._validate_state(state)
        #2. 调用mcp工具进行网络检索::
        #这一步又重新定义了一个方法,该方法的作用就是
        execute_tool_result = asyncio.run(self.mcp_web_search(rewritten_query))
        #3. 对mcp检索的结果进行格式化
        #3.1 获取查询结果中的text，这其实就是一个json字符串
        #3.2 对json字符串进行反序列化
        #3.3 取出pages
        #声明一个存储web_search结果的容器
        #3.4 遍历pages
        #4. 将web_search_docs存入state中

    def _validate_state(self, state:QueryGraphState):
        #1.获取rewritten_query和item_names
        rewritten_query = state.get("rewritten_query")
        item_names = state.get("item_names")
        #2.校验两者
        if not rewritten_query or not isinstance(rewritten_query, str):
            self.logger.error("rewritten_query is not a string and cannot be None")
            raise StateFieldError(node_name=self.name,field_name="rewritten_query",expected_type=str)
        if not item_names or not isinstance(item_names, list):
            self.logger.error("item_names is not a list and cannot be None")
            raise StateFieldError(node_name=self.name,field_name="item_names",expected_type=list)
        return rewritten_query, item_names

    def mcp_web_search(self, rewritten_query:str):
        pass
