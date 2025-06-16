#!/usr/bin/env python3
"""
GLBファイルのより詳細な分析とバッファービューの内容確認
"""

import os
import json
import pygltflib
import numpy as np

def analyze_buffer_views(glb_path):
    """バッファービューの詳細分析"""
    print(f"=== バッファービューの詳細分析 ===\n")
    
    gltf = pygltflib.GLTF2().load(glb_path)
    
    print(f"バッファービュー数: {len(gltf.bufferViews) if gltf.bufferViews else 0}")
    
    if gltf.bufferViews:
        for i, buffer_view in enumerate(gltf.bufferViews):
            print(f"\nバッファービュー {i}:")
            print(f"  バッファー: {buffer_view.buffer}")
            print(f"  オフセット: {buffer_view.byteOffset}")
            print(f"  長さ: {buffer_view.byteLength:,} bytes ({buffer_view.byteLength / 1024:.1f} KB)")
            if hasattr(buffer_view, 'byteStride') and buffer_view.byteStride:
                print(f"  ストライド: {buffer_view.byteStride}")
            if hasattr(buffer_view, 'target') and buffer_view.target:
                target_type = {
                    34962: "ARRAY_BUFFER (頂点データ)",
                    34963: "ELEMENT_ARRAY_BUFFER (インデックスデータ)"
                }.get(buffer_view.target, f"UNKNOWN ({buffer_view.target})")
                print(f"  ターゲット: {target_type}")
    
    # アクセサーとバッファービューの関係
    print(f"\n=== アクセサーとバッファービューの関係 ===")
    if gltf.accessors:
        for i, accessor in enumerate(gltf.accessors):
            print(f"\nアクセサー {i}:")
            print(f"  バッファービュー: {accessor.bufferView}")
            print(f"  オフセット: {accessor.byteOffset if accessor.byteOffset else 0}")
            print(f"  タイプ: {accessor.type}")
            print(f"  コンポーネントタイプ: {accessor.componentType}")
            print(f"  カウント: {accessor.count}")
            
            # データサイズ計算
            component_size = {
                5120: 1,  # BYTE
                5121: 1,  # UNSIGNED_BYTE
                5122: 2,  # SHORT
                5123: 2,  # UNSIGNED_SHORT
                5125: 4,  # UNSIGNED_INT
                5126: 4   # FLOAT
            }.get(accessor.componentType, 4)
            
            type_size = {
                "SCALAR": 1,
                "VEC2": 2,
                "VEC3": 3,
                "VEC4": 4,
                "MAT2": 4,
                "MAT3": 9,
                "MAT4": 16
            }.get(accessor.type, 1)
            
            total_size = accessor.count * component_size * type_size
            print(f"  データサイズ: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
    
    # メッシュ属性の使用状況
    print(f"\n=== メッシュ属性の使用状況 ===")
    if gltf.meshes:
        for i, mesh in enumerate(gltf.meshes):
            print(f"\nメッシュ {i} ({mesh.name}):")
            for j, primitive in enumerate(mesh.primitives):
                print(f"  プリミティブ {j}:")
                if primitive.attributes:
                    attrs = {}
                    if hasattr(primitive.attributes, 'POSITION') and primitive.attributes.POSITION is not None:
                        attrs['POSITION'] = primitive.attributes.POSITION
                    if hasattr(primitive.attributes, 'NORMAL') and primitive.attributes.NORMAL is not None:
                        attrs['NORMAL'] = primitive.attributes.NORMAL
                    if hasattr(primitive.attributes, 'TEXCOORD_0') and primitive.attributes.TEXCOORD_0 is not None:
                        attrs['TEXCOORD_0'] = primitive.attributes.TEXCOORD_0
                    if hasattr(primitive.attributes, 'TEXCOORD_1') and primitive.attributes.TEXCOORD_1 is not None:
                        attrs['TEXCOORD_1'] = primitive.attributes.TEXCOORD_1
                    if hasattr(primitive.attributes, 'COLOR_0') and primitive.attributes.COLOR_0 is not None:
                        attrs['COLOR_0'] = primitive.attributes.COLOR_0
                    if hasattr(primitive.attributes, 'TANGENT') and primitive.attributes.TANGENT is not None:
                        attrs['TANGENT'] = primitive.attributes.TANGENT
                    
                    for attr_name, accessor_index in attrs.items():
                        accessor = gltf.accessors[accessor_index]
                        component_size = {
                            5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4
                        }.get(accessor.componentType, 4)
                        type_size = {
                            "SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16
                        }.get(accessor.type, 1)
                        attr_size = accessor.count * component_size * type_size
                        print(f"    {attr_name}: アクセサー{accessor_index}, {attr_size:,} bytes ({attr_size / 1024:.1f} KB)")
                
                if primitive.indices is not None:
                    accessor = gltf.accessors[primitive.indices]
                    component_size = {
                        5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4
                    }.get(accessor.componentType, 4)
                    indices_size = accessor.count * component_size
                    print(f"    INDICES: アクセサー{primitive.indices}, {indices_size:,} bytes ({indices_size / 1024:.1f} KB)")

def estimate_size_reduction(glb_path):
    """サイズ削減の見積もり"""
    print(f"\n=== サイズ削減見積もり ===")
    
    gltf = pygltflib.GLTF2().load(glb_path)
    
    # 不要な属性のサイズ計算
    unnecessary_size = 0
    
    if gltf.meshes:
        for mesh in gltf.meshes:
            for primitive in mesh.primitives:
                if primitive.attributes:
                    # 不要な属性のサイズを計算
                    unnecessary_attrs = ['NORMAL', 'TEXCOORD_1', 'COLOR_0', 'TANGENT']
                    
                    for attr in unnecessary_attrs:
                        if hasattr(primitive.attributes, attr):
                            accessor_index = getattr(primitive.attributes, attr)
                            if accessor_index is not None:
                                accessor = gltf.accessors[accessor_index]
                                component_size = {
                                    5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4
                                }.get(accessor.componentType, 4)
                                type_size = {
                                    "SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16
                                }.get(accessor.type, 1)
                                attr_size = accessor.count * component_size * type_size
                                unnecessary_size += attr_size
                                print(f"{attr}: {attr_size:,} bytes ({attr_size / 1024:.1f} KB)")
    
    print(f"\n削除可能な属性の総サイズ: {unnecessary_size:,} bytes ({unnecessary_size / 1024 / 1024:.2f} MB)")
    
    original_size = os.path.getsize(glb_path)
    estimated_new_size = original_size - unnecessary_size
    reduction_percentage = (unnecessary_size / original_size) * 100
    
    print(f"元のファイルサイズ: {original_size:,} bytes ({original_size / 1024 / 1024:.2f} MB)")
    print(f"削減後の推定サイズ: {estimated_new_size:,} bytes ({estimated_new_size / 1024 / 1024:.2f} MB)")
    print(f"推定削減率: {reduction_percentage:.1f}%")

def main():
    glb_file = "/Users/goodsun/develop/bonsoleil/glbopt/original_ultra.glb"
    
    if not os.path.exists(glb_file):
        print(f"エラー: ファイルが見つかりません: {glb_file}")
        return
    
    analyze_buffer_views(glb_file)
    estimate_size_reduction(glb_file)

if __name__ == "__main__":
    main()