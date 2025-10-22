"""
Utils - Python通用工具库
包含各种实用工具类和函数，提高开发效率
"""
from __future__ import annotations
import datetime
import hashlib
import json
import os
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, Union

import psutil


class PerfMonitor:
    """
    性能监控器

    使用方式:
    1. 上下文管理器: with PerfMonitor() as monitor: ...
    2. 装饰器: @PerfMonitor.measure
    3. 手动控制: monitor = PerfMonitor(); monitor.start(); ...; monitor.stop()
    """

    def __init__(self, name: str = "Performance"):
        """
        初始化性能监控器

        Args:
            name: 监控任务名称，用于输出时的标识
        """
        self.name = name
        self.start_time: Optional[float] = None
        self.start_memory: Optional[int] = None
        self.end_time: Optional[float] = None
        self.end_memory: Optional[int] = None
        self.process = psutil.Process(os.getpid())
        self._is_running = False
        self._stats: Optional[dict[str, Any]] = None  # 保存统计信息

    def start(self) -> PerfMonitor:
        """开始监控"""
        if self._is_running:
            raise RuntimeError("监控器已经在运行中")

        # 强制垃圾回收以获得更准确的内存读数
        import gc

        gc.collect()

        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        self._is_running = True
        return self

    def stop(self) -> dict[str, Any]:
        """停止监控并返回统计数据"""
        if not self._is_running:
            raise RuntimeError("监控器尚未启动")

        if self.start_time is None or self.start_memory is None:
            raise RuntimeError("监控器数据不完整")

        self.end_time = time.time()
        self.end_memory = self.process.memory_info().rss
        self._is_running = False

        # 保存统计信息
        self._stats = self._calculate_stats()
        self.print_stats()
        return self._stats

    def _calculate_stats(self) -> dict[str, Any]:
        """计算统计数据"""
        if self.start_time is None or self.end_time is None or self.start_memory is None or self.end_memory is None:
            raise RuntimeError("数据不完整，无法计算统计信息")

        elapsed_ms = (self.end_time - self.start_time) * 1000
        memory_delta = self.end_memory - self.start_memory

        return {
            "name": self.name,
            "elapsed_ms": elapsed_ms,
            "memory_delta_bytes": memory_delta,
            "memory_delta_mb": memory_delta / 1024 / 1024,
            "final_memory_bytes": self.end_memory,
            "final_memory_mb": self.end_memory / 1024 / 1024,
        }

    def get_stats(self) -> dict[str, Any]:
        """获取性能统计数据"""
        if self._stats is not None:
            return self._stats

        if self.start_time is None or self.end_time is None or self.start_memory is None or self.end_memory is None:
            raise RuntimeError("没有可用的性能数据")

        return self._calculate_stats()

    def print_stats(self, prefix: str = "") -> None:
        """打印格式化的统计信息"""
        stats = self.get_stats()
        output = f"{prefix}=== {stats['name']} 性能统计 ===\n"
        output += f"{prefix}运行时间: {stats['elapsed_ms']:.2f}ms，"
        output += f"ΔMem: {stats['memory_delta_bytes']:,} bytes ({stats['memory_delta_mb']:.2f} MB)\n"
        output += f"{prefix}当前内存: {stats['final_memory_bytes']:,} bytes ({stats['final_memory_mb']:.2f} MB)"
        print(output)

    # 上下文管理器支持
    def __enter__(self) -> PerfMonitor:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    # 装饰器支持
    @staticmethod
    def measure(name: str = "Function"):
        """
        装饰器：自动测量函数性能

        使用方式:
        @PerfMonitor.measure("MyFunction")
        def my_function(): ...
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                monitor = PerfMonitor(name)
                monitor.start()
                try:
                    result = func(*args, **kwargs)
                finally:
                    monitor.stop()
                    monitor.print_stats()
                return result

            return wrapper

        return decorator


class FileUtils:
    """文件操作工具类"""

    @staticmethod
    def read_json(filepath: Union[str, Path], encoding: str = "utf-8") -> dict:
        """安全读取JSON文件"""
        filepath = Path(filepath)
        try:
            with filepath.open("r", encoding=encoding) as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {filepath}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误 in {filepath}: {e}")

    @staticmethod
    def write_json(data: dict, filepath: Union[str, Path], encoding: str = "utf-8", indent: int = 2) -> None:
        """写入JSON文件"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)

    @staticmethod
    def get_file_hash(filepath: Union[str, Path], algorithm: str = "md5") -> str:
        """计算文件哈希值"""
        filepath = Path(filepath)
        hash_func = getattr(hashlib, algorithm)()
        with filepath.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()


class StringUtils:
    """字符串处理工具类"""

    @staticmethod
    def get_display_width(text: str) -> int:
        """计算字符串的显示宽度（中文字符算2，英文字符算1）"""
        width = 0
        for char in text:
            if (
                    ("\u4e00" <= char <= "\u9fff")  # CJK统一汉字
                    or ("\u3000" <= char <= "\u303f")  # CJK标点符号
                    or ("\uff00" <= char <= "\uffef")  # 全角ASCII、全角标点
                    or ("\u2000" <= char <= "\u206f")  # 常用标点
                    or ("\u3200" <= char <= "\u32ff")  # 括号CJK字符
                    or ("\u3300" <= char <= "\u33ff")  # CJK兼容
                    or ("\u2e80" <= char <= "\u2eff")  # CJK部首补充
                    or ("\u3400" <= char <= "\u4dbf")  # CJK扩展A
                    or ("\u2f00" <= char <= "\u2fdf")  # 康熙部首
                    or char in "（）【】《》「」『』〈〉〔〕｛｝"
            ):
                width += 2
            else:
                width += 1
        return width

    @staticmethod
    def pad_to_width(text: str, target_width: int, fill_char: str = " ") -> str:
        """填充字符串到指定显示宽度"""
        current_width = StringUtils.get_display_width(text)
        padding_needed = target_width - current_width
        return text + fill_char * padding_needed


class Logger:
    """简单的日志记录器"""

    def __init__(self, name: str = "Logger", save_to_file: bool = False, filepath: Optional[Path] = None):
        self.name = name
        self.save_to_file = save_to_file
        self.filepath = filepath or Path(f"{name}_{datetime.datetime.now():%Y%m%d_%H%M%S}.log")
        self.logs: list[str] = []

    def log(self, message: str, level: str = "INFO") -> None:
        """记录日志"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"
        print(formatted_message)
        self.logs.append(formatted_message)

        if self.save_to_file:
            with self.filepath.open("a", encoding="utf-8") as f:
                f.write(formatted_message + "\n")

    def info(self, message: str) -> None:
        self.log(message, "INFO")

    def warning(self, message: str) -> None:
        self.log(message, "WARNING")

    def error(self, message: str) -> None:
        self.log(message, "ERROR")

    def get_logs(self) -> list[str]:
        """获取所有日志"""
        return self.logs.copy()
