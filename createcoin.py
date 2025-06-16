import sys 
from PIL import Image
import numpy as np
import trimesh
from trimesh.exchange import gltf
import os

if len(sys.argv) != 2:
    print("使用方法: python createcoin.py <画像ファイル>")
    sys.exit(1)

input_file = sys.argv[1]
base_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = f"{base_name}_coin.glb"

image = Image.open(input_file).convert("RGBA")

radius = 1.0 
thickness = 0.1 

coin = trimesh.creation.cylinder(radius=radius, height=thickness, sections=64)

uvs = np.array([
    [0.5 + 0.5 * (v[0] / radius), 0.5 + 0.5 * (v[1] / radius)] for v in coin.vertices
])

material = trimesh.visual.material.PBRMaterial(
    baseColorTexture=image,
    baseColorFactor=[1.2, 1.2, 1.2, 1.0],  # 色を強調
    metallicFactor=0.0,  # メタリック感を無効
    roughnessFactor=0.3,  # 滑らかにして反射を増加
    emissiveFactor=[0.0, 0.0, 0.0]  # 自己発光を無効化
)

coin.visual = trimesh.visual.texture.TextureVisuals(
    uv=uvs, 
    material=material
)

with open(output_file, "wb") as f:
    f.write(gltf.export_glb(coin))

print(f"GLBファイルを生成しました: {output_file}")

