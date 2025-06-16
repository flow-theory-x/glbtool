"""シーン要素管理（ライト、カメラ削除、フラット化）"""

import trimesh
from typing import List


class SceneManager:
    """シーン要素の管理を担当するクラス"""
    
    def remove_scene_elements(self, scene):
        """シーンから不要な要素を安全に削除（ライト、カメラ、ノード階層）"""
        try:
            removed = []
            
            # ライトを削除
            if hasattr(scene, 'lights') and scene.lights:
                light_count = len(scene.lights)
                try:
                    scene.lights.clear()
                    removed.append(f"ライト({light_count}個)")
                except:
                    pass
            
            # カメラを削除
            if hasattr(scene, 'camera') and scene.camera is not None:
                try:
                    scene.camera = None
                    removed.append("カメラ")
                except:
                    pass
            
            # シーンをフラット化
            try:
                original_nodes = len(scene.graph.nodes) if hasattr(scene, 'graph') and scene.graph else 0
                scene = self.flatten_scene(scene)
                new_nodes = len(scene.graph.nodes) if hasattr(scene, 'graph') and scene.graph else 0
                if original_nodes > new_nodes:
                    removed.append(f"ノード階層({original_nodes}→{new_nodes})")
            except Exception as e:
                print(f"[!] ノード階層削除エラー: {e}")
            
            if removed:
                print(f"[✓] シーン要素削除: {', '.join(removed)}")
            else:
                print("[i] 削除可能なシーン要素なし")
            
            return scene
            
        except Exception as e:
            print(f"[!] シーン要素削除エラー: {e}")
            return scene
    
    def flatten_scene(self, scene):
        """複数シーンを1つのフラットなシーンにまとめる"""
        try:
            from trimesh.scene.scene import Scene
            
            # 新しいフラットなシーンを作成
            flat_scene = Scene()
            flattened_count = 0
            
            if hasattr(scene, 'geometry') and scene.geometry:
                # すべてのジオメトリを新しいシーンに直接追加
                for name, geometry in scene.geometry.items():
                    if hasattr(geometry, 'vertices') and hasattr(geometry, 'faces'):
                        # シンプルな名前で追加
                        simple_name = f"mesh_{flattened_count}"
                        flat_scene.add_geometry(geometry, node_name=simple_name)
                        flattened_count += 1
                        print(f"[✓] フラット化: {name} → {simple_name}")
            
            print(f"[✓] シーンフラット化完了: {flattened_count}個のメッシュ")
            return flat_scene
            
        except Exception as e:
            print(f"[!] シーンフラット化エラー: {e}")
            return scene
    
    def create_minimal_glb(self, scene):
        """最小限のGLBを作成（メッシュ+テクスチャのみ）"""
        try:
            # 新しいシーンを作成
            from trimesh.scene.scene import Scene
            minimal_scene = Scene()
            
            # ジオメトリのみをコピー
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    # 必要最小限の属性のみを保持
                    if hasattr(geometry, 'vertices') and hasattr(geometry, 'faces'):
                        # 新しいメッシュを作成
                        minimal_mesh = trimesh.Trimesh(
                            vertices=geometry.vertices,
                            faces=geometry.faces
                        )
                        
                        # UV座標とテクスチャを保持
                        if hasattr(geometry, 'visual'):
                            minimal_mesh.visual = geometry.visual
                        
                        # 法線は再計算（より軽量）
                        if hasattr(minimal_mesh, 'vertex_normals'):
                            minimal_mesh.vertex_normals
                        
                        minimal_scene.add_geometry(minimal_mesh, node_name=name)
            
            print("[✓] 最小限のGLB構造を作成")
            return minimal_scene
            
        except Exception as e:
            print(f"[!] 最小限GLB作成エラー: {e}")
            return scene
    
    def clean_scene_metadata(self, scene):
        """不要なメタデータを削除"""
        try:
            # Sceneオブジェクトの場合は何もしない（メタデータがない）
            if str(type(scene)) == "<class 'trimesh.scene.scene.Scene'>":
                print("[✓] メタデータ削除完了（Scene type）")
                return
            
            # 不要な属性を削除
            unnecessary_attrs = ['metadata', 'extras', 'extensions', 'copyright', 'generator']
            
            for attr in unnecessary_attrs:
                if hasattr(scene, attr):
                    try:
                        delattr(scene, attr)
                    except:
                        pass
            
            # ジオメトリからも不要データを削除
            if hasattr(scene, 'geometry'):
                for geometry in scene.geometry.values():
                    for attr in unnecessary_attrs:
                        if hasattr(geometry, attr):
                            try:
                                delattr(geometry, attr)
                            except:
                                pass
            
            print("[✓] メタデータ削除完了")
            
        except Exception as e:
            print(f"[!] メタデータ削除エラー: {e}")
            raise e