# 08 共通基盤 7 種にデータ指向の考え方を当てはめる

調査日：2026-11-18

## 1. 問い（このノートが答えること。対応する Part）

対応する Part：13（ステップ 9「7 つの共通基盤に、どう当てはめるか」）。Part 14（共通基盤が全体を止める型）への橋渡しも含む。

データ基盤・ETL 基盤・ログ基盤・認証基盤・AI 基盤・分析基盤・セキュリティ基盤の 7 つを、同じ 4 つの問いで設計する。

1. その基盤が持つデータは記録の正本か派生か。所有者は誰か
2. データはどう流れ込み、どう出ていくか（同期か非同期か、利用側との契約は何か）
3. 利用側を止めずに変える・入れ替えるには、何を契約にするか
4. 基盤が止まったとき、利用側はどうふるまうべきか（静的な安定性、フェイルオープンかフェイルクローズか）

DDIA 2e はこの領域（基盤の運営、認証、可観測性、AI 基盤、セキュリティ基盤）をほとんど扱わないので、このノートは一次資料だけで組み立てる。4 つの層（標準／製品／事故／権威の推奨）は節で分ける。「設計上の推論」と書いた箇所は、一次資料の記述を組み合わせた筆者の整理で、資料そのものの主張ではない。

## 2. 標準・定義（節番号）

### 2.1 共通基盤（プラットフォーム）の定義

- CNCF Platforms White Paper（v1、2023-03 完成。発行は CNCF TAG App Delivery の Platforms WG）は、プラットフォームを能力の「integrated collection of capabilities」とし、内部の利用者に一貫した体験で提供する層と定義する。属性は 7 つ：製品として扱う、利用者体験、文書と導入、セルフサービス、認知負荷の軽減、任意かつ組み合わせ可能（optional and composable）、既定で安全 [S1]
- 同書の能力の一覧（13 領域）に、可観測性、データサービス、メッセージングとイベント、ID と秘密情報、セキュリティが入る。つまりこのガイドの 7 基盤のうち、ログ・データ・認証・セキュリティは CNCF の定義でも「プラットフォームの能力」に当たる。AI 基盤と分析基盤は一覧に無い [S1]
- 同書はプラットフォームチームの負荷への対策として「thinnest viable platform」を挙げ、基盤そのものは外部提供のサービスに頼り、ほかに供給元が無いときだけ自作する、とする [S1]
- CNCF Platform Engineering Maturity Model（v1）は 5 つの側面（投資・採用・インターフェース・運用・計測）× 4 段階（Provisional／Operational／Scalable／Optimizing）。最上位を目指すこと自体を目的にしない、と明記する任意の指針で、規範ではない [S2]
- Team Topologies（公式サイト Key Concepts）は、プラットフォームチームをストリームアラインドチームの配送を速める「compelling internal product」を出す存在とし、相互作用の型として X-as-a-Service（提供側と利用側が最小のやりとりで明確な境界を持つ）を定める [S3]

### 2.2 データメッシュの 4 原則（Dehghani の 2 論考）

- 第 1 論考（2019-05-20）：中央集権のデータ基盤の失敗の型を 3 つ挙げる。(a) 中央集権で一枚岩、(b) パイプラインの段（取り込み・洗浄・集計・提供）で分割するので、機能を 1 つ足すと全段に変更が及ぶ、(c) データエンジニアがドメインから切り離された専門サイロになる [S7]
- 同論考の提案：ドメインがデータを所有して提供する。パイプラインはドメインの内部実装になる。発生源のドメインは業務の事実を時刻つきの不変のイベントとして出す。利用側に合わせたデータセットは発生源のデータから作り直せる。データプロダクトの性質は 6 つ（発見できる・アドレスで指せる・信頼できる・自己記述的・相互運用できる・安全）。データレイクや DWH はメッシュの 1 つの節になる [S7]
- 第 2 論考（2020-12-03）：4 原則は (1) ドメイン指向の分散したデータ所有とアーキテクチャ、(2) プロダクトとしてのデータ、(3) セルフサービスのデータ基盤、(4) 連合型の計算によるガバナンス。データプロダクトは「architectural quantum」（コード＋データとメタデータ＋インフラを含む、独立して配備できる最小単位）[S8]
- 同論考は、業務データ（現在の状態、マイクロサービスの中）と分析データ（時間軸つきの集計された見え方）を、統合されているが別の 2 つの面として扱う。全体で決めるのは相互運用の標準・品質と SLO の表し方・機密度の区分・ドメインをまたぐ識別子。ドメインが決めるのは自分のデータモデルと品質の測り方 [S8]

### 2.3 メタデータ・系譜・カタログの仕様

- OpenLineage（仕様 1.55.0 のオブジェクトモデル）：Job（処理）、Run（1 回の実行。クライアントが生成する UUID の runId、UUIDv7 推奨）、Dataset（名前空間＋名前で一意）。イベントは RunEvent・JobEvent・DatasetEvent。実行側が実行時にイベントを出す形（スキーマや品質は facet で足す）[S12]
- Apache Iceberg 表仕様：フォーマット版は v1〜v4 が仕様に載る（v4 は「Metadata Structure and Representation」）。目標に直列化可能な分離、スキーマと分割の進化（列の追加・削除・並べ替え・改名が安全）を挙げる。コミットは表メタデータファイルの原子的な入れ替えで、これが直列化可能な分離の基礎になる [S13]
- Iceberg REST カタログ：OpenAPI で定義した共通 API。目的は、言語やエンジンごとにカタログの実装を持つ問題の解消。変更ベースのコミットでサーバー側が衝突の解消と再試行を行い、ルートのメタデータはカタログが書く。認証情報の払い出し（credential vending）またはリモート署名による表の共有にも対応。Iceberg 0.14.0 で導入 [S14]

### 2.4 可観測性（OpenTelemetry）

- シグナルごとの安定度（仕様のステータスページ、2026-11-18 閲覧。ページに日付と版の表示なし）[S20]

| シグナル | API | SDK | プロトコル（OTLP） |
| --- | --- | --- | --- |
| Traces | Stable | Stable | Stable |
| Metrics | Stable | Mixed | Stable |
| Baggage | Stable | Stable | 該当なし |
| Logs | Stable（Bridge API） | Stable | Stable |
| Profiles | 記載なし | 記載なし | Development |

- OTLP 1.11.1：トレース・メトリクス・ログは Stable、プロファイルは Development。保証の範囲は 1 組のクライアントとサーバーの間だけで、中継をまたぐ端から端の保証は範囲外。再送でサーバー側に重複が生じうることは「a deliberate choice」。再試行できないエラーではクライアントはデータを捨てなければならず（MUST）、捨てた件数を数えるべき（SHOULD）。絞り込みは gRPC の UNAVAILABLE＋RetryInfo、HTTP の 429／503＋Retry-After [S21]
- ログ仕様：既存のロギングを置き換えず、既存のライブラリからブリッジ（appender）で OTel のデータモデルに載せる。LogRecord に TraceId・SpanId と Resource を入れて、トレース・メトリクスと突き合わせる。ファイルや標準出力のログは Collector の filelog receiver で集めることを勧める [S26]
- セマンティック規約 1.45.0：スパン名、メトリクスの計器と単位、属性の名前・型・意味を定める。安定度は領域ごと（データベースのスパンは「Stable（別記を除く）」）。生成 AI の規約は別リポジトリへ移った（移転先の安定度は未確認）[S25]

### 2.5 認証・認可

- RFC 7662（OAuth 2.0 Token Introspection、2015-10、Proposed Standard）§4：保護対象リソースは応答をキャッシュしてよい（MAY）が、性能と安全のトレードオフを考えなければならない（MUST）。長いキャッシュは、失効したトークンが使える時間の窓を作る。`exp` を超えてキャッシュしてはならない。問い合わせそのものが失敗したとき（通信断・タイムアウト）のふるまいは、この RFC は定めていない [S36]
- RFC 9068（JWT Profile for OAuth 2.0 Access Tokens、2021-10、Proposed Standard）§4：リソースサーバーは認可サーバーのメタデータの `jwks_uri` から鍵を得て、`typ`・`iss`・`aud`・署名・`exp` を検証する。失効の仕組みと鍵のローテーション手順は、この RFC は定めていない [S37]
- OpenID Connect Core 1.0（errata set 2、2023-12-15）§10.1.1：署名鍵のローテーションは、新しい鍵を `jwks_uri` の JWK Set に足し、`kid` で検証側に知らせる。検証側は知らない `kid` を見たら `jwks_uri` を取り直す。退役した署名鍵は、移行のためしばらく残すべき（SHOULD）。§10.2.1 は `jwks_uri` の応答に `Cache-Control` の `max-age` を付けるべき（SHOULD）とする [S38]
- NIST SP 800-207（Zero Trust Architecture、2020-08、Final）§2.1：7 つの原則。アクセスはセッション単位で与え、動的なポリシーで決める。§5.2：ポリシーエンジン／ポリシー管理者に到達できなくなると、運用上の誤りひとつで企業全体が機能しなくなりうる、と自ら脅威に数える。対策は複数拠点への複製だが、危険は消えないと書く。§5.5：ポリシーの保管先と監視データそのものが攻撃の的になる [S33]
- NIST SP 800-207A（2023-09、Final）：ネットワークの位置ではなく、サービスとアプリケーションの ID に基づく制御へ。API ゲートウェイ、サイドカープロキシ、SPIFFE などの ID 基盤で、場所によらず方針を強制する [S34]
- NIST SP 800-204 系（すべて Final）[S35]

| 番号 | 題名 | 公開日 |
| --- | --- | --- |
| SP 800-204 | Security Strategies for Microservices-based Application Systems | 2019-08-07 |
| SP 800-204A | Building Secure Microservices-based Applications Using Service-Mesh Architecture | 2020-05-27 |
| SP 800-204B | Attribute-based Access Control for Microservices-based Applications using a Service Mesh | 2021-08-06 |
| SP 800-204C | Implementation of DevSecOps for a Microservices-based Application with Service Mesh | 2022-03-08 |
| SP 800-204D | Strategies for the Integration of Software Supply Chain Security in DevSecOps CI/CD Pipelines | 2024-02-12 |

- SP 800-204 本文 §4.1：MS-SS-1 は、有効なセッションは取り消せないのでトークンの有効期限をできるだけ短くせよ、とする。MS-SS-2 は、粗い方針は入口の API ゲートウェイで、細かい方針はサービスの近くで強制する。方針データのキャッシュは、アクセスサーバーに届かないときだけ頼り、環境に合った期間で失効させる。トークンはハンドル型でも、表明を運ぶ型でもよい。MS-SS-5（監視）、MS-SS-6（サーキットブレーカー）も定める [S35]
- OpenID AuthZEN Authorization API 1.0：2026-01-11 に Final（Standards Track）。PDP と PEP の間の要求（subject・action・resource・context）と応答（真偽の decision）を定め、PDP のポリシー言語・構成・状態管理は範囲外。複数評価（`execute_all` など 3 つの意味）と検索 API を持つ [S41]

### 2.6 ログ管理・鍵管理の指針（NIST）

- NIST SP 800-92「Guide to Computer Security Log Management」は 2006-09 の Final が現行。目次で確かめた範囲では、§2.3.2 がログの保護、§3.1 が基盤の構成、§4.2 がポリシー、§5.4 が長期保管で、保管したログの完全性はメッセージダイジェストで確かめるとする [S30]
- SP 800-92 Rev.1「Cybersecurity Log Management Planning Guide」は 2023-10-11 の初期公開草案（IPD）のまま。意見募集は 2023-11-29 で終了。CSRC のページに Final の記載は無い（2026-11-18 閲覧）[S31]
- NIST SP 800-57 Part 1 Rev.5（鍵管理の一般指針）は 2020-05 の Final。CSRC のページに Rev.6 の記載は無い [S66]
- NIST AI RMF 1.0（2023-01-26）は任意の枠組み。生成 AI プロファイル（NIST AI 600-1）は 2024-07-26。2026-04-07 に重要インフラ向けプロファイルの構想メモが出ており、ページには 1.0 を改訂中との記載がある [S53]

## 3. 製品ごとの違い（表。公式文書の URL・版・日付）

版と日付は出典の欄を参照。クラウド製品は公式文書に基づく比較で、実測していない。

### 3.1 データ基盤・分析基盤の参照アーキテクチャ

| 提供元 | 文書 | 言っていること | 出典 |
| --- | --- | --- | --- |
| AWS | Well-Architected Data Analytics Lens（2023-12-22） | データメッシュは分散した所有でドメインをまたぐ分析を可能にする型。構成が複雑になる代償がある。向くのは、データ戦略が確立し、モダンデータアーキテクチャを実装済みで、事業部門が自律している組織 | [S9] |
| Google Cloud | Architecture and functions in a data mesh | 役割は、ドメインの生産者チーム、利用者チーム、中央のガバナンスチーム、中央のセルフサービス基盤チーム。消費の口は表・ビュー・ファイル・トピック・ストリーム。参照実装は BigQuery の承認済みビューと Pub/Sub。基盤の決定を中央に寄せすぎるとボトルネックになると警告 | [S10] |
| Microsoft | Cloud Adoption Framework「Unified data platform adoption」（2026-10-23） | 旧来の cloud-scale analytics のデータメッシュのページ（URL）は、この記事へ転送される。Fabric を中心に、ドメインがデータプロダクトを作り、Purview でカタログ・分類・方針を一元化する構成 | [S11] |

注：Azure の旧「What is data mesh」ページの本文は確認できなかった（転送されたため）。

### 3.2 メタデータ・カタログ

| 製品・仕様 | 位置づけ | 正本と派生の分け方 | 出典 |
| --- | --- | --- | --- |
| OpenLineage 1.55.0 | 系譜のイベントの仕様（製品ではない）。実行側が出す | イベントが事実の記録。グラフは受け側が組む | [S12] |
| Iceberg REST カタログ | 表の現在のメタデータの場所を持つ。コミットの調停役 | カタログが「表の現在」の正本。データファイルとメタデータファイルは不変 | [S13][S14] |
| DataHub 1.8.0 | 「第 3 世代」のカタログ。スキーマ先行のメタデータモデル、ストリーム指向（変更が数秒で反映、Kafka で購読できる）、連合したメタデータ提供 | 公式の構成ページでは保管と索引の関係までは書かれていない（未確認） | [S15] |
| OpenMetadata | JSON Schema でエンティティを定義。API 先行。MySQL がエンティティの保管先、Elasticsearch が検索の索引。変更イベントを表に記録 | 関係 DB が正本、検索索引が派生（ページの記述から） | [S16] |

### 3.3 ETL・オーケストレーション

| 製品 | 版 | 公式文書の言い方 | 出典 |
| --- | --- | --- | --- |
| Apache Airflow | 3.4.0 | タスクは DB のトランザクションと同じに扱う。再実行のたびに同じ結果を出す。INSERT ではなく UPSERT。「最新」を読まず、決まった分割（data_interval_start など）を読む。重要な計算に now() を使わない。ローカルのファイルに状態を置かない | [S19] |

### 3.4 ログ基盤（OpenTelemetry Collector）

| 項目 | 既定・挙動 | 出典 |
| --- | --- | --- |
| 位置づけ | ベンダー非依存の受信・加工・送出。サービスの横に置くことを一般に勧める（再試行・バッチ・暗号化・機微な情報の除去を肩代わり）。安定度は部品ごとで「mixed」 | [S22] |
| 送信キュー | メモリ上。既定は多くの場合 1000 バッチ。満杯になると、入ってくるデータを捨てる | [S23] |
| 再試行 | 指数バックオフ。既定の上限は 5 分（300 秒）。超えると古いデータを捨てる | [S23] |
| 永続化 | `file_storage` 拡張で WAL に書けば再起動をまたげる。ただし保証は専用のメッセージキューほど強くない、と公式が書く | [S23] |
| 中継 | エージェントとゲートウェイの間に Kafka を置く構成が公式に載る。運用は複雑になる | [S23] |
| 失う場面 | 上限時間の超過、キューあふれ、永続化なしでのクラッシュ、ディスク障害、メッセージキューの障害、設定の誤り、耐障害機能の無効化の 7 つ | [S23] |
| サンプリング | 先頭（head）は簡単だがエラーのあるトレースを必ず残すことはできない。末尾（tail）は状態を持つ大きな仕組みが要る。毎秒 1000 トレース以上が検討の目安 | [S24] |
| カーディナリティ | Prometheus は、ラベルの組み合わせ 1 つが新しい時系列になるので、ユーザー ID やメールなど上限の無い値をラベルにするなと明記 | [S27] |

### 3.5 認証・認可（ポリシーをデータとして配る）

| 製品・仕様 | 版・状態 | 配り方と障害時 | 出典 |
| --- | --- | --- | --- |
| Open Policy Agent | 文書は Rego v1 系（ページに個別の版の表示なし） | バンドル（ポリシー＋データ）をポーリングで取得。更新は「eventually consistent」。ETag と 304、ロングポーリング、差分バンドル（データのみ）、署名検証（失敗したら現在のバンドルを使い続ける）。`persist: true` でディスクに保存し、バンドルサーバーに届かなくても直近のバンドルで起動できる | [S39] |
| Cedar | ポリシー言語 4.6 | ポリシーと、判断に要るエンティティ（所属など）を要求と一緒に渡す。スキーマはポリシーの作成・更新時の検証にだけ使い、評価時には使わない | [S40] |
| AuthZEN Authorization API | 1.0 Final（2026-01-11） | PEP と PDP の間の API だけを決める。配布は範囲外 | [S41] |
| Kubernetes アドミッション Webhook | v1.37 の文書 | `failurePolicy` は Ignore か Fail。既定は Fail（呼び出しの失敗で要求を拒否）。タイムアウトは既定 10 秒、1〜30 秒。失敗した Webhook が `subjectaccessreviews` に当たるとクラスタ自身の認可を止めうるので、v1.37 から既定で対象外 | [S42] |
| Microsoft Entra のバックアップ認証 | 文書 2026-03-24 | 主系が使えないとき、既存セッションに限ってトークンを再発行する（再認証は全認証の 90% 超）。新規セッションとゲストは対象外。条件つきアクセスの条件のうち、グループ・ロール・リスクなどは障害中に実時間で評価できない。既定（resilience defaults 有効）はセッション開始時のデータで評価して通す。無効にすると拒否する | [S48] |

### 3.6 AI 基盤

| 項目 | 公式文書の言い方 | 出典 |
| --- | --- | --- |
| MLOps の段階（Google Cloud） | レベル 0（手作業）、1（パイプラインの自動化・継続的な学習）、2（CI/CD）。特徴量ストアは学習と推論で同じ特徴量を供給して学習と推論のずれを避ける任意の部品。ML メタデータストアは、実行ごとにパイプラインと部品の版、引数、成果物へのポインタ、前のモデルへのポインタ、評価指標を残す | [S51] |
| 時点の正しさ（Feast） | エンティティの各行の時刻の時点での特徴量の値を結合する。さかのぼる幅は TTL（各行の時刻が基準で、問い合わせの時刻ではない）。`created_timestamp` での絞り込みは、後から埋め戻した値が学習データに漏れるのを防ぐ | [S52] |
| AWS | Well-Architected Machine Learning Lens（2025-11-19）。生成 AI は別の Generative AI Lens。本文の細部は未確認 | [S54] |
| ベクトル索引（Azure AI Search、2026-11-09） | 索引は、同じ埋め込みモデルの埋め込みで埋めたベクトル項目から成る「embedding space」を暗に作る。次元数はモデルで決まる。既存の項目の変更・削除には、削除して全体を作り直すことが多い | [S56] |
| ベクトル索引（pgvector 0.8.7） | 既定は厳密な検索。近似索引（HNSW・IVFFlat）を足すと再現率と引き換えに速くなり、同じ問い合わせの結果が変わりうる。ベクトルはほかのデータと同じ表に置く | [S57] |
| LLM ゲートウェイ（Azure Architecture Center、2026-04-30） | ゲートウェイは再試行・負荷分散・認証の連携・流量制限・横断の監視・費用の配賦を利用側から引き取る。一方で単一障害点になりうる、攻撃面が増える、生の要求と応答が通るので法令対応の範囲に入る、遅延が増える。SLO を危うくするなら入れるな、と明記 | [S55] |
| LLM ゲートウェイ（Thoughtworks Radar） | LiteLLM が Trial、agentgateway が Assess（2026-11 の版。検索結果の要約で確認、ページ本文は未確認） | [S58] |

### 3.7 セキュリティ基盤

| 項目 | 製品の挙動 | 出典 |
| --- | --- | --- |
| 鍵のローテーション（AWS KMS） | 鍵素材だけが変わり、KMS キーという論理的な資源（ID）は同じ。復号では暗号化に使った鍵素材を KMS が自動で選ぶ。既定の周期は 365 日。**ローテーションは、守っているデータにもデータキーにも影響しない（再暗号化しない）**。漏れたデータキーの影響は緩和しない。対称鍵以外（非対称・HMAC・カスタムキーストア）は手動 | [S59] |
| エンベロープ暗号化（Google Cloud KMS） | データを DEK で暗号化し、DEK を KEK で包む。DEK は手元で生成し、書き込みごとに新しくし、包んだ形でデータの近くに置く。KEK は中央に置き、KMS の外に出ない。KMS の Encrypt／Decrypt の入力は 64KiB まで | [S60] |
| 再暗号化（Google Cloud KMS） | ローテーションは既存の暗号文を再暗号化しない。不正使用が疑われるときは、復号→新しい主版で暗号化→古い版を無効化または破棄予約 | [S61] |
| 監査ログの完全性（AWS CloudTrail） | ログファイルごとにハッシュ（SHA-256）。1 時間ごとにダイジェストファイルを作り、秘密鍵で署名（SHA-256 with RSA）。各ダイジェストは前のダイジェストの署名を含む（連鎖）。変更・削除の検出と、「この期間は配信が無かった」ことの証明ができる | [S62] |
| 行レベルの制御（PostgreSQL 18） | 行セキュリティを有効にしてポリシーが無ければ既定で拒否。スーパーユーザーと BYPASSRLS は常に迂回、表の所有者も通常は迂回（FORCE で適用）。一意・主キー・外部キーの検査は行セキュリティを迂回するので、隠れた経路の漏えいに注意。`row_security = off` は迂回ではなく、絞られる問い合わせをエラーにする（バックアップで黙って欠けない） | [S63] |
| 行・列レベルの制御（BigQuery） | 行アクセスポリシー（フィルタ式＋対象の主体）。列レベル（ポリシータグ）・マスキングと併用できる。問い合わせ時間によるサイドチャネル、分割の刈り込みに効かないなどの制限を公式が列挙 | [S64] |
| 秘密情報の配布（Vault Agent、v2.x の文書） | トークンとリース付きの秘密をクライアント側でキャッシュし、更新も引き受ける。サーバーに直接出された失効は見逃しうる（古い項目が残る）。サーバーに届かないときにキャッシュから返すかは、このページには書かれていない | [S65] |

## 4. 事故・失敗例（一次報告）

### 4.1 Cloudflare 2024-11-14：ログの損失（ログ基盤）

- 約 3.5 時間、Logpush で顧客へ送るはずのログの約 55% が送られず、失われた（事後報告は 2024-11-26 公開）[S28]
- 経路は Logfwdr（転送）→ Logreceiver → Buftee（Logpush のジョブごとのバッファ）→ Logpush。新しいデータセットを足す変更で、Logfwdr に空の設定が渡った。Logfwdr はそれを「設定が得られない」ときの安全策として**フェイルオープン**（全顧客のログを送る）で扱った [S28]
- この安全策は、通信の一時的な不調でログを失わないために初期に作られたもので、当時は通信量が小さかった。変更は 5 分未満で戻されたが、その間に Buftee のバッファが通常の 100 万超から約 40 倍に増え、Buftee が応答しなくなった。復旧には全体の作り直しと再起動が要り、数時間かかった [S28]
- Buftee には、バッファの急増による連鎖障害を防ぐ仕組みがあったが、設定されていなかった。報告はシートベルトのたとえで、締めていなかったと書く。再発防止は、設定の誤りの警告、過負荷の定期的な試験 [S28]
- 示すこと：フェイルオープンは「失わない」ための選択でも、下流に予定外の負荷を流す。めったに通らない経路は、規模が育った後に試されていない（[S70] の「フォールバックの危険」と同じ型）

### 4.2 Slack 2021-01-04：監視が本番と同じ依存先を持っていた（ログ基盤）

- 原因は VPC をつなぐ AWS Transit Gateway の飽和によるパケット損失。休暇明けの通信の急増に拡張が追いつかなかった（事後報告は 2021-02-01 公開、Laura Nolan）[S29]
- ダッシュボードと警告のサービスは、その裏のデータベースと別の VPC にあり、Transit Gateway に依存していた。障害の調査に要る道具が、同じ障害で使えなくなった [S29]
- 技術者はメトリクスの裏側に直接問い合わせて調べたが、既成のダッシュボードよりずっと効率が悪かった。是正は、ダッシュボードのサービスをデータベースと同じ VPC に置いて依存を外すこと [S29]
- あわせて、ネットワークの待ちで CPU 使用率が下がり、自動スケールが Web 層を縮めた。派生した指標（CPU）を制御に使うと、原因が違うときに逆向きに動く例 [S29]

### 4.3 Google 2020-12-14：認証基盤の停止（認証基盤）

- 影響は 03:46〜04:33（US/Pacific）の約 47 分。全 Google ユーザーの認証と、アカウント情報の参照が失敗した。注：ステータスページの見出しの時刻（04:07〜06:23）は、本文の時系列と一致しない [S44]
- User ID Service はアカウントごとの一意な ID を持ち、OAuth トークンと Cookie の認証情報を扱う。アカウントのデータは Paxos を使う分散データベースにある。割り当て（クオータ）の仕組みの移行で、古い仕組みが使用量を 0 と報告し、猶予期間が切れたところで割り当てが下げられ、Paxos のリーダーが書き込めなくなった [S44]
- 読み取りはほどなく古くなり、このサービスは**安全のために古いデータを拒む**設計だったので、認証の参照がエラーになった（フェイルクローズ）[S44]
- 社内の利用者と道具も同じ認証に依存していたので、サポートの道具が使えず、ステータスページの更新が遅れた [S44]
- ネットワークは、データプレーンを変える操作だけが失敗し、既存の構成は動き続けた（静的な安定性の実例）。再発防止に、User ID Service が落ちたときのデータプレーンへの影響をより厳しく限ることが入る [S44]

### 4.4 Microsoft Entra ID／Azure AD（認証基盤）

- 2021-03-15（Azure AD、署名鍵）：一次の RCA は Azure のステータス履歴から消えていた（保持は 5 年）。Microsoft の社員が Microsoft Q&A に転記した暫定の分析で確認した範囲では、使われていない鍵を時間で消す自動処理が、クラウド間の移行のため「retain」と印を付けた鍵を消した。署名鍵のメタデータが変わり、アプリケーションはその鍵で署名したトークンを信用しなくなった。約 19:00 UTC に始まり、21:05 UTC にメタデータを戻したが、**利用側がキャッシュを更新する速さがばらばら**で、残りの影響の解消は翌 09:25 UTC。バックアップ認証はトークンの発行を覆っていたが、トークンの検証（メタデータの取得口）は覆っていなかった [S47]（暫定の報告。結論の唯一の根拠にしない）
- 2025-02-25（Entra ID、追跡 ID TMS9-J_8）：IPv6 対応の経路の片づけで、Seamless SSO と Entra Connect Sync のドメインの名前解決の途中にある DNS レコードと Traffic Manager を消した。構成のずれを検出する仕組みの欠陥で、未使用と判定された。変更は高リスクと印が付いていたが、影響を正しく見積もれず承認された。CNAME で戻して 94% が回復したが、元は A レコードで、一部の Kerberos クライアントはその種類を要した。完全な復旧は 01:15 UTC（約 8.5 時間）[S45]
- 2024-01-21（Azure Resource Manager、追跡 ID NKRF-1TG）：ARM に 2020-06 から入っていた、Entra の継続的アクセス評価（CAE）の非公開プレビューに潜在的な欠陥があった。プレビューに入ったテナントへの認証に失敗すると、ARM のノードが起動に失敗した。定期的に再起動するノードが次々に落ち、再試行が残りを押しつぶした。**ARM から RBAC のデータを得ていた下流のサービス（Key Vault、Service Bus、Event Hubs など）は、キャッシュした方針が切れた時点で要求を拒み始めた**。是正に、これらのサービスの RBAC を ARM に頼らない実装へ移すことが入る [S46]

### 4.5 CrowdStrike 2024-07-19：セキュリティ製品の内容更新（セキュリティ基盤）

- 04:09 UTC に Windows 向けの Rapid Response Content（チャネルファイル 291）を配り、05:27 UTC に戻した。その間にオンラインで更新を受けた、センサー 7.11 以降の Windows が異常終了した。Mac と Linux は影響なし [S68]
- 公式 RCA（2024-08-06）：IPC の Template Type は入力を 21 個と定義していたが、センサーのコードが渡すのは 20 個だった。試験と初期の配布では 21 番目がワイルドカードだったので表に出なかった。7 月 19 日の Template Instance が 21 番目にワイルドカードでない条件を入れ、Content Interpreter が配列の外を読んだ [S67]
- RCA は Rapid Response Content を「configuration data」であり、コードでもカーネルドライバーでもないと書く。検証役（Content Validator）は 21 個を前提に通した [S67]
- 所見 6：Template Instance は段階的に配るべきだった。対策は、カナリアを通ったものを順に広い輪へ進め、各段で様子を見る時間を置くこと。顧客が、いつどこへ配るかを選べるようにすること [S67]
- 示すこと：データ（設定・検出の内容）の配布は、コードの配布と同じ安全策（検証・段階的な配布・巻き戻し）が要る。型（21 個）と実体（20 個）の食い違いは、Part 7 のスキーマの契約と同じ問題

## 5. 権威の推奨と位置づけ（規範か任意か）

| 推奨 | 出どころ | 位置づけ |
| --- | --- | --- |
| 依存先が傷んでも、していたことを続けられるように作る（静的な安定性）。データプレーンは、制御プレーンが止まっても手元の情報で動き続ける。復旧の経路を制御プレーンに依存させず、容量は先に確保しておく | AWS Builders' Library「Static stability using Availability Zones」（Mike Furr、2019-12-05）[S69] | 事業者の実践の紹介。任意 |
| 制御プレーンは複雑で依存が多く、データプレーンより広い障害が起きやすい。データプレーンへの依存のほうが可用性は高い | AWS Fault Isolation Boundaries [S71] | 事業者の白書。任意 |
| フォールバック（別の仕組みで同じ結果を得る）は避ける。試しにくく、それ自体が失敗し、障害を広げ、潜在的な欠陥が長く残る。代わりに、主経路を信頼できるものにする、呼び出し側に誤りを返す、要るデータを先に押し込んでおく、フォールバックをフェイルオーバーに変えて常に両方を動かす | AWS Builders' Library「Avoiding fallback in distributed systems」（Jacob Gabrielson、2019-12-05）[S70] | 同上 |
| 同論考の例：IAM のロールの認証情報は、取得に失敗したときの代替を作らず、先に各インスタンスへ配っておく。認証情報は何時間も有効なので、配布が少し止まっても動き続ける | 同上 [S70] | 同上 |
| 同論考の例（2001 年）：キャッシュが落ちたら DB を直接引く作りにしていたところ、キャッシュが同時に落ち、全サーバーが DB に殺到してサイト全体が止まった | 同上 [S70] | 同上 |
| セルベース：作業負荷を分割キーで独立したセルに分け、薄い経路選択の層で振り分ける。セルは状態を共有しない。悪い更新や毒入りの要求の影響を 1 つのセルに閉じ込める | AWS Well-Architected「Reducing the Scope of Impact with Cell-Based Architecture」[S72] | 任意 |
| 段階的な配布：1 台（全要求の 10% 以下）→ 小さい波 → 大きい波。各段で待ち時間を置き、警告で自動的に戻す。機能フラグなどの設定も、コードと同じ安全策の専用パイプラインで配る | AWS Builders' Library「Automating safe, hands-off deployments」（Clare Liguori、2020-06-18）[S73] | 事業者の実践。任意 |
| 周期的なパイプラインは、育つと締め切り落ち・資源の枯渇・止まった塊で壊れる。一斉の起動（thundering herd）と、複数のパイプラインの負荷の重なり（Moiré）に注意。連続処理（Workflow）では、設定のタスクを障壁にする、リース、一意な名前の出力ファイル、サーバートークンの 4 つで正しさを守る | Google SRE 本 25 章（Dan Dennison）[S17] | 実践の紹介。任意 |
| パイプラインの SLO は鮮度と正しさ。段ごとではなく全段の合計で測る。**遅れたデータは誤ったデータよりまし**で、入力がそろうまで待つ。冪等な変更と 2 段階の変更（一時的な場所に書いて検証してから適用）。チェックポイント。依存先の最大の障害を想定する | Google SRE Workbook 13 章 [S18] | 同上 |
| ML では、特徴量を推論時に記録して学習に使う（#29）。結合する表の中身は学習と推論の間で変わりうる（#31）。学習と推論でコードを共有する（#32）。ずれを測る（#37）。鮮度の要件を知る（#8）。黙って壊れる失敗に注意（#10）。特徴量の列に所有者と文書を付ける（#11） | Google「Rules of Machine Learning」（Martin Zinkevich）[S50] | 実践の紹介。任意 |
| ML システムの負債：絡み合い、宣言されていない利用者、不安定なデータ依存（対策は信号の版つきの写し）、使い切れていないデータ依存、接着コード、パイプラインの密林 | Sculley ほか「Hidden Technical Debt in Machine Learning Systems」（NIPS 2015）[S49] | 論文 |
| ゼロトラストの 7 原則。PE／PA が到達不能になる危険は残る | NIST SP 800-207 [S33] | NIST SP は米連邦機関向けの指針。民間には任意 |
| トークンは短命に。方針のキャッシュはアクセスサーバーが使えないときだけ、期限つきで | NIST SP 800-204 [S35] | 同上 |
| データプロダクトの考え方を、データ管理の既定の助言にする | Thoughtworks Radar「Data product thinking」（2025-04、Adopt）[S6] | 一社の見解。現在の版には載っていない |
| データメッシュ | Thoughtworks Radar（2022-03、Trial。統合の費用が高く、採用は大組織の一部にとどまる、と注記）[S5] | 同上 |
| プラットフォームを製品として作るチーム | Thoughtworks Radar（2021-10、Adopt。看板だけ替えた「プラットフォームチーム」と、チケット駆動の運営に警告）[S4] | 同上 |
| イベントログのベストプラクティス | ASD ACSC と CISA ほか（日本の NISC・JPCERT/CC を含む）「Best Practices for Event Logging and Threat Detection」（2024-08-21）[S32] | 各国機関の共同の指針。任意。本文 PDF は未確認（案内ページのみ） |

## 6. 設計判断の分かれ目（何を選ぶと何を得て何を失うか。表）

| 分かれ目 | 選択肢 | 得るもの | 失うもの | 根拠 |
| --- | --- | --- | --- | --- |
| 分析データの所有 | 中央のチームが集めて持つ | 道具と技能の集約、統一した見え方 | ドメインの変化に追いつけない。変更が全段に及ぶ | [S7] |
| | ドメインがデータプロダクトとして持つ | 変更が局所で済む。品質の責任が発生源に寄る | 構成の複雑さ、統合の費用、組織の作り直し | [S8][S9][S5] |
| ETL の起動 | 周期的なバッチ | 単純 | 育つと締め切り落ち、一斉起動、監視の空白 | [S17] |
| | 連続処理 | 遅延が小さく、負荷が平ら | 仕組みが要る | [S17] |
| テレメトリの中継 | アプリから直接バックエンドへ | 部品が少ない | バックエンドを替えるとアプリに手が入る。再試行と絞り込みを各アプリが持つ | [S22] |
| | Collector を挟む | 送り先の入れ替えが設定で済む。再試行・バッチ・除去を肩代わり | 運用する部品が増える。キューあふれで失う | [S22][S23] |
| テレメトリの耐久性 | メモリのキュー | 速い、単純 | クラッシュで失う | [S23] |
| | WAL／Kafka | 再起動と下流の停止をまたぐ | ディスクと運用、Kafka 自体の障害 | [S23] |
| サンプリング | 先頭 | 安く、どこでも動く | エラーのトレースを必ず残せない | [S24] |
| | 末尾 | エラーや遅い要求を選んで残す | 状態を持つ大きな仕組み、ベンダー固有になりがち | [S24] |
| トークンの検証 | 手元で署名を検証（JWT） | 認証基盤に毎回問い合わせない。基盤が止まっても有効期限までは検証できる | 失効が効かない窓。主張は発行時点の写し | [S37][S35] |
| | 都度の問い合わせ（introspection） | 失効がすぐ効く | 認証基盤が全要求の同期の依存先になる。キャッシュすると失効の窓が戻る | [S36] |
| 認可の判断 | 方針を各サービスへ配って手元で判断（OPA） | 判断が速く、配布元が止まっても直近の方針で動く | 結果整合。配布の遅れの間は古い方針 | [S39] |
| | 中央の関係データに問い合わせ（Zanzibar 型） | 一貫した判断、細かい共有 | 中央が同期の依存先。整合性トークンの扱いが要る | [S43] |
| 認証基盤の障害時 | 拒否（フェイルクローズ） | 古い情報で通さない | 認証に依存する全体が止まる | [S44][S42] |
| | 開始時の情報で通す | 既存の利用は続く | その間の所属・ロールの変更が反映されない | [S48] |
| 鍵のローテーション | 鍵素材だけ替える | 利用側の変更なし。止めない | 既存のデータは古い鍵素材のまま。漏えいの対処にならない | [S59] |
| | 再暗号化まで行う | 古い鍵を捨てられる | 全データの読み書き。エンベロープなら DEK の包み直しで済む（設計上の推論） | [S61][S60] |
| LLM への接続 | 各サービスが直接 | 部品が少ない、遅延が小さい | 再試行・流量・費用の配賦・切り替えを各サービスが持つ | [S55] |
| | ゲートウェイを挟む | モデルや提供元の入れ替え、流量と費用の統制、横断の記録 | 単一障害点、遅延、機微なデータが通る点が増える | [S55] |
| 設定・検出内容の配布 | 一斉 | 速い（脅威への対応） | 誤りが全体に同時に届く | [S67] |
| | 段階的 | 誤りを小さい範囲で止める | 行き渡るまでの時間 | [S67][S73] |
| 依存先が落ちたとき | 別の仕組みへフォールバック | うまくいけば続く | 試されていない経路が障害を広げる | [S70][S28] |
| | 先に配っておく／誤りを返す | 予測できるふるまい | 鮮度、または一部の機能 | [S70][S69] |

### 6.1 Zanzibar から読む「認可データの整合性」

- Zanzibar（USENIX ATC 2019）は、認可を「関係のタプル」というデータとして全社で 1 つの仕組みに持つ。2 兆を超える ACL、毎秒数百万の検査、95 パーセンタイルで 10 ミリ秒未満、3 年間で 99.999% を超える可用性と報告する [S43]
- 「new enemy」問題（§2.2）：ACL の更新の順序を守らない、または古い ACL を新しい内容に当てると、外したはずの人に見えてしまう。防ぐには、ACL と内容の更新の因果の順序を守る必要がある [S43]
- zookie（§2.2、§2.4）：内容の版ごとに、その時点の全体の時刻を符号化した不透明なトークンをクライアントが保存し、後の検査で送る。検査は zookie より新しいスナップショットで評価される。zookie が無い検査は既定の古さ（複製済みのデータ）で速く返す。つまり**鮮度を要求ごとに指定する契約**になっている [S43]
- Watch API（§2.4.3）でタプルの変更を順に流し、深い入れ子のグループを扱う Leopard 索引（§3.2.4）はそこから作る派生データ。認可の仕組みの中でも「正本＋変更の流れ＋派生の索引」の形を取る [S43]

## 7. 設計レビューで問うこと（問い｜なぜ問うか｜危ない兆候）

| # | 問い | なぜ問うか | 危ない兆候 |
| --- | --- | --- | --- |
| 1 | この基盤が持つデータのうち、ここにしか無いもの（正本）は何か。作り直せるものは何から、何時間で作り直せるか | 正本と派生で、守り方と障害時のふるまいが変わる | 「全部大事」で区別が無い。作り直しの手順を試したことが無い |
| 2 | データプロダクト（表・トピック・索引）ごとに、所有するチームの名前が書かれているか | 中央のチームがドメインの知識なしに持つと変化に追いつけない [S7] | 所有者が「データ基盤チーム」だけ |
| 3 | 利用側の要求の経路で、この基盤に同期で問い合わせている箇所はどこか | 同期の依存が、基盤の停止を全体の停止に変える [S44][S46] | 全要求で認証基盤・方針・秘密情報を引く |
| 4 | 基盤に届かないとき、利用側は手元の何で、いつまで動き続けられるか | 静的な安定性 [S69] | キャッシュの期限が数分。期限が切れた後の動作が決まっていない |
| 5 | フェイルオープンとフェイルクローズを、基盤ごと・操作ごとに決めて文書にしたか | 決めていないと、障害のときに実装の偶然で決まる [S28][S42][S48] | 「たぶん落ちる」「たぶん通る」 |
| 6 | 障害時だけ通る経路（フォールバック、フェイルオープン）を、今の規模で試したのはいつか | めったに通らない経路は、育った後に壊れている [S28][S70] | 作ったときから試していない |
| 7 | 署名鍵を替えたとき、検証側のキャッシュは何をきっかけに、いつ更新されるか。退役した鍵はいつまで公開するか | 利用側のキャッシュの更新の速さはばらばら [S47][S38] | `jwks_uri` を起動時に 1 回だけ取る。知らない `kid` で取り直さない |
| 8 | トークンの有効期限と、失効が効くまでの時間はいくつか。それは業務が許せる長さか | 手元の検証は失効の窓と引き換え [S35][S36] | 有効期限が 1 日以上で、失効の手段が無い |
| 9 | 権限を外した直後の操作で、古い権限が使われないことを、どう保証するか | new enemy 問題 [S43] | 認可のキャッシュに鮮度の指定が無い |
| 10 | テレメトリを失ってよい条件と、失った件数の数え方は決まっているか。監査ログは別の経路か | OTLP は捨てる場面を定め、数えることを求める [S21][S23] | 監査の記録と診断のログが同じ「失ってよい」経路にある |
| 11 | 監視・警告・連絡の道具は、本番と同じネットワーク・認証・基盤に依存していないか | 同じ障害で道具が使えなくなる [S29][S44] | ダッシュボードの認証が本番の認証基盤だけ |
| 12 | メトリクスのラベルに、上限の無い値（ユーザー ID など）が入っていないか | 時系列の数が費用を決める [S27] | 費用の急増を請求で知る |
| 13 | ETL のタスクは、同じ入力で 2 回流しても結果が同じか。「最新」ではなく決まった範囲を読むか | 再実行と埋め戻しの前提 [S19][S18] | INSERT だけ。now() で範囲を決める |
| 14 | 上流のスキーマが変わったとき、取り込みは止まるか、黙って落とすか、通すか | 黙って壊れる失敗は気づくのが遅い [S50] | 型の合わない行を黙って捨てる |
| 15 | パイプラインの鮮度の SLO は、全段の合計で測っているか。遅れたとき、古い結果を出すか、待つか | 遅れは誤りよりまし [S18] | 段ごとの成功だけを見ている |
| 16 | 特徴量は学習と推論で同じ定義・同じコードか。学習データは時点の正しい値で作っているか | 学習と推論のずれ、未来の値の漏れ [S50][S52] | 学習は DWH の SQL、推論はアプリの別実装 |
| 17 | ベクトル索引は、どの埋め込みモデルのどの版で作ったかを記録しているか。モデルを替えるとき、全件の作り直しの時間と費用は見積もったか | 索引は埋め込みモデルに結びついた派生データ [S56] | 索引にモデルの名前が無い。元の文書を保管していない |
| 18 | 推論の入力・出力・モデルの版・使った特徴量を、あとで突き合わせられる形で残しているか。そこに入る個人情報の扱いは | 再現と監査、学習データへの還流 [S50][S51]。ゲートウェイには生の要求と応答が通る [S55] | 予測を記録していない。プロンプトを無制限に保存している |
| 19 | 鍵のローテーションで、既存のデータは新しい鍵で暗号化し直されるか。漏えいが疑われるときの手順は別にあるか | ローテーションは再暗号化しない [S59][S61] | 「毎年ローテーションしているので安全」 |
| 20 | 監査ログは、書いた本人（特権を持つ運用者を含む）が消したり変えたりしたら分かるか | 完全性の検証 [S62][S30] | 監査ログが、監査される側と同じ権限で消せる |
| 21 | 方針・設定・検出の内容など「データとして配るもの」は、検証・段階的な配布・巻き戻しを持つか | 設定はコードと同じ破壊力を持つ [S67][S73] | 設定の変更だけ審査も段階も無い |
| 22 | 基盤を入れ替えるとき、利用側が握っているのは標準の口（OTLP、OIDC／JWKS、SQL＋表の仕様、OpenLineage）か、製品固有の口か | 契約が標準なら裏を替えられる [S14][S21][S41] | 利用側のコードに製品固有の SDK が散らばる |

## 8. ケーススタディで測れること・測れないこと

測れること（題材 C を中心に、既存の構成で）：

- ログ・分析を行指向（PostgreSQL）／列指向（ClickHouse）／ファイル（DuckDB＋Parquet）で持ったときの容量・取り込み時間・問い合わせ時間（同一環境内の相対比較）
- 取り込み時スキーマと読み出し時スキーマで、項目が揺れたとき（型の変更、項目の追加・欠落）の失敗の出方：止まる／黙って落とす／通す（問い 14）
- ログの経路で、下流を止めたとき（Toxiproxy）に失う件数。メモリのバッファ／ログ（Redpanda）経由で比べ、送った連番と届いた連番の差で数える（問い 10。[S23] の「失う場面」の再現）
- カーディナリティ：ラベルの種類を増やしたときの容量と問い合わせ時間の増え方（ClickHouse での相対比較）
- ETL の冪等：同じ範囲を 2 回流したときの重複の件数（INSERT と UPSERT／分割の入れ替えで比べる。問い 13）
- 派生データの作り直し：ログから分析の表を作り直したときの一致率と所要時間（題材 B と共通）

測れないこと（実機にしない。Part 13 では公式文書と事後報告に基づく、と明記する）：

- 認証基盤：JWKS のキャッシュと鍵のローテーション、認証基盤の停止時のふるまい、認可の整合性（new enemy）。実機を組まない
- AI 基盤：特徴量の時点の正しさ、学習と推論のずれ、ベクトル索引の作り直しの費用
- セキュリティ基盤：KMS の停止、再暗号化の所要時間、監査ログの完全性の検証
- 可用性ゾーンやリージョンをまたぐ静的な安定性、セルベース（単一ホストのため）
- クラウドの製品の既定値（文書の記述のみ。未検証）

## 9. 未確定・要確認

- CNCF Platforms White Paper：v1 の完成は 2023-03（リポジトリの README で確認）。Web ページには日付の表示が無い。README のあるリポジトリは 2025-09-09 にアーカイブされており、その後の改訂の有無は確認できていない。Maturity Model v1 の公開日もページに表示が無い（記憶では 2023 年後半・要確認）
- OpenTelemetry のステータスページには日付と仕様の版の表示が無い。閲覧日（2026-11-18）時点の内容として扱う。Events は独立の節が無く、Logs の中で実験的な扱い。Collector の版、生成 AI のセマンティック規約の安定度（別リポジトリへ移転）は未確認
- Cloudflare 2024-11-14 の開始時刻は、事後報告の本文からは読み取れなかった（継続時間は約 3.5 時間）
- Google 2020-12-14 は、ステータスページの見出しの時刻と本文の時系列が食い違う。スライドでは本文の時系列（03:46〜04:33 US/Pacific）を使い、注を付ける
- Azure AD 2021-03-15 の最終の RCA（追跡 ID は記憶では LN01-P8Z・要確認）は一次の場所で確認できなかった。Microsoft Q&A への転記（暫定）だけが根拠。Web Archive は取得できなかった。スライドで使うなら「暫定の報告による」と書くか、TMS9-J_8 と NKRF-1TG を主に使う
- Azure の旧データメッシュのページの本文は未確認（転送）。Azure の MLOps の参照アーキテクチャ（MLOps v2）は未確認。AWS の ML Lens と Data Analytics Lens は冒頭ページとデータメッシュの節だけ確認
- Iceberg のフォーマット版：仕様の目次に v4 があることは確認したが、v3・v4 の各エンジンでの対応状況は未確認
- DataHub の保管の構成（関係 DB が正本、検索とグラフの索引が派生）は、構成ページからは確認できなかった（記憶・要確認）
- Cedar の評価の規則（既定で拒否、forbid が permit に勝つ）は、確認したページに無い（記憶・要確認）。Cedar の CNCF での位置づけも未確認
- Vault Agent がサーバーに届かないときにキャッシュから返すかは、確認したページに記述が無い
- 監査ログを書けないときに業務の操作を止めるべきか（フェイルクローズ）について、明示する一次資料は見つからなかった。SP 800-92 の本文は目次と一部の節だけ確認
- LLM ゲートウェイの障害時のふるまい（別のモデルへの切り替え、AI を使わない経路）を定める標準は見つからなかった。Azure の指針は「単一障害点になりうる」「SLO を危うくするなら入れるな」まで
- 推論の入出力の記録について、NIST AI RMF の本文（機能ごとの記述）は未確認。ページで確かめたのは版・日付・任意であることだけ
- Thoughtworks Radar の LiteLLM／agentgateway の位置は検索結果の要約による（ページ本文は未確認）
- ASD ACSC／CISA のイベントログの指針は案内ページだけ確認（保持期間などの本文は未確認）
- 「分析基盤」を「データ基盤」と分ける一次資料上の定義は見つからなかった。このノートでは、データ基盤＝保管・カタログ・共有の仕組み、分析基盤＝その上の問い合わせ・集計・BI・指標の定義、と分けた（設計上の整理）

## 10. 結論（スライドに書くこと。箇条書き 15〜30 個、各項目に出典の番号）

共通：

1. 共通基盤は、CNCF の定義では「能力の統合された集まり」を内部の利用者に製品として出すもの。ログ・データ・ID と秘密情報・セキュリティはその能力の一覧に入る。任意で組み合わせ可能であることが属性の 1 つ [S1]
2. 基盤の成熟度の指針（CNCF Maturity Model）も Team Topologies も Radar も任意の助言で、規範ではない。看板だけの「プラットフォームチーム」とチケット駆動の運営は、Radar が名指しで警告している [S2][S3][S4]
3. どの基盤も同じ 4 つの問いで見る：正本か派生か・流れと契約・止めずに替える契約・止まったときのふるまい。7 基盤 × 4 問いの表（12 節）を設計レビューの出発点にする
4. 基盤が全体を止めるのは、利用側の要求の経路に同期の依存があるとき。Google 2020-12 は認証、Azure 2024-01 は ARM 経由の RBAC が、キャッシュの期限切れとともに下流を止めた [S44][S46]
5. 対策の軸は静的な安定性：データプレーンは制御プレーンが止まっても手元の情報で動き続ける。要るデータは先に配っておく。Google の障害でも、ネットワークの既存の構成は動き続けた [S69][S71][S44]
6. フォールバックとフェイルオープンは、試されていない経路で障害を広げる。Cloudflare 2024-11 は、ログを失わないためのフェイルオープンが下流を約 40 倍の負荷で止め、55% を失った [S28][S70]
7. 設定・方針・検出の内容は「データ」だが、コードと同じ破壊力を持つ。検証・段階的な配布・巻き戻しを同じ水準で持つ。CrowdStrike 2024-07 は、型（21 個）と実体（20 個）の食い違いを一斉に配った [S67][S73]
8. 監視と連絡の道具を、本番と同じ依存先に載せない。Slack 2021-01 と Google 2020-12 は、障害で調査と告知の道具も失った [S29][S44]

データ基盤・分析基盤：

9. 分析データは業務データの派生。所有はドメイン、基盤チームが持つのは仕組み。パイプラインはドメインの内部実装で、契約はデータプロダクトの出口（発見できる・アドレスで指せる・信頼できる・自己記述的・相互運用できる・安全）[S7][S8]
10. データメッシュは組織の作り直しを伴い、構成は複雑になる。AWS は向く条件を限定し、Radar は Trial のまま統合の費用を注記した。一方「データプロダクトの考え方」は、メッシュかどうかによらず Adopt [S9][S5][S6]
11. 入れ替えの契約は、表の仕様とカタログの API。Iceberg は表メタデータの原子的な入れ替えで直列化可能な分離を得て、REST カタログがエンジンとカタログの実装を切り離す。カタログは「表の現在」の正本になる [S13][S14]
12. 系譜は、実行側が出すイベント（OpenLineage の Run・Job・Dataset）を正とし、グラフは受け側の派生にする [S12]

ETL 基盤：

13. ETL 基盤が持つ正本は「何を、どの入力で、いつ流したか」の実行の記録だけ。出力は派生で、同じ入力から作り直せることが契約。タスクはトランザクションのように扱い、冪等にし、「最新」ではなく決まった範囲を読む [S19][S18]
14. 鮮度と正しさを全段の合計で測る。遅れは誤りよりまし。周期的なバッチは育つと一斉起動と締め切り落ちで壊れる [S18][S17]

ログ基盤：

15. OpenTelemetry はトレース・メトリクス（SDK は Mixed）・ログが Stable、プロファイルは Development。利用側との契約は OTLP とセマンティック規約で、Collector が送り先の入れ替えの継ぎ目になる [S20][S21][S22][S25]
16. テレメトリは「失いうる」ことが仕様に入っている：OTLP は端から端の保証を範囲外とし、再送の重複を認め、捨てたら数えることを求める。Collector の既定は、メモリのキューと 5 分の再試行 [S21][S23]
17. 失ってよい診断のログと、失ってはならない監査の記録を、同じ経路に載せない（設計上の推論。監査ログの完全性は [S62][S30]）
18. 費用はカーディナリティとサンプリングで決まる。上限の無い値をラベルにしない。末尾サンプリングは状態を持つ仕組みが要る [S27][S24]
19. ログ管理の NIST の現行は SP 800-92（2006）。Rev.1 は 2023-10 の草案のまま [S30][S31]

認証基盤：

20. 認証基盤の正本は ID・資格情報・鍵・方針。トークンは発行時点の写し、検証側の鍵のキャッシュは派生。手元の検証は「基盤が止まっても有効期限までは動く」ことと「失効が効かない窓」の交換 [S37][S36][S35]
21. 鍵の配布は `jwks_uri`＋`kid`。知らない `kid` で取り直し、退役した鍵はしばらく残す。利用側のキャッシュの更新の速さはばらばらなので、鍵の誤った削除は戻した後も長く尾を引く [S38][S47]
22. 認証基盤が落ちたときのふるまいは、選んで書く。既定はフェイルクローズになりやすい（Google は古いデータを拒む設計、Kubernetes の Webhook の既定は Fail）。Entra は「開始時の情報で通す」を既定にし、方針ごとに拒否へ切り替えられる [S44][S42][S48]
23. 方針をデータとして配れば（OPA のバンドル）、配布元が止まっても直近の方針で判断できる。代償は結果整合。権限を外した直後の正しさが要るなら、鮮度を要求ごとに指定する契約（Zanzibar の zookie）が要る [S39][S43]
24. ゼロトラストは、判断の点（PE／PA）への到達不能を自ら脅威に数える。PDP と PEP の間の API は AuthZEN 1.0（2026-01-11 Final）で標準になった [S33][S41]

AI 基盤：

25. 特徴量・埋め込み・ベクトル索引・モデルは、すべてデータとコードから作る派生。正本は学習に使ったデータの版、ラベル、実行の記録。ベクトル索引は 1 つの埋め込みモデルに結びつき、モデルを替えると全件を作り直す [S56][S51][S49]
26. 学習と推論のずれは、同じ特徴量を同じ定義で供給し、推論時に記録し、時点の正しい値で学習データを作ることで防ぐ [S50][S52][S51]
27. LLM ゲートウェイは入れ替えと統制の継ぎ目になるが、単一障害点・遅延・機微なデータが通る点を足す。SLO を危うくするなら入れない、が Azure の指針 [S55]

セキュリティ基盤：

28. 鍵のローテーションは再暗号化ではない。鍵の ID を契約にして利用側を変えずに替えられるが、既存のデータは古い鍵素材のまま。漏えいの対処には、別の再暗号化の手順が要る [S59][S61]
29. エンベロープ暗号化は、データ（DEK で暗号化）と鍵（KEK で包む）を分け、KEK を中央に置く。KMS への依存を「DEK を包む・ほどくとき」に限る構造 [S60]
30. 監査ログは追記だけの正本として扱い、ハッシュの連鎖と署名で、変更・削除・欠落を検出できるようにする。行・列レベルの制御は、所有者や特権ロールが迂回する経路と、サイドチャネルを確かめる [S62][S63][S64]

## 11. 出典（番号｜題名｜発行者｜版・日付｜URL｜確認の深さ）

| 番号 | 題名 | 発行者 | 版・日付 | URL | 確認の深さ |
| --- | --- | --- | --- | --- | --- |
| S1 | CNCF Platforms White Paper | CNCF TAG App Delivery | v1、2023-03 完成（README で確認。リポジトリは 2025-09-09 にアーカイブ） | https://tag-app-delivery.cncf.io/whitepapers/platforms/ ／ https://github.com/cncf/tag-app-delivery/blob/main/platforms-whitepaper/README.md | 本文確認 |
| S2 | Platform Engineering Maturity Model | CNCF TAG App Delivery | v1（日付はページに表示なし） | https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/ | 本文確認 |
| S3 | Key Concepts | Team Topologies | 日付なし（閲覧 2026-11-18） | https://teamtopologies.com/key-concepts | 本文確認 |
| S4 | Platform engineering product teams | Thoughtworks Technology Radar | 2017-03 Assess → 2020-05 Trial → 2021-04・2021-10 Adopt（現在の版には無い） | https://www.thoughtworks.com/radar/techniques/platform-engineering-product-teams | 本文確認 |
| S5 | Data mesh | Thoughtworks Technology Radar | 2019-11 Assess → 2020-10〜2022-03 Trial（現在の版には無い） | https://www.thoughtworks.com/radar/techniques/data-mesh | 本文確認 |
| S6 | Data product thinking | Thoughtworks Technology Radar | 2023-09 Trial → 2025-04 Adopt（現在の版には無い） | https://www.thoughtworks.com/radar/techniques/data-product-thinking | 本文確認 |
| S7 | How to Move Beyond a Monolithic Data Lake to a Distributed Data Mesh | Zhamak Dehghani（martinfowler.com） | 2019-05-20 | https://martinfowler.com/articles/data-monolith-to-mesh.html | 本文確認 |
| S8 | Data Mesh Principles and Logical Architecture | Zhamak Dehghani（martinfowler.com） | 2020-12-03 | https://martinfowler.com/articles/data-mesh-principles.html | 本文確認 |
| S9 | Data Analytics Lens（冒頭、Data mesh の節） | AWS Well-Architected | 2023-12-22 | https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/analytics-lens.html ／ …/analytics-lens/data-mesh.html | 本文確認（2 ページのみ） |
| S10 | Architecture and functions in a data mesh | Google Cloud Architecture Center | 日付は取得できず（閲覧 2026-11-18） | https://docs.cloud.google.com/architecture/data-mesh | 本文確認 |
| S11 | Unified data platform adoption | Microsoft Cloud Adoption Framework | 2026-10-23 | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/data/executive-strategy-unified-data-platform | 本文確認（旧 URL …/cloud-scale-analytics/architectures/what-is-data-mesh からの転送先。旧ページは未確認） |
| S12 | Object Model | OpenLineage | 仕様 1.55.0 | https://openlineage.io/docs/spec/object-model | 本文確認 |
| S13 | Iceberg Table Spec | Apache Iceberg | ライブラリ 1.12.0 時点の文書。フォーマット v1〜v4 | https://iceberg.apache.org/spec/ | 本文確認（抜粋） |
| S14 | REST Catalog Spec ／ Terms | Apache Iceberg | 同上 | https://iceberg.apache.org/rest-catalog-spec/ ／ https://iceberg.apache.org/terms/ | 本文確認（抜粋。OpenAPI の YAML は未確認） |
| S15 | DataHub Architecture Overview | DataHub | 1.8.0 | https://docs.datahub.com/docs/architecture/architecture | 本文確認 |
| S16 | High Level Design | OpenMetadata | 版の表示なし（閲覧 2026-11-18） | https://docs.open-metadata.org/latest/main-concepts/high-level-design | 本文確認 |
| S17 | Site Reliability Engineering 25 章 Data Processing Pipelines | Google（Dan Dennison） | 書籍 2016（Web 版） | https://sre.google/sre-book/data-processing-pipelines/ | 本文確認 |
| S18 | The Site Reliability Workbook 13 章 Data Processing Pipelines | Google（Rita Sodt、Igor Maravić） | 書籍 2018（Web 版） | https://sre.google/workbook/data-processing/ | 本文確認 |
| S19 | Best Practices | Apache Airflow | 3.4.0 | https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html | 本文確認 |
| S20 | Specification Status Summary | OpenTelemetry | 日付・版の表示なし（閲覧 2026-11-18） | https://opentelemetry.io/docs/specs/status/ | 本文確認 |
| S21 | OTLP Specification | OpenTelemetry | 1.11.1 | https://opentelemetry.io/docs/specs/otlp/ | 本文確認 |
| S22 | Collector | OpenTelemetry | 版の表示なし（閲覧 2026-11-18） | https://opentelemetry.io/docs/collector/ | 本文確認 |
| S23 | Collector Resiliency | OpenTelemetry | 同上 | https://opentelemetry.io/docs/collector/resiliency/ | 本文確認 |
| S24 | Sampling | OpenTelemetry | 同上 | https://opentelemetry.io/docs/concepts/sampling/ | 本文確認 |
| S25 | Semantic Conventions ／ Database spans ／ Generative AI（移転の案内） | OpenTelemetry | 1.45.0 | https://opentelemetry.io/docs/specs/semconv/ ／ …/semconv/database/database-spans/ ／ …/semconv/gen-ai/ | 本文確認（移転先の GenAI リポジトリは未確認） |
| S26 | OpenTelemetry Logging | OpenTelemetry | 仕様 v1.62.0 への参照あり | https://opentelemetry.io/docs/specs/otel/logs/ | 本文確認 |
| S27 | Metric and label naming | Prometheus | 日付なし（閲覧 2026-11-18） | https://prometheus.io/docs/practices/naming/ | 本文確認 |
| S28 | Cloudflare incident on November 14, 2024, resulting in lost logs | Cloudflare | 2024-11-26 | https://blog.cloudflare.com/cloudflare-incident-on-november-14-2024-resulting-in-lost-logs/ | 本文確認 |
| S29 | Slack's Outage on January 4th 2021 | Slack Engineering（Laura Nolan） | 2021-02-01（02-03 更新） | https://slack.engineering/slacks-outage-on-january-4th-2021/ | 本文確認 |
| S30 | SP 800-92 Guide to Computer Security Log Management | NIST | Final、2006-09 | https://csrc.nist.gov/pubs/sp/800/92/final | 本文確認（CSRC のページ、PDF は目次と一部の節） |
| S31 | SP 800-92 Rev.1 Cybersecurity Log Management Planning Guide | NIST | 初期公開草案、2023-10-11 | https://csrc.nist.gov/pubs/sp/800/92/r1/ipd | 本文確認（CSRC のページ。草案） |
| S32 | Best Practices for Event Logging and Threat Detection | ASD ACSC、CISA ほか | 2024-08-21 | https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection | 題名のみ（案内ページ） |
| S33 | SP 800-207 Zero Trust Architecture | NIST | Final、2020-08 | https://csrc.nist.gov/pubs/sp/800/207/final ／ https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf | 本文確認（§2.1、§5.2、§5.5） |
| S34 | SP 800-207A A Zero Trust Architecture Model for Access Control in Cloud-Native Applications in Multi-Cloud Environments | NIST | Final、2023-09-13 | https://csrc.nist.gov/pubs/sp/800/207/a/final | 本文確認（CSRC のページの要旨） |
| S35 | SP 800-204 系（204・204A・204B・204C・204D） | NIST | すべて Final。日付は 2.5 節の表 | https://csrc.nist.gov/publications/search?keywords-lg=800-204 ／ https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-204.pdf | 本文確認（一覧、および 204 の §4.1・§4.4・§4.5）。204A〜D は題名のみ |
| S36 | RFC 7662 OAuth 2.0 Token Introspection | IETF | 2015-10、Proposed Standard | https://www.rfc-editor.org/rfc/rfc7662 | 本文確認 |
| S37 | RFC 9068 JWT Profile for OAuth 2.0 Access Tokens | IETF | 2021-10、Proposed Standard | https://www.rfc-editor.org/rfc/rfc9068 | 本文確認 |
| S38 | OpenID Connect Core 1.0 incorporating errata set 2 | OpenID Foundation | Final、2023-12-15 | https://openid.net/specs/openid-connect-core-1_0.html | 本文確認（§10.1.1、§10.2.1） |
| S39 | Bundles | Open Policy Agent | Rego v1 系の文書（閲覧 2026-11-18） | https://www.openpolicyagent.org/docs/management-bundles | 本文確認 |
| S40 | Cedar Policy Language Reference Guide | Cedar（AWS） | 4.6 | https://docs.cedarpolicy.com/ | 本文確認（冒頭ページのみ） |
| S41 | Authorization API 1.0 | OpenID Foundation（AuthZEN WG） | Final、2026-01-11 | https://openid.net/specs/authorization-api-1_0.html | 本文確認（末尾の約 4% は未読） |
| S42 | Dynamic Admission Control | Kubernetes | v1.37 の文書 | https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/ | 本文確認 |
| S43 | Zanzibar: Google's Consistent, Global Authorization System | Pang ほか（USENIX ATC 2019） | 2019 | https://www.usenix.org/system/files/atc19-pang.pdf | 本文確認 |
| S44 | Google Cloud Infrastructure Components Incident #20013 | Google Cloud | 2020-12-14 | https://status.cloud.google.com/incident/zall/20013 | 本文確認 |
| S45 | PIR – Microsoft Entra ID – DNS authentication failures using Seamless SSO and Microsoft Entra Connect Sync（TMS9-J_8） | Microsoft Azure | 2025-02-25 | https://azure.status.microsoft/status/history/?trackingId=TMS9-J_8 | 本文確認 |
| S46 | PIR – Azure Resource Manager – Services impacted by ARM failures（NKRF-1TG） | Microsoft Azure | 2024-01-21 | https://azure.status.microsoft/status/history/?trackingId=NKRF-1TG | 本文確認 |
| S47 | Notification: Authentication errors across multiple Microsoft services（status.azure.com の更新の転記） | Microsoft Q&A（Microsoft の社員による投稿） | 2021-03-15〜16。暫定の分析 | https://learn.microsoft.com/en-us/answers/questions/315440/notification-authentication-errors-across-multiple | 本文確認（転記・暫定。一次の RCA は未確認） |
| S48 | Resilience defaults for Microsoft Entra Conditional Access | Microsoft Learn | 2026-03-24 | https://learn.microsoft.com/en-us/entra/identity/conditional-access/resilience-defaults | 本文確認 |
| S49 | Hidden Technical Debt in Machine Learning Systems | Sculley ほか（NIPS 2015） | 2015 | https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html | 本文確認（要旨と各節の冒頭） |
| S50 | Rules of Machine Learning: Best Practices for ML Engineering | Google（Martin Zinkevich） | 日付は取得できず（閲覧 2026-11-18） | https://developers.google.com/machine-learning/guides/rules-of-ml | 本文確認 |
| S51 | MLOps: Continuous delivery and automation pipelines in machine learning | Google Cloud Architecture Center | 日付は取得できず（閲覧 2026-11-18） | https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning | 本文確認 |
| S52 | Point-in-time joins | Feast | 版の表示なし（閲覧 2026-11-18） | https://docs.feast.dev/getting-started/concepts/point-in-time-joins | 本文確認 |
| S53 | AI Risk Management Framework | NIST | AI RMF 1.0（2023-01-26）、AI 600-1（2024-07-26） | https://www.nist.gov/itl/ai-risk-management-framework | 本文確認（案内ページ。RMF 本文は未確認） |
| S54 | Machine Learning Lens | AWS Well-Architected | 2025-11-19 | https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html | 題名のみ（冒頭ページ） |
| S55 | Access Foundry Models and Other Language Models Through a Gateway | Azure Architecture Center | 2026-04-30 | https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/azure-openai-gateway-guide | 本文確認 |
| S56 | Create a Vector Index | Microsoft Learn（Azure AI Search） | 2026-11-09 | https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-create-index | 本文確認 |
| S57 | pgvector README | pgvector | 0.8.7 | https://github.com/pgvector/pgvector | 本文確認 |
| S58 | LiteLLM（Platforms） | Thoughtworks Technology Radar | 2026-11 の版で Trial（検索結果の要約） | https://www.thoughtworks.com/en-us/radar/platforms/litellm | 未確認（検索結果の要約のみ） |
| S59 | Rotate AWS KMS keys | AWS KMS Developer Guide | 日付なし（閲覧 2026-11-18） | https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html | 本文確認 |
| S60 | Envelope encryption | Google Cloud KMS | 日付は取得できず（閲覧 2026-11-18） | https://docs.cloud.google.com/kms/docs/envelope-encryption | 本文確認 |
| S61 | Re-encrypt data | Google Cloud KMS | 同上 | https://docs.cloud.google.com/kms/docs/re-encrypt-data | 本文確認 |
| S62 | Validating CloudTrail log file integrity | AWS CloudTrail User Guide | 日付なし（閲覧 2026-11-18） | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html | 本文確認 |
| S63 | Row Security Policies | PostgreSQL | 18 | https://www.postgresql.org/docs/18/ddl-rowsecurity.html | 本文確認 |
| S64 | Introduction to BigQuery row-level security | Google Cloud | 日付は取得できず（閲覧 2026-11-18） | https://docs.cloud.google.com/bigquery/docs/row-level-security-intro | 本文確認 |
| S65 | Vault Agent caching | HashiCorp Vault | v2.x の文書 | https://developer.hashicorp.com/vault/docs/agent-and-proxy/agent/caching | 本文確認 |
| S66 | SP 800-57 Part 1 Rev.5 Recommendation for Key Management: Part 1 – General | NIST | Final、2020-05 | https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final | 本文確認（CSRC のページのみ） |
| S67 | External Technical Root Cause Analysis — Channel File 291 | CrowdStrike | 2024-08-06 | https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf | 本文確認 |
| S68 | Preliminary Post Incident Review: Content Configuration Update Impacting the Falcon Sensor and the Windows Operating System | CrowdStrike | 2024-07-24（07-25 更新） | https://www.crowdstrike.com/en-us/blog/falcon-content-update-preliminary-post-incident-report/ | 本文確認 |
| S69 | Static stability using Availability Zones | AWS Builders' Library（Mike Furr） | 2019-12-05 | https://builder.aws.com/content/3K9SiqiJ369TGkkGzqPM95BuYWI/static-stability-using-availability-zones（旧 URL aws.amazon.com/builders-library/… から転送） | 本文確認 |
| S70 | Avoiding fallback in distributed systems | AWS Builders' Library（Jacob Gabrielson） | 2019-12-05 | https://builder.aws.com/content/3EuS9Sakq7L3VLQIF3qzfMfke1Y/avoiding-fallback-in-distributed-systems（同上） | 本文確認 |
| S71 | AWS Fault Isolation Boundaries：Control planes and data planes | AWS Whitepaper | 日付は取得できず（閲覧 2026-11-18） | https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/control-planes-and-data-planes.html | 本文確認 |
| S72 | Reducing the Scope of Impact with Cell-Based Architecture：What is a cell-based architecture? | AWS Well-Architected | 日付は取得できず（閲覧 2026-11-18） | https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/what-is-a-cell-based-architecture.html | 本文確認 |
| S73 | Automating safe, hands-off deployments | AWS Builders' Library（Clare Liguori） | 2020-06-18 | https://builder.aws.com/content/3ErTKQOTKc5NIw031UePBPxTQ6I/automating-safe-hands-off-deployments（同上） | 本文確認 |

## 12. 7 基盤 × 4 つの問い（全セル。根拠の番号つき）

「推論」は一次資料の記述を組み合わせた設計上の整理。「一次資料なし（一般論）」は、その点を直接述べる一次資料を見つけられなかったセルで、理由を添える。

| 基盤 | (1) 正本か派生か・所有者 | (2) 流れ（同期か非同期か）と契約 | (3) 止めずに変える・入れ替える契約 | (4) 止まったときの利用側のふるまい |
| --- | --- | --- | --- | --- |
| データ基盤 | 中身の大半は業務サービスの正本から作る**派生**（分析用の写し）。発生源のドメインが出す不変のイベントが元。所有はドメイン（データプロダクトの所有者）、基盤チームが持つのは仕組み [S7][S8]。例外として、カタログは「表の現在のメタデータ」の**正本** [S13][S14] | 非同期で流れ込む（イベント、定期のスナップショット）。出口は表・ビュー・ファイル・トピック・ストリーム [S7][S10]。契約はデータプロダクトの 6 つの性質と、品質の SLO [S7][S8] | 表の仕様（Iceberg：スキーマの進化、原子的なコミット）とカタログの API（REST カタログ）。エンジンとカタログの実装を別々に替えられる [S13][S14]。系譜は OpenLineage のイベント [S12] | 業務の要求の経路に置かない（分析の面と業務の面は別 [S8]）。止まれば分析は古くなるだけで済むようにする。カタログが止まるとコミットはできない（原子的な入れ替えが要るため [S13]。読み取りへの影響は**一次資料なし（一般論）**：製品ごとのキャッシュの挙動を確かめていない） |
| ETL 基盤 | 出力は**派生**。ETL 基盤だけが持つ正本は、実行の記録（何を・どの入力で・いつ）と設定。SRE 本の Workflow では Task Master が状態を同期で記録する [S17]。データの所有は上流と下流のドメイン（パイプラインはドメインの内部実装 [S7]） | 非同期（バッチまたは連続処理）。契約は、読む範囲（決まった分割）、冪等な出力、鮮度と正しさの SLO [S19][S18] | タスクの冪等と 2 段階の変更（別の場所に書いて検証してから適用）[S18]。設定の変更を障壁にして、古い設定の仕掛かりを無効にする [S17]。系譜を OpenLineage で出しておけば、実行する製品を替えても追える [S12] | 下流は古いデータで動き続ける。**遅れは誤りよりまし**なので、入力がそろうまで待つ [S18]。復旧時の一斉起動に注意 [S17]。依存先の最大の障害を想定しておく [S18] |
| ログ基盤 | テレメトリ（診断のログ・メトリクス・トレース）は、起きたことの観測で、失いうる前提の**派生的な記録** [S21]。監査ログは「誰が何をしたか」の**正本**として別扱い [S62][S30]。意味（属性の名前）の所有は出す側のサービス、経路の所有は基盤 [S25]（区別そのものは推論） | 非同期の押し出し（OTLP）。保証は 1 区間だけ、重複ありうる、捨てたら数える [S21]。契約は OTLP＋セマンティック規約＋LogRecord のモデル（TraceId・SpanId・Resource）[S25][S26] | Collector を継ぎ目にして送り先を替える [S22]。既存のロギングはブリッジで載せ、アプリのログの書き方は変えない [S26]。安定度が Stable のシグナルと規約だけを契約にする [S20][S25] | アプリは止めない：キューが満ちたら捨てて数える（テレメトリはフェイルオープン）[S21][S23]。ただし、フェイルオープンが下流を過負荷にしないか試す [S28]。監視の道具は本番と別の依存先に [S29]。監査ログを書けないときに業務を止めるかは**一次資料なし（一般論）**：明示する標準を見つけられず、法令と業務の要件で決める |
| 認証基盤 | ID・資格情報・署名鍵・方針・関係データは**正本** [S44][S43]。トークンは発行時点の**写し**、検証側の JWKS のキャッシュと配られた方針は**派生** [S37][S38][S39]。所有は認証基盤のチーム。細かい認可の方針は各サービスの近く [S35] | 発行（ログイン・更新）は同期。検証は手元（JWT）か都度の問い合わせ [S37][S36]。鍵は `jwks_uri` から引いてキャッシュ [S38]。方針はバンドルで結果整合に配る [S39]。契約は OIDC／OAuth、主張の意味、有効期限 | 鍵は `kid` を足してから切り替え、退役した鍵をしばらく残す [S38]。PDP は AuthZEN の API の裏で替えられる [S41]。認可データの鮮度は zookie のように要求で指定する [S43] | 既存のトークンは有効期限まで手元で検証できる（静的な安定性 [S69] の当てはめ。推論）。新規のログインは失敗する。判断の点に届かないときは、**既定は拒否**になりやすい [S44][S42]。通すなら、何を根拠に・いつまでかを決めて書く [S48][S35]。鍵の誤りは利用側のキャッシュのせいで長引く [S47] |
| AI 基盤 | 特徴量・埋め込み・ベクトル索引・モデルは**派生** [S56][S51]。正本は、学習に使ったデータの版とラベル（データ基盤・ドメインの所有）、実行の記録（ML メタデータ）[S51]、推論の入出力の記録 [S50]。特徴量の列には所有者を付ける [S50] | 学習は非同期（データ基盤から、時点の正しい結合で）[S52]。推論は同期。推論時の特徴量を記録して学習へ戻す [S50]。契約は、特徴量の定義、モデルの版と入出力の形、埋め込みモデルと次元数 [S56] | 不安定な入力の信号は版つきの写しで固定する [S49]。モデルの切り替えは検証とカナリアを通す [S51]。埋め込みモデルを替えるときは索引を全件作り直す（並行して作り、切り替える。推論。[S56]）。LLM の提供元の切り替えはゲートウェイで [S55] | ゲートウェイは単一障害点になりうる [S55]。別のモデルへの切り替えは、常に両方を動かすフェイルオーバーにする（フォールバックにしない [S70] の当てはめ。推論）。AI を使わない経路に落とすかどうかは**一次資料なし（一般論）**：定める標準を見つけられず、機能ごとに決める。特徴量が古くなる失敗は黙って進むので監視する [S50] |
| 分析基盤 | 集計・マート・ダッシュボードは、データ基盤の上の**派生**で、作り直せる [S7]。指標の定義（何をどう数えるか）は分析側が所有する正本（**一次資料なし（一般論）**：定義の所有を直接述べる資料を確かめていない。データプロダクトの「自己記述的」[S7] からの推論） | 非同期（バッチまたはストリーム）。消費は SQL・ビュー・BI [S10]。契約はデータプロダクトの出口の形と鮮度の SLO [S8][S18] | 利用側には実表ではなくビュー（承認済みビュー）を見せ、裏の表を替える [S10]。行・列レベルの制御は方針として表に付け、問い合わせを変えない [S63][S64] | 業務の面と分けておけば、止まっても業務は続く [S8]。分析の結果を業務に戻して使っている場合は、古い結果で動き続けてよいかを決める（[S18] の「遅れは誤りよりまし」の当てはめ。推論）。その構成（逆向きの連携）の障害時を直接述べる資料は**一次資料なし（一般論）** |
| セキュリティ基盤 | KEK・秘密情報・監査の記録は**正本** [S60][S62]。SIEM の中身はログから作る**派生**（推論。[S30] の集中管理の構成から）。検出の内容・方針は、基盤が配る設定データ [S67]。所有はセキュリティのチーム。データの分類はデータの所有者（**一次資料なし（一般論）**：分類の所有を直接述べる資料を確かめていない） | KMS は DEK を包む・ほどくときだけ同期で呼ぶ [S60]。秘密情報は引いてキャッシュ（リースと更新）[S65]。監査ログは非同期の追記＋ダイジェストの連鎖 [S62]。検出の内容は基盤から端末へ押し出す [S67]。契約は鍵の ID、暗号文の形、ログの形式 | 鍵の ID を変えずに鍵素材を替える（利用側は無変更）。再暗号化は別の手順 [S59][S61]。検出の内容と設定は、検証・段階的な配布・巻き戻し。利用側が配布の時期を選べるようにする [S67][S73] | KMS に届かなければ、新しい DEK はほどけない＝暗号の性質上フェイルクローズ（推論。[S60]）。認可の Webhook は既定で拒否 [S42]。秘密情報は、失効を見逃す危険と引き換えにキャッシュで続ける [S65]。セキュリティ製品自身の更新が全体を止めうるので、影響範囲を輪で区切る [S67][S72] |
