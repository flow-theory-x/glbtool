#!/usr/bin/env python3
"""
GLB最適化ツール（アドバンス版）

リファクタリングされた高機能版のGLB最適化ツール
- 型安全性
- 詳細なログ機能
- 進捗表示
- パフォーマンス監視
- 強力な入力検証
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

from glbtools import (
    GLBOptimizer, OptimizationConfig, get_mode_config, validate_target_ratio,
    get_logger, set_log_level, enable_file_logging,
    get_performance_monitor, ProgressTracker,
    get_file_validator, get_parameter_validator,
    OptimizationMode
)


def setup_logging(config: OptimizationConfig) -> None:
    """ログ設定を初期化"""
    # ログレベルを設定
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    
    level = log_levels.get(config.log_level.upper(), logging.INFO)
    set_log_level(level)
    
    # ファイルログを有効化
    if config.enable_file_logging:
        log_file = Path(config.log_file_path)
        enable_file_logging(log_file)


def print_usage() -> None:
    """使用方法を表示"""
    print("GLB最適化ツール v1.0.0")
    print("=" * 50)
    print("Usage: python glbopt.py <input.glb> [options]")
    print()
    print("オプション:")
    print("  --mode MODE          最適化モード (default: normal)")
    print("  --ratio RATIO        面削減率 0.01-1.0 (default: モード依存)")
    print("  --output PATH        出力ファイルパス (default: 自動生成)")
    print("  --log-level LEVEL    ログレベル DEBUG|INFO|WARNING|ERROR")
    print("  --file-log           ファイルログを有効化")
    print("  --no-progress        進捗バーを無効化")
    print("  --no-validation      入力検証をスキップ")
    print("  --timeout SECONDS    処理タイムアウト秒数")
    print("  --help, -h           このヘルプを表示")
    print()
    print("最適化モード:")
    print("  normal     - 安全最適化（テクスチャ保持、品質重視）")
    print("  aggressive - 適度軽量化（WebP85%品質）")
    print("  ultra      - 積極軽量化（WebP70%品質+75%リサイズ）")
    print("  vertex     - 頂点削除特化（重複・未使用頂点の徹底削除）")
    print("  repair     - 軽量修復（基本的なメッシュクリーンアップ）")
    print()
    print("使用例:")
    print("  python glbopt.py model.glb")
    print("  python glbopt.py model.glb --mode ultra --ratio 0.3")
    print("  python glbopt.py model.glb --output optimized.glb --file-log")


def parse_arguments() -> dict:
    """コマンドライン引数を解析"""
    args = sys.argv[1:]
    
    if not args or "--help" in args or "-h" in args:
        print_usage()
        sys.exit(0)
    
    # 必須引数
    input_file = args[0]
    
    # オプション引数のデフォルト値
    options = {
        "input_file": input_file,
        "mode": "normal",
        "ratio": None,  # モード依存
        "output": None,  # 自動生成
        "log_level": "INFO",
        "file_log": False,
        "progress": True,
        "validation": True,
        "timeout": 300
    }
    
    # オプション解析
    i = 1
    while i < len(args):
        arg = args[i]
        
        if arg == "--mode" and i + 1 < len(args):
            options["mode"] = args[i + 1]
            i += 2
        elif arg == "--ratio" and i + 1 < len(args):
            try:
                options["ratio"] = float(args[i + 1])
            except ValueError:
                print(f"エラー: 無効な比率値: {args[i + 1]}")
                sys.exit(1)
            i += 2
        elif arg == "--output" and i + 1 < len(args):
            options["output"] = args[i + 1]
            i += 2
        elif arg == "--log-level" and i + 1 < len(args):
            options["log_level"] = args[i + 1]
            i += 2
        elif arg == "--timeout" and i + 1 < len(args):
            try:
                options["timeout"] = int(args[i + 1])
            except ValueError:
                print(f"エラー: 無効なタイムアウト値: {args[i + 1]}")
                sys.exit(1)
            i += 2
        elif arg == "--file-log":
            options["file_log"] = True
            i += 1
        elif arg == "--no-progress":
            options["progress"] = False
            i += 1
        elif arg == "--no-validation":
            options["validation"] = False
            i += 1
        else:
            i += 1
    
    return options


def validate_input(options: dict) -> bool:
    """入力を検証"""
    logger = get_logger()
    file_validator = get_file_validator()
    param_validator = get_parameter_validator()
    
    # ファイル検証
    is_valid, errors = file_validator.validate_input_file(options["input_file"])
    if not is_valid:
        for error in errors:
            logger.error(error)
        return False
    
    # GLB内容検証
    if options["validation"]:
        logger.info("GLBファイルの内容を検証中...")
        is_valid, errors = file_validator.validate_glb_content(options["input_file"])
        if not is_valid:
            for error in errors:
                logger.error(error)
            return False
        logger.success("GLBファイルの検証完了")
    
    # パラメータ検証
    is_valid, errors = param_validator.validate_mode(options["mode"])
    if not is_valid:
        for error in errors:
            logger.error(error)
        return False
    
    if options["ratio"] is not None:
        is_valid, errors = param_validator.validate_target_ratio(options["ratio"])
        if not is_valid:
            for error in errors:
                logger.error(error)
            return False
    
    return True


def generate_output_path(input_path: str, mode: str) -> str:
    """出力パスを自動生成"""
    input_path_obj = Path(input_path)
    stem = input_path_obj.stem
    suffix = input_path_obj.suffix
    
    output_name = f"{stem}_{mode}{suffix}"
    return str(input_path_obj.parent / output_name)


def show_file_info(input_path: str, output_path: Optional[str] = None) -> None:
    """ファイル情報を表示"""
    logger = get_logger()
    
    # 入力ファイル情報
    input_size = os.path.getsize(input_path)
    logger.info(f"入力ファイル: {input_path}")
    logger.info(f"ファイルサイズ: {input_size / 1024 / 1024:.2f} MB")
    
    # 出力ファイル情報（処理後）
    if output_path and os.path.exists(output_path):
        output_size = os.path.getsize(output_path)
        compression_ratio = (1 - output_size / input_size) * 100
        
        logger.success(f"出力ファイル: {output_path}")
        logger.success(f"最適化後サイズ: {output_size / 1024 / 1024:.2f} MB")
        logger.stats(f"圧縮率: {compression_ratio:.1f}%")
        
        # 異常チェック
        if output_size < input_size * 0.005:
            logger.warning("出力ファイルが異常に小さいです。内容を確認してください。")


def main() -> int:
    """メイン関数"""
    logger = None
    try:
        # 引数解析
        options = parse_arguments()
        
        # 設定初期化
        config = OptimizationConfig()
        config.log_level = options["log_level"]
        config.enable_file_logging = options["file_log"]
        config.enable_progress_bar = options["progress"]
        config.max_processing_time_seconds = options["timeout"]
        
        # ログ設定
        setup_logging(config)
        logger = get_logger()
        
        logger.info("=== GLB最適化ツール（アドバンス版）開始 ===")
        
        # 入力検証
        if not validate_input(options):
            logger.error("入力検証に失敗しました")
            return 1
        
        # モード設定の取得
        if options["ratio"] is None:
            default_ratio, mode_config = get_mode_config(options["mode"])
            options["ratio"] = default_ratio
        
        # 出力パス生成
        if options["output"] is None:
            options["output"] = generate_output_path(options["input_file"], options["mode"])
        
        # 出力パス検証
        file_validator = get_file_validator()
        is_valid, errors = file_validator.validate_output_path(options["output"])
        if not is_valid:
            for error in errors:
                logger.error(error)
            return 1
        
        # ファイル情報表示
        show_file_info(options["input_file"])
        
        # 処理設定表示
        logger.info(f"最適化モード: {options['mode']}")
        logger.info(f"面削減率: {options['ratio']}")
        logger.info(f"出力パス: {options['output']}")
        
        # パフォーマンス監視開始
        monitor = get_performance_monitor()
        
        with monitor.measure("全体処理"):
            # 最適化実行
            optimizer = GLBOptimizer(config)
            
            mode_map = {
                "normal": optimizer.optimize_safe_texture_preserving,
                "aggressive": optimizer.optimize_aggressive,
                "ultra": optimizer.optimize_ultra_light,
                "vertex": optimizer.optimize_vertex_cleanup,
                "repair": optimizer.optimize_hole_filling
            }
            
            optimize_func = mode_map.get(options["mode"], optimizer.optimize_safe_texture_preserving)
            
            if options["mode"] in ["vertex", "repair"]:
                # 比率不要なモード
                success = optimize_func(options["input_file"], options["output"])
            else:
                # 比率が必要なモード
                success = optimize_func(options["input_file"], options["output"], options["ratio"])
        
        # 結果表示
        if success:
            show_file_info(options["input_file"], options["output"])
            logger.success("最適化が正常に完了しました")
            
            # パフォーマンスサマリー
            if config.enable_performance_monitoring:
                monitor.log_summary()
            
            return 0
        else:
            logger.error("最適化に失敗しました")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("ユーザーによって処理が中断されました")
        return 1
    except Exception as e:
        if logger:
            logger.error(f"予期しないエラーが発生しました: {e}")
        else:
            print(f"エラー: {e}")
        return 1
    finally:
        if logger:
            logger.info("=== GLB最適化ツール終了 ===")


if __name__ == "__main__":
    sys.exit(main())