"""GLB最適化の設定値管理"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class OptimizationConfig:
    """最適化設定"""
    # テクスチャ圧縮設定
    webp_quality_normal: int = 85
    webp_quality_aggressive: int = 70
    webp_resize_factor: float = 0.75
    min_texture_size: int = 64
    
    # メッシュ簡略化設定
    min_face_ratio: float = 0.5
    safe_face_ratio: float = 0.8
    min_face_count: int = 100
    
    # ファイルサイズ設定
    min_output_size: int = 1000
    abnormal_size_ratio: float = 0.005
    
    # 頂点処理設定
    merge_vertex_threshold: float = 1e-6
    
    # パフォーマンス設定
    max_repair_time_seconds: int = 30  # 修復処理の最大時間
    enable_complex_hole_filling: bool = False  # 複雑な穴埋めを無効化
    max_processing_time_seconds: int = 300  # 全体処理の最大時間（5分）
    enable_progress_bar: bool = True  # 進捗バー表示
    enable_performance_monitoring: bool = True  # パフォーマンス監視
    
    # ログ設定
    log_level: str = "INFO"  # ログレベル
    enable_file_logging: bool = False  # ファイルログ出力
    log_file_path: str = "glbtools.log"  # ログファイルパス
    
    # 検証設定
    strict_validation: bool = True  # 厳密な入力検証
    max_file_size_mb: int = 500  # 最大ファイルサイズ（MB）


# モード別のデフォルト設定
MODE_CONFIGS: Dict[str, Dict[str, float]] = {
    "normal": {
        "target_ratio": 0.7,
        "webp_quality": 85,
        "resize_factor": 1.0,
    },
    "aggressive": {
        "target_ratio": 0.3,
        "webp_quality": 85,
        "resize_factor": 1.0,
    },
    "ultra": {
        "target_ratio": 0.1,
        "webp_quality": 70,
        "resize_factor": 0.75,
    },
    "vertex": {
        "target_ratio": 1.0,
        "webp_quality": 85,
        "resize_factor": 1.0,
    },
    "repair": {
        "target_ratio": 1.0,
        "webp_quality": 85,
        "resize_factor": 1.0,
    },
}


def get_mode_config(mode: str) -> Tuple[float, Dict[str, float]]:
    """モードに応じた設定を取得"""
    if mode not in MODE_CONFIGS:
        mode = "normal"
    
    config = MODE_CONFIGS[mode]
    return config["target_ratio"], config


def validate_target_ratio(ratio: float) -> bool:
    """target_ratioの妥当性をチェック"""
    return 0.05 <= ratio <= 1.0