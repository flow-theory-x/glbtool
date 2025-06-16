"""GLB最適化のカスタム例外クラス"""


class GLBOptimizationError(Exception):
    """GLB最適化に関する基底例外クラス"""
    pass


class MeshProcessingError(GLBOptimizationError):
    """メッシュ処理に関する例外"""
    pass


class TextureProcessingError(GLBOptimizationError):
    """テクスチャ処理に関する例外"""
    pass


class SceneManagementError(GLBOptimizationError):
    """シーン管理に関する例外"""
    pass


class FileOperationError(GLBOptimizationError):
    """ファイル操作に関する例外"""
    pass


class ValidationError(GLBOptimizationError):
    """検証に関する例外"""
    pass