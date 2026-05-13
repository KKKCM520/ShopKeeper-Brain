import uvicorn
from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from starlette.staticfiles import StaticFiles

# from knowledge.core.deps import get_file_process_service
from knowledge.core.paths import get_front_page_dir
from knowledge.core.deps import get_file_process_service
from knowledge.service.file_process_service import FileProcessService
from knowledge.schema.upload_schema import UploadResponse, TaskStatusResponse
# from knowledge.service.file_process_service import FileProcessService
from knowledge.utils.task_util import get_task_info

#路由
file_process_service = FileProcessService()
def register_router(app: FastAPI):
    @app.get("/hello")
    def hello():
        return "Hello World!"

    @app.post("/upload",response_model=UploadResponse)
    def upload_file(file:UploadFile,
                    background_tasks: BackgroundTasks,
                    file_process_service:FileProcessService = Depends(get_file_process_service)):
        #1. 将上传的文件进行处理(保存)
        import_file_path,file_dir,task_id = file_process_service.process_upload_file(file)
        #2. 执行导入的主流程
        background_tasks.add_task(file_process_service.run_main_graph,import_file_path,file_dir,task_id)

        return UploadResponse(message="上传成功",task_id=task_id)

    @app.get("/status/{task_id}",response_model=TaskStatusResponse)
    def get_task_status(task_id: str):
        #1. 获取当前任务的信息
        task_info = get_task_info(task_id)

        return TaskStatusResponse(**task_info)


def create_app():
    app = FastAPI(
        description="掌柜智库导入api",
        version="1.0"
    )
#处理跨域问题
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ← 和 credentials=True 冲突
        allow_credentials=False,  # 自定义cookies Authorization  tsl客户端证书信息
        allow_methods=["*"],  # ← 和 credentials=True 冲突  GET(获取资源)  POST(新增)  DELETE（删除） PUT（修改）
        allow_headers=["*"],  # ← 和 credentials=True 冲突   自定义的头字段 token  content-type:application/json
    )
#挂载静态文件,也就是写静态资源的匹配路径
    front_dir = get_front_page_dir()
    app.mount("/front",StaticFiles(directory=front_dir))
    #注册路由
    register_router(app)
    return app
if __name__ == '__main__':
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)







