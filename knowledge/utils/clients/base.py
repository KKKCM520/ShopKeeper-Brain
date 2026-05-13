import os
import logging
import threading
from typing import TypeVar, Optional

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseClientManager:

    @staticmethod
    def _require_env(key: str) -> str:
        """读取必需的环境变量，缺失时立即抛异常。"""
        value = os.getenv(key)
        if not value:
            raise EnvironmentError(f"缺少必需的环境变量: {key}")
        return value

    @classmethod
    def _get_or_create(cls, attr_name: str, lock: threading.Lock, factory):
        # 第一次检查（无锁，快速路径）
        instance = getattr(cls, attr_name, None)
        if instance is not None:
            return instance

        with lock:
            # 第二次检查（持锁，防并发重复创建）
            instance = getattr(cls, attr_name, None)
            if instance is not None:
                return instance

            instance = factory()
            setattr(cls, attr_name, instance)
            return instance
