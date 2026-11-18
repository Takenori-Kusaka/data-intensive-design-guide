# verify_p13：Part 13 前半（deck/p13.js、扉＋10 枚）の事実の確かめ直し

確認日：2026-11-18。書籍は `research/books/text/<ISBN>.txt` の該当ページを本文で確認。Web は URL を開いて確認（取得ツールの要約経由。引用文は英語の原文を突き合わせた）。

| スライドの題 | 事実 | 出典（URL か書籍ページ） | 確かめ方 | 結果 |
| --- | --- | --- | --- | --- |
| 共通基盤は内部の利用者に出す製品。作る前に問う | CNCF の定義「integrated collection of capabilities defined and presented according to the needs of the platform's users」 | https://tag-app-delivery.cncf.io/whitepapers/platforms/ | 本文確認 | 一致 |
| 同上 | 属性は 7 つ（Platform as a product、Self-service、Optional and composable ほか）。能力の一覧は 13 領域で、Observability・Data services・Identity and secret management・Security services を含み、AI・分析に当たる項目は無い | 同上 | 本文確認 | 一致 |
| 同上 | 外部のサービスにできるだけ頼り、ほかで得られない能力だけを作る | 同上 | 本文確認 | 一致 |
| 同上 | 版と日付：ページに日付の表示なし。PDF の名前が v1.0。ノート 08 の「2023-03 完成」は確かめていない | 同上 | 本文確認 | 修正した（「2023-03」は載せず「v1.0（2026-11 確認）」とした） |
| 同上 | 『プラットフォームエンジニアリング』の定義（API・ツール・サービス・知識・サポートを社内プロダクトとして構成。Wiki と「クラウド」は含めない） | 0141-3 p.4（1.1 節） | 書籍本文で確認 | 一致（スライドは要約。引用符つきの転記なし） |
| 同上 | 代替手段を尽くしたときだけ作る。同じ問題に 3 世代の解を運用し、消す計画が無いのは製品の失敗 | 0141-3 p.104（5.2.1 節） | 書籍本文で確認 | 一致 |
| 同上 | 変化予算：顧客が一度に吸収できる変化には限界がある | 0141-3 p.122（5.4.2 節） | 書籍本文で確認 | 一致 |
| どの基盤も、同じ 4 つの問いで設計する | 記録のシステムと導出データの定義 | 0180-2 p.10–11 | 書籍本文で確認 | 一致 |
| 同上 | 組織全体のデータフローを 1 つの巨大なデータベースと見る。ETL は DB のサブシステムのようにふるまう | 0180-2 p.544（13.2.1.2） | 書籍本文で確認 | 一致（ノートのみで使用） |
| 同上 | 4 つの問いそのもの | 一次資料なし | — | `L.note(s,'add')` で「本ガイドの整理」と明示 |
| 7 基盤 × 4 つの問い | データ・ETL・ログ・分析の行 | 下の各行 | — | 各基盤のスライドと同じ内容に絞った |
| 同上 | 認証・AI・セキュリティの行 | ノート 08 の 12 節 | ノートのみ（書き手は原典を確かめていない） | p13b.js の確かめ直しに依存。推論を含むセル（既存トークンは期限まで検証できる、索引を並行して作り直す、KMS に届かなければ復号できない）がある。注記に「一次資料を組み合わせた整理を含む」と書いた |
| 同上 | ※の 5 セル（カタログの読み取り、監査ログ、AI なしの経路、指標の定義の所有、逆向きの連携） | 一次資料なし | — | `L.note(s,'add')` で明示 |
| データ基盤の中身は導出。所有はドメインに置く | データプロダクトの定義「消費されることを目的…（中略）」 | 0071-3 p.96 | 書籍本文で確認 | 一致（ノートで使用） |
| 同上 | Dehghani 2019-05-20。失敗の型 3 つ（Centralized and monolithic／Coupled pipeline decomposition／Siloed and hyper-specialized ownership）。パイプラインはドメインの内部実装。出口の性質 6 つ | https://martinfowler.com/articles/data-monolith-to-mesh.html | 本文確認 | 一致 |
| 同上 | 完全連合型が難しい理由（標準への準拠は自発的に起きない、機能の重複、粒度、人材）。全社で一貫した報告の典型的な解はデータをまとめること | 0071-3 p.60–61 | 書籍本文で確認 | 一致 |
| 同上 | 基盤が動かなくなっても動かす必要がある利用側は、複製が合理的 | 0071-3 p.133（4.5.10） | 書籍本文で確認 | 一致 |
| 同上 | 各チームが自分のパイプラインを持てるようになった | 0180-2 p.473 | 書籍本文で確認 | 一致（refs のみ） |
| 同上 | ノート 08 の「AWS は向く条件を限定」「Radar は Trial／Adopt」 | AWS Data Analytics Lens、Thoughtworks Radar | 確かめていない | 載せるのをやめた |
| カタログは表の現在を持つ正。系譜は実行側が出す | 「An atomic swap of one table metadata file for another provides the basis for serializable isolation」。スキーマの進化は add・drop・reorder・rename が安全 | https://iceberg.apache.org/spec/ | 本文確認 | 一致 |
| 同上 | 表形式は v1〜v4 が載る。v4 は「under active development and has not been formally adopted」 | 同上 | 本文確認 | 修正した（ノート 08 は v4 を並列に書いていた。「策定中」と明記） |
| 同上 | REST カタログ：OpenAPI の共通 API。1 つのクライアント実装でどのカタログにも。変更ベースのコミットでサーバー側が衝突の解消と再試行 | https://iceberg.apache.org/rest-catalog-spec/ | 本文確認 | 一致 |
| 同上 | REST カタログは Iceberg 0.14.0 で導入 | 同上 | ページに記載なし | 載せるのをやめた |
| 同上 | OpenLineage 1.55.0：Job・Run（runId はクライアント生成の UUID、UUIDv7 推奨）・Dataset。RunEvent は「emitted at runtime」 | https://openlineage.io/docs/spec/object-model | 本文確認 | 一致 |
| 同上 | ドメインの責務：メタデータの提供、スキーマ登録、リネージの提供 | 0071-3 p.52 | 書籍本文で確認 | 一致 |
| 同上 | メタデータの 4 分類、リネージの定義 | 0071-3 p.255–256、p.266 | 書籍本文で確認 | 一致（refs とノート） |
| 同上 | カタログが止まるとコミットできない／読み取りへの影響 | 一次資料なし | — | 前者は「仕様からの推論」、後者は「確かめられていない」と `add` で明示 |
| 同上 | OpenMetadata・DataHub の保管と索引の構成 | — | 確かめていない | 載せるのをやめた |
| 取り込みは、スキーマが揺れたときの動きを先に決める | 品質がしきい値を下回ればデータを保留し、データオーナーに確認。問題はソースで直す | 0071-3 p.116（4.4.3） | 書籍本文で確認 | 一致 |
| 同上 | ETL と ELT をまとめて ETL と呼ぶ。入力に項目が欠けていれば調べて直して再実行できる | 0180-2 p.472–473 | 書籍本文で確認 | 一致 |
| 同上 | パイプラインの所有はドメインチーム | 0071-3 p.52 | 書籍本文で確認 | 一致 |
| 同上 | 4 つの動きの得失と「向く場面」、「ETL 基盤の正は実行の記録と設定」 | 一次資料なし | — | `add` とノートで「本ガイドの整理」と明示 |
| 同上 | ノート 08 の「黙って壊れる失敗」（Rules of ML #10） | — | 確かめていない | 載せるのをやめた |
| 再実行しても同じ結果になるタスクが作り直しの前提 | Airflow 3.4.0 Best Practices：タスクをトランザクションと同じに扱う、再実行のたびに同じ結果、INSERT ではなく UPSERT、最新を読まず分割を読む（data_interval_start）、重要な計算に now() を使わない | https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html | 本文確認（版は版選択の表示） | 一致 |
| 同上 | SRE Workbook 13 章：冪等な変更、2 段階の変更（一時的な場所に保存）、利用側が気にするのは全段の合計の SLO | https://sre.google/workbook/data-processing/ | 本文確認 | 一致 |
| 同上 | 「遅れたデータは誤ったデータよりまし」 | 同上 | 本文確認 | 修正した（原文は「Stale data is almost always better than incorrect data」。「古いデータは、ほとんどの場合、誤ったデータよりまし」とした） |
| 同上 | ジョブから本番 DB へ 1 件ずつ直接書くのは悪い方法。ストリームへ出すのがより良い | 0180-2 p.476（11.4.4） | 書籍本文で確認 | 一致 |
| 同上 | SQL のコード例 | 本ガイドの作例 | — | コード内に「本ガイドの例」と明記 |
| ログ基盤の契約は OTLP と規約。安定度はシグナルで違う | Traces：API・SDK・Protocol とも stable。Metrics：stable／mixed／stable。Logs：Bridge API・SDK・Protocol とも stable。Profiles：Protocol が development、API・SDK は記載なし。Baggage：stable／stable／N/A | https://opentelemetry.io/docs/specs/status/ | 本文確認（2026-11-18） | 一致。ページに日付・版の表示が無いことも確認 |
| 同上 | Collector：「Vendor-agnostic way to receive, process and export telemetry data」。サービスの横に置く利点は retries・batching・encryption・sensitive data filtering。安定度は mixed | https://opentelemetry.io/docs/collector/ | 本文確認 | 一致 |
| 同上 | ログ仕様：既存のロギングを受け入れ、ブリッジで載せる | https://opentelemetry.io/docs/specs/otel/logs/ | 本文確認 | 一致 |
| 同上 | セマンティック規約の版は 1.45.0 | https://opentelemetry.io/docs/specs/semconv/ | 本文確認 | 一致。「データベースのスパンは Stable」は確かめておらず、載せていない |
| テレメトリは失いうる前提。監査の記録は経路を分ける | OTLP 1.11.1：保証は 1 組のクライアントとサーバーの間。再試行できないエラーでは MUST drop、件数を数えるのは SHOULD | https://opentelemetry.io/docs/specs/otlp/ | 本文確認 | 一致 |
| 同上 | Collector：キューは「default is often 1000 batches/requests」。満杯で入ってくるデータを捨てる。再試行は既定で 5 分（300 秒）。WAL は専用のメッセージキューほど強くない。Kafka を間に置く構成。失う場面 7 つ | https://opentelemetry.io/docs/collector/resiliency/ | 本文確認 | 一致 |
| 同上 | サンプリング：毎秒 1000 トレース以上が目安の 1 つ。先頭は全体を見て決められない。末尾は状態を持つ仕組みが要る | https://opentelemetry.io/docs/concepts/sampling/ | 本文確認 | 一致 |
| 同上 | ラベルの組み合わせ 1 つが新しい時系列。ユーザー ID など上限の無い値をラベルにしない | https://prometheus.io/docs/practices/naming/ | 本文確認 | 一致 |
| 同上 | 保持：古い分を別の媒体へ移す、TTL の GROUP BY で集約だけ残す（ClickHouse） | https://clickhouse.com/docs/guides/developer/ttl | 本文確認 | 一致（スライドは製品名を出さず一般形で記載） |
| 同上 | Cloudflare 2024-11-14：「roughly 3.5 hours」「about 55% of the logs we normally send to customers were not sent and were lost」。公開 2024-11-26 | https://blog.cloudflare.com/cloudflare-incident-on-november-14-2024-resulting-in-lost-logs/ | 本文確認 | 一致 |
| 同上 | 同：空の設定 → フェイルオープンで全顧客分を送る。5 分未満で戻した。バッファは通常 100 万超、約 40 倍。Buftee が応答しなくなった | 同上 | 本文確認 | 一致。開始時刻は原文に無いので載せていない |
| 同上 | 監査ログを書けないとき業務を止めるか | 一次資料なし | — | `add` で明示し「法務に確認」を添えた |
| 分析基盤は導出。指標の定義だけは所有者を決める | 分析の問い合わせの 2 つの型（事前集計、アドホック） | 0180-2 p.474（11.4.2） | 書籍本文で確認 | 一致 |
| 同上 | セマンティックレイヤーの定義。裏のデータストアを切り離し、構造を変えてもレポートにすぐ影響が及ぶとは限らない。キャッシュ型は少し古くなりうる | 0071-3 p.320–321（11.4.1） | 書籍本文で確認 | 一致 |
| 同上 | 運用レポートは運用システムを直接使う。分析レポートと区別 | 0071-3 p.207 | 書籍本文で確認 | 一致。「分けておけば業務は続く」は本ガイドの読み |
| 同上 | ノート 08 の「承認済みビューを見せて裏の表を替える」（Google Cloud） | https://docs.cloud.google.com/architecture/data-mesh | 本文確認 | 載せるのをやめた（ページにその勧めは無い。根拠を『大規模データ管理 第2版』p.321 に替えた） |
| 同上 | 指標の定義の所有、逆向きの連携の障害時 | 一次資料なし | — | `add` 2 つで明示 |

## 不確かな点

- 一覧表の認証・AI・セキュリティの行はノート 08 に拠る。p13b.js の内容と突き合わせて、言い回しをそろえる必要がある
- OpenTelemetry のステータスページは日付・版の表示が無い。閲覧日の内容として記載
- CNCF Platforms White Paper の完成年月（2023-03）は確かめていない
- Web の確認は取得ツール（要約モデル）経由。数字と引用は原文の英語で返させたが、ページ全体を自分の目で通読したわけではない
- 発表者ノートは 500〜580 字で、目安（250〜450 字）をやや超える
