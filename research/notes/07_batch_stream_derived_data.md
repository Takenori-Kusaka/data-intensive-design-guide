# 07 バッチ・ストリーム・派生データ、ストレージと分析基盤

調査日：2026-11-18

## 1. 問い（このノートが答えること。対応する Part）

- Part 5（基礎）：ストレージと索引は何を買い、何を払うか。B ツリーと LSM、行指向と列指向、全文検索とベクトル検索。OLTP と分析を分ける理由と、分けない判断
- Part 4（ステップ 3）：データモデル（リレーショナル・ドキュメント・グラフ・イベント）をどう選ぶか
- Part 12（ステップ 8）：派生データをどう作り、作り直すか。バッチとストリーム、時間と遅延データ、「厳密に 1 回」、ログからの再構築の前提条件、マテリアライズドビューの増分更新
- Part 13 の一部（分析基盤・ログ基盤・ETL 基盤）：費用の決まり方、データ品質と系譜

このノートの読み方：本文の `[n]` は 11 節の出典番号。「記憶・要確認」と書いた箇所は、今回の調査で本文を開いて確かめていない。

## 2. 標準・定義（節番号）

この領域に、設計の選択そのものを決める国際標準はほとんどない。用語の定義は原論文と仕様（Apache の各プロジェクトの仕様文書）に置かれている。

### 2.1 ストレージエンジンの用語

| 用語 | 定義 | 出典 |
| --- | --- | --- |
| LSM ツリー | 索引の変更を遅らせてまとめ、メモリ上の構成要素からディスク上の構成要素へ、マージソートに似た形で順に流し込むディスクベースの構造。挿入が多く、検索より挿入が多い用途（履歴表・ログ）に向くと要旨が明言。即時応答が要る索引検索では I/O 効率を失う場合があるとも明言 | [1] 要旨 |
| 書き込み増幅 | ストレージに書いたバイト数 ÷ データベースに書いたバイト数 | [2] Amplification factors |
| 読み取り増幅 | 1 回の問い合わせあたりのディスク読み取り回数 | [2] |
| 空間増幅 | ディスク上のファイルの大きさ ÷ データの大きさ | [2] |
| MVCC | 各 SQL 文が、ある時点のスナップショットを見る多版型の並行制御。読み取りは書き込みを妨げず、書き込みは読み取りを妨げない | [5] 13.1 |
| HOT（Heap-Only Tuple） | 索引が参照する列を変えず、同じページに空きがある更新で、索引エントリの追加を省く PostgreSQL の最適化 | [4] |

### 2.2 列指向と実行方式

| 用語 | 定義 | 出典 |
| --- | --- | --- |
| 行ストア／列ストア | 行ストアは 1 レコードの属性を連続して置き、1 回の書き込みで 1 件を出せる「書き込み最適化」。列ストアは列ごとに置く「読み取り最適化」 | [8] 1 節 |
| ネストした列形式 | Dremel が示した、ネストしたデータの列表現。Parquet は「Dremel encoding」（definition level と repetition level）を使うと仕様に書く | [9][10] |
| Parquet のレイアウト | ファイル → row group → column chunk（→ page）。メタデータは末尾（フッター）。読み手はフッターから必要な列のチャンクだけを読む | [10] File format |
| ベクトル化実行 | Volcano 型の反復子を保ちつつ、1 回の呼び出しで値の束（ベクトル）を処理する方式。MonetDB/X100 が提示 | [11] 要旨 |
| データ中心のコンパイル | 問い合わせを LLVM で機械語に変換する方式。HyPer が提示 | [12] 要旨 |

### 2.3 表形式（オープンテーブル形式）の仕様の位置づけ

| 仕様 | 管理主体 | 版の状態（2026-11-18 時点） | 一貫性の根拠 | 出典 |
| --- | --- | --- | --- | --- |
| Apache Iceberg Table Spec | Apache Software Foundation | 形式の版 1・2・3 は完成・採択済み。版 4 は「under active development」で未採択。ライブラリは 1.12.0（2026-09-29） | メタデータファイルの原子的な差し替え（atomic swap）が直列化可能な分離の基礎。原子操作の実現方法はカタログ依存で、仕様は標準化しない | [20] Format Versioning、Goals、Optimistic Concurrency |
| Delta Transaction Log Protocol | Linux Foundation（delta-io） | 版番号ではなく reader／writer の版＋「table features」で機能を宣言。Delta Lake 4.4.1（10 月 5 日。ページは年を表示しないが直近の公開のため 2026 年と判断）。catalog-managed tables の章が仕様にある | 表は原子的な版の直列の履歴。書き手は既存のログエントリを上書きしてはならない（MUST） | [21] |
| Apache Hudi | Apache Software Foundation | 文書の版は 1.2.1（公開日はダウンロードページに記載なし）。Copy-on-Write と Merge-on-Read の 2 つの表タイプ | タイムライン（今回は仕様本文を開けず、表タイプの文書のみ確認） | [22] |

- 3 つとも「オブジェクトストレージ上の不変ファイル（主に Parquet）＋どのファイルが表の現在の版に属するかを決めるメタデータ層」という同じ構造。Lakehouse 論文はこれを「transactional metadata layer」と呼ぶ [19] 3 節
- Iceberg の版 2 は行単位の削除（delete file）、版 3 は variant・geometry などの型、既定値、行の系譜、バイナリの deletion vector、版 4（開発中）はメタデータ構造の作り直し [20]。**版 4 を前提にした設計は「草案」扱い**

### 2.4 ストリーム処理の用語

| 用語 | 定義 | 出典 |
| --- | --- | --- |
| イベント時間／処理時間 | イベント時間は事象が発生元で起きた時刻、処理時間は処理する機械の時計の時刻。処理時間は協調が要らず遅延が最小だが、決定的でない | [39] Timely Stream Processing |
| ウォーターマーク | イベント時間の進み具合を示す仕組み。現実の分散データでは 100% 正しいウォーターマークは作れず、ヒューリスティックになる | [53] 脚注 6、[39] |
| Dataflow Model の 4 つの問い | 何を計算するか／イベント時間のどこで／処理時間のいつ結果を出すか／後からの修正をどう扱うか（what・where・when・how） | [53] 本文（節番号は未記録） |
| 無限データの前提 | 「全部そろった」とは分からない前提で、正しさ・遅延・費用の 3 軸の釣り合いを選ばせる | [53] 要旨 |
| チェックポイント | ストリームの再生（replay）と状態のスナップショットの組み合わせ。障害時は状態を戻し、その時点から記録を流し直す。Flink の既定は無効 | [39] Stateful Stream Processing |
| ログコンパクション | キーごとに少なくとも最後の値を残す保持方式。順序は変えず、オフセットも変えない。値が null のレコード（tombstone）は削除を表し、一定時間後に消える | [45] Log Compaction |

### 2.5 国際標準に当たるもの

- グラフ問い合わせ言語 GQL：ISO/IEC 39075:2024（第 1 版、2024）。ISO のカタログページで題名と版を確認 [29]。本文は有料で未確認
- SQL の中でプロパティグラフを問い合わせる SQL/PGQ は ISO/IEC 9075-16:2023（記憶・要確認）
- OpenLineage（LF AI & Data 傘下。記憶・要確認）：Run・Job・Dataset・Facet の 4 つの概念と、Run の状態遷移イベント（START と COMPLETE／FAIL／ABORT のいずれかが必須）を定める [68]。文書の版は 1.55.0

## 3. 製品ごとの違い（表。公式文書の URL・版・日付）

### 3.1 ストレージエンジン：B ツリー系と LSM 系

| 観点 | PostgreSQL 18（ヒープ＋B ツリー） | RocksDB（LSM、level compaction） | RocksDB（universal compaction） |
| --- | --- | --- | --- |
| 更新の方式 | 新しい行の版をヒープに書く。古い版は VACUUM が回収 [3] | 追記し、背景のコンパクションで整理 [2] | 同左 |
| 書き込みの代償 | 更新のたびに全索引へエントリ追加（HOT が効けば省ける）[4]。チェックポイント後の最初の変更でページ全体を WAL に書く（full_page_writes）[7] | 公式の例：500GB で書き込み増幅が約 33（1+2+10+10+10）[2] | 書き込み増幅を下げる目的。空間増幅は必ず増える [2] |
| 読み取りの代償 | 索引 → ヒープ。可視性マップが新しければ索引だけで返せる [3] | 点検索は L0 の全ファイル＋各レベル 1 つ。ブルームフィルタで減らす（10 bits/key で偽陽性約 1%）。範囲走査には効かない [2] | 読み取り増幅が増える場合がある [2] |
| 空間の代償 | 死んだ行の版（膨張）。標準の VACUUM は OS に領域をほぼ返さない [3] | 公式の例で空間増幅 1.14 [2] | コンパクション中に一時的に 2 倍。既定 max_size_amplification_percent=200 [2] |
| 運用の落とし穴 | XID は 32 ビット。残り約 4,000 万で警告、300 万未満で新しい XID の割り当てを拒否。autovacuum_freeze_max_age の既定は 2 億 [3] | 「通常の SSD 上のアプリなら細かく調整しない」ことを公式が勧める [2] | 約 100GB を超える DB には非推奨 [2] |

- PostgreSQL 18.7 の文書（ページのフッターで版を確認）。RocksDB の wiki は最終編集 2023-03-28（**古い。数値は例であり現行版の既定を保証しない**）
- PostgreSQL の B ツリーは、MVCC による同一行の複数版を知らないため「version churn」が性能に効く。bottom-up index deletion と重複排除で緩和する [6] 65.1.4
- 「B ツリーは読み取りに強く LSM は書き込みに強い」は傾向であり、[2] 自身が「どの増幅を最適化すべきか明らかでない場合がある」と書く。測って決める

### 3.2 行指向・列指向・埋め込み分析（ケーススタディ C の 3 製品）

| 観点 | PostgreSQL 18.7 | ClickHouse 26.8 LTS（2026-08-27）／26.10（2026-10-22）[61] | DuckDB 2.0.0 LTS（2026-10-21）[64] |
| --- | --- | --- | --- |
| 格納 | 行（ヒープ） | 列。挿入ごとに part を作り、背景でマージ [60] | 列。単一ファイルの独自形式、または Parquet などを直接読む [64] |
| 主キーの意味 | 一意制約つきの密な索引 | **疎な索引**。8,192 行のかたまり（granule）を指す。一意性は保証しない。マージは同じ主キーの行が同じ part に集まることも保証しない [60] | — |
| 実行 | 行単位 | ベクトル化（文書は今回未確認。記憶・要確認） | 列指向のベクトル化。X100 論文に着想と公式が明記 [64] |
| 並行性 | MVCC。多数の同時書き込み | 挿入はバッチ向き | 1 プロセスが読み書き。複数プロセスからの書き込みは 2.0 の Quack プロトコル経由 [64] |
| 圧縮 | TOAST など（今回未確認） | ソートキーで並べた列を圧縮。ソートキーと型の選び方が圧縮率を左右すると公式が説明 [60] | — |
| 保持 | 自前（パーティションの DROP など） | TTL で削除・移動・ロールアップ。**削除は即時でなくマージ時**。TTL とパーティションキーをそろえるとパーティション単位で落とせる [60] | — |
| 半構造 | jsonb（分解済みのバイナリ形式。GIN 索引）[28] | JSON 型は 25.3 から production ready。パスを部分列として保存し、max_dynamic_paths を超えた分は shared data にまとめる [60] | — |

### 3.3 クラウド DWH の計算とストレージの分離（公式文書に基づく比較。未検証）

| 製品 | 公式の説明 | 出典 |
| --- | --- | --- |
| Snowflake | 論文：共有なし（shared-nothing）は計算とストレージを固く結びつける点が欠点。「multi-cluster, shared-data」構成で分離。表は不変の大きなファイルに水平分割し、ファイル内は列ごとにまとめる。不変ファイルゆえに MVCC が自然な選択。公式文書：shared-disk と shared-nothing の混成、3 層 | [16] 2 節・3 節、[17] |
| BigQuery | 取り込み・保存・最適化を行うストレージ層と、分析を行う計算層に分かれ、独立に動く。列形式（Capacitor）で保存。ページの更新日 2026-11-10 | [18] |
| レイクハウス | DWH と湖の 2 層構成の問題（鮮度の低下・信頼性・総費用・ロックイン・用途の制限）を、開いた形式＋メタデータ層で解くという主張。**著者は Databricks 所属であり、提唱者の立場の論文** | [19] 要旨・1 節 |

### 3.4 全文検索とベクトル検索

| 観点 | 転置索引（Lucene 10.3.0／PostgreSQL GIN） | pgvector 0.8.7（PostgreSQL 13 以降） | Elasticsearch の kNN |
| --- | --- | --- | --- |
| 構造 | 語 → その語を含む文書の一覧。Lucene はセグメントの集まりで、追加は新しいセグメントの作成、のちにマージ [24] | HNSW（多層グラフ）と IVFFlat の 2 種の近似索引 [26] | 近似 kNN と総当たりの厳密 kNN の 2 つ [27] |
| 更新の代償 | GIN：1 行の挿入が多数の索引挿入になり遅い。fastupdate は保留リストにためるが、リストが大きいと検索が遅くなる。大量投入時は索引を落として作り直すことを公式が勧める [23] | HNSW は構築が遅くメモリを多く使う。IVFFlat は構築が速く省メモリだが速度と再現率の釣り合いで劣る。IVFFlat はデータ投入後に作る [26] | — |
| 既定値 | — | 索引なしは厳密検索（再現率は完全）。HNSW：m=16、ef_construction=64、hnsw.ef_search=40。IVFFlat：probes=1 [26] | — |
| 上限 | — | 索引できる次元：vector 2,000、halfvec 4,000、bit 64,000 [26] | — |
| 絞り込み | — | 近似索引では**絞り込みは索引走査の後**。条件が 10% に当たり ef_search=40 なら平均 4 行しか返らない。0.8.0 から iterative index scan [26] | 小さいデータや絞り込み済みの部分集合には厳密 kNN を勧める [27] |

- HNSW の原論文は、層の最大値を指数的に減る確率で無作為に選ぶ多層グラフで、対数的な計算量の伸びを主張 [25]。**近似であり、再現率は 100% ではない**
- 専用ストアと既存 DB の拡張の使い分けについて、中立な権威の規範は一次資料に見つからなかった。確かめられた判断材料は、pgvector の次元上限・絞り込みの挙動・索引の構築費用 [26] と、「小さいデータは厳密検索で足りる」という Elastic と pgvector の共通の記述 [26][27]

### 3.5 ログベースのブローカー：Apache Kafka 4.4 と Redpanda 26.2

| 観点 | Apache Kafka 4.4.0（2026-10-22）[51] | Redpanda 26.2 [52] |
| --- | --- | --- |
| 消費位置の持ち方 | パーティションごとに 1 つの整数（オフセット）。消費者が古いオフセットへ巻き戻して読み直せる。公式は「キューの通常の契約に反するが多くの消費者に不可欠」と説明 [45] | Kafka API 互換（プロトコル 0.11 以降のクライアント）[52] |
| 保持の既定 | retention.ms＝7 日、retention.bytes＝-1（無制限）。公式は retention.ms を「消費者がどれだけ早く読むべきかの SLA」と表現 [46] | 今回は既定値を未確認 |
| コンパクション | cleanup.policy=compact。tombstone は delete.retention.ms（既定 1 日）後に消える。**オフセット 0 から読む消費者は、この時間内に読み終えないと削除を見落とし得る** [45][46] | コンパクション設定の文書あり（題名のみ確認） |
| 消費者グループ | 新しいリバランスプロトコル（KIP-848）は 4.0 で GA。サーバ側では自動で有効だが、消費者側は既定で有効でなく group.protocol の設定が要る [48] | — |
| キュー（share groups） | **Queues for Kafka（KIP-932）は 4.1 でプレビュー、4.2 で production-ready**。レコード単位の確認応答、配信回数の計数、ロック既定 30 秒。4.4 で DLQ（KIP-1191、share.version=2）。4.3.2 に share group の経路の重大なデッドロックの修正 [45][47] | 互換性ページに share groups の記述は見つからなかった（未対応とも書かれていない。要確認）[52] |
| 複製 | ISR。コミット済み＝ISR の全レプリカが適用 [45] | Raft。過半数が書いたらコミット。パーティションごとに Raft グループ [52] |
| 互換の例外 | — | min.insync.replicas、unclean.leader.election.enable、flush.messages などは**設定を受け付けるが効果がない**。KIP-890 のサーバ側は未実装（Redpanda の実装はこの類の誤りを受けないと自己申告）[52] |
| 階層化ストレージ | 制限：コンパクションされたトピックは非対応 [50] | Tiered Storage あり [52] |
| モード | 4.x は KRaft のみ。ZooKeeper モードは削除 [47] | 単一バイナリ（記憶・要確認） |

- 従来のメッセージキューとの違いを Kafka の公式設計文書は次のように書く：多くのメッセージングシステムは「何を消費したか」をブローカー側に持ち、消費済みをすぐ消せる代わりに、ブローカーと消費者の合意が難しくなる。Kafka はオフセットを消費者側に持たせて確認応答を安くし、読み直しを可能にした [45]（消費位置の節。節番号は現行サイトに表示なし）
- share groups は「順序つきのストリームとしてではなく 1 件ずつ処理する場合」に使うと公式が明記 [47]。**ログとキューの両方を 1 つのブローカーで扱えるようになったが、順序の保証は消費者グループとは違う**

### 3.6 ストリーム処理と「厳密に 1 回」

| 製品・版 | 仕組み | 条件・限界 | 出典 |
| --- | --- | --- | --- |
| Flink 2.3.0 のチェックポイント | 障壁（barrier）を流して分散スナップショットを取り、再生可能なソースと組み合わせる | 再生できる永続ソースと、状態の永続ストレージが要る。既定は無効。既定のモードは exactly-once（＝Flink の内部状態に対して） | [39] |
| Flink の端から端までの厳密に 1 回 | 外部への書き込みを、チェックポイントに合わせてコミット・ロールバックできること。2 相コミット：チェックポイント開始＝事前コミット、完了通知＝コミット | 外部システムにトランザクションが要る。原典（2018-02-28 の公式ブログ）は TwoPhaseCommitSinkFunction（Flink 1.4）。**Flink 2.0 で SinkFunction 系は削除され Sink V2 へ移行** | [40] |
| Flink の KafkaSink | DeliveryGuarantee は NONE（既定）／AT_LEAST_ONCE／EXACTLY_ONCE。EXACTLY_ONCE はチェックポイントごとに Kafka トランザクションをコミット | transaction.timeout.ms を「最大チェックポイント時間＋最大再起動時間」より十分長くしないと**データを失い得る**。消費側は read_committed が要る。文書時点で Flink 2.3 用の Kafka コネクタは「まだない」 | [39] Kafka connector |
| Kafka Streams 4.4 | processing.guarantee の既定は at_least_once。exactly_once_v2 でトランザクションを使う（ブローカー 2.5 以降） | 有効時 commit.interval.ms の既定が 100ms に変わる。レプリケーション係数 3 未満は「effectively voids EOS」。Kafka 内で閉じた読み→処理→書きに限る | [49] |
| Kafka の公式設計文書 | 「厳密に 1 回」をうたう多くのシステムは細則を読む必要があると警告。Kafka のトランザクションは生産者側だけがトランザクショナル | 外部システムへの副作用は範囲外 | [45] |
| Spark 4.3.0 Structured Streaming | 既定はマイクロバッチ。exactly-once の耐障害性をうたう | 条件（再生可能なソースと冪等なシンク）は今回の確認範囲の外。記憶・要確認 | [38] |

- ストリーム結合：Flink の通常の結合は**両側の入力を状態に永久に持つ**。状態 TTL で抑えられるが結果の正しさに影響し得る、と公式が明記。区間結合・時間的結合（版つきの表との結合）・ルックアップ結合は状態を抑える代わりに意味が変わる [39] Joins
- セーブポイント：演算子に uid を明示しないと、トポロジーの変更で状態が正しく戻らない場合がある [39] Savepoints。**コードを変えて再処理する前提条件**

### 3.7 マテリアライズドビューの増分更新

| 製品 | 更新の方式 | 制限 | 出典 |
| --- | --- | --- | --- |
| PostgreSQL 18 | REFRESH MATERIALIZED VIEW は中身を**完全に置き換える**。CONCURRENTLY で読み取りを止めずに更新できる | CONCURRENTLY は、列名だけを使い全行を含む UNIQUE 索引が 1 つ以上要る。増分更新は標準機能にない。データは常に最新とは限らないと公式が明記 | [63] |
| ClickHouse（増分 MV） | 「ただのトリガ」。挿入されたブロックに対して問い合わせを走らせ、結果を別の表に入れる | **左端の表への挿入だけが発火**。JOIN の右側の表が変わっても更新されない。集約は AggregatingMergeTree などの表エンジンと ORDER BY＝GROUP BY の整合が要る。元表の更新・削除が反映されるとは書かれていない | [59] |
| ClickHouse（refreshable MV） | 問い合わせを定期的に全体に対して実行し、結果を原子的に入れ替える。APPEND も可 | 鮮度は更新間隔しだい。dbt のジョブや単純な DAG の代替になると公式が説明（自己申告） | [59] |
| Materialize | ビューに索引を張るとメモリ上で増分更新。マテリアライズドビューは永続ストレージに保存し増分更新。既定の分離レベルは Strict Serializable | メモリとクラスタの費用。今回は制限のページを未確認 | [56] |
| RisingWave | PostgreSQL 互換の前面。状態はオブジェクトストレージ（LSM）に置く。既定で 1 秒ごとに障壁を出しチェックポイント。MV の作成時に過去分をバックフィル | 今回は意味論（一貫性の水準）の文書を未確認 | [57] |
| （理論）DBSP | 関係代数・集約・再帰を含む問い合わせの増分ビュー保守を、一般的なアルゴリズムとして与える | 論文。製品の保証ではない | [58] |

### 3.8 バッチ・オーケストレーション・変換

| 製品・版 | 位置づけ | 再実行・バックフィルについて公式が言うこと | 出典 |
| --- | --- | --- | --- |
| MapReduce（OSDI 2004） | 失敗したタスクを再実行するだけで耐障害。map・reduce が**決定的な関数なら**、障害のない逐次実行と同じ出力になる。出力はグローバルなファイルシステムへの原子的な確定 | 非決定的な演算子では保証が弱まる。複数出力ファイルの原子的な 2 相コミットは提供しない | [36] 3.3 節 |
| Spark（RDD、NSDI 2012） | データそのものではなく、作り方（lineage）を記録して再計算で耐障害 | 「再構築できない RDD は参照できない」 | [37] |
| Airflow 3.4.0 | DAG のスケジューラ。バックフィルは「過去の日付の実行を作ること」 | タスクは再実行のたびに同じ結果を出すべき。**INSERT ではなく UPSERT**。「最新のデータ」を読まず特定のパーティションを読み書きする（data_interval_start）。now() を計算に使わない | [41] Best Practices |
| Dagster（版は文書に表示なし） | 資産（asset）＝永続ストレージ上の表・ファイルを宣言し、作り方をコードで持つ | パーティション単位のバックフィル。ロジックを変えたときの過去分の更新が主な用途の 1 つ | [42] |
| dbt v2.0（2026-09-14 初版）| DWH 内の変換（ELT の T）。SQL のモデル | 増分モデルは is_incremental() と unique_key。--full-refresh で作り直せる。SQL は増分でも全量でも正しく動く必要がある | [43] |

### 3.9 データ品質と系譜

| 道具・版 | 何をするか | 位置づけ | 出典 |
| --- | --- | --- | --- |
| OpenLineage 1.55.0 | 実行（Run）・ジョブ・データセットのメタデータをイベントで送る仕様。拡張は Facet | 仕様（収集の形式）。検査そのものはしない | [68] |
| dbt のデータテスト | SQL で「失敗する行」を返す問い合わせを書く。組み込みは unique・not_null・accepted_values・relationships | 変換の後段での検査。DWH の中で完結 | [43] |
| Great Expectations（GX Core 1.25.0） | 期待（Expectation）を定義し検証する Python ライブラリ | パイプラインの任意の位置に置ける検査 | [69] |
| Soda | データ品質のプラットフォーム。監視・データ契約・CI での検査 | ベンダーの製品（自己申告）。概要ページのみ確認 | [70] |

## 4. 事故・失敗例（一次報告）

| 事例 | 何が起きたか（事業者自身の報告） | このノートの論点との関係 | 出典 |
| --- | --- | --- | --- |
| Cloudflare 2025-11-18 | ClickHouse の権限変更で、メタデータ表への問い合わせが重複した行を返すようになり、5 分ごとに生成していた Bot Management の「feature file」が 2 倍の大きさになった。読む側のソフトウェアの上限を超えて失敗。更新済みのノードで問い合わせが走ったときだけ壊れたため、良いファイルと悪いファイルが交互に配られた | **派生データ（生成物）の検査がなく、上流の変更が下流を止めた**。問い合わせがデータベース名で絞っていなかった。派生データにも入力の契約と出力の検査が要る | [73] |
| Sentry 2015-07-20 | PostgreSQL の XID 周回の保護が働き、書き込みを受け付けなくなった。米国の営業時間の大半で停止。書き込みの多い巨大な表で autovacuum が追いつかなかった | MVCC の代償は運用で払う。3.1 の「運用の落とし穴」の実例 | [74] |
| Mailchimp Mandrill 2019-02-04〜05 | シャードの 1 つ（負荷が偏っていた）で autovacuum が遅れ、XID が上限に達して安全停止。VACUUM は最長 40 日と見積もられ、ダンプとリストアで復旧。2018-11 に兆候を把握していたが監視はバックログに残っていた | 同上。偏ったシャードほど早く周回する。監視項目（XID の年齢）を決めておく | [75] |
| GitLab.com 2017-01-31 | 誤って本番の DB ディレクトリを削除。pg_dump のバックアップは版の不一致（9.2 のバイナリで 9.6 を対象）で黙って失敗しており存在しなかった。17:20〜00:00 UTC の変更を失った | 「バックアップではなく復元を試す」（SRE 本 26 章）の実例。再構築の手順は、実行して確かめるまで手順ではない | [76] |

- ログからの再構築（リプレイ）が、保持期間切れ・コンパクション・スキーマ非互換で失敗した事例の、事業者自身による一次報告は、今回の調査では見つからなかった。前提条件（6.6）は公式文書の記述から導いたもので、事故の裏づけはない

## 5. 権威の推奨と位置づけ（規範か任意か）

| 権威 | 言っていること | 位置づけ | 出典 |
| --- | --- | --- | --- |
| Google SRE 本 25 章 | 定期実行のパイプラインは最初は安定するが、成長と変化で**もろくなる**。問題の型：hanging chunk、thundering herd（数千のワーカーが同時に始動）、Moiré load pattern（複数のパイプラインの実行が重なり共有資源を同時に使う）。監視の問題は定期実行型と強く結びつく。Google の Workflow は、設定のタスク・有効なリース・一意な出力ファイル名・サーバトークンの 4 つで正しさを保証する | Google の経験の記述。任意。大規模な社内基盤が前提 | [71] |
| Google SRE 本 26 章 | **レプリケーションと冗長性は復旧可能性ではない**。バックアップではなく復元が目的。多層防御：第 1 層＝ソフト削除、第 2 層＝バックアップと復旧、第 3 層＝定期的なデータ検証（帯域外の検査）。データが使えない時間の「長すぎる」の出発点として 24 時間。ソフト削除の猶予は 15・30・45・60 日などが一般的。最も深刻な削除は、削除に関わるバッチ処理を不慣れな開発者が触ったときに起きる | 同上。任意 | [72] |
| Azure Architecture Center：Event Sourcing パターン（2026-03-27） | 「complex pattern that introduces significant trade-offs」。移行は入るのも出るのも高くつく。ほとんどのシステムとその大部分では従来のデータ管理で足りる。イベントは不変なので、バグで作った誤ったイベントは残る（補償イベントか upcaster）。配信は通常 at-least-once なので消費側は冪等に。全体ではなく一部（台帳・注文処理など）に選んで使う | 設計指針。任意。Azure の利用者向けだが内容は製品非依存 | [34] |
| Azure Architecture Center：CQRS パターン（2025-02-20） | 複雑さが増す（特に Event Sourcing と組み合わせると）。読み取りモデルは結果整合で古いデータを返し得る。ドメインや業務ルールが単純なら向かない | 同上 | [33] |
| Azure Architecture Center：Materialized View パターン（2026-09-21） | ビューは「completely disposable」。元データから作り直せる。更新の合図が失われるとビューは**黙って古い結果を返す**ので、更新の新しさを監視する | 同上 | [35] |
| Fowler（2011-07-14） | 「for most systems CQRS adds risky complexity」。CQRS はシステム全体ではなく特定の部分（境界づけられたコンテキスト）にだけ使う | 個人の見解（原典の 1 つ）。任意 | [31] |
| Fowler（2005-12-12） | イベントソーシングの利点：完全な再構築・時点問い合わせ・イベントの再生。再生時、外部システムへの更新は Gateway で包み、止められるようにする | 同上 | [30] |
| AWS Well-Architected（性能効率の柱 PERF03-BP01） | 用途に合わせた（purpose-built）データストアを選ぶ。アンチパターン：社内の経験があるという理由で 1 つのデータストアに固執する。確立しない場合のリスク水準は「高」 | AWS の利用者向けのベストプラクティス。任意。**AWS は用途別の製品を売る立場** | [77] |
| Azure Architecture Center：データストアモデル（2025-08-21） | 1 つのデータストアがすべてのアクセスパターンを効率よく満たすことはまれで、多くの本番システムは polyglot persistence を採る。一方、運用を複雑にする形でモデルを組み合わせない | 設計指針。任意 | [78] |
| Thoughtworks Technology Radar | DuckDB：Trial（2023-04。現行版のレーダーには載っていない）。Lakehouse architecture：Trial（2023-04。同）| 1 社の見解。古い。現行の評価は未確認 | [79] |
| Airflow 公式のベストプラクティス | 3.8 のとおり（冪等、UPSERT、パーティション、now() を使わない） | 製品の公式文書の推奨。任意 | [41] |

- 「OLTP と分析は 1 つで足りるなら分けない」を**規範として**勧める権威は、今回は見つからなかった。AWS と Azure はどちらも用途別に分ける側に寄っている [77][78]。分けない判断の根拠にできるのは、Azure の「運用を複雑にする組み合わせを避ける」[78]、Event Sourcing・CQRS の注意書き [33][34]、そしてケーススタディの実測（データ量と問い合わせの形で、PostgreSQL 1 つで足りる境目を測る）
- 「One size fits all は終わった」という主張の原典は Stonebraker・Çetintemel [14]。市場が独立したエンジンに分かれるという予測であり、小規模なシステムに複数のエンジンを勧める規範ではない

## 6. 設計判断の分かれ目（何を選ぶと何を得て何を失うか。表）

### 6.1 ストレージエンジンと格納形式

| 選択 | 得るもの | 失うもの・払うもの | 根拠 |
| --- | --- | --- | --- |
| B ツリー＋ヒープ（PostgreSQL） | 点検索・範囲検索の読み取りが安定。成熟したトランザクション | 更新は新しい版と索引エントリを増やす。VACUUM と XID 周回の監視が必須 | [3][4][6] |
| LSM | 逐次書き込みで高い挿入速度 | コンパクションの書き込み増幅。点検索は複数の層を見る。空間増幅 | [1][2] |
| 行指向 | 1 件の読み書きが 1 か所。OLTP 向き | 少数の列の大量走査で不要な列まで読む | [8] |
| 列指向 | 必要な列だけ読む。並べ替えた列は圧縮が効く | 1 件単位の頻繁な更新・削除は苦手。小さな挿入が多いと part が増える | [8][10][60] |
| ベクトル化とコンパイル | 両者とも OLAP では似た性能。計算が重い問い合わせはコンパイル、メモリアクセスが支配的ならベクトル化がやや有利 | コンパイルはコンパイル時間、ベクトル化は解釈の間接コスト。製品選定の決め手にはなりにくい | [13] 10 節 |

### 6.2 OLTP と分析を分けるか

| 選択 | 得るもの | 失うもの・払うもの | 見直し条件 |
| --- | --- | --- | --- |
| 1 つの RDB で兼ねる | 派生データがなく、ずれ・遅れ・再構築の手順が要らない。運用する製品が 1 つ | 大きな集計が OLTP の資源を食う。行指向の走査の遅さ | 集計が OLTP の遅延の SLO を脅かす／容量が単一ノードを超える |
| 読み取りレプリカに分析を逃がす | 構成が単純。同じスキーマ | 行指向のまま。長い問い合わせとレプリケーションの衝突（Part 8 のノート参照） | 走査量が増え列指向が要る |
| 列指向の分析 DB に複製（CDC／ETL） | 走査と圧縮で大きな利得 | 派生データになる：遅れ、欠落・重複の検査、スキーマ変更の伝播、再構築の手順 | — |
| HTAP（行と列のレプリカを 1 製品で） | 一貫した新しいデータを分析に使える。論文は、干渉を除くには用途別の**別々のレプリカ**が要ると述べる | 結局レプリカは 2 種類ある。製品への依存が強い | [15] 要旨 |
| クラウド DWH（計算とストレージの分離） | 計算を独立に伸縮。不変ファイルによる単純な並行制御 | ネットワーク越しの読み取り。課金モデルへの依存。未検証 | [16][18] |
| レイクハウス（開いた表形式） | 複数のエンジンが同じファイルを読める。ロックインを下げる | カタログ（原子的な差し替え）が新しい要。小さなファイル・メタデータの保守。形式の版と各エンジンの対応のずれ | [19][20][21] |

### 6.3 データモデル

| 選択 | 得るもの | 失うもの・払うもの | 根拠 |
| --- | --- | --- | --- |
| リレーショナル（正規化） | 多対多・結合・制約。問い合わせの形が変わっても耐える | 1 つの集約を読むのに結合が要る | [78] |
| ドキュメント（jsonb を含む） | 要件が流動的な部分の柔軟さ。1 文書を 1 回で読める | PostgreSQL 公式：**文書はある程度決まった構造を持つべき**。更新は行全体に行ロック、大きな文書は競合を増やす。文書は「それ以上分けて独立に更新できない単位」が理想 | [28] 8.14.2 |
| jsonb＋GIN | 任意のキーで検索（jsonb_ops）、または小さく速い索引（jsonb_path_ops。キー存在演算子は不可） | 索引が全キー・全値の写しを持つ。式索引のほうが小さく速い | [28] 8.14.4 |
| グラフ | 多段の関係の探索 | 標準は GQL（ISO/IEC 39075:2024）ができたばかり。PostgreSQL 19 のリリースノート（2026-10-09 時点の RC 版）に property graph の記述は見つからなかった | [29][80] |
| イベントソーシング | 監査・時点問い合わせ・完全な再構築 | 6.4 のとおり | [30][34] |

### 6.4 イベントソーシングと CQRS

| 選択 | 得るもの | 失うもの・払うもの | 根拠 |
| --- | --- | --- | --- |
| CRUD（現在の状態だけ） | 単純。読んだ直後に自分の書き込みが見える | 履歴がない。派生データを作り直す元は現在の状態だけ | [34] |
| CRUD＋変更ログ（CDC・アウトボックス） | 既存のモデルを変えずに、変更の流れを得る | イベントはテーブル変更であり業務の意図ではない | Part 6 のノート |
| イベントソーシング（一部の集約だけ） | 意図つきの完全な履歴。投影を作り直せる | イベントのスキーマの進化（版・upcaster）。スナップショット。結果整合。誤ったイベントが残る。チームの経験が要る。出るのも高くつく | [34] |
| CQRS（読み取りモデルを分ける） | 読み取りに合わせたスキーマ。独立に伸縮 | 読み取りモデルは古くなり得る。同期の仕組みと監視 | [31][33] |

### 6.5 バッチとストリーム

| 選択 | 得るもの | 失うもの・払うもの | 根拠 |
| --- | --- | --- | --- |
| バッチ（定期実行） | 入力が固定で決定的。失敗したら丸ごとやり直せる。検査しやすい | 遅延は実行間隔以上。規模が伸びると hanging chunk・thundering herd・実行の重なり | [36][71] |
| マイクロバッチ／増分モデル | 遅延の短縮。SQL のまま | 増分と全量の 2 つの経路が同じ結果になることを保つ責任。遅れて届く行の扱い | [38][43] |
| ストリーム（イベント時間） | 低遅延。順不同・遅延データを明示的に扱える | ウォーターマークはヒューリスティック。状態とチェックポイントの運用。結合の状態が増え続ける | [39][53] |
| 処理時間で窓を切る | 単純・最小の遅延 | 決定的でない。再処理で結果が変わる | [39] |
| at-least-once＋冪等な受け手 | 仕組みが単純。外部システムにも使える | 受け手の冪等キーの設計 | [34][41] |
| トランザクションによる exactly-once | 重複排除を枠組みに任せられる | Kafka 内か、トランザクション対応の外部シンクに限る。タイムアウトの設定を誤るとデータを失う。遅延がコミット間隔（チェックポイント間隔）に縛られる | [39][40][49] |
| ログ（消費者グループ） | 順序、読み直し、複数の独立した消費者 | 並列度はパーティション数まで。1 件の失敗が後続を止める | [45] |
| キュー（share groups、Kafka 4.2 以降） | パーティション数を超える消費者、1 件ごとの確認、再配信の計数 | 順序つきの処理には向かない。新しい機能（4.3.2 で重大な修正） | [45][47] |

### 6.6 Lambda・Kappa と、ログからの再構築の前提条件

- Lambda の原典（Marz、2011-10-13）：データは不変の事実で、問い合わせは「全データの関数」。全データから計算し直すバッチ層に、直近だけを補うリアルタイム層を足す。最大の利点として挙げるのは**人為的な誤りへの耐性**（不変データと再計算）。この投稿には「Lambda」という語は出てこない（本文を検索して確認）[54]
- Kappa の原典（Kreps、2014-07-02）：Lambda の問題は、同じ結果を出すべきコードを 2 つの分散システムで保守すること。代案は、再処理したい分のログを保持し、コードを変えたら同じ枠組みの新しいジョブを最初から流して新しい出力表を作り、追いついたら切り替える。著者自身が「ギリシャ文字に値しないほど単純かもしれない」と書く。必要な時だけ再処理し、その間は出力の保存域が 2 倍要る [55]
- 現在の評価：Lambda か Kappa かを規範として勧める権威は、今回は見つからなかった。確かめられたのは、(a) Dataflow Model 以降、バッチとストリームを同じモデルで書く枠組みが主流になったこと [38][39][53]、(b) それでも dbt の増分モデルや ClickHouse の refreshable MV のように「定期的な全量の作り直し」は現役の選択肢であること [43][59]

| 前提条件 | 崩れると何が起きるか | 確かめ方 | 根拠 |
| --- | --- | --- | --- |
| 保持期間が再処理の範囲を覆う | 古いログが消えていて最初から作り直せない。Kafka の既定は 7 日 | retention.ms と、再構築に要る期間を突き合わせる | [46][55] |
| 保持しない分はスナップショットで補う | 状態の初期値がない | スナップショット＋それ以降のログで再現できるか実行して確かめる | [30][34] |
| コンパクションの意味を受け手が知っている | tombstone が消えた後に最初から読むと、削除を見落とす（delete.retention.ms 既定 1 日）。中間の状態は残らない | 再構築が delete.retention.ms 内に終わるか。履歴が要るならコンパクションしない | [45][46] |
| 古いイベントを今のコードが読める | スキーマの非互換で再生が止まる・誤読する | 最古のレコードから読む試験。版の識別子と upcaster | [34] |
| 処理が決定的 | 再処理のたびに結果が変わる。now()・乱数・「最新」の参照・処理時間の窓 | 同じ入力で 2 回流して差分を取る | [36][39][41] |
| 外部への副作用を止められる | 再生でメール・決済などを二重に実行 | 副作用を Gateway に集め、再生時に無効化 | [30] |
| 出力を並べて持てる | 切り替え・切り戻しができない | 新旧 2 つの出力表の容量 | [55] |
| 状態の対応づけが安定 | コード変更後、セーブポイントから状態が戻らない | 演算子に uid を付ける | [39] |
| 階層化ストレージの制限 | Kafka の階層化はコンパクションされたトピックに非対応 | 長期保持の方式を先に決める | [50] |

### 6.7 分析基盤・ログ基盤の費用の決まり方

| 要因 | 何で決まるか | 設計での操作 | 根拠 |
| --- | --- | --- | --- |
| 保持 | 期間 × 1 日の量。削除の実行方式 | ClickHouse：TTL とパーティションをそろえ、パーティション単位で落とす。削除はマージ時で即時ではない。段階的に安い媒体へ移す・古い分は集約（ロールアップ）だけ残す | [60] |
| 圧縮 | 並び順（ソートキー）、型の幅、コーデック | ソートキーと、列ごとの型・ビット幅を選ぶ（公式の例は、型を最適化しソートキーを付けた表で圧縮率が上がることを示す）。「濃度の低い列を先頭に」という定石は今回の確認範囲の外（記憶・要確認） | [60] |
| カーディナリティ | 異なる値の数。辞書符号化は少ないほど効く | ClickHouse の LowCardinality：1 万未満で有利、10 万超で通常の型より悪くなり得る。Prometheus：ユーザ ID のような高カーディナリティをラベルに入れない | [60][66] |
| 取り込み時スキーマ | 取り込み時に解析して列にする。問い合わせは速く、圧縮も効く | スキーマが変わると取り込みが失敗する・変更作業が要る | [19][62] |
| 読み出し時スキーマ | 生のまま保存し、問い合わせ時に抽出 | 取り込みは速く索引も小さいが、問い合わせのたびに計算。Elastic：よく絞り込む項目は索引し、残りを runtime field に | [62][67] |
| 中間（半構造の列型） | 頻出パスは部分列、残りはまとめて保存 | ClickHouse の JSON 型：max_dynamic_paths を超えたパスは shared data へ | [60] |
| 計算 | 走査した量と時間。クラウド DWH は計算とストレージを別に課金 | 事前集計（MV）で走査を減らす。料金の数値は今回未調査 | [18][59] |

- ClickBench の位置づけ：ClickHouse のチームが作り運営するベンチマーク（README が「created and used by the ClickHouse team」と明記）。データは 1 つの平らな表、約 1 億行、問い合わせは 43 本を逐次実行で、同時実行も容量も測らない。正規化したスター型を使う従来型 DWH には不利になり得ると README 自身が書く。結果は「grain of salt」で受け取るよう求めている [65]。**製品選定の根拠ではなく、同種の負荷での相対的な目安**

## 7. 設計レビューで問うこと（問い｜なぜ問うか｜危ない兆候）

| # | 問い | なぜ問うか | 危ない兆候 |
| --- | --- | --- | --- |
| 1 | この表・索引・ビューは正本か派生か。派生なら、元から作り直す手順を最後に実行したのはいつか | 派生データは捨てて作り直せることが価値 [35]。手順は実行するまで手順ではない [72][76] | 「作り直せるはず」。手順書はあるが実行記録がない |
| 2 | 再構築に要るログは、保持期間の中にあるか。足りない分のスナップショットはあるか | Kafka の既定の保持は 7 日 [46] | retention が既定のまま。スナップショットの取得元と時点が不明 |
| 3 | コンパクションしたトピックを最初から読む消費者は、delete.retention.ms 内に読み終えるか | 遅れると削除を見落とす [45] | 再構築の所要時間を測っていない |
| 4 | この処理は、同じ入力で 2 回流して同じ出力になるか | 再実行・バックフィル・リプレイの前提 [36][41] | now()、乱数、「最新のパーティション」の参照、処理時間の窓 |
| 5 | バッチの再実行は追記か、置き換えか | INSERT の再実行は重複を生む [41] | UPSERT やパーティションの置き換えでなく INSERT |
| 6 | 「厳密に 1 回」は、どこからどこまでの保証か。外部への副作用は含むか | 保証は枠組みの内部か、トランザクション対応のシンクまで [40][45][49] | 「Kafka が exactly-once だから重複しない」。受け手が冪等でない |
| 7 | トランザクションのタイムアウトは、チェックポイント時間＋再起動時間より長いか | 短いと未コミットのトランザクションが失効しデータを失う [39] | 既定値のまま。チェックポイントの最大時間を測っていない |
| 8 | 窓はイベント時間か処理時間か。遅れて届くデータはどこまで待ち、その後はどうするか | ウォーターマークはヒューリスティック [53]。捨てる・修正を出す・別経路に回すの選択が要る | 遅延データの件数を数えていない。許容遅延の根拠がない |
| 9 | ストリーム結合の状態は、どこまで増えるか。TTL を付けたとき結果はどう変わるか | 通常の結合は両側を永久に保持 [39] | 状態サイズの監視がない。TTL の影響を説明できない |
| 10 | 分析を OLTP から分ける理由は、測った数字か | 分けると派生データの費用（遅れ・検査・再構築）を払う | 「分析は DWH で」が前提になっている。現行の RDB での実測がない |
| 11 | 列指向の表のソートキー・パーティション・TTL は、主な問い合わせと保持の方針から決めたか | 圧縮率・走査量・削除の費用を決める [60] | 主キーを一意制約のつもりで使っている。TTL とパーティションが不整合 |
| 12 | 高カーディナリティの値を、ラベル・ソートキーの先頭・辞書符号化の列に入れていないか | 費用が非線形に増える [60][66] | ユーザ ID・リクエスト ID がラベルにある |
| 13 | ログ・イベントのスキーマは取り込み時か読み出し時か。スキーマが揺れたとき、どこで失敗が見えるか | 取り込み時は入口で止まり、読み出し時は問い合わせで黙って欠ける [62][67] | 失敗の出方を試していない |
| 14 | マテリアライズドビューは、元表の更新・削除・結合相手の変更に追随するか | ClickHouse の増分 MV は左端の表への挿入だけで発火 [59]。PostgreSQL は全置き換え [63] | 「MV だから常に最新」。更新の新しさの監視がない [35] |
| 15 | PostgreSQL の XID の年齢、死んだ行、autovacuum の遅れを監視しているか | 周回の保護は書き込みを止める [3][74][75] | autovacuum を止めている表。長時間のトランザクション・放置されたレプリケーションスロット |
| 16 | jsonb の文書は、独立に更新される部分を含んでいないか。大きさの上限は | 更新は行全体のロック [28] | 1 文書に追記し続ける配列。複数の書き手が同じ文書を更新 |
| 17 | イベントソーシング・CQRS を使う範囲は、システムの一部に限っているか。やめる費用を見積もったか | 権威と原典がそろって慎重な適用を勧める [31][33][34] | 全サービスの標準にしている。イベントの版の方針がない |
| 18 | ベクトル検索の再現率を測ったか。絞り込みと併用したとき件数は足りるか | 近似索引は絞り込みを後で適用 [26] | 厳密検索との比較がない。件数が足りない問い合わせを見ていない |
| 19 | 表形式（Iceberg・Delta）の版・機能と、読む全エンジンの対応を確かめたか。カタログは単一障害点になっていないか | 新しい版の機能は古い読み手が読めない [20][21]。原子的な差し替えはカタログ依存 [20] | 書き手だけ新しい版。カタログの可用性を見ていない |
| 20 | 派生データの出力に検査（件数・一意性・大きさの上限）があるか。検査に落ちたとき前の版を使い続けられるか | 上流の変更で生成物が壊れ、下流が止まった [73] | 生成物をそのまま全体に配る。直前の良い版を保持していない |
| 21 | 定期パイプラインの開始時刻は重なっていないか。同時に何ワーカーが始動するか | thundering herd、Moiré load pattern [71] | すべて毎時 0 分開始。共有資源の使用量を重ねて見ていない |
| 22 | 削除はソフト削除か。猶予は何日か。バッチの削除処理を誰がレビューするか | 多層防御の第 1 層。最も深刻な削除はバッチ処理から [72] | 物理削除のバッチ。削除の取り消し手順がない |
| 23 | ベンチマークの数字は、自分たちの負荷に近いか。誰が運営しているか | ClickBench はベンダー運営・単一表・逐次実行 [65] | 順位表だけで製品を決めている |

## 8. ケーススタディで測れること・測れないこと

### 測れること（WSL の Docker、同一環境内の相対比較）

| 題材 | 測り方 | 対応する論点 |
| --- | --- | --- |
| C：行と列とファイル | 同じイベントデータを PostgreSQL 18（ヒープ）、ClickHouse（MergeTree）、DuckDB＋Parquet に入れ、容量・取り込み時間・集計の時間を比べる。ClickHouse はソートキーと型（LowCardinality の有無）を変えた除去実験 | 3.2、6.1、6.7 |
| C：取り込み時と読み出し時のスキーマ | 同じ JSON ログを、列に展開／jsonb（GIN あり・なし）／ClickHouse の JSON 型／文字列のまま、で保存。途中でフィールドの型と名前を変え、どこで失敗が見えるか（取り込みで止まる／問い合わせで欠ける）を数える | 6.7、問い 13 |
| C：保持 | ClickHouse で TTL とパーティションがそろう場合・そろわない場合の、削除後の容量と削除までの時間 | 6.7 |
| B：ログからの再構築 | Redpanda のトピックから派生ストア（ClickHouse）を作り、捨てて最初から作り直す。一致率（件数・集計値）と所要時間。保持を短くした場合、コンパクション＋tombstone 失効後に読んだ場合の欠落・復活した行を数える | 6.6、問い 2・3 |
| B：冪等なバッチと再実行 | 同じ日次バッチを 2 回流す。INSERT／パーティション置き換え／UPSERT で重複件数を比べる。途中で強制終了して再実行 | 3.8、問い 4・5 |
| B：ClickHouse の重複排除 | 挿入の再試行で重複が入るか。非レプリケートの MergeTree は重複排除ログが既定 0（＝効かない）と文書が明記 [61]。26.2 で既定が変わっているため、使う版で実測する | 6.5 |
| B：マテリアライズドビュー | PostgreSQL の REFRESH（CONCURRENTLY の有無）での読み取りの待ち時間。ClickHouse の増分 MV で、元表の行を更新・削除したとき、結合の右側を変えたときの不一致件数 | 3.7、問い 14 |
| 5：MVCC の代償 | 更新を繰り返した表の死んだ行・表と索引の大きさ、HOT 更新の割合（pg_stat_all_tables の n_tup_hot_upd）、fillfactor を変えた場合 | 3.1 |
| A の一部：Kafka と Redpanda の照合 | 保持・コンパクション・オフセットの巻き戻しの挙動が Kafka 4.4 と Redpanda で同じか。Redpanda が無視するトピック設定（min.insync.replicas など）を設定して効果を見る | 3.5 |
| 任意：pgvector | 厳密検索と HNSW の再現率・時間、絞り込み併用時の返却件数、ef_search と iterative scan の効果 | 3.4、問い 18 |

### 測れないこと（理由つき。「未検証」と書く）

- クラウド DWH（Snowflake・BigQuery）の計算とストレージの分離、料金：公式文書に基づく比較のみ
- 絶対的な性能・大規模（TB 以上）での挙動：単一ホスト・小さなデータのため。結果は相対比較としてだけ示す
- LSM と B ツリーの書き込み増幅の厳密な比較：ClickHouse の MergeTree は LSM に似たマージ方式だが、RocksDB を直接測る構成は実機の製品に含めていない。RocksDB の数値は公式 wiki の例 [2] の引用にとどめる
- Flink・Kafka Streams の exactly-once、ウォーターマークと遅延データ：実機の構成に含めていない（追加するならイメージ容量の確認が要る）。公式文書に基づく説明にとどめる
- Kafka の share groups、階層化ストレージ、Iceberg・Delta・Hudi、HTAP 製品、Materialize・RisingWave：未検証
- XID 周回：単一ホストで 20 億トランザクションは非現実的。年齢の伸びの観測と、公式文書・事故報告の引用にとどめる
- ストレージ媒体の違い（WSL の仮想ディスク）：fsync とシーケンシャル書き込みの特性が本番と異なる

## 9. 未確定・要確認

1. O'Neil ほかの LSM 論文の書誌（Acta Informatica 33(4)、1996）は記憶。PDF には「To be published: Acta Informatica」とだけある
2. HNSW 論文の掲載誌（IEEE TPAMI、2020 年。記憶・要確認）。確認したのは arXiv 版の要旨
3. Snowflake の公式文書ページの更新日、Materialize・RisingWave・Dagster の文書の版・日付は記録できなかった
4. Delta Lake 4.4.1 の公開年はページに表示がなく、2026 年と判断した。Hudi 1.2.1 の公開日は不明。Hudi の仕様本文は開けなかった（題名のみ）
5. Redpanda が Kafka の share groups（KIP-932）に対応しているかは、互換性ページからは判断できなかった
6. RocksDB の wiki は 2023-03-28 の編集で古い。現行版の既定値とは照合していない
7. Spark Structured Streaming の exactly-once の条件、ClickHouse の実行方式（ベクトル化）は、公式文書の該当箇所を今回開いていない
8. PostgreSQL 19 は RC 2（2026-11-12 の告知）。リリースノート（2026-10-09 時点）に property graph（SQL/PGQ）の記述は見つからず、該当しそうな文書ページも 404 だった。「入っていない」と断定はしない
9. SQL/PGQ の規格番号（ISO/IEC 9075-16:2023）は記憶。GQL の本文は未確認（ISO のカタログページのみ）
10. Greg Young の「CQRS Documents」（2010）は目次と冒頭のみ確認。注意書きの引用は Fowler と Azure に頼っている
11. Thoughtworks Radar の該当項目（DuckDB、Lakehouse）は 2023-04 が最後で、現行版には載っていない。Iceberg・dbt・pgvector の個別ページは取得できなかった
12. Kappa と Lambda の「現在の評価」を述べる権威の文書は見つからなかった。6.6 の評価は、原典と現行製品の文書からの整理
13. 「1 つで足りるなら分けない」を勧める権威の文書は見つからなかった（5 節）。ガイドでは実測と判断の表で示し、規範として書かない
14. ログからの再構築が失敗した事故の一次報告は見つからなかった（4 節）
15. Kafka の原論文の会議名（NetDB 2011）は記憶。取得した PDF は著者ページではない写し
16. クラウド DWH・ログ SaaS の料金の数値は調べていない（6.7 は費用を決める要因の整理まで）
17. pgvector の README は GitHub の master を参照（v0.8.7 を導入手順で確認）。PostgreSQL 18 での動作は README の「13 以降」の記述のみ

## 10. 結論（スライドに書くこと。箇条書き 15〜30 個、各項目に出典の番号）

1. ストレージエンジンは、書き込み・読み取り・空間の 3 つの増幅のどれを払うかの選択。全部を同時には下げられない [2]
2. LSM は「変更を遅らせてまとめる」ことで挿入を安くし、検索で払う。原論文は、検索より挿入が多い用途に向くと明言している [1]
3. PostgreSQL の MVCC は「読み取りと書き込みが互いを妨げない」を買い、死んだ行の回収（VACUUM）と XID 周回の監視で払う。残り 300 万 XID 未満で新しい書き込みを拒否する [3][5]。実際に長時間の停止が起きている [74][75]
4. 行指向は 1 件の読み書き、列指向は少数の列の大量走査に合う。列指向の利得は「必要な列だけ読む」と「並べた列の圧縮」から来る [8][10][60]
5. ベクトル化とコンパイルは OLAP では似た性能。エンジンの方式より、格納形式・並び順・データ量のほうが設計に効く [13]
6. OLTP と分析を分けると、分析側は派生データになる。遅れ・検査・スキーマ変更の伝播・再構築の手順という費用を払う。分ける理由は測った数字で示す [35][78]
7. 権威（AWS・Azure）は用途別のデータストアを勧める側に寄っている。「1 つで足りるなら分けない」を規範として勧める文書は見つからなかった。境目は実測で示す [77][78]
8. クラウド DWH の「計算とストレージの分離」は、不変ファイルと独立に伸縮する計算層の組み合わせ。Snowflake の論文と BigQuery の公式文書が同じ構造を説明する（未検証）[16][18]
9. オープンテーブル形式（Iceberg・Delta・Hudi）は、不変ファイルの上に「どのファイルが表の現在の版か」を決めるメタデータ層を載せたもの。一貫性はカタログの原子的な差し替えに依存する [19][20][21]
10. Iceberg の形式の版は 3 までが採択済み、4 は開発中（2026-11-18 時点）。新しい版の機能は古い読み手が読めないので、読む全エンジンの対応を先に確かめる [20]
11. 全文検索の転置索引は、1 件の更新が多数の索引更新になる。更新の速さと検索の速さの釣り合いを選ぶ [23][24]
12. ベクトル検索の HNSW は近似。pgvector 0.8.7 では索引なしが厳密検索で、近似索引では絞り込みが索引走査の後に適用され、件数が足りなくなり得る [25][26]
13. jsonb は柔軟さを買うが、PostgreSQL の公式文書は「ある程度決まった構造」と「独立に更新されない単位」を勧める。更新は行全体をロックする [28]
14. イベントソーシングと CQRS は、原典の著者も Azure の指針も「一部にだけ、利点が複雑さに見合うときに」と書く。入るのも出るのも高くつく [31][33][34]
15. バッチの耐障害性は「決定的な処理を再実行する」ことで成り立つ。MapReduce の原論文がこの条件を明記している [36]
16. 再実行できるバッチの条件：同じ結果を返す、INSERT でなく UPSERT かパーティションの置き換え、「最新」ではなく特定のパーティションを読む、now() を計算に使わない [41]
17. 定期実行のパイプラインは、成長と変化でもろくなる。同時始動（thundering herd）と実行の重なり（Moiré load pattern）を設計時に見る [71]
18. ログベースのブローカーは、消費位置を消費者側のオフセットに持たせ、読み直しを可能にした。これが派生データの作り直しの土台 [45]
19. Kafka は 4.2 でキュー（share groups）が production-ready になった。順序つきの処理は消費者グループ、1 件ずつの処理は share groups と使い分ける。新しい機能であり、4.3.2 で重大な修正が入っている [45][47]
20. Redpanda は Kafka 互換だが、受け付けるだけで効果のないトピック設定がある（min.insync.replicas など）。互換は「同じ設定で同じ挙動」を意味しない [52]
21. イベント時間で考える。「全部そろった」とは分からない前提で、正しさ・遅延・費用の釣り合いを選ぶ。ウォーターマークは推定であり、遅れて届くデータの扱いを決める [39][53]
22. 「厳密に 1 回」は、枠組みの内部状態か、トランザクションに対応したシンクまでの保証。外部への副作用は受け手の冪等性で守る。Kafka Streams の既定は at_least_once [40][45][49]
23. Flink の Kafka への exactly-once は、トランザクションのタイムアウトがチェックポイント時間＋再起動時間より短いとデータを失う。設定は「保証」の一部 [39]
24. ストリーム結合は状態を持ち続ける。TTL で抑えると結果の正しさが変わる [39]
25. Lambda は「不変のデータから計算し直す」ことで人為的な誤りに耐える案、Kappa は「同じコードをログの最初から流し直す」案。どちらも核は再計算できること [54][55]
26. ログからの再構築には前提条件がある：保持期間、スナップショット、コンパクションの意味、スキーマの互換、決定性、副作用の停止、出力を並べて持つ容量 [30][34][45][46][55]
27. Kafka の保持の既定は 7 日、tombstone の保持の既定は 1 日。既定のままでは「最初から作り直す」は成り立たないことが多い [46]
28. マテリアライズドビューは製品で意味が違う。PostgreSQL は全置き換え、ClickHouse の増分 MV は挿入時のトリガで、元表の更新・削除や結合相手の変更に追随しない [59][63]
29. ビューは捨てて作り直せるもの。更新の合図が失われると黙って古い結果を返すので、新しさを監視する [35]
30. 分析・ログ基盤の費用は、保持・圧縮（並び順と型）・カーディナリティ・スキーマをいつ適用するか、で決まる。高カーディナリティの値をラベルやソートキーの先頭に置かない [60][66][67]
31. ClickBench は ClickHouse のチームが運営する、単一表・約 1 億行・逐次実行のベンチマーク。README 自身が限界を列挙している。順位表を製品選定の根拠にしない [65]
32. 派生データにも出力の検査が要る。上流の問い合わせの挙動が変わって生成物が 2 倍になり、全体が止まった事例がある [73]
33. レプリケーションは復旧可能性ではない。ソフト削除・復元を試したバックアップ・定期的な検証の 3 層で守る [72][76]
34. 系譜（OpenLineage）は実行・ジョブ・データセットの関係を記録する仕様で、検査（dbt tests・Great Expectations・Soda）とは役割が違う。両方が要る [43][68][69][70]

## 11. 出典（番号｜題名｜発行者｜版・日付｜URL｜確認の深さ）

| # | 題名 | 発行者 | 版・日付 | URL | 確認の深さ |
| --- | --- | --- | --- | --- | --- |
| 1 | The Log-Structured Merge-Tree (LSM-Tree) | P. O'Neil, E. Cheng, D. Gawlick, E. O'Neil | Acta Informatica、1996（巻号は記憶） | https://www.cs.umb.edu/~poneil/lsmtree.pdf | 本文確認（要旨・序論） |
| 2 | RocksDB Tuning Guide | facebook/rocksdb wiki | 最終編集 2023-03-28 | https://github.com/facebook/rocksdb/wiki/RocksDB-Tuning-Guide | 本文確認 |
| 3 | 24.1 Routine Vacuuming | PostgreSQL Global Development Group | PostgreSQL 18.7 文書 | https://www.postgresql.org/docs/18/routine-vacuuming.html | 本文確認 |
| 4 | Heap-Only Tuples (HOT) | 同上 | 18.7 | https://www.postgresql.org/docs/18/storage-hot.html | 本文確認 |
| 5 | 13.1 Introduction（MVCC） | 同上 | 18.7 | https://www.postgresql.org/docs/18/mvcc-intro.html | 本文確認 |
| 6 | 65.1 B-Tree Indexes | 同上 | 18.7 | https://www.postgresql.org/docs/18/btree.html | 本文確認（65.1.4 の一部） |
| 7 | 19.5 Write Ahead Log（full_page_writes） | 同上 | 18.7 | https://www.postgresql.org/docs/18/runtime-config-wal.html | 本文確認（該当項目） |
| 8 | C-Store: A Column-oriented DBMS | Stonebraker ほか | VLDB 2005 | https://www.vldb.org/archives/website/2005/program/paper/thu/p553-stonebraker.pdf | 本文確認（要旨・1 節） |
| 9 | Dremel: Interactive Analysis of Web-Scale Datasets | Melnik ほか（Google） | VLDB 2010 | https://research.google/pubs/dremel-interactive-analysis-of-web-scale-datasets-2/ | 要旨のみ確認 |
| 10 | File Format／Nested Encoding | Apache Parquet | 取得 2026-11-18（版の表示なし） | https://parquet.apache.org/docs/file-format/ ・ https://parquet.apache.org/docs/file-format/nestedencoding/ | 本文確認 |
| 11 | MonetDB/X100: Hyper-Pipelining Query Execution | Boncz, Zukowski, Nes | CIDR 2005 | https://www.cidrdb.org/cidr2005/papers/P19.pdf | 要旨のみ確認 |
| 12 | Efficiently Compiling Efficient Query Plans for Modern Hardware | T. Neumann | PVLDB 4(9)、2011 | https://www.vldb.org/pvldb/vol4/p539-neumann.pdf | 要旨のみ確認 |
| 13 | Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask | Kersten ほか | PVLDB 11(13)、2018 | https://www.vldb.org/pvldb/vol11/p2209-kersten.pdf | 本文確認（要旨・10 節） |
| 14 | "One Size Fits All": An Idea Whose Time Has Come and Gone | Stonebraker, Çetintemel | ICDE 2005（会議名は記憶） | https://cs.brown.edu/~ugur/fits_all.pdf | 要旨のみ確認 |
| 15 | TiDB: A Raft-based HTAP Database | Huang ほか（PingCAP） | PVLDB 13(12)、2020 | https://www.vldb.org/pvldb/vol13/p3072-huang.pdf | 要旨のみ確認。ベンダーの論文 |
| 16 | The Snowflake Elastic Data Warehouse | Dageville ほか（Snowflake） | SIGMOD 2016 | https://www.cs.cmu.edu/~15721-f24/papers/Snowflake.pdf（講義サイトの写し） | 本文確認（要旨・2 節・3 節の一部）。ベンダーの論文 |
| 17 | Snowflake key concepts and architecture | Snowflake | 取得 2026-11-18（日付は未記録） | https://docs.snowflake.com/en/user-guide/intro-key-concepts | 本文確認（冒頭） |
| 18 | BigQuery overview／Overview of BigQuery storage | Google Cloud | Last updated 2026-11-10 | https://docs.cloud.google.com/bigquery/docs/introduction ・ https://docs.cloud.google.com/bigquery/docs/storage_overview | 本文確認（該当箇所） |
| 19 | Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics | Armbrust, Ghodsi, Xin, Zaharia（Databricks ほか） | CIDR 2021 | https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf | 本文確認（要旨・1〜3 節の一部）。提唱者の論文 |
| 20 | Iceberg Table Spec／Releases | Apache Iceberg | 形式 v1〜v3 採択済み・v4 開発中。1.12.0（2026-09-29） | https://iceberg.apache.org/spec/ ・ https://iceberg.apache.org/releases/ | 本文確認（Format Versioning、Goals、Overview、Optimistic Concurrency） |
| 21 | Delta Transaction Log Protocol／Releases | delta-io | master（取得 2026-11-18）。Delta Lake 4.4.1（10 月 5 日、年は表示なし） | https://github.com/delta-io/delta/blob/master/PROTOCOL.md ・ https://github.com/delta-io/delta/releases | 本文確認（見出しと該当箇所） |
| 22 | Table & Query Types／Download | Apache Hudi | 文書 1.2.1（公開日の記載なし） | https://hudi.apache.org/docs/table_types ・ https://hudi.apache.org/releases/download | 本文確認（表タイプ）。仕様本文は未確認 |
| 23 | 65.4 GIN Indexes | PostgreSQL | 18.7 | https://www.postgresql.org/docs/18/gin.html | 本文確認（該当箇所） |
| 24 | org.apache.lucene.codecs.lucene103（索引ファイル形式の概説） | Apache Lucene | 10.3.0（参照した版。最新かは未確認） | https://lucene.apache.org/core/10_3_0/core/org/apache/lucene/codecs/lucene103/package-summary.html | 本文確認（冒頭） |
| 25 | Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs | Malkov, Yashunin | arXiv:1603.09320（掲載誌は記憶） | https://arxiv.org/abs/1603.09320 | 要旨のみ確認 |
| 26 | pgvector README | pgvector | v0.8.7（master、取得 2026-11-18） | https://github.com/pgvector/pgvector | 本文確認 |
| 27 | kNN search in Elasticsearch | Elastic | 取得 2026-11-18 | https://www.elastic.co/docs/solutions/search/vector/knn | 本文確認（冒頭） |
| 28 | 8.14 JSON Types | PostgreSQL | 18.7 | https://www.postgresql.org/docs/18/datatype-json.html | 本文確認 |
| 29 | ISO/IEC 39075:2024 Information technology — Database languages — GQL | ISO | 第 1 版、2024 | https://www.iso.org/standard/76120.html | 題名のみ（カタログページ） |
| 30 | Event Sourcing | Martin Fowler | 2005-12-12 | https://martinfowler.com/eaaDev/EventSourcing.html | 本文確認 |
| 31 | CQRS | Martin Fowler | 2011-07-14 | https://martinfowler.com/bliki/CQRS.html | 本文確認 |
| 32 | CQRS Documents | Greg Young | 2010 | https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf | 目次と冒頭のみ |
| 33 | CQRS pattern | Microsoft（Azure Architecture Center） | ms.date 2025-02-20 | https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs | 本文確認 |
| 34 | Event Sourcing pattern | 同上 | ms.date 2026-03-27 | https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing | 本文確認 |
| 35 | Materialized View pattern | 同上 | ms.date 2026-09-21 | https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view | 本文確認 |
| 36 | MapReduce: Simplified Data Processing on Large Clusters | Dean, Ghemawat（Google） | OSDI 2004 | https://static.googleusercontent.com/media/research.google.com/en//archive/mapreduce-osdi04.pdf | 本文確認（要旨・3.3 節・4 節の一部） |
| 37 | Resilient Distributed Datasets | Zaharia ほか | NSDI 2012 | https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf | 本文確認（lineage の記述） |
| 38 | Structured Streaming Programming Guide | Apache Spark | 4.3.0 | https://spark.apache.org/docs/latest/streaming/index.html | 本文確認（概要のみ） |
| 39 | Timely Stream Processing／Stateful Stream Processing／Checkpointing／Savepoints／Joins／Kafka connector | Apache Flink | 2.3.0（stable。Joins・Checkpointing・Savepoints は release-2.3） | https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/ ほか（同サイトの docs/concepts/stateful-stream-processing/、docs/dev/datastream/fault-tolerance/checkpointing/、docs/ops/state/savepoints/、docs/sql/reference/queries/joins/、docs/connectors/datastream/kafka/） | 本文確認（該当箇所） |
| 40 | An Overview of End-to-End Exactly-Once Processing in Apache Flink／Release Notes Flink 2.0 | Apache Flink | 2018-02-28／2.0 | https://flink.apache.org/2018/02/28/an-overview-of-end-to-end-exactly-once-processing-in-apache-flink-with-apache-kafka-too/ ・ https://nightlies.apache.org/flink/flink-docs-release-2.0/release-notes/flink-2.0/ | 本文確認（ブログ）。リリースノートは該当行のみ |
| 41 | Best Practices／Backfill | Apache Airflow | 3.4.0 | https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html ・ https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/backfill.html | 本文確認（該当箇所） |
| 42 | Assets／Backfilling data | Dagster | 取得 2026-11-18（版の表示なし） | https://docs.dagster.io/guides/build/assets ・ https://docs.dagster.io/guides/build/partitions-and-backfills/backfilling-data | 本文確認（冒頭） |
| 43 | Add data tests to your DAG／Incremental models／About dbt versions | dbt Labs | dbt v2.0（初版 2026-09-14） | https://docs.getdbt.com/docs/build/data-tests ・ https://docs.getdbt.com/docs/build/incremental-models ・ https://docs.getdbt.com/docs/dbt-versions/core | 本文確認（該当箇所） |
| 44 | Kafka: a Distributed Messaging System for Log Processing | Kreps, Narkhede, Rao（LinkedIn） | NetDB 2011（会議名は記憶） | https://notes.stephenholiday.com/Kafka.pdf（第三者の写し） | 要旨のみ確認 |
| 45 | Design | Apache Kafka | 4.4 文書 | https://kafka.apache.org/44/design/design/ | 本文確認 |
| 46 | Topic Configs | 同上 | 4.4 | https://kafka.apache.org/44/configuration/topic-configs/ | 本文確認（該当項目） |
| 47 | Upgrading | 同上 | 4.4 | https://kafka.apache.org/44/getting-started/upgrade/ | 本文確認（share groups 関連） |
| 48 | Consumer Rebalance Protocol | 同上 | 4.4 | https://kafka.apache.org/44/operations/consumer-rebalance-protocol/ | 本文確認 |
| 49 | Configuring a Streams Application | 同上 | 4.4 | https://kafka.apache.org/44/streams/developer-guide/config-streams/ | 本文確認（processing.guarantee） |
| 50 | Tiered Storage | 同上 | 4.4 | https://kafka.apache.org/44/operations/tiered-storage/ | 本文確認（Limitations の 1 行） |
| 51 | Downloads | 同上 | 4.4.0（2026-10-22） | https://kafka.apache.org/community/downloads/ | 本文確認 |
| 52 | Kafka Compatibility／How Redpanda Works／What's New | Redpanda Data | 26.2（current） | https://docs.redpanda.com/current/develop/kafka-clients/ ・ https://docs.redpanda.com/current/get-started/architecture/ ・ https://docs.redpanda.com/current/get-started/release-notes/redpanda/ | 本文確認（該当箇所）。ベンダーの公式文書 |
| 53 | The Dataflow Model | Akidau ほか（Google） | PVLDB 8(12)、2015 | https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf | 本文確認（要旨・脚注 6・4 節・結論の一部） |
| 54 | How to beat the CAP theorem | Nathan Marz | 2011-10-13 | http://nathanmarz.com/blog/how-to-beat-the-cap-theorem.html | 本文確認 |
| 55 | Questioning the Lambda Architecture | Jay Kreps（O'Reilly Radar） | 2014-07-02 | https://www.oreilly.com/radar/questioning-the-lambda-architecture/ | 本文確認 |
| 56 | Views／Isolation levels | Materialize | 取得 2026-11-18 | https://materialize.com/docs/concepts/views/ ・ https://materialize.com/docs/get-started/isolation-level/ | 本文確認（該当箇所）。ベンダーの公式文書 |
| 57 | RisingWave architecture | RisingWave Labs | 取得 2026-11-18 | https://docs.risingwave.com/get-started/architecture | 本文確認。ベンダーの公式文書 |
| 58 | DBSP: Automatic Incremental View Maintenance for Rich Query Languages | Budiu ほか | PVLDB 16(7)、2023 | https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf | 要旨のみ確認 |
| 59 | Incremental materialized view／Refreshable materialized view | ClickHouse | 取得 2026-11-18 | https://clickhouse.com/docs/materialized-view/incremental-materialized-view ・ https://clickhouse.com/docs/materialized-view/refreshable-materialized-view | 本文確認（該当箇所） |
| 60 | MergeTree table engine／Manage data with TTL／Compression in ClickHouse／LowCardinality(T)／JSON Data Type | ClickHouse | 取得 2026-11-18 | https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree ・ https://clickhouse.com/docs/guides/developer/ttl ・ https://clickhouse.com/docs/data-compression/compression-in-clickhouse ・ https://clickhouse.com/docs/sql-reference/data-types/lowcardinality ・ https://clickhouse.com/docs/sql-reference/data-types/newjson | 本文確認（該当箇所） |
| 61 | Deduplicating inserts on retries／CHANGELOG | ClickHouse | 26.10（2026-10-22）、26.8 LTS（2026-08-27） | https://clickhouse.com/docs/guides/developer/deduplicating-inserts-on-retries ・ https://github.com/ClickHouse/ClickHouse/blob/master/CHANGELOG.md | 本文確認（該当箇所） |
| 62 | Designing a schema for observability | ClickHouse | 取得 2026-11-18 | https://clickhouse.com/docs/use-cases/observability/schema-design | 本文確認（該当箇所） |
| 63 | REFRESH MATERIALIZED VIEW／39.3 Materialized Views | PostgreSQL | 18.7 | https://www.postgresql.org/docs/18/sql-refreshmaterializedview.html ・ https://www.postgresql.org/docs/18/rules-materializedviews.html | 本文確認 |
| 64 | Why DuckDB／Concurrency／Release Calendar | DuckDB | 2.0.0 LTS（2026-10-21） | https://duckdb.org/why_duckdb ・ https://duckdb.org/docs/2.0/connect/concurrency.html ・ https://duckdb.org/release_calendar | 本文確認 |
| 65 | ClickBench README | ClickHouse（ベンダー運営） | main（取得 2026-11-18） | https://github.com/ClickHouse/ClickBench | 本文確認（Overview、Limitations、History の該当行） |
| 66 | Metric and label naming | Prometheus | 取得 2026-11-18 | https://prometheus.io/docs/practices/naming/ | 本文確認（該当箇所） |
| 67 | Runtime fields | Elastic | 取得 2026-11-18 | https://www.elastic.co/docs/manage-data/data-store/mapping/runtime-fields | 本文確認 |
| 68 | OpenLineage.md（仕様）／About OpenLineage | OpenLineage | 文書 1.55.0、仕様は main | https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md ・ https://openlineage.io/docs/ | 本文確認（冒頭の概念定義） |
| 69 | GX Core overview | Great Expectations | 1.25.0 | https://docs.greatexpectations.io/docs/core/introduction/gx_overview | 本文確認（冒頭） |
| 70 | What is Soda? | Soda | 取得 2026-11-18 | https://docs.soda.io/soda-documentation/get-started/readme.md | 本文確認（冒頭）。ベンダーの自己申告 |
| 71 | Site Reliability Engineering 25 章 Data Processing Pipelines | Google（O'Reilly、2016） | Web 版 | https://sre.google/sre-book/data-processing-pipelines/ | 本文確認 |
| 72 | Site Reliability Engineering 26 章 Data Integrity: What You Read Is What You Wrote | 同上 | Web 版 | https://sre.google/sre-book/data-integrity/ | 本文確認（前半〜第 2 層まで。第 3 層以降は見出しのみ） |
| 73 | Cloudflare outage on November 18, 2025 | Cloudflare | 2025-11-18 | https://blog.cloudflare.com/18-november-2025-outage/ | 本文確認。事業者自身の事後報告 |
| 74 | Transaction ID Wraparound in Postgres | Sentry | 2015-07-23 | https://blog.sentry.io/transaction-id-wraparound-in-postgres/ | 本文確認。事業者自身の事後報告 |
| 75 | What We Learned from the Recent Mandrill Outage | Mailchimp | 2019-03-26 | https://mailchimp.com/what-we-learned-from-the-recent-mandrill-outage/ | 本文確認。事業者自身の事後報告 |
| 76 | Postmortem of database outage of January 31 | GitLab | 2017-02（公開日は記憶） | https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ | 本文確認（該当箇所）。事業者自身の事後報告 |
| 77 | PERF03-BP01 Use a purpose-built data store…／Data Analytics Lens | AWS Well-Architected | 取得 2026-11-18／Lens は 2023-12-22 | https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/perf_data_use_purpose_built_data_store.html ・ https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/analytics-lens.html | BP は本文確認（冒頭）。Lens は題名と公開日のみ |
| 78 | Understand data models | Microsoft（Azure Architecture Center） | ms.date 2025-08-21 | https://learn.microsoft.com/en-us/azure/architecture/data-guide/technology-choices/understand-data-store-models | 本文確認（冒頭と該当箇所） |
| 79 | Technology Radar：DuckDB／Lakehouse architecture | Thoughtworks | どちらも 2023-04 に Trial（現行版には非掲載） | https://www.thoughtworks.com/radar/platforms/duckdb ・ https://www.thoughtworks.com/radar/techniques/lakehouse-architecture | 評価と日付のみ確認 |
| 80 | E.1 Release 19 | PostgreSQL | 19（RC 段階。リリースノートは 2026-10-09 時点） | https://www.postgresql.org/docs/19/release-19.html | 「graph」「PGQ」で検索して該当なしを確認 |
