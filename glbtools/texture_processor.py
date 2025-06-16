"""テクスチャ処理とWebP圧縮機能"""

import io
import numpy as np
from PIL import Image
from typing import Optional

from .config import OptimizationConfig


class TextureProcessor:
    """テクスチャ圧縮とWebP変換を担当するクラス"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
    
    def compress_scene_textures_webp(self, scene, quality: int = 80, resize_factor: float = 1.0) -> bool:
        """シーン内のテクスチャをWebP形式で圧縮"""
        try:
            texture_found = False
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    print(f"[i] チェック中: {name}")
                    if hasattr(geometry, 'visual') and hasattr(geometry.visual, 'material'):
                        material = geometry.visual.material
                        
                        # ベーステクスチャのWebP圧縮
                        if hasattr(material, 'image') and material.image is not None:
                            print(f"[i] {name}: テクスチャ画像発見")
                            texture_found = True
                            compressed_image = self._compress_texture_webp(
                                material.image, quality, resize_factor
                            )
                            if compressed_image is not None:
                                material.image = compressed_image
                                print(f"[✓] {name}: WebPテクスチャ圧縮完了")
                        else:
                            print(f"[i] {name}: テクスチャ画像なし")
            
            if not texture_found:
                print("[i] 圧縮可能なテクスチャが見つかりませんでした")
            
            return texture_found
            
        except Exception as e:
            print(f"[!] WebPテクスチャ圧縮エラー: {e}")
            return False
    
    def compress_scene_textures(self, scene, quality: float = 0.5) -> bool:
        """シーン内のテクスチャを従来方式で圧縮"""
        try:
            texture_found = False
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    if hasattr(geometry, 'visual') and hasattr(geometry.visual, 'material'):
                        material = geometry.visual.material
                        
                        # ベーステクスチャの圧縮
                        if hasattr(material, 'image') and material.image is not None:
                            compressed_image = self._compress_texture(material.image, quality)
                            if compressed_image is not None:
                                material.image = compressed_image
                                texture_found = True
                                print(f"[✓] {name}: テクスチャ圧縮完了")
            
            return texture_found
            
        except Exception as e:
            print(f"[!] テクスチャ圧縮エラー: {e}")
            return False
    
    def _compress_texture_webp(self, image, quality: int = 80, resize_factor: float = 1.0) -> Optional[np.ndarray]:
        """テクスチャをWebP形式で圧縮"""
        try:
            # NumPy配列をPIL Imageに変換
            pil_image = self._numpy_to_pil(image)
            if pil_image is None:
                return None
            
            original_size = pil_image.size
            
            # リサイズ
            if resize_factor != 1.0:
                new_size = (
                    int(original_size[0] * resize_factor), 
                    int(original_size[1] * resize_factor)
                )
                new_size = (
                    max(self.config.min_texture_size, new_size[0]), 
                    max(self.config.min_texture_size, new_size[1])
                )
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"[i] テクスチャリサイズ: {original_size} → {new_size}")
            
            # WebP形式で圧縮
            webp_buffer = io.BytesIO()
            
            # アルファチャンネルの処理
            if pil_image.mode == 'RGBA':
                pil_image.save(webp_buffer, format='WebP', quality=quality, method=6)
            else:
                # RGBに変換してWebP保存
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                pil_image.save(webp_buffer, format='WebP', quality=quality, method=6)
            
            # WebPからPIL Imageに戻す
            webp_buffer.seek(0)
            compressed_pil = Image.open(webp_buffer)
            
            # NumPy配列に変換
            compressed_array = self._pil_to_numpy(compressed_pil)
            
            print(f"[✓] WebP圧縮完了: 品質{quality}%")
            return compressed_array
            
        except Exception as e:
            print(f"[!] WebP圧縮失敗: {e}")
            return None
    
    def _compress_texture(self, image, quality: float = 0.5) -> Optional[np.ndarray]:
        """テクスチャ画像を圧縮（従来の方式）"""
        try:
            # NumPy配列をPIL Imageに変換
            pil_image = self._numpy_to_pil(image)
            if pil_image is None:
                return None
            
            # 解像度削減
            original_size = pil_image.size
            new_size = (
                int(original_size[0] * quality), 
                int(original_size[1] * quality)
            )
            new_size = (
                max(self.config.min_texture_size, new_size[0]), 
                max(self.config.min_texture_size, new_size[1])
            )
            
            compressed = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # PIL ImageをNumPy配列に戻す
            compressed_array = self._pil_to_numpy(compressed)
            
            print(f"[i] テクスチャ: {original_size} → {new_size}")
            return compressed_array
            
        except Exception as e:
            print(f"[!] テクスチャ圧縮失敗: {e}")
            return None
    
    def _numpy_to_pil(self, image) -> Optional[Image.Image]:
        """NumPy配列をPIL Imageに変換"""
        try:
            if isinstance(image, np.ndarray):
                if image.dtype != np.uint8:
                    image = (image * 255).astype(np.uint8)
                
                if len(image.shape) == 3:
                    if image.shape[2] == 4:
                        return Image.fromarray(image, 'RGBA')
                    else:
                        return Image.fromarray(image, 'RGB')
                else:
                    return Image.fromarray(image, 'L')
            else:
                return image
                
        except Exception as e:
            print(f"[!] NumPy→PIL変換エラー: {e}")
            return None
    
    def _pil_to_numpy(self, pil_image: Image.Image) -> Optional[np.ndarray]:
        """PIL ImageをNumPy配列に変換"""
        try:
            compressed_array = np.array(pil_image)
            if compressed_array.dtype != np.uint8:
                compressed_array = compressed_array.astype(np.uint8)
            
            # float32に正規化
            return compressed_array.astype(np.float32) / 255.0
            
        except Exception as e:
            print(f"[!] PIL→NumPy変換エラー: {e}")
            return None