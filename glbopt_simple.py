#!/usr/bin/env python3
"""
GLB最適化ツール（シンプル版）

基本的な最適化機能のみを提供する軽量版
"""

import sys
import os
from pathlib import Path

from glbtools import GLBOptimizer, OptimizationConfig, get_mode_config


def print_usage():
    """使用方法を表示"""
    print("GLB最適化ツール（シンプル版）")
    print("Usage: python glbopt_simple.py <input.glb> [mode] [target_ratio]")
    print()
    print("モード:")
    print("  normal     - 安全最適化（デフォルト）")
    print("  aggressive - 適度軽量化")
    print("  ultra      - 積極軽量化")
    print("  vertex     - 頂点削除特化")
    print("  repair     - 軽量修復")
    print()
    print("使用例:")
    print("  python glbopt_simple.py model.glb")
    print("  python glbopt_simple.py model.glb ultra 0.3")


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print_usage()
        return 1
    
    input_file = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "normal"
    target_ratio = float(sys.argv[3]) if len(sys.argv) > 3 else None
    
    # 入力ファイルチェック
    if not os.path.exists(input_file):
        print(f"エラー: ファイルが見つかりません: {input_file}")
        return 1
    
    # デフォルト比率取得
    if target_ratio is None:
        target_ratio, _ = get_mode_config(mode)
    
    # 出力パス生成
    input_path = Path(input_file)
    output_file = str(input_path.parent / f"{input_path.stem}_{mode}{input_path.suffix}")
    
    print(f"入力: {input_file}")
    print(f"出力: {output_file}")
    print(f"モード: {mode}")
    print(f"比率: {target_ratio}")
    
    # 最適化実行
    config = OptimizationConfig()
    optimizer = GLBOptimizer(config)
    
    mode_map = {
        "normal": optimizer.optimize_safe_texture_preserving,
        "aggressive": optimizer.optimize_aggressive,
        "ultra": optimizer.optimize_ultra_light,
        "vertex": optimizer.optimize_vertex_cleanup,
        "repair": optimizer.optimize_hole_filling
    }
    
    optimize_func = mode_map.get(mode, optimizer.optimize_safe_texture_preserving)
    
    if mode in ["vertex", "repair"]:
        success = optimize_func(input_file, output_file)
    else:
        success = optimize_func(input_file, output_file, target_ratio)
    
    if success:
        # ファイルサイズ比較
        original_size = os.path.getsize(input_file)
        output_size = os.path.getsize(output_file)
        reduction = (1 - output_size / original_size) * 100
        
        print(f"最適化完了!")
        print(f"ファイルサイズ: {original_size/1024/1024:.2f}MB → {output_size/1024/1024:.2f}MB")
        print(f"削減率: {reduction:.1f}%")
        return 0
    else:
        print("最適化に失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())