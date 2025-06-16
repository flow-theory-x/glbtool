"""進捗表示とパフォーマンス監視機能"""

import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
from .logger import get_logger


class ProgressTracker:
    """進捗追跡クラス"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.logger = get_logger()
        self.step_times: list[float] = []
    
    def update(self, step: int = 1, message: Optional[str] = None):
        """進捗を更新"""
        self.current_step += step
        
        # 進捗率を計算
        progress_ratio = min(self.current_step / self.total_steps, 1.0)
        percentage = progress_ratio * 100
        
        # 経過時間と予想残り時間を計算
        elapsed_time = time.time() - self.start_time
        if progress_ratio > 0:
            estimated_total_time = elapsed_time / progress_ratio
            remaining_time = estimated_total_time - elapsed_time
        else:
            remaining_time = 0
        
        # 進捗バーを作成
        bar_length = 30
        filled_length = int(bar_length * progress_ratio)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # メッセージを構築
        status_msg = f"{self.description}: [{bar}] {percentage:.1f}% ({self.current_step}/{self.total_steps})"
        
        if remaining_time > 60:
            time_msg = f" - 残り約{remaining_time/60:.1f}分"
        elif remaining_time > 0:
            time_msg = f" - 残り約{remaining_time:.0f}秒"
        else:
            time_msg = ""
        
        if message:
            status_msg += f" - {message}"
        
        status_msg += time_msg
        
        self.logger.progress(status_msg)
        
        # ステップ時間を記録
        self.step_times.append(elapsed_time)
    
    def finish(self, message: Optional[str] = None):
        """処理完了を報告"""
        total_time = time.time() - self.start_time
        
        if message:
            self.logger.success(f"{self.description}完了: {message} (所要時間: {total_time:.2f}秒)")
        else:
            self.logger.success(f"{self.description}完了 (所要時間: {total_time:.2f}秒)")
        
        # 平均処理時間を計算
        if len(self.step_times) > 1:
            avg_step_time = total_time / len(self.step_times)
            self.logger.stats(f"平均ステップ時間: {avg_step_time:.3f}秒/ステップ")


class PerformanceMonitor:
    """パフォーマンス監視クラス"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.logger = get_logger()
    
    @contextmanager
    def measure(self, operation_name: str):
        """操作時間を測定するコンテキストマネージャー"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            duration = end_time - start_time
            memory_delta = end_memory - start_memory if start_memory and end_memory else 0
            
            self.metrics[operation_name] = {
                'duration': duration,
                'memory_delta': memory_delta,
                'timestamp': start_time
            }
            
            self.logger.stats(f"{operation_name}: {duration:.3f}秒")
            if memory_delta > 0:
                self.logger.stats(f"{operation_name}: メモリ使用量 +{memory_delta:.1f}MB")
    
    def _get_memory_usage(self) -> Optional[float]:
        """メモリ使用量を取得（MB単位）"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        if not self.metrics:
            return {}
        
        total_duration = sum(m['duration'] for m in self.metrics.values())
        total_memory = sum(m['memory_delta'] for m in self.metrics.values() if m['memory_delta'] > 0)
        
        return {
            'total_duration': total_duration,
            'total_memory_delta': total_memory,
            'operation_count': len(self.metrics),
            'operations': self.metrics
        }
    
    def log_summary(self):
        """パフォーマンスサマリーをログ出力"""
        summary = self.get_summary()
        if not summary:
            return
        
        self.logger.stats("=== パフォーマンスサマリー ===")
        self.logger.stats(f"総処理時間: {summary['total_duration']:.3f}秒")
        self.logger.stats(f"実行操作数: {summary['operation_count']}個")
        
        if summary['total_memory_delta'] > 0:
            self.logger.stats(f"総メモリ使用量: {summary['total_memory_delta']:.1f}MB")
        
        # 最も時間のかかった操作
        slowest_op = max(summary['operations'].items(), key=lambda x: x[1]['duration'])
        self.logger.stats(f"最長処理: {slowest_op[0]} ({slowest_op[1]['duration']:.3f}秒)")


# グローバルパフォーマンスモニター
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """グローバルパフォーマンスモニターを取得"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor