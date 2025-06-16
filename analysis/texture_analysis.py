#!/usr/bin/env python3
"""
GLBファイル内のテクスチャデータ分析
"""

import os
import pygltflib
from PIL import Image
import io

def analyze_textures(glb_path):
    """テクスチャデータの詳細分析"""
    print(f"=== テクスチャデータ分析 ===\n")
    
    gltf = pygltflib.GLTF2().load(glb_path)
    
    # バッファーデータを読み込み
    try:
        if gltf.buffers[0].uri:
            buffer_data = gltf.get_data_from_buffer_uri(gltf.buffers[0].uri)
        else:
            # GLBファイルの場合、バイナリデータを直接取得
            with open(glb_path, 'rb') as f:
                # GLBヘッダーをスキップ（12バイト）
                f.seek(12)
                # JSON chunkの長さを読み取り
                json_length = int.from_bytes(f.read(4), byteorder='little')
                json_type = f.read(4)  # 'JSON'
                # JSONデータをスキップ
                f.seek(12 + 8 + json_length)
                # バイナリchunkの長さを読み取り
                bin_length = int.from_bytes(f.read(4), byteorder='little')
                bin_type = f.read(4)  # 'BIN\x00'
                # バイナリデータを読み取り
                buffer_data = f.read(bin_length)
    except Exception as e:
        print(f"バッファーデータ読み込みエラー: {e}")
        buffer_data = None
    
    if gltf.images:
        total_texture_size = 0
        for i, image in enumerate(gltf.images):
            print(f"画像 {i}:")
            if image.name:
                print(f"  名前: {image.name}")
            print(f"  MIMEタイプ: {image.mimeType}")
            
            if image.bufferView is not None:
                buffer_view = gltf.bufferViews[image.bufferView]
                image_size = buffer_view.byteLength
                total_texture_size += image_size
                print(f"  データサイズ: {image_size:,} bytes ({image_size / 1024 / 1024:.2f} MB)")
                
                # 画像データを抽出してPILで解析
                try:
                    if buffer_data is None:
                        print("  画像データを取得できませんでした")
                        continue
                    
                    start = buffer_view.byteOffset
                    end = start + buffer_view.byteLength
                    image_data = buffer_data[start:end]
                    
                    # PILで画像を開く
                    pil_image = Image.open(io.BytesIO(image_data))
                    print(f"  解像度: {pil_image.width} x {pil_image.height}")
                    print(f"  モード: {pil_image.mode}")
                    print(f"  フォーマット: {pil_image.format}")
                    
                    # 圧縮効率の計算
                    pixel_count = pil_image.width * pil_image.height
                    if pil_image.mode == 'RGB':
                        uncompressed_size = pixel_count * 3
                    elif pil_image.mode == 'RGBA':
                        uncompressed_size = pixel_count * 4
                    else:
                        uncompressed_size = pixel_count
                    
                    compression_ratio = image_size / uncompressed_size
                    print(f"  非圧縮サイズ: {uncompressed_size:,} bytes ({uncompressed_size / 1024 / 1024:.2f} MB)")
                    print(f"  圧縮率: {compression_ratio:.3f} ({100 * (1 - compression_ratio):.1f}% 削減)")
                    
                except Exception as e:
                    print(f"  画像解析エラー: {e}")
            
            print()
        
        print(f"総テクスチャサイズ: {total_texture_size:,} bytes ({total_texture_size / 1024 / 1024:.2f} MB)")
        
        file_size = os.path.getsize(glb_path)
        texture_percentage = (total_texture_size / file_size) * 100
        print(f"ファイル全体に占める割合: {texture_percentage:.1f}%")
    
    # ジオメトリデータのサイズ
    print(f"\n=== ジオメトリデータ分析 ===")
    geometry_size = 0
    
    if gltf.meshes:
        for i, mesh in enumerate(gltf.meshes):
            print(f"\nメッシュ {i} ({mesh.name}):")
            mesh_size = 0
            
            for j, primitive in enumerate(mesh.primitives):
                print(f"  プリミティブ {j}:")
                
                # 各属性のサイズ
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
                        buffer_view = gltf.bufferViews[accessor.bufferView]
                        attr_size = buffer_view.byteLength
                        mesh_size += attr_size
                        geometry_size += attr_size
                        print(f"    {attr_name}: {attr_size:,} bytes ({attr_size / 1024:.1f} KB)")
                
                # インデックスのサイズ
                if primitive.indices is not None:
                    accessor = gltf.accessors[primitive.indices]
                    buffer_view = gltf.bufferViews[accessor.bufferView]
                    indices_size = buffer_view.byteLength
                    mesh_size += indices_size
                    geometry_size += indices_size
                    print(f"    INDICES: {indices_size:,} bytes ({indices_size / 1024:.1f} KB)")
            
            print(f"  メッシュ合計: {mesh_size:,} bytes ({mesh_size / 1024 / 1024:.2f} MB)")
    
    print(f"\n総ジオメトリサイズ: {geometry_size:,} bytes ({geometry_size / 1024 / 1024:.2f} MB)")
    
    # ファイル構成の内訳
    print(f"\n=== ファイル構成内訳 ===")
    file_size = os.path.getsize(glb_path)
    print(f"総ファイルサイズ: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print(f"ジオメトリデータ: {geometry_size:,} bytes ({geometry_size / 1024 / 1024:.2f} MB, {geometry_size/file_size*100:.1f}%)")
    if gltf.images:
        print(f"テクスチャデータ: {total_texture_size:,} bytes ({total_texture_size / 1024 / 1024:.2f} MB, {total_texture_size/file_size*100:.1f}%)")
    
    other_size = file_size - geometry_size - (total_texture_size if gltf.images else 0)
    print(f"その他（JSON等）: {other_size:,} bytes ({other_size / 1024:.1f} KB, {other_size/file_size*100:.1f}%)")

def main():
    glb_file = "/Users/goodsun/develop/bonsoleil/glbopt/original_ultra.glb"
    
    if not os.path.exists(glb_file):
        print(f"エラー: ファイルが見つかりません: {glb_file}")
        return
    
    analyze_textures(glb_file)

if __name__ == "__main__":
    main()