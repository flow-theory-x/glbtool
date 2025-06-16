"""メッシュ処理機能（簡略化、クリーンアップ、穴埋め）"""

import numpy as np
from typing import List, Tuple, Optional
import trimesh

from .config import OptimizationConfig


class MeshProcessor:
    """メッシュ処理を担当するクラス"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
    
    def simplify_geometry_safely(self, geometry, target_faces_ratio: float) -> Tuple[bool, int, int]:
        """安全なメッシュ簡略化"""
        try:
            if not hasattr(geometry, 'faces') or len(geometry.faces) < self.config.min_face_count:
                return False, 0, 0
            
            original_faces = len(geometry.faces)
            
            # 安全な簡略化（極端な削減を避ける）
            safe_ratio = max(self.config.safe_face_ratio, target_faces_ratio)
            target_face_count = int(original_faces * safe_ratio)
            
            # Trimeshの簡略化を使用
            simplified = geometry.simplify_quadric_decimation(face_count=target_face_count)
            
            if simplified and hasattr(simplified, 'faces') and len(simplified.faces) > 0:
                # ジオメトリを更新
                geometry.vertices = simplified.vertices
                geometry.faces = simplified.faces
                if hasattr(simplified, 'visual'):
                    geometry.visual = simplified.visual
                
                new_faces = len(simplified.faces)
                return True, original_faces, new_faces
            
            return False, original_faces, original_faces
            
        except Exception as e:
            print(f"[!] メッシュ簡略化エラー: {e}")
            return False, 0, 0
    
    def clean_geometry(self, geometry) -> bool:
        """ジオメトリをクリーンアップ（孤立頂点、重複頂点、無効面を削除）"""
        try:
            original_vertices = len(geometry.vertices) if hasattr(geometry, 'vertices') else 0
            original_faces = len(geometry.faces) if hasattr(geometry, 'faces') else 0
            
            # 未使用頂点を削除
            self._remove_unused_vertices(geometry)
            
            # 重複頂点を統合
            if hasattr(geometry, 'merge_vertices'):
                geometry.merge_vertices()
            
            # 孤立した頂点を削除
            if hasattr(geometry, 'remove_unreferenced_vertices'):
                geometry.remove_unreferenced_vertices()
            
            # 無効な面を削除
            self._remove_invalid_faces(geometry)
            
            # 重複した面を削除
            self._remove_duplicate_faces(geometry)
            
            # 面の法線を修正
            if hasattr(geometry, 'fix_normals'):
                geometry.fix_normals()
            
            # 結果を確認
            new_vertices = len(geometry.vertices) if hasattr(geometry, 'vertices') else 0
            new_faces = len(geometry.faces) if hasattr(geometry, 'faces') else 0
            
            if original_vertices > 0 or original_faces > 0:
                vertex_reduction = original_vertices - new_vertices
                face_reduction = original_faces - new_faces
                if vertex_reduction > 0 or face_reduction > 0:
                    print(f"[i] クリーンアップ: 頂点-{vertex_reduction}, 面-{face_reduction}")
            
            return True
            
        except Exception as e:
            print(f"[!] ジオメトリクリーンアップエラー: {e}")
            return False
    
    def _remove_unused_vertices(self, geometry) -> bool:
        """使用されていない頂点を削除"""
        try:
            if not hasattr(geometry, 'vertices') or not hasattr(geometry, 'faces'):
                return False
            
            original_vertices = len(geometry.vertices)
            if original_vertices == 0:
                return False
            
            # 面で使用されている頂点インデックスを取得
            used_vertex_indices = set()
            if len(geometry.faces) > 0:
                used_vertex_indices = set(geometry.faces.flatten())
            
            # 使用されていない頂点を特定
            all_indices = set(range(original_vertices))
            unused_indices = all_indices - used_vertex_indices
            
            if len(unused_indices) == 0:
                return True
            
            # 使用されている頂点のみを保持
            used_indices_list = sorted(list(used_vertex_indices))
            new_vertices = geometry.vertices[used_indices_list]
            
            # インデックスマッピングを作成
            old_to_new_index = {}
            for new_idx, old_idx in enumerate(used_indices_list):
                old_to_new_index[old_idx] = new_idx
            
            # 面のインデックスを更新
            new_faces = []
            for face in geometry.faces:
                new_face = [old_to_new_index[old_idx] for old_idx in face]
                new_faces.append(new_face)
            
            # ジオメトリを更新
            geometry.vertices = new_vertices
            geometry.faces = np.array(new_faces)
            
            # UV座標やその他の頂点属性も更新
            if hasattr(geometry.visual, 'uv') and geometry.visual.uv is not None:
                geometry.visual.uv = geometry.visual.uv[used_indices_list]
            
            removed_count = len(unused_indices)
            print(f"[✓] 未使用頂点削除: {removed_count}個 ({original_vertices} → {len(new_vertices)})")
            
            return True
            
        except Exception as e:
            print(f"[!] 未使用頂点削除エラー: {e}")
            return False
    
    def _remove_invalid_faces(self, geometry):
        """無効な面を削除"""
        if hasattr(geometry, 'nondegenerate_faces'):
            try:
                valid_faces = geometry.nondegenerate_faces()
                geometry.update_faces(valid_faces)
            except:
                # 古いメソッドを使用
                if hasattr(geometry, 'remove_degenerate_faces'):
                    geometry.remove_degenerate_faces()
    
    def _remove_duplicate_faces(self, geometry):
        """重複した面を削除"""
        if hasattr(geometry, 'unique_faces'):
            try:
                unique_faces = geometry.unique_faces()
                geometry.update_faces(unique_faces)
            except:
                # 古いメソッドを使用
                if hasattr(geometry, 'remove_duplicate_faces'):
                    geometry.remove_duplicate_faces()
    
    def detect_mesh_holes(self, geometry) -> List[str]:
        """メッシュの穴を簡易検出（高速版）"""
        try:
            if not hasattr(geometry, 'vertices') or not hasattr(geometry, 'faces'):
                return []
            
            holes_detected = []
            
            # 基本統計情報を表示
            vertex_count = len(geometry.vertices)
            face_count = len(geometry.faces)
            print(f"[i] メッシュ情報: {vertex_count}頂点, {face_count}面")
            
            # 基本的な水密性チェックのみ（高速）
            if hasattr(geometry, 'is_watertight'):
                try:
                    is_watertight = geometry.is_watertight
                    if not is_watertight:
                        print("[!] 🔍 開口部を検出: メッシュが水密ではありません")
                        holes_detected.append("開口部あり")
                        
                        # 追加情報を表示
                        if hasattr(geometry, 'is_winding_consistent'):
                            if not geometry.is_winding_consistent:
                                print("[!] 📐 面の向きが不整合")
                                holes_detected.append("面向き不整合")
                        
                        if hasattr(geometry, 'is_volume'):
                            if not geometry.is_volume:
                                print("[!] 📦 有効なボリュームではありません")
                                holes_detected.append("無効ボリューム")
                    else:
                        print("[✓] ✨ メッシュは水密です（穴なし）")
                except Exception as e:
                    # is_watertightの計算に時間がかかる場合はスキップ
                    print(f"[i] ⏭️  水密性チェックをスキップ（高速化のため）: {e}")
                    holes_detected.append("チェックスキップ")
            
            # 検出結果のサマリー
            if len(holes_detected) == 0:
                print("[✓] 🎉 簡易チェックで問題は検出されませんでした")
            else:
                print(f"[!] 🔍 検出された問題: {len(holes_detected)}種類")
                for i, issue in enumerate(holes_detected, 1):
                    print(f"    {i}. {issue}")
            
            return holes_detected
            
        except Exception as e:
            print(f"[!] 穴検出エラー: {e}")
            return []
    
    def fill_mesh_holes(self, geometry) -> bool:
        """メッシュの基本的な修復（軽量版 - 時間のかかる穴埋めは除外）"""
        try:
            if not hasattr(geometry, 'vertices') or not hasattr(geometry, 'faces'):
                return False
            
            print("[i] 🔧 基本的なメッシュ修復を実行（高速化のため）")
            
            # 修復前の状態を記録
            original_vertices = len(geometry.vertices)
            original_faces = len(geometry.faces)
            
            repairs_performed = []
            
            # 基本的なメッシュクリーンアップのみ実行
            try:
                # 重複頂点を統合
                if hasattr(geometry, 'merge_vertices'):
                    pre_merge_vertices = len(geometry.vertices)
                    geometry.merge_vertices()
                    post_merge_vertices = len(geometry.vertices)
                    merged_count = pre_merge_vertices - post_merge_vertices
                    
                    if merged_count > 0:
                        print(f"[✓] 🔗 重複頂点を統合: {merged_count}個削除")
                        repairs_performed.append(f"重複頂点削除({merged_count}個)")
                    else:
                        print("[i] 💫 重複頂点なし")
                
                # 面の向きを修正
                if hasattr(geometry, 'fix_normals'):
                    geometry.fix_normals()
                    print("[✓] 📐 面の向きを修正")
                    repairs_performed.append("面向き修正")
                
                # 無効な面を削除（高速）
                pre_clean_faces = len(geometry.faces)
                self._remove_invalid_faces(geometry)
                post_clean_faces = len(geometry.faces)
                removed_faces = pre_clean_faces - post_clean_faces
                
                if removed_faces > 0:
                    print(f"[✓] 🗑️  無効な面を削除: {removed_faces}個")
                    repairs_performed.append(f"無効面削除({removed_faces}個)")
                else:
                    print("[i] ✨ 無効な面なし")
                
                # 修復結果のサマリー
                final_vertices = len(geometry.vertices)
                final_faces = len(geometry.faces)
                
                print(f"[i] 📊 修復結果:")
                print(f"    頂点: {original_vertices} → {final_vertices} ({original_vertices - final_vertices:+d})")
                print(f"    面: {original_faces} → {final_faces} ({original_faces - final_faces:+d})")
                
                if repairs_performed:
                    print(f"[✓] 🎯 実行された修復: {', '.join(repairs_performed)}")
                    print("[✓] ✨ 基本的なメッシュ修復完了")
                else:
                    print("[i] 💎 修復不要（既にクリーンなメッシュ）")
                
                return True
                
            except Exception as e:
                print(f"[!] ❌ メッシュ修復エラー: {e}")
                return False
            
        except Exception as e:
            print(f"[!] ❌ メッシュ修復エラー: {e}")
            return False
    
    def validate_and_repair_mesh(self, geometry) -> bool:
        """メッシュの検証と修復"""
        try:
            # 基本的な検証
            if not hasattr(geometry, 'vertices') or not hasattr(geometry, 'faces'):
                return False
            
            if len(geometry.vertices) == 0 or len(geometry.faces) == 0:
                return False
            
            repaired = False
            
            # 面のインデックスが頂点数を超えていないかチェック
            max_vertex_index = len(geometry.vertices) - 1
            if hasattr(geometry, 'faces') and len(geometry.faces) > 0:
                face_max = np.max(geometry.faces)
                if face_max > max_vertex_index:
                    print(f"[!] 無効な面インデックス検出: {face_max} > {max_vertex_index}")
                    # 無効な面を削除
                    valid_faces = []
                    for face in geometry.faces:
                        if np.all(face <= max_vertex_index) and np.all(face >= 0):
                            valid_faces.append(face)
                    
                    if len(valid_faces) > 0:
                        geometry.faces = np.array(valid_faces)
                        repaired = True
                        print(f"[✓] 無効な面を削除: {len(geometry.faces)} 面が残存")
                    else:
                        return False
            
            # メッシュの整合性をチェック
            if hasattr(geometry, 'is_valid'):
                if not geometry.is_valid:
                    print("[!] メッシュの整合性に問題があります")
                    # 可能であれば修復を試行
                    if hasattr(geometry, 'fill_holes'):
                        try:
                            geometry.fill_holes()
                            repaired = True
                            print("[✓] メッシュの穴を修復")
                        except:
                            pass
            
            if repaired:
                print("[✓] メッシュ修復完了")
            
            return True
            
        except Exception as e:
            print(f"[!] メッシュ検証エラー: {e}")
            return False