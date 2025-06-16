"""
GLB最適化ツールライブラリ

リファクタリングされたGLB最適化機能を提供するパッケージ
"""

from .config import OptimizationConfig, get_mode_config, validate_target_ratio
from .glb_optimizer import GLBOptimizer
from .mesh_processor import MeshProcessor
from .texture_processor import TextureProcessor
from .scene_manager import SceneManager
from .logger import GLBLogger, get_logger, set_log_level, enable_file_logging
from .progress import ProgressTracker, PerformanceMonitor, get_performance_monitor
from .validators import FileValidator, ParameterValidator, get_file_validator, get_parameter_validator
from .types import OptimizationMode, ProcessingResult, MeshProcessingResult, HoleDetectionResult
from .exceptions import (
    GLBOptimizationError,
    MeshProcessingError,
    TextureProcessingError,
    SceneManagementError,
    FileOperationError,
    ValidationError
)

__version__ = "1.0.0"
__author__ = "GLB Tools Development Team"

__all__ = [
    # Core classes
    "OptimizationConfig",
    "GLBOptimizer",
    "MeshProcessor",
    "TextureProcessor", 
    "SceneManager",
    
    # Logging and monitoring
    "GLBLogger",
    "get_logger",
    "set_log_level",
    "enable_file_logging",
    "ProgressTracker",
    "PerformanceMonitor",
    "get_performance_monitor",
    
    # Validation
    "FileValidator",
    "ParameterValidator",
    "get_file_validator",
    "get_parameter_validator",
    
    # Types and enums
    "OptimizationMode",
    "ProcessingResult",
    "MeshProcessingResult",
    "HoleDetectionResult",
    
    # Utility functions
    "get_mode_config", 
    "validate_target_ratio",
    
    # Exceptions
    "GLBOptimizationError",
    "MeshProcessingError",
    "TextureProcessingError",
    "SceneManagementError",
    "FileOperationError",
    "ValidationError"
]