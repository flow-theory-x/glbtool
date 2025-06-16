# GLB Optimizer

GLBファイルのファイルサイズを大幅に削減するPythonスクリプト。メッシュの簡略化、頂点の最適化、テクスチャ圧縮により、用途に応じて4つの最適化モードを選択できます。

## 機能

- **メッシュ簡略化**: ポリゴン数を削減してファイルサイズを縮小
- **頂点最適化**: 未使用・重複・孤立頂点を削除
- **テクスチャ圧縮**: WebP形式での高効率圧縮
- **メタデータ削除**: 不要な情報を除去
- **4つの最適化モード**: 用途に応じて選択可能
- **安全な処理**: テクスチャとマテリアル情報を可能な限り保持

## インストール

```bash
pip3 install trimesh pillow numpy networkx
```

## 使用方法

### 基本的な使用法

```bash
# 通常モード（デフォルト）- テクスチャ保持重視
python3 glbopt.py input.glb

# 大幅軽量化モード
python3 glbopt.py input.glb aggressive

# 超軽量化モード
python3 glbopt.py input.glb ultra

# 頂点削除特化モード（NEW!）
python3 glbopt.py input.glb vertex

# 穴埋め特化モード（NEW!）
python3 glbopt.py input.glb repair
```

### 詳細オプション

```bash
python3 glbopt.py <input.glb> [mode] [target_ratio]
```

**パラメータ:**
- `input.glb`: 入力GLBファイル
- `mode`: 最適化モード（省略可）
- `target_ratio`: メッシュ削減率 0.05-1.0（省略可、vertex・repairモードでは無効）

## 最適化モード

### 1. Normal（通常）
```bash
python3 glbopt.py model.glb normal
# または
python3 glbopt.py model.glb
```
- **用途**: 品質を重視したい場合
- **処理**: 重複頂点削除、テクスチャ保持
- **特徴**: テクスチャとマテリアルを最大限保持

### 2. Aggressive（大幅軽量化）
```bash
python3 glbopt.py model.glb aggressive
```
- **用途**: ファイルサイズとのバランス重視
- **処理**: 重複頂点削除、WebP85%品質圧縮
- **特徴**: 軽度なテクスチャ圧縮で適度な軽量化

### 3. Ultra（超軽量化）
```bash
python3 glbopt.py model.glb ultra
```
- **用途**: 最小ファイルサイズ重視
- **処理**: 重複頂点削除、WebP70%品質+75%リサイズ
- **特徴**: 極限まで軽量化、品質は犠牲に

### 4. Vertex（頂点削除特化）⭐️ NEW
```bash
python3 glbopt.py model.glb vertex
```
- **用途**: 頂点数削減による軽量化
- **処理**: 未使用・重複・孤立頂点を徹底削除
- **特徴**: 
  - 面で使用されていない頂点を自動検出・削除
  - 重複頂点の統合
  - 孤立頂点の除去
  - UV座標も適切に更新
  - 詳細な削減レポート表示

### 5. Repair（穴埋め特化）⭐️ NEW
```bash
python3 glbopt.py model.glb repair
```
- **用途**: メッシュの穴・開口部の修復
- **処理**: 穴の検出と自動修復
- **特徴**: 
  - 水密性チェックによる開口部検出
  - 境界エッジの特定
  - 自動穴埋め処理
  - 修復前後の詳細レポート
  - メッシュ整合性の検証・修復

## カスタム削減率

```bash
# 通常モードでメッシュを50%に削減
python3 glbopt.py model.glb normal 0.5

# 大幅軽量化モードでメッシュを20%に削減
python3 glbopt.py model.glb aggressive 0.2

# 頂点削除モード（target_ratioは無視される）
python3 glbopt.py model.glb vertex

# 穴埋めモード（target_ratioは無視される）
python3 glbopt.py model.glb repair
```

## 出力ファイル

最適化されたファイルは元のファイル名にモード名を追加して保存されます：

- `model.glb` → `model_normal.glb`
- `model.glb` → `model_aggressive.glb`
- `model.glb` → `model_ultra.glb`
- `model.glb` → `model_vertex.glb`
- `model.glb` → `model_repair.glb`

## 使用例

### 頂点数が多すぎるモデルの最適化
```bash
# 未使用頂点を削除して軽量化
python3 glbopt.py character.glb vertex
```

### メッシュに穴が空いているモデルの修復
```bash
# 穴を検出して自動修復
python3 glbopt.py broken_model.glb repair
```

### Webアプリケーション用
```bash
# 読み込み速度重視
python3 glbopt.py character.glb ultra
```

### VR/AR用
```bash
# 品質とパフォーマンスのバランス
python3 glbopt.py environment.glb aggressive
```

### 高品質表示用
```bash
# 品質重視
python3 glbopt.py product.glb normal 0.8
```

## 実行結果例

### 頂点削除特化モード
```
[i] 入力: character.glb
[i] 出力: character_vertex.glb
[i] モード: vertex
[i] 元のファイルサイズ: 24.66 MB
[i] 頂点削除特化モード: 未使用・重複頂点を徹底削除
[i] Character_Body: 15420頂点を処理中...
[✓] 未使用頂点削除: 3240個 (15420 → 12180)
[✓] Character_Body: 重複頂点を統合
[✓] Character_Body: 孤立頂点を削除
[✓] Character_Body: 15420 → 11980頂点 (22.3%削減)
[✓] 全体: 15420 → 11980頂点
[✓] 削減量: 3440頂点 (22.3%)
[✓] 頂点削除特化最適化完了: character_vertex.glb
[✓] 最適化後のファイルサイズ: 19.85 MB
[✓] 圧縮率: 19.5%
```

### 穴埋め特化モード
```
[i] 入力: broken_model.glb
[i] 出力: broken_model_repair.glb
[i] モード: repair
[i] 元のファイルサイズ: 18.45 MB
[i] 穴埋め特化モード: メッシュの穴を検出・修復
[i] Mesh_01: 穴の検出を開始...
[i] メッシュに開口部が検出されました
[i] 境界エッジを検出: 24本
[!] Mesh_01: 検出された問題: 開口部あり, 境界エッジ: 24本
[✓] 穴を埋めました: 12面を追加
[✓] Mesh_01: 穴埋め完了 (12面追加)
[i] 処理完了: 1個のメッシュを検査
[i] 検出された問題: 2個
[✓] 修復成功: 1個
[✓] 穴埋め特化最適化完了: broken_model_repair.glb
[✓] 最適化後のファイルサイズ: 18.52 MB
[✓] 圧縮率: -0.4%
```

### 超軽量化モード
```
[i] 入力: character.glb
[i] 出力: character_ultra.glb
[i] モード: ultra
[i] 簡略化率: 0.1
[i] 元のファイルサイズ: 24.66 MB
[i] 積極的軽量化モード: サイズ削減を重視
[✓] Character_01: 12534 → 1253 faces
[✓] Character_02: 8924 → 892 faces
[i] テクスチャ: (1024, 1024) → (768, 768)
[✓] WebP圧縮完了: 品質70%
[✓] 超軽量化完了: character_ultra.glb
[✓] 最適化後のファイルサイズ: 2.15 MB
[✓] 圧縮率: 91.3%
```

## 注意事項

- **バックアップ**: 元のファイルは自動で保持されます
- **品質低下**: ultraモードでは見た目の品質が大幅に低下する可能性があります
- **テクスチャ**: 一部の複雑なマテリアル設定は失われる場合があります
- **互換性**: Three.js、Babylon.js等の主要な3Dライブラリで動作確認済み
- **頂点削除**: vertexモードは頂点数は削減しますが、ポリゴン形状は保持されます
- **穴埋め**: repairモードは穴を埋めるため、わずかにファイルサイズが増加する場合があります

## トラブルシューティング

### エラー: No module named 'PIL'
```bash
pip3 install pillow
```

### エラー: No module named 'trimesh'
```bash
pip3 install trimesh
```

### エラー: No module named 'networkx'
```bash
pip3 install networkx
```

### 出力ファイルが小さすぎる警告
- より保守的なモード（normal）を試してください
- target_ratioを大きな値（0.7-0.9）に設定してください

### 最適化に失敗した場合
- 元のファイルが自動的にコピーされます
- 入力ファイルの形式を確認してください

### 頂点削除モードで削減効果が少ない場合
- すでに最適化されたファイルの可能性があります
- 他のモード（aggressive、ultra）との組み合わせも検討してください

### 穴埋めモードで修復できない場合
- メッシュが複雑すぎる可能性があります
- 3Dモデリングソフトで手動修復を検討してください
- normalモードで基本的なクリーンアップを試してください

## ライセンス

MIT License

## 必要な依存関係

- Python 3.7+
- trimesh
- pillow
- numpy
- networkx

## 更新履歴

- v1.0.0: 初回リリース
- v1.1.0: 3つの最適化モード追加
- v1.2.0: テクスチャ圧縮機能追加
- v1.3.0: メタデータ削除機能追加
- v1.4.0: 頂点削除特化モード追加、未使用頂点削除機能実装
- v1.5.0: 穴埋め特化モード追加、メッシュ修復機能実装