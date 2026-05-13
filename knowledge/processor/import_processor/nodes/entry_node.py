import logging
import os
from pathlib import Path

from knowledge.processor.import_processor.base import BaseNode, T
from knowledge.processor.import_processor.exceptions import StateFieldError, ValidationError
from knowledge.processor.import_processor.state import ImportGraphState


class EntryNode(BaseNode):
    name = "entry_node"
    def process(self, state: ImportGraphState) -> ImportGraphState:
        # 1.获取state中的import_file_path,file_dir,并且判断是否为空
        self.log_step(step_name="Step1",message="获取state中的import_file_path,file_dir,并且判断是否为空")
        import_file_path = state.get("import_file_path")
        file_dir = state.get("file_dir")
        if not import_file_path:
            self.logger.error(f"import_file_path not found in state {state}")
            raise StateFieldError(node_name=self.name,field_name="import_file_path",expected_type=str)
        if not file_dir:
            self.logger.error(f"file_dir not found in state {state}")
            raise StateFieldError(node_name=self.name,field_name="file_dir",expected_type=str)

        # 2.判断import_file_path,file_dir是否真实存在
        self.log_step(step_name="Step2", message="判断import_file_path,file_dir是否真实存在")
        import_file_path_obj = Path(import_file_path)
        file_dir_obj = Path(file_dir)
        if not import_file_path_obj.exists():
            self.logger.error(f"import_file_path not exist")
            raise StateFieldError(node_name=self.name,field_name="import_file_path",expected_type=Path)
        if not file_dir_obj.exists():
            self.logger.error(f"file_dir not exist")
            raise StateFieldError(node_name=self.name,field_name="file_dir",expected_type=Path)
        # 3.判断文件类型
        self.log_step(step_name="Step3", message="判断文件类型")
        # 3.1获取文件后缀+判断文件后缀
        suffix = import_file_path_obj.suffix
        if suffix == ".pdf":
            #3.2.1 如果pdf文件, 则设is_pdf_enable为True, 设買pdf_path的值为import_file_path
            state ['is_pdf_read_enabled'] = True
            state ['pdf_path'] = import_file_path
        elif suffix == ".md":
            #3.2.2 如果是md文件,则设置is_md_enable为Ture,设md_path的值为import_file_path
            state ['is_md_read_enabled'] = True
            state ['md_path'] = import_file_path
        else:
            self.logger.error(f"unsupported suffix{suffix}")
            raise ValidationError(f"unsupported suffix{suffix}",node_name=self.name)
        #4.获取文件标题
        self.log_step(step_name="Step4"
                                ""
                                ""
                                ""
                                ""
                                "", message="获取文件标题")
        file_title = import_file_path_obj.stem
        # 4.1将文件标题设置到state中
        state ['file_title'] = file_title
        # 4.返回state
        return state

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    entry_node = EntryNode()
    init_state = {
        "import_file_path":r"E:\atguigu\demo\workspace_pycharm\ShopKeeper-Brain\knowledge\processor\import_processor\input_dir\万用表RS-12的使用.pdf",
        "file_dir":r"E:\atguigu\demo\workspace_pycharm\ShopKeeper-Brain\knowledge\processor\import_processor\output_dir"
    }

    state = entry_node(init_state)
    print(state)