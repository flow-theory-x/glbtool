import trimesh
import json
import sys
import os

def analyze_glb(file_path):
    """GLBファイルの詳細分析"""
    if not os.path.exists(file_path):
        print(f"ファイルが見つかりません: {file_path}")
        return
    
    print(f"=== GLB ファイル分析: {file_path} ===")
    print(f"ファイルサイズ: {os.path.getsize(file_path) / 1024 / 1024:.2f} MB")
    print()
    
    try:
        # Trimeshでロード
        scene = trimesh.load(file_path, force='scene')
        
        print("=== シーン構造 ===")
        print(f"シーンタイプ: {type(scene)}")
        print(f"ジオメトリ数: {len(scene.geometry) if hasattr(scene, 'geometry') else 0}")
        print()
        
        # ジオメトリの詳細
        if hasattr(scene, 'geometry'):
            print("=== ジオメトリ詳細 ===")
            for name, geometry in scene.geometry.items():
                print(f"名前: {name}")
                print(f"  タイプ: {type(geometry)}")
                print(f"  頂点数: {len(geometry.vertices) if hasattr(geometry, 'vertices') else 0}")
                print(f"  面数: {len(geometry.faces) if hasattr(geometry, 'faces') else 0}")
                
                # 属性チェック
                attributes = []
                if hasattr(geometry, 'vertex_normals'):
                    attributes.append(f"法線({len(geometry.vertex_normals)})")
                if hasattr(geometry, 'visual') and hasattr(geometry.visual, 'uv'):
                    attributes.append(f"UV座標({len(geometry.visual.uv)})")
                if hasattr(geometry, 'vertex_colors'):
                    attributes.append(f"頂点色({len(geometry.vertex_colors)})")
                
                print(f"  属性: {', '.join(attributes) if attributes else 'なし'}")
                
                # マテリアル
                if hasattr(geometry, 'visual') and hasattr(geometry.visual, 'material'):
                    material = geometry.visual.material
                    print(f"  マテリアル: {type(material)}")
                    if hasattr(material, 'image') and material.image is not None:
                        if hasattr(material.image, 'shape'):
                            print(f"  テクスチャサイズ: {material.image.shape}")
                print()
        
        # シーン全体の要素チェック
        print("=== シーン要素 ===")
        scene_attrs = []
        
        # ライト
        if hasattr(scene, 'lights') and scene.lights:
            scene_attrs.append(f"ライト({len(scene.lights)})")
        
        # カメラ
        if hasattr(scene, 'camera'):
            scene_attrs.append("カメラ")
        
        # アニメーション
        if hasattr(scene, 'animations') and scene.animations:
            scene_attrs.append(f"アニメーション({len(scene.animations)})")
        
        # ノード階層
        if hasattr(scene, 'graph') and scene.graph:
            node_count = len(scene.graph.nodes)
            scene_attrs.append(f"ノード({node_count})")
        
        # メタデータ
        metadata_attrs = []
        check_attrs = ['metadata', 'extras', 'extensions', 'copyright', 'generator']
        for attr in check_attrs:
            if hasattr(scene, attr):
                metadata_attrs.append(attr)
        
        if metadata_attrs:
            scene_attrs.append(f"メタデータ({', '.join(metadata_attrs)})")
        
        print(f"追加要素: {', '.join(scene_attrs) if scene_attrs else 'なし'}")
        print()
        
        # 生データアクセス
        try:
            import pygltflib
            gltf = pygltflib.GLTF2().load(file_path)
            
            print("=== GLTF構造詳細 ===")
            print(f"シーン数: {len(gltf.scenes) if gltf.scenes else 0}")
            print(f"ノード数: {len(gltf.nodes) if gltf.nodes else 0}")
            print(f"メッシュ数: {len(gltf.meshes) if gltf.meshes else 0}")
            print(f"マテリアル数: {len(gltf.materials) if gltf.materials else 0}")
            print(f"テクスチャ数: {len(gltf.textures) if gltf.textures else 0}")
            print(f"イメージ数: {len(gltf.images) if gltf.images else 0}")
            print(f"アニメーション数: {len(gltf.animations) if gltf.animations else 0}")
            
            # 不要な要素をチェック
            unnecessary = []
            if gltf.animations:
                unnecessary.append("アニメーション")
            if gltf.cameras:
                unnecessary.append("カメラ")
            if gltf.lights:
                unnecessary.append("ライト")
            
            # ノード階層が複雑かチェック
            if gltf.nodes and len(gltf.nodes) > len(gltf.meshes):
                unnecessary.append("複雑なノード階層")
            
            # 拡張機能
            if gltf.extensions:
                unnecessary.append(f"拡張機能({list(gltf.extensions.keys())})")
            
            if gltf.extensionsUsed:
                unnecessary.append(f"使用拡張({gltf.extensionsUsed})")
            
            print(f"削除可能な要素: {', '.join(unnecessary) if unnecessary else 'なし'}")
            
        except ImportError:
            print("pygltflibがインストールされていません。詳細分析をスキップ")
        except Exception as e:
            print(f"GLTF詳細分析エラー: {e}")
        
    except Exception as e:
        print(f"分析エラー: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_glb(sys.argv[1])
    else:
        print("Usage: python3 analyze_glb.py <file.glb>")