"""入力検証とファイル検査機能"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
import trimesh

from .types import FilePath, ValidationResult
from .logger import get_logger


class FileValidator:
    """ファイル検証クラス"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def validate_input_file(self, file_path: FilePath) -> ValidationResult:
        """入力ファイルを検証"""
        errors = []
        
        # ファイル存在チェック
        if not os.path.exists(file_path):
            errors.append(f"ファイルが存在しません: {file_path}")
            return False, errors
        
        # ファイルサイズチェック
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                errors.append("ファイルサイズが0バイトです")
            elif file_size > 500 * 1024 * 1024:  # 500MB
                self.logger.warning(f"大きなファイルです: {file_size / 1024 / 1024:.1f}MB")
        except OSError as e:
            errors.append(f"ファイルサイズの取得に失敗: {e}")
        
        # 拡張子チェック
        path = Path(file_path)
        if path.suffix.lower() not in ['.glb', '.gltf']:
            errors.append(f"サポートされていない拡張子: {path.suffix}")
        
        # 読み取り権限チェック
        if not os.access(file_path, os.R_OK):
            errors.append("ファイルの読み取り権限がありません")
        
        return len(errors) == 0, errors
    
    def validate_output_path(self, output_path: FilePath) -> ValidationResult:
        """出力パスを検証"""
        errors = []
        
        # 出力ディレクトリの存在チェック
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                self.logger.info(f"出力ディレクトリを作成: {output_dir}")
            except OSError as e:
                errors.append(f"出力ディレクトリの作成に失敗: {e}")
        
        # 書き込み権限チェック
        if output_dir and not os.access(output_dir, os.W_OK):
            errors.append("出力ディレクトリへの書き込み権限がありません")
        
        # 出力ファイルが既に存在する場合の警告
        if os.path.exists(output_path):
            self.logger.warning(f"出力ファイルが既に存在します（上書きされます）: {output_path}")
        
        return len(errors) == 0, errors
    
    def validate_glb_content(self, file_path: FilePath) -> ValidationResult:
        """GLBファイルの内容を検証"""
        errors = []
        
        try:
            # Trimeshでロードを試行
            scene = trimesh.load(file_path)
            
            # シーンタイプのチェック
            if scene is None:
                errors.append("GLBファイルの読み込みに失敗")
                return False, errors
            
            # ジオメトリの存在チェック
            geometry_count = 0
            if hasattr(scene, 'geometry') and scene.geometry:
                geometry_count = len(scene.geometry)
            elif hasattr(scene, 'faces'):
                geometry_count = 1
            
            if geometry_count == 0:
                errors.append("有効なジオメトリが見つかりません")
            else:
                self.logger.info(f"ジオメトリ数: {geometry_count}")
            
            # 基本的な整合性チェック
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    geo_errors = self._validate_geometry(geometry, name)
                    errors.extend(geo_errors)
            elif hasattr(scene, 'vertices') and hasattr(scene, 'faces'):
                geo_errors = self._validate_geometry(scene, "main")
                errors.extend(geo_errors)
            
        except Exception as e:
            errors.append(f"GLBファイルの検証中にエラー: {e}")
        
        return len(errors) == 0, errors
    
    def _validate_geometry(self, geometry, name: str) -> List[str]:
        """個別ジオメトリを検証"""
        errors = []
        
        if not hasattr(geometry, 'vertices') or not hasattr(geometry, 'faces'):
            errors.append(f"{name}: 頂点または面データが不正")
            return errors
        
        vertex_count = len(geometry.vertices)
        face_count = len(geometry.faces)
        
        # 最小要件チェック
        if vertex_count < 3:
            errors.append(f"{name}: 頂点数が不足 ({vertex_count})")
        
        if face_count < 1:
            errors.append(f"{name}: 面数が不足 ({face_count})")
        
        # 面のインデックス範囲チェック
        if face_count > 0:
            max_index = geometry.faces.max()
            if max_index >= vertex_count:
                errors.append(f"{name}: 面のインデックスが頂点数を超過 ({max_index} >= {vertex_count})")
        
        return errors


class ParameterValidator:
    """パラメータ検証クラス"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def validate_target_ratio(self, ratio: float) -> ValidationResult:
        """target_ratioを検証"""
        errors = []
        
        if not isinstance(ratio, (int, float)):
            errors.append("target_ratioは数値である必要があります")
            return False, errors
        
        if not (0.01 <= ratio <= 1.0):
            errors.append(f"target_ratioは0.01-1.0の範囲で指定してください: {ratio}")
        
        if ratio < 0.1:
            self.logger.warning(f"target_ratioが小さいです({ratio})。品質が大幅に低下する可能性があります")
        
        return len(errors) == 0, errors
    
    def validate_mode(self, mode: str) -> ValidationResult:
        """最適化モードを検証"""
        errors = []
        
        valid_modes = ["normal", "aggressive", "ultra", "vertex", "repair"]
        
        if not isinstance(mode, str):
            errors.append("モードは文字列である必要があります")
            return False, errors
        
        if mode.lower() not in valid_modes:
            errors.append(f"無効なモード: {mode}. 有効なモード: {', '.join(valid_modes)}")
        
        return len(errors) == 0, errors
    
    def validate_quality_setting(self, quality: int, min_val: int = 1, max_val: int = 100) -> ValidationResult:
        """品質設定を検証"""
        errors = []
        
        if not isinstance(quality, int):
            errors.append("品質設定は整数である必要があります")
            return False, errors
        
        if not (min_val <= quality <= max_val):
            errors.append(f"品質設定は{min_val}-{max_val}の範囲で指定してください: {quality}")
        
        return len(errors) == 0, errors


# グローバルバリデーターインスタンス
_file_validator: Optional[FileValidator] = None
_param_validator: Optional[ParameterValidator] = None


def get_file_validator() -> FileValidator:
    """ファイルバリデーターを取得"""
    global _file_validator
    if _file_validator is None:
        _file_validator = FileValidator()
    return _file_validator


def get_parameter_validator() -> ParameterValidator:
    """パラメータバリデーターを取得"""
    global _param_validator
    if _param_validator is None:
        _param_validator = ParameterValidator()
    return _param_validator