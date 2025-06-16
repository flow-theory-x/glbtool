"""GLB最適化ツールのログ機能"""

import logging
import sys
from typing import Optional
from pathlib import Path


class GLBLogger:
    """GLB最適化専用のログクラス"""
    
    def __init__(self, name: str = "glbtools", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # ハンドラーが既に存在する場合は追加しない
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """ログハンドラーを設定"""
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # フォーマッター
        formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def add_file_handler(self, log_file: Path):
        """ファイルハンドラーを追加"""
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(detailed_formatter)
        
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, *args, **kwargs):
        """情報ログ"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告ログ"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """エラーログ"""
        self.logger.error(message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """デバッグログ"""
        self.logger.debug(message, *args, **kwargs)
    
    def success(self, message: str, *args, **kwargs):
        """成功ログ（緑色）"""
        self.info(f"✓ {message}", *args, **kwargs)
    
    def failure(self, message: str, *args, **kwargs):
        """失敗ログ（赤色）"""
        self.error(f"✗ {message}", *args, **kwargs)
    
    def progress(self, message: str, *args, **kwargs):
        """進捗ログ（青色）"""
        self.info(f"🔄 {message}", *args, **kwargs)
    
    def stats(self, message: str, *args, **kwargs):
        """統計ログ（黄色）"""
        self.info(f"📊 {message}", *args, **kwargs)


# グローバルロガーインスタンス
_global_logger: Optional[GLBLogger] = None


def get_logger() -> GLBLogger:
    """グローバルロガーを取得"""
    global _global_logger
    if _global_logger is None:
        _global_logger = GLBLogger()
    return _global_logger


def set_log_level(level: int):
    """ログレベルを設定"""
    logger = get_logger()
    logger.logger.setLevel(level)


def enable_file_logging(log_file: Path):
    """ファイルログを有効化"""
    logger = get_logger()
    logger.add_file_handler(log_file)