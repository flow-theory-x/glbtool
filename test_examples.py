#!/usr/bin/env python3
"""
GLBToolsのテスト用サンプルコード

リファクタリングされたGLBToolsライブラリの使用例とテストコード
"""

import os
import tempfile
from pathlib import Path

# GLBToolsライブラリのインポート
from glbtools import (
    GLBOptimizer, OptimizationConfig,
    MeshProcessor, TextureProcessor, SceneManager,
    get_logger, set_log_level, get_performance_monitor,
    get_file_validator, get_parameter_validator,
    ProgressTracker, OptimizationMode
)


def test_basic_optimization():
    """基本的な最適化のテスト"""
    print("=== 基本的な最適化テスト ===")
    
    # ログ設定
    logger = get_logger()
    logger.info("基本最適化テストを開始")
    
    # 設定作成
    config = OptimizationConfig()
    config.enable_performance_monitoring = True
    
    # オプティマイザー作成
    optimizer = GLBOptimizer(config)
    
    # テスト用ファイルがある場合のみ実行
    test_file = "sample.glb"
    if os.path.exists(test_file):
        output_file = "test_output.glb"
        
        logger.info(f"テストファイル: {test_file}")
        
        # 最適化実行
        success = optimizer.optimize_safe_texture_preserving(
            test_file, output_file, target_faces_ratio=0.7
        )
        
        if success:
            logger.success("基本最適化テスト成功")
        else:
            logger.failure("基本最適化テスト失敗")
        
        # クリーンアップ
        if os.path.exists(output_file):
            os.remove(output_file)
    else:
        logger.warning(f"テストファイル {test_file} が見つかりません")


def test_individual_processors():
    """個別プロセッサーのテスト"""
    print("\n=== 個別プロセッサーテスト ===")
    
    logger = get_logger()
    config = OptimizationConfig()
    
    # 各プロセッサーの初期化テスト
    try:
        mesh_processor = MeshProcessor(config)
        texture_processor = TextureProcessor(config)
        scene_manager = SceneManager()
        
        logger.success("全プロセッサーの初期化成功")
        
        # メッシュプロセッサーの機能テスト
        logger.info("メッシュプロセッサー機能をテスト中...")
        
        # テスト用の簡単なメッシュデータ（存在する場合）
        test_file = "sample.glb"
        if os.path.exists(test_file):
            import trimesh
            scene = trimesh.load(test_file)
            
            if hasattr(scene, 'geometry'):
                for name, geometry in scene.geometry.items():
                    logger.info(f"ジオメトリ {name} を処理中...")
                    
                    # 穴検出テスト
                    holes = mesh_processor.detect_mesh_holes(geometry)
                    logger.info(f"検出された問題: {len(holes)}個")
                    
                    # クリーンアップテスト
                    success = mesh_processor.clean_geometry(geometry)
                    if success:
                        logger.success(f"{name}: クリーンアップ成功")
                    else:
                        logger.failure(f"{name}: クリーンアップ失敗")
                    
                    break  # 最初のジオメトリのみテスト
        
        logger.success("個別プロセッサーテスト完了")
        
    except Exception as e:
        logger.error(f"プロセッサーテストエラー: {e}")


def test_validation():
    """検証機能のテスト"""
    print("\n=== 検証機能テスト ===")
    
    logger = get_logger()
    file_validator = get_file_validator()
    param_validator = get_parameter_validator()
    
    # ファイル検証テスト
    test_cases = [
        ("sample.glb", "存在するファイル"),
        ("nonexistent.glb", "存在しないファイル"),
        ("test.txt", "不正な拡張子"),
    ]
    
    for file_path, description in test_cases:
        logger.info(f"テスト: {description}")
        is_valid, errors = file_validator.validate_input_file(file_path)
        
        if is_valid:
            logger.success(f"✓ {description}: 検証成功")
        else:
            logger.info(f"✗ {description}: 検証失敗 - {errors}")
    
    # パラメータ検証テスト
    param_tests = [
        (0.5, "正常な比率"),
        (1.5, "範囲外の比率"),
        ("invalid", "無効な型"),
    ]
    
    for ratio, description in param_tests:
        logger.info(f"テスト: {description}")
        try:
            is_valid, errors = param_validator.validate_target_ratio(ratio)
            
            if is_valid:
                logger.success(f"✓ {description}: 検証成功")
            else:
                logger.info(f"✗ {description}: 検証失敗 - {errors}")
        except Exception as e:
            logger.info(f"✗ {description}: 例外発生 - {e}")


def test_progress_tracking():
    """進捗追跡のテスト"""
    print("\n=== 進捗追跡テスト ===")
    
    logger = get_logger()
    
    # 進捗追跡のシミュレーション
    total_steps = 10
    tracker = ProgressTracker(total_steps, "テスト処理")
    
    import time
    
    for i in range(total_steps):
        # 擬似的な処理時間
        time.sleep(0.1)
        
        # 進捗更新
        tracker.update(1, f"ステップ {i+1} 完了")
    
    tracker.finish("全ステップ完了")
    logger.success("進捗追跡テスト完了")


def test_performance_monitoring():
    """パフォーマンス監視のテスト"""
    print("\n=== パフォーマンス監視テスト ===")
    
    logger = get_logger()
    monitor = get_performance_monitor()
    
    # 擬似的な処理をパフォーマンス監視
    with monitor.measure("テスト処理1"):
        import time
        time.sleep(0.2)
        logger.info("テスト処理1を実行中...")
    
    with monitor.measure("テスト処理2"):
        time.sleep(0.1)
        logger.info("テスト処理2を実行中...")
    
    # サマリー表示
    monitor.log_summary()
    logger.success("パフォーマンス監視テスト完了")


def test_configuration():
    """設定のテスト"""
    print("\n=== 設定テスト ===")
    
    logger = get_logger()
    
    # デフォルト設定
    config1 = OptimizationConfig()
    logger.info(f"デフォルトWebP品質: {config1.webp_quality_normal}")
    logger.info(f"デフォルトログレベル: {config1.log_level}")
    
    # カスタム設定
    config2 = OptimizationConfig()
    config2.webp_quality_normal = 90
    config2.max_processing_time_seconds = 600
    config2.enable_progress_bar = False
    
    logger.info(f"カスタムWebP品質: {config2.webp_quality_normal}")
    logger.info(f"カスタムタイムアウト: {config2.max_processing_time_seconds}秒")
    
    logger.success("設定テスト完了")


def test_error_handling():
    """エラーハンドリングのテスト"""
    print("\n=== エラーハンドリングテスト ===")
    
    logger = get_logger()
    
    # 意図的にエラーを発生させるテスト
    try:
        optimizer = GLBOptimizer()
        
        # 存在しないファイルで最適化を試行
        success = optimizer.optimize_safe("nonexistent.glb", "output.glb")
        
        if not success:
            logger.success("エラーハンドリング: 適切に失敗を検出")
        else:
            logger.warning("エラーハンドリング: 予期しない成功")
            
    except Exception as e:
        logger.info(f"エラーハンドリング: 例外をキャッチ - {e}")
    
    logger.success("エラーハンドリングテスト完了")


def run_all_tests():
    """全テストを実行"""
    print("GLBTools ライブラリテスト開始")
    print("=" * 60)
    
    # ログレベルを設定
    import logging
    set_log_level(logging.INFO)
    
    # 各テストを実行
    test_basic_optimization()
    test_individual_processors()
    test_validation()
    test_progress_tracking()
    test_performance_monitoring()
    test_configuration()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("全テスト完了")


def demo_advanced_usage():
    """高度な使用例のデモ"""
    print("\n=== 高度な使用例デモ ===")
    
    logger = get_logger()
    
    # カスタム設定で最適化実行
    config = OptimizationConfig()
    config.webp_quality_aggressive = 80
    config.enable_performance_monitoring = True
    config.max_processing_time_seconds = 120
    
    optimizer = GLBOptimizer(config)
    
    test_file = "sample.glb"
    if os.path.exists(test_file):
        logger.info("高度な使用例を実行中...")
        
        # パフォーマンス監視付きで最適化
        monitor = get_performance_monitor()
        
        with monitor.measure("カスタム最適化"):
            success = optimizer.optimize_aggressive(
                test_file, 
                "demo_output.glb",
                target_faces_ratio=0.6,
                texture_quality=0.8
            )
        
        if success:
            logger.success("高度な使用例: 成功")
            
            # ファイルサイズ比較
            original_size = os.path.getsize(test_file)
            output_size = os.path.getsize("demo_output.glb")
            reduction = (1 - output_size / original_size) * 100
            
            logger.stats(f"ファイルサイズ削減: {reduction:.1f}%")
            
            # クリーンアップ
            os.remove("demo_output.glb")
        
        # パフォーマンスサマリー
        monitor.log_summary()
    else:
        logger.warning("デモ用のサンプルファイルが見つかりません")


if __name__ == "__main__":
    # 全テストを実行
    run_all_tests()
    
    # 高度な使用例デモ
    demo_advanced_usage()