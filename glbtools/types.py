"""GLB最適化ツールの型定義"""

from typing import Dict, List, Tuple, Union, Optional, Any, Protocol
from enum import Enum
import trimesh
import numpy as np


class OptimizationMode(Enum):
    """最適化モード"""
    NORMAL = "normal"
    AGGRESSIVE = "aggressive"
    ULTRA = "ultra"
    VERTEX = "vertex"
    REPAIR = "repair"


class ProcessingResult(Enum):
    """処理結果"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PARTIAL = "partial"


# Trimesh関連の型エイリアス
Scene = Union[trimesh.Scene, Any]
Geometry = Union[trimesh.Trimesh, Any]
Vertices = np.ndarray
Faces = np.ndarray
Material = Any

# 処理結果の型定義
MeshProcessingResult = Tuple[bool, int, int]  # (success, original_count, new_count)
HoleDetectionResult = List[str]  # 検出された問題のリスト
ValidationResult = Tuple[bool, List[str]]  # (is_valid, error_messages)

# 統計情報の型定義
ProcessingStats = Dict[str, Union[int, float, str]]
OptimizationSummary = Dict[str, Any]

# 設定関連の型定義
ConfigDict = Dict[str, Union[int, float, str, bool]]
ModeConfig = Dict[str, Union[float, int]]

# ファイル処理関連の型定義
FilePath = str
FileSize = int
CompressionRatio = float


class OptimizationProtocol(Protocol):
    """最適化処理のプロトコル"""
    
    def optimize(self, input_path: FilePath, output_path: FilePath, **kwargs) -> bool:
        """最適化を実行する"""
        ...


class ProcessorProtocol(Protocol):
    """プロセッサーのプロトコル"""
    
    def process(self, geometry: Geometry, **kwargs) -> bool:
        """ジオメトリを処理する"""
        ...