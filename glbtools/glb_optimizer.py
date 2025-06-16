"""GLB最適化のメインクラス"""

import os
import trimesh
from typing import Tuple, Optional

from .config import OptimizationConfig, get_mode_config
from .mesh_processor import MeshProcessor
from .texture_processor import TextureProcessor
from .scene_manager import SceneManager


class GLBOptimizer:
    """GLB最適化のメインクラス"""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.mesh_processor = MeshProcessor(self.config)
        self.texture_processor = TextureProcessor(self.config)
        self.scene_manager = SceneManager()
    
    def optimize_safe(self, input_path: str, output_path: str, target_faces_ratio: float = 0.5) -> bool:
        """安全なGLB最適化（テクスチャとマテリアルを保持）"""
        try:
            # GLBをシーンとしてロード
            scene = trimesh.load(input_path)
            print(f"[i] シーンタイプ: {type(scene)}")
            
            if hasattr(scene, 'geometry') and scene.geometry:
                # 複数のメッシュを持つシーンの場合
                total_original = 0
                total_simplified = 0
                
                for name, geometry in scene.geometry.items():
                    if hasattr(geometry, 'faces') and len(geometry.faces) > 0:
                        success, original_faces, new_faces = self.mesh_processor.simplify_geometry_safely(
                            geometry, target_faces_ratio
                        )
                        
                        total_original += original_faces
                        total_simplified += new_faces
                        
                        if success:
                            print(f"[✓] {name}: {original_faces} → {new_faces} faces")
                        else:
                            print(f"[!] {name}: 簡略化失敗、保持原状")
                
                print(f"[i] 合計: {total_original} → {total_simplified} faces")
                
            elif hasattr(scene, 'faces'):
                # 単一メッシュの場合
                original_faces = len(scene.faces)
                safe_ratio = max(self.config.min_face_ratio, target_faces_ratio)
                
                success, _, new_faces = self.mesh_processor.simplify_geometry_safely(scene, safe_ratio)
                if success:
                    print(f"[✓] メッシュ簡略化: {original_faces} → {new_faces} faces")
                else:
                    print(f"[!] 簡略化失敗、保持原状")
            
            # GLBとして安全に出力
            scene.export(output_path, file_type='glb')
            print(f"[✓] GLB出力完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"[×] 最適化に失敗: {e}")
            return False
    
    def optimize_texture_preserving(self, input_path: str, output_path: str, 
                                  target_faces_ratio: float = 0.5) -> bool:
        """テクスチャ保持重視の最適化"""
        try:
            scene = trimesh.load(input_path, force='scene')
            
            simplified_count = 0
            total_count = 0
            
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    if hasattr(geometry, 'faces') and len(geometry.faces) > self.config.min_face_count:
                        total_count += 1
                        
                        success, original_faces, new_faces = self.mesh_processor.simplify_geometry_safely(
                            geometry, target_faces_ratio
                        )
                        
                        if success:
                            simplified_count += 1
                            print(f"[✓] {name}: {original_faces} → {new_faces} faces")
                        else:
                            print(f"[!] {name}: 簡略化結果が無効のため保持")
            
            print(f"[i] {simplified_count}/{total_count} のメッシュを簡略化")
            
            # 出力前の最終検証
            scene.export(output_path, file_type='glb')
            
            # 出力ファイルの検証
            if os.path.exists(output_path) and os.path.getsize(output_path) > self.config.min_output_size:
                print(f"[✓] 安全に出力完了: {output_path}")
                return True
            else:
                print(f"[×] 出力ファイルが小さすぎます")
                return False
                
        except Exception as e:
            print(f"[×] テクスチャ保持最適化に失敗: {e}")
            return False
    
    def optimize_safe_texture_preserving(self, input_path: str, output_path: str, 
                                       target_faces_ratio: float = 0.5) -> bool:
        """テクスチャとメッシュ品質を保持する安全な最適化"""
        try:
            scene = trimesh.load(input_path, force='scene')
            print("[i] 安全モード: テクスチャとメッシュ品質を最優先")
            
            # 簡略化をスキップ（品質保持）
            print("[i] メッシュ簡略化をスキップ（品質保持のため）")
            
            # カメラ・ライト削除
            scene = self.scene_manager.remove_scene_elements(scene)
            
            # ジオメトリクリーンアップのみ実行
            self._deep_clean_scene(scene)
            
            # テクスチャはそのまま保持
            print("[✓] テクスチャを完全保持")
            
            scene.export(output_path, file_type='glb')
            print(f"[✓] 安全最適化完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"[×] 安全最適化に失敗: {e}")
            return False
    
    def optimize_aggressive(self, input_path: str, output_path: str, 
                          target_faces_ratio: float = 0.3, texture_quality: float = 0.5) -> bool:
        """適度な軽量化（品質とサイズのバランス）"""
        try:
            scene = trimesh.load(input_path, force='scene')
            print(f"[i] 適度軽量化モード: 品質とサイズのバランス重視")
            
            # テクスチャをWebP軽度圧縮（85%品質）
            print("[i] テクスチャをWebP軽度圧縮...")
            self.texture_processor.compress_scene_textures_webp(scene, quality=85, resize_factor=1.0)
            
            # カメラ・ライト削除
            scene = self.scene_manager.remove_scene_elements(scene)
            
            # ジオメトリクリーンアップ
            self._deep_clean_scene(scene)
            
            # テクスチャは保持
            print("[✓] テクスチャを保持")
            
            scene.export(output_path, file_type='glb')
            print(f"[✓] 適度軽量化完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"[×] 適度軽量化に失敗: {e}")
            return False
    
    def optimize_ultra_light(self, input_path: str, output_path: str) -> bool:
        """積極的な軽量化（品質とサイズ重視）"""
        try:
            scene = trimesh.load(input_path, force='scene')
            print("[i] 積極的軽量化モード: サイズ削減を重視")
            
            # テクスチャをWebP積極圧縮（70%品質＋リサイズ）
            print("[i] テクスチャをWebP積極圧縮...")
            self.texture_processor.compress_scene_textures_webp(
                scene, quality=70, resize_factor=0.75
            )
            
            # カメラ・ライト削除
            scene = self.scene_manager.remove_scene_elements(scene)
            
            # ジオメトリクリーンアップ
            self._deep_clean_scene(scene)
            
            # テクスチャは保持
            print("[✓] テクスチャを保持")
            
            # 安全にエクスポート
            scene.export(output_path, file_type='glb')
            print(f"[✓] 控えめ軽量化完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"[×] 控えめ軽量化に失敗: {e}")
            return False
    
    def optimize_vertex_cleanup(self, input_path: str, output_path: str) -> bool:
        """頂点削除特化モード（未使用頂点・重複頂点を徹底削除）"""
        try:
            scene = trimesh.load(input_path, force='scene')
            print("[i] 頂点削除特化モード: 未使用・重複頂点を徹底削除")
            
            total_original_vertices = 0
            total_cleaned_vertices = 0
            cleaned_meshes = 0
            
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    if hasattr(geometry, 'vertices') and hasattr(geometry, 'faces'):
                        original_vertices = len(geometry.vertices)
                        total_original_vertices += original_vertices
                        
                        print(f"[i] {name}: {original_vertices}頂点を処理中...")
                        
                        # クリーンアップ処理
                        if self.mesh_processor.clean_geometry(geometry):
                            cleaned_meshes += 1
                        
                        cleaned_vertices = len(geometry.vertices)
                        total_cleaned_vertices += cleaned_vertices
                        
                        reduction = original_vertices - cleaned_vertices
                        if reduction > 0:
                            reduction_percent = (reduction / original_vertices) * 100
                            print(f"[✓] {name}: {original_vertices} → {cleaned_vertices}頂点 ({reduction_percent:.1f}%削減)")
                        else:
                            print(f"[i] {name}: 削除対象頂点なし")
            
            # 全体の削減結果を表示
            total_reduction = total_original_vertices - total_cleaned_vertices
            if total_reduction > 0:
                total_reduction_percent = (total_reduction / total_original_vertices) * 100
                print(f"[✓] 全体: {total_original_vertices} → {total_cleaned_vertices}頂点")
                print(f"[✓] 削減量: {total_reduction}頂点 ({total_reduction_percent:.1f}%)")
            else:
                print("[i] 削除対象の余計な頂点は見つかりませんでした")
            
            # エクスポート
            scene.export(output_path, file_type='glb')
            print(f"[✓] 頂点削除特化最適化完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"[×] 頂点削除特化最適化に失敗: {e}")
            return False
    
    def optimize_hole_filling(self, input_path: str, output_path: str) -> bool:
        """穴埋め特化モード（メッシュの穴を検出・修復）"""
        try:
            scene = trimesh.load(input_path, force='scene')
            print("[i] 軽量修復モード: 基本的なメッシュクリーンアップ（高速化）")
            
            processed_meshes = 0
            cleaned_meshes = 0
            
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    if hasattr(geometry, 'vertices') and hasattr(geometry, 'faces'):
                        processed_meshes += 1
                        print(f"\n[i] 🔍 メッシュ '{name}' を処理中...")
                        print(f"{'='*50}")
                        
                        # 簡易チェックのみ
                        holes_detected = self.mesh_processor.detect_mesh_holes(geometry)
                        
                        if holes_detected:
                            print(f"[!] 🚨 問題検出: 修復処理を実行します")
                            # 基本的な修復のみ（高速）
                            if self.mesh_processor.fill_mesh_holes(geometry):
                                cleaned_meshes += 1
                                print(f"[✓] 🎉 '{name}' の修復完了")
                            else:
                                print(f"[!] ⚠️  '{name}' の修復に一部失敗")
                        else:
                            print(f"[✓] 💎 '{name}' は既にクリーンです")
                            cleaned_meshes += 1
                        
                        # 基本的なメッシュ検証
                        self.mesh_processor.validate_and_repair_mesh(geometry)
                        
                        print(f"{'='*50}")
            
            # 結果を表示
            print(f"\n[i] 📋 処理サマリー:")
            print(f"    ✅ 処理完了: {processed_meshes}個のメッシュを検査")
            print(f"    🔧 修復実行: {cleaned_meshes}個のメッシュ")
            success_rate = (cleaned_meshes / processed_meshes * 100) if processed_meshes > 0 else 0
            print(f"    📊 成功率: {success_rate:.1f}%")
            print(f"[i] ⚡ 注意: 高速化のため複雑な穴埋めは省略されました")
            
            # エクスポート
            scene.export(output_path, file_type='glb')
            print(f"[✓] 軽量修復完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"[×] 軽量修復に失敗: {e}")
            return False
    
    def _deep_clean_scene(self, scene) -> bool:
        """シーン全体の深いクリーンアップ"""
        try:
            cleaned_count = 0
            total_count = 0
            
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    total_count += 1
                    if hasattr(geometry, 'vertices') and hasattr(geometry, 'faces'):
                        if self.mesh_processor.clean_geometry(geometry):
                            cleaned_count += 1
            elif hasattr(scene, 'vertices') and hasattr(scene, 'faces'):
                # 単一メッシュの場合
                total_count = 1
                if self.mesh_processor.clean_geometry(scene):
                    cleaned_count = 1
            
            print(f"[✓] ジオメトリクリーンアップ完了: {cleaned_count}/{total_count}")
            return True
            
        except Exception as e:
            print(f"[×] シーンクリーンアップエラー: {e}")
            return False