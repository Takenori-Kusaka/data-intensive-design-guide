# 02 データの所有と流れ（記録の正本と派生データ、サービスごとの DB と共通基盤の境界、二重書き込み・アウトボックス・CDC・ログ中心の統合）

調査日：2026-11-18

## 1. 問い（このノートが答えること。対応する Part）

対応する Part：3（ステップ 2「どのデータを誰が持ち、どれが正本でどれが派生か」）、6（ステップ 4「サービスと基盤の間を、データはどう流れるべきか」）。Part 11・12・13 にも材料を渡す。

1. 「記録の正本（system of record）」と「派生（導出）データ」は、どこで、どう定義されているか
2. サービスごとの DB と共有 DB の得失を、クラウド各社の指針はどう書いているか。どこまでが規範でどこからが任意か
3. 二重書き込み（dual write）は何が問題で、どんな型の不整合が起きるか
4. トランザクショナル・アウトボックスと CDC は、何を保証し、何を保証しないか。ポーリング方式とログ追尾方式は何が違うか
5. Debezium 3.x × PostgreSQL 18 で、設計者が知っておくべき既定値と制限は何か
6. 「ログを 1 本の正にする」という考え方の原典は何で、限界はどこか
7. データの流れの 3 形態（DB 経由・サービス呼び出し・非同期メッセージ）の得失と、分散モノリスの兆候
8. 共通データ基盤への取り込み（ETL・ELT・リバース ETL）を、権威はどう整理しているか
9. 上記に関する一次の事故報告は何があるか（ないものは「ない」と書く）

## 2. 標準・定義（節番号）

このテーマには ISO・IETF などの**公的な標準はない**。「system of record」「dual write」「transactional outbox」「distributed monolith」はいずれも業界の用語で、標準化団体による定義は一次資料に見つからなかった。以下は「どの文書が、どう定義しているか」の記録である。

| 用語 | 定義している文書 | 定義の要点（自分の言葉） | 出典 |
| --- | --- | --- | --- |
| 記録のシステム（system of record）／信頼できる情報源（source of truth） | DDIA 2e 1.1.3（印刷 p.10〜11） | データの正式な版を持つ。新しいデータは最初にここへ書く。各事実は 1 回だけ表す。食い違ったら定義上こちらが正しい | [1] |
| 導出データシステム（derived data system） | 同上 | 別のシステムのデータを変換・処理した結果。失っても元から作り直せる。キャッシュ・索引・マテリアライズドビュー・非正規化した値・学習済みモデルを含む | [1] |
| 「正本か派生か」は製品ではなく使い方で決まる | 同上 | DB は道具で、どちらにもなる。どれがどれから導出されるかを明らかにすることが、構成の見通しをよくする | [1] |
| 単一の情報源（single source of truth） | Azure Architecture Center「Data considerations for microservices」 | 強い整合性が要るときは 1 つのサービスを情報源にして API で出す。ほかのサービスは結果整合のコピーを持ってよいが、それは情報源ではない | [5] |
| 二重書き込み（dual writes） | DDIA 2e 12.2.1（印刷 p.497〜498） | データが変わるたび、アプリのコードが各システムへ個別に書くこと。競合状態と部分的な失敗の 2 つの問題がある | [2] |
| 二重書き込み（dual write operation） | AWS Prescriptive Guidance「Transactional outbox pattern」 | アプリが 2 つの異なるシステムに書くこと。片方の失敗で不整合になりうる | [8] |
| トランザクショナル・アウトボックス | AWS Prescriptive Guidance [8]、Azure Architecture Center [7]、microservices.io [10]（個人サイト）、DDIA 2e 12.2.2（印刷 p.504）[3] | 業務データの更新と、送るべきイベントの記録を、同じ DB の 1 つのトランザクションで行う。別のプロセスがそれを読み出してブローカーへ送る | [3][7][8][10] |
| ログ（log） | Kreps「The Log」（2013-12-16） | 追記のみで、全順序で、時刻順に並んだレコードの列 | [20] |
| ログに必要な性質 | Kleppmann ほか「Online Event Processing」（CACM 62(5)、2019-05） | 永続・追記のみ・順次読み取り（全購読者が同じ順序、単調増加の LSN）・耐障害・分割（分割をまたぐ順序保証はない） | [22] |
| 論理デコード | PostgreSQL 18 公式文書 47.2（Logical Decoding Concepts） | WAL から、テーブルへの永続的な変更を、内部状態の知識なしで解釈できる形式に取り出す処理 | [16] |

補足：

- 「分散モノリス（distributed monolith）」の**権威ある定義は見つからなかった**。AWS・Azure・Google Cloud・Thoughtworks・martinfowler.com に絞った検索でもこの語を定義する一次の文書は出ず、近い内容は「共有 DB は開発時と実行時の結合を生む」[4][11]、「同期呼び出しの連鎖はアンチパターン」[28]、「統合データベースは避けるべき」[29] の 3 つに分かれて書かれている。ガイドでは「分散モノリス」を定義済みの用語として使わず、この 3 つの兆候の総称として導入するのが安全。
- DDIA 2e は、アウトボックスを「二重書き込みに見えるし、実際そうだ」としたうえで、同じ DB の 1 トランザクションに収まる点が違う、という趣旨で説明している（12.2.2、印刷 p.504。前後の文脈は [3] の担当ノートで確認すること）。

## 3. 製品ごとの違い（表。公式文書の URL・版・日付）

### 3.1 Debezium 3.7（PostgreSQL コネクタ）

確認した版：文書の版表示は「3.7（latest stable）」。3.7 系の最新は 3.7.1.Final（2026-11-06）[13]。`/reference/stable/` の URL は常に最新の安定版を指すので、ガイドに載せるときは版を明記する。

| 項目 | 文書が言うこと | 出典 |
| --- | --- | --- |
| 対応する PostgreSQL | 14・15・16・17・18（3.7 の試験済みの版）。Java 17 以上、Kafka Connect 3.1 以上 | [13] |
| 論理デコードのプラグイン | `pgoutput`（PostgreSQL 10 以降に同梱）と `decoderbufs`（Debezium のコミュニティが保守）の 2 つ | [12] |
| `plugin.name` の既定値 | **`decoderbufs`**。`pgoutput` を使うなら明示する必要がある（RDS・Cloud SQL などでは `pgoutput` を指定せよと書かれている） | [12] |
| `publication.autocreate.mode` の既定値 | **`all_tables`**（DB の全テーブルの publication を作る）。絞るなら `filtered` | [12] |
| スナップショット | `snapshot.mode` の既定は `initial`（オフセットがないときだけ初回スナップショットを取り、その後ストリーミング）。ほかに `always`・`initial_only`・`no_data`・`when_needed` など | [12] |
| DDL | 論理デコードは DDL の変更を扱わない。コネクタは DDL のイベントを出せない | [12] |
| 列のスキーマの取り方 | 列の構成はプラグインのイベントから、主キーの情報は JDBC のメタデータ（別経路）から取る。主キーを変えるときは、DB を読み取り専用にする → 残りを処理させる → 止める → 変える → 戻す、の手順が要る | [12] |
| REPLICA IDENTITY | `DEFAULT`（主キーの旧値のみ）、`NOTHING`、`FULL`（UPDATE・DELETE で全列の旧値）、`INDEX`。主キーのないテーブルは `DEFAULT` だと作成イベントしか出ない | [12] |
| TOAST の値 | 変わっていない TOAST の値は、レプリカ識別に含まれない限りメッセージに入らず、`unavailable.value.placeholder` の値が入る | [12] |
| 生成列 | `pgoutput` は生成列の値を取り込まない、と文書にある（PostgreSQL 18 で生成列の複製が入ったこととの関係は 9 節） | [12] |
| 配信保証 | 正常時は各イベントを 1 回、**障害のあとは少なくとも 1 回**（重複がありうる）。受け手は重複を前提にする。LSN が重複の検出に使える | [12][14] |
| Kafka Connect が異常終了したとき | 最後に記録したオフセットから再開するので、直前のイベントを出し直すことがある | [12] |
| コネクタが長く止まったとき | 変更は WAL に溜まり、再開すれば続きから読む | [12] |
| WAL が溜まる理由 | スロットは Debezium が止まっていても必要な WAL を保持し続ける。同じホストに「更新の多い DB」と「取り込み対象だが更新の少ない DB」があると、コネクタが LSN を確認応答する機会がなく、処理済みの WAL が残る | [12] |
| ハートビート | `heartbeat.interval.ms` の既定は **0（送らない）**。`heartbeat.action.query` で更新の少ない DB に定期的に書き込ませる方法が示されている | [12] |
| フェイルオーバーとスロット | PostgreSQL 15 以前：スロットはプライマリにしか作れず、スタンバイへ伝わらない。16：スタンバイにスロットを作れるが自動同期はしない。17 以降：`slot.failover=true` でフェイルオーバースロットを作れる（既定は `false`） | [12] |
| スロットを落とすな | オフセットはスロットが無傷である間だけ有効。スロットなしで版を上げるとイベントを飛ばし、「黙ったデータ損失」になりうる、と文書にある | [12] |
| `slot.drop.on.stop` | 既定は `false`。`true` は試験・開発だけにせよ、とある | [12] |

### 3.2 Debezium 3.7 Outbox Event Router（SMT）

確定した URL：<https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html>（版の表示は 3.7）[15]。版を固定した URL が必要なら `/reference/3.7/transformations/outbox-event-router.html` の形になるはずだが、**この形の URL は開いていない（未確認）**。

| 項目 | 文書が言うこと |
| --- | --- |
| 既定のアウトボックス表の列 | `id`（uuid）、`aggregatetype`、`aggregateid`、`type`、`payload`（jsonb） |
| 既定のトピック | `outbox.event.` ＋ `aggregatetype` の値 |
| メッセージのキー | `aggregateid`。同じ集約のイベントが同じパーティションに入り、順序が保たれる |
| 重複への備え | イベントの `id` をヘッダーに出す。受け手はこれで重複を取り除ける |
| DELETE | アウトボックス表の DELETE は自動で捨てる。つまり**挿入した行をすぐ消してよい**設計 |
| UPDATE | 想定外。既定では警告を出すだけ（`table.op.invalid.behavior=warn`） |
| MongoDB | この SMT は非対応（別の SMT がある） |

### 3.3 PostgreSQL 18（論理レプリケーション・論理デコード）

確認した版：文書の表示は「PostgreSQL 18.7 Documentation」。PostgreSQL 18 のリリースは 2025-09-25 [18]。

| 項目 | 文書が言うこと | 出典 |
| --- | --- | --- |
| DDL | スキーマと DDL は複製されない。初期のスキーマは `pg_dump --schema-only` で写し、その後の変更は手で合わせる。追加型の変更は購読側へ先に入れると途中のエラーを避けやすい | [17] 29.8 |
| シーケンス | シーケンスのデータは複製されない。serial・identity 列の値はテーブルのデータとして届くが、購読側のシーケンスは進まない。切り替えの前に進める必要がある | [17] 29.8 |
| TRUNCATE | 複製される。ただし購読の外のテーブルへの外部キーがあると失敗する | [17] 29.8 |
| ラージオブジェクト | 複製されない | [17] 29.8 |
| 対象 | テーブルのみ（パーティション表を含む）。ビュー・マテリアライズドビュー・外部テーブルは不可 | [17] 29.8 |
| REPLICA IDENTITY FULL | B-tree・Hash の既定の演算子クラスがない型（`point`・`box` など）の列があると UPDATE・DELETE を適用できない | [17] 29.8 |
| レプリカ識別のない表 | UPDATE・DELETE を複製する publication に入っていると、**発行側で** UPDATE・DELETE がエラーになる（INSERT は通る） | [19] 29.1 |
| スロットの配信 | 通常は各変更を 1 回だけ出す。クラッシュ後は以前の LSN に戻り、直近の変更を送り直すことがある。重複の害を避けるのはクライアントの責任 | [16] 47.2 |
| スロットと資源 | スロットはクラッシュをまたいで残り、消費側の状態を知らない。接続がなくても必要な WAL とカタログの行を保持する。極端な場合はトランザクション ID の周回を防ぐために DB が停止しうる | [16] 47.2 |
| `max_slot_wal_keep_size` | 既定は **-1（無制限）** | [18b] |
| `idle_replication_slot_timeout` | **18 で追加**。使われていないスロットを一定時間で無効にする。既定は 0（無効） | [18][18b] |
| スロットの同期 | スロットに `failover` を付け、スタンバイで `sync_replication_slots` を有効にする（既定は無効）。プライマリの `synchronized_standby_slots` に物理スロットを書くことが強く勧められている | [16][18b] |
| 18 での変更点（論理レプリケーション） | 生成列の値を複製できる（`publish_generated_columns`）／`CREATE SUBSCRIPTION` の `streaming` の既定が `off` から `parallel` へ／適用時の競合をログに出し、`pg_stat_subscription_stats` に列を追加／`ALTER SUBSCRIPTION` で two-phase の挙動を変更可能／`pg_recvlogical --enable-failover`／`pg_createsubscriber --all` ほか | [18] |

### 3.4 ログの保持とコンパクション（Kafka 4.4・Redpanda 26.2）

| 項目 | Apache Kafka 4.4 | Redpanda 26.2 |
| --- | --- | --- |
| 保持の既定 | `log.retention.hours=168`（7 日）、`log.retention.bytes=-1`、`log.cleanup.policy=delete` [25] | `cleanup.policy` の既定は `delete` [26]。保持時間の既定値は**確認できなかった**（9 節） |
| コンパクションが保つもの | 各キーの少なくとも最新の値。順序は入れ替えない。オフセットは変わらない [24] | 各キーの最新のレコード。ただし**ベストエフォート**で、同じキーの重複が残ることがある [26] |
| 削除の印（tombstone） | キーあり・値 null のレコード。`delete.retention.ms`（既定 24 時間）のあと取り除かれる。それより長く遅れた受け手は削除を見逃しうる [24][25] | `delete.retention.ms`（トピック）／`tombstone_retention_ms`（クラスタ）。既定値は当該ページに明記なし [26] |
| 遅延の上下限 | `min.compaction.lag.ms`（既定 0）、`max.compaction.lag.ms`（上限は厳密な保証ではない）[24][25] | — |
| 注意点 | アクティブなセグメントはコンパクションされない [24] | Tiered Storage へ移したセグメントは再コンパクションされない。トランザクションのマーカーは既定で残り続ける [26] |
| 配信の意味 | 既定は at-least-once。冪等プロデューサー（0.11.0.0 以降）とトランザクションで Kafka 内の exactly-once。**外部システムとの exactly-once は相手側の協力が要る** [24] | — |
| 複製の既定 | `min.insync.replicas=1`、`unclean.leader.election.enable=false` [25] | — |

### 3.5 クラウド製品（公式文書に基づく比較のみ・未検証）

- AWS Prescriptive Guidance のアウトボックスの実装例は 2 つ：(a) RDS のアウトボックス表を別サービスが定期的に読み、SQS へ送って成功したら行を消す（ポーリング）、(b) DynamoDB Streams を CDC として使い、別の表を持たない [8]。
- Azure Architecture Center は、Cosmos DB の `TransactionalBatch` で業務オブジェクトとイベントを同時に書き、別のワーカーが発行して「処理済み」に印を付ける実装を示している [7]（検索の抜粋で確認。本文は開いていない）。

## 4. 事故・失敗例（一次報告）

| # | 事例 | 何が起きたか（報告に書かれていること） | このノートの論点との関係 | 出典 |
| --- | --- | --- | --- | --- |
| 1 | Slack 2022-02-22 | Consul エージェントの段階的な更新（25% ずつ）で memcached のノードが順に入れ替わり、キャッシュのヒット率が下がった。グループ DM の所属を引く問い合わせが、ユーザー ID で分割したキースペースの全シャードを当たる形で、キャッシュが空くと DB（Vitess）への負荷がミス率に対して超線形に増えた。DB が読めないのでキャッシュも埋まらず、自力で戻らない状態（メタステーブル障害）になった。起動要求を絞って復旧 | **派生データ（キャッシュ）が失われたとき、正本がその再構築の負荷に耐えるか**。「失っても作り直せる」は、作り直す費用が正本の容量に収まるときだけ成り立つ | [30] |
| 2 | GitHub 2018-10-21 | 43 秒のネットワーク分断で、Orchestrator が MySQL のプライマリを米国東海岸から西海岸へ昇格。東に「西へ複製されていない数秒分の書き込み」、西に「30〜40 分ぶんの新しい書き込み」が残り、両側が相手にない書き込みを持った。データの完全性を優先して 24 時間 11 分のあいだ縮退。最も忙しいクラスタの 1 つで、対象の時間帯の書き込みは 954 件。Webhook は 500 万件超が滞留し、約 20 万件は内部の TTL 切れで破棄 | **正本が 2 つになった**事例。複製が非同期であるかぎり、昇格は「応答済みの書き込み」を置き去りにしうる。派生側の流れ（Webhook）の TTL が、復旧より先に切れる | [31] |
| 3 | Meta（TAO のキャッシュ）2022-06-08 の技術記事 | キャッシュの充填と無効化の競合で、古い値がキャッシュに残り続ける型を説明。版番号が同じまま中身が違う状態になり、エラー処理の中の「版が低いときだけ捨てる」処理が効かず、古いメタデータが無期限に残った不具合を報告。監視（Polaris）で検知し、30 分未満で原因に到達 | **キャッシュと DB の二重書き込みの競合**の具体例。事後報告ではなく技術記事（自己申告）。障害の規模・影響の記載はない | [32] |
| 4 | Zalando 2023-11-09・2025-12-19 の技術記事 | 更新の少ない DB でスロットが進まず WAL が溜まり続ける問題が、イベント基盤を広げるうえで最大の運用上の問題だった、と報告。pgjdbc と Debezium（3.4.0.Final の `lsn.flush.mode`・`offset.mismatch.strategy`）に修正を寄せた | **CDC の WAL 肥大**の一次の記述。ただし自社でディスクが埋まって止まった、という具体の障害は書かれていない（自己申告） | [33] |

**見つからなかったもの**（2026-11-18 時点。検索語は 11 節末尾）：

- **二重書き込みそのものを原因と明記した、大手事業者の事後報告**は見つからなかった。Confluent・AWS・Azure・DDIA の説明はすべて仕組みの解説で、実名の事故の引用はない。
- **「レプリケーションスロットが WAL を保持してディスクが埋まり、正本の DB が止まった」ことを書いた、大手事業者の公式の事後報告**は見つからなかった。出てきたのは個人・小規模事業者のブログ（dev.to、hams.tech など。本文未確認）、ベンダーの解説（Streamkap、Netdata、AWS Database Blog など）、Zalando の技術記事 [33] だけ。ガイドでは「公式文書が警告している既知の危険」[12][16] として書き、事故の実例があるかのようには書かない。
- **CDC の遅延が利用者に見える障害になった一次報告**も、今回の検索では見つからなかった。

## 5. 権威の推奨と位置づけ（規範か任意か）

いずれも**任意の指針**（ベンダーの設計ガイド）で、法令や標準の要求ではない。対象読者も文書ごとに違う。

| 文書 | 位置づけ | 何を勧めているか | 注意 |
| --- | --- | --- | --- |
| AWS Prescriptive Guidance「Enabling data persistence in microservices」[4] | 任意。モノリスからの移行（モダナイゼーション）の連作の 1 本。読者はアプリの所有者・アーキテクト・テックリード・PM。著者は AWS の 2 名。**ページに発行日の表示は見つからなかった** | 6 パターン：Database-per-service／API composition／CQRS／Event sourcing／Saga／Shared-database-per-service。データストアを分散させ、データは各サービスの API を通す | **共有 DB を禁じてはいない**。「既存のコードを大きく変えたくない」「ACID で整合性を保ちたい」「DB を 1 つだけ運用したい」ときの選択肢として挙げ、ホットテーブルを避けること・変更を後方互換にすることを条件にしている |
| 同・Database-per-service [4] | 任意 | 疎結合・サービスごとに違う準拠要件・細かいスケール制御が要るとき。欠点は、サービスをまたぐトランザクションと問い合わせの難しさ、複数 DB の運用。またぐ問い合わせには別のパターン（API composition＋CQRS、またはイベントソーシング）が**必須** | CAP に触れる一文は表現が粗い。引用しない |
| 同・Shared-database-per-service [4] | 任意 | 開発時の結合（スキーマ変更の調整）と実行時の結合（長いトランザクションがほかのサービスの表をロックする）を生む、と明記 | — |
| Azure Architecture Center「Data considerations for microservices」[5] | 任意。ms.date 2022-07-26、ページ更新 2026-09-29 | 「2 つのサービスはデータストアを共有すべきでない」。理由は、スキーマの変更が、その DB に依存する全サービスの調整を要するから。整合性の水準を部品ごとに決め、可能なら結果整合／強い整合性が要るなら単一の情報源／サービスが要るデータだけを持つ／イベント駆動にしてイベントのスキーマを公開する | **「同じ物理 DB サーバーを共有するのは安全」**と注記。問題になるのは、同じスキーマ・同じ表を読み書きすること。AWS より強い言い方だが、物理の分離までは求めていない |
| microservices.io（Chris Richardson）[9][10][11] | **個人のサイト**（著作権表示は Chris Richardson 個人）。権威ではなく、用語の出どころとして参照 | Database per service は「表を分ける／スキーマを分ける／サーバーを分ける」の 3 段階。前の 2 つが最も負担が小さい。共有 DB も得失つきのパターンとして載せ、アンチパターンとは呼んでいない。アウトボックスの中継は Polling publisher と Transaction log tailing の 2 つ | AWS の 6 パターンの名前はこのサイトの用語とほぼ重なる。根拠にするなら AWS・Azure の側を引く |
| AWS Prescriptive Guidance「Cloud design patterns」Transactional outbox [8] | 任意 | 受け手を冪等にする（処理済みのメッセージを記録）／DB の更新と同じ順で送る／ロールバックしたら送らない／サービスをまたぐならサーガ | 例のポーリングは `ORDER BY id` で読んで送ってから消す実装。順序の落とし穴（6.3）には触れていない |
| Microsoft「.NET Microservices」Communication in a microservice architecture [28] | 任意。ms.date 2020-01-30。.NET 向けの電子書籍の一部 | マイクロサービス間に同期の依存を作らない。同期呼び出しの連鎖は**アンチパターン**と図で明示。ほかのサービスのデータが要るなら、必要な属性だけを結果整合で自分の DB に写す | 強い言い方（「できれば決して」）だが、.NET の参考実装の本であり、規範ではない |
| Martin Fowler「IntegrationDatabase」[29] | 個人の記事（2004-05-25、2015-07-01 更新）。Thoughtworks の公式見解ではない | 複数のアプリが共有する DB は結合点になる。避けるべき | 古典。用語の出どころとして |
| AWS Well-Architected「Data Analytics Lens」[27] | 任意。発行日 2023-12-22。レンズ（質問と BP の一覧） | BP 1.1 取り込み前に元データの品質を検証／BP 4.5 データと DB の変更を追う／BP 6.1 データの流れの依存関係を図にする（Required）／BP 6.4 ETL の再実行を自動化し冪等にする／BP 7.1 中央のデータカタログ／BP 7.3 データの系譜を追う。シナリオに modern data architecture・data mesh・streaming ingest など | 目次（llms.txt）には「ELT」「reverse ETL」の語は出てこない。CDC は提案 4.5.4 にあると検索の抜粋で見たが、**当該ページの本文は取得できなかった** |
| Azure Architecture Center「Extract, transform, load (ETL)」[6] | 任意。ms.date 2025-09-15 | ELT は変換の場所が違うだけ（変換を宛先のストアで行う）。ETL を選ぶ：宛先が非力／複雑な業務規則／読み込み前の監査が要る。ELT を選ぶ：宛先が伸縮する計算資源を持つ／生データを残したい。リバース ETL＝分析系で整えたデータを業務のツールへ戻す流れ。ストリーミングはチェックポイントで at-least-once、変換は冪等に | リバース ETL を公式の指針として定義している数少ない一次資料 |

リバース ETL と正本の関係について：DDIA 2e 1.1.2（印刷 p.10）もリバース ETL の語を挙げている [1]。**リバース ETL は「派生データを業務システムへ書き戻す」流れ**なので、書き戻した先でそれを正本として扱い始めると、正本が 2 つになる。これを明示的に警告する権威の文書は見つからなかった（設計上の推論として書く）。

## 6. 設計判断の分かれ目（何を選ぶと何を得て何を失うか。表）

### 6.1 データの置き場所

| 選択 | 得るもの | 失うもの・払うもの | 根拠 |
| --- | --- | --- | --- |
| サービスごとに DB（サーバーも分ける） | スキーマ変更の独立、製品の選択の自由、障害とスケールの分離 | サービスをまたぐトランザクションと結合。DB の運用の数。またぐ問い合わせのための別の仕組み | [4][5][9] |
| サービスごとにスキーマ・表を分け、サーバーは共有 | 所有の境界は保てる。運用は軽い | 実行時の資源（接続・ロック・I/O・障害）は共有。権限で境界を強制しないと破られる | [5]（注記）[9] |
| 共有 DB（同じ表を複数のサービスが読み書き） | ローカルの ACID トランザクション、結合、運用は 1 つ | 開発時の結合（変更のたびに全員と調整）と実行時の結合（ロックの巻き添え）。置換性 | [4][11][29] |

### 6.2 複数の場所へ同じ事実を届ける方法

| 選択 | 得るもの | 失うもの・起きる不整合 | 根拠 |
| --- | --- | --- | --- |
| 二重書き込み（アプリが DB とブローカー／キャッシュ／検索へ個別に書く） | 実装が最も簡単。追加の部品なし | (a) **部分的な失敗**：片方だけ成功し、欠落または「DB にない出来事」が残る。(b) **順序の入れ替わり**：並行する 2 つの更新が、2 つのシステムで逆の順に届き、エラーなしで恒久的に食い違う。(c) 書く順を逆にしても、DB のトランザクションで包んでも直らない | [2][8][21][22] |
| 分散トランザクション（XA／2PC） | 原子性 | 参加する全システムの対応が要る（検索索引などは非対応）。準備の段階でアプリが落ちると処理が止まる。デッドロック検出なし。どれか 1 つが落ちると全体が中断 | [22] |
| アウトボックス＋ポーリング | 原子性を DB の 1 トランザクションに畳める。どの SQL DB でも動く。CDC の基盤が要らない | 遅延はポーリング間隔に依存。順序どおりの発行が難しい。at-least-once（重複）。表の掃除と索引の負荷 | [8][10][10b] |
| アウトボックス＋ログ追尾（Debezium の Outbox Event Router） | コミット順で届く。行はすぐ消せる。内部スキーマと外向きのスキーマを分けられる | Kafka Connect・スロット・WAL の運用。at-least-once。内部スキーマとアウトボックスの変換の保守。書き込み量の増加 | [3][12][15] |
| 表そのものの CDC | アプリの変更が要らない。既存の表から始められる | **内部のスキーマがそのまま外向きの契約になる**。DDL は流れない。行の変更は「何が起きたか」の意図を持たない | [3][12][17][22] |
| イベントを先にログへ書き、DB はその購読者にする（OLEP・イベントソーシング） | ログへの 1 回の追記が原子的。全購読者が同じ順序で見る。購読者を足すだけで新しい派生ビューを作れる。誤ったイベントからの回復と再計算が容易 | 書いた直後に自分の書き込みを読めない。購読者をまたぐ読み取りに分離性がない（ある時点で食い違って見える）。処理までの時間に上限がない | [21][22] |

### 6.3 ポーリング方式とログ追尾方式の違い

| 観点 | ポーリング | ログ追尾（WAL を読む） |
| --- | --- | --- |
| 何を読むか | アウトボックス表への問い合わせ（コミット済みの行だけが見える）[8] | トランザクションログ。コミットの時点で、コミット順に出る [12] |
| 順序 | 「難しい」とだけ書かれている [10b]。AWS の例は ID 順で読む [8] | ログの順序がそのまま届く。キーを `aggregateid` にして集約ごとの順序を保つ [15] |
| 遅延 | ポーリング間隔 | ストリーミング（ただしスロットと Connect の健全性に依存） |
| DB への負荷 | 問い合わせと削除の負荷 | WAL の保持（消費が止まると溜まる）[12][16] |
| 要る部品 | アプリ内のスケジューラだけ | Kafka Connect、コネクタ、スロットの監視 |
| 重複 | 送ったあと、消す前に落ちると出し直す [10] | Connect が異常終了すると出し直す [12] |

**記憶・要確認**：ポーリングで連番（シーケンス）の順に読むと、番号の採番順とコミット順が一致しないため、あとからコミットされた小さい番号の行を読み飛ばす恐れがある。これは一次資料で直接確かめていない（microservices.io は「順序どおりの発行が難しい」と書くだけ [10b]）。ケーススタディ A で実測して確かめる候補。

### 6.4 データの流れの 3 形態

| 形態 | 得るもの | 失うもの | 危ない兆候 | 根拠 |
| --- | --- | --- | --- | --- |
| DB 経由（共有 DB・統合 DB） | 即時の整合、結合、簡単 | スキーマが全員の契約になる。変更に全員の調整。ロックの巻き添え | 表を落とす・列名を変えるのに複数チームの合意が要る | [4][5][11][29] |
| サービス呼び出し（同期の API） | 最新の値、契約が明示的 | 呼び先の可用性と遅延を引き継ぐ。連鎖すると応答時間と障害が足し算になる | 1 つの要求が複数のサービスを直列に呼ぶ。1 つ落ちると全部落ちる | [28] |
| 非同期メッセージ（イベント・ログ） | 時間的な結合が切れる。受け手を足しやすい。再生できる | 結果整合。重複と順序の扱い。スキーマの進化の管理。遅延の監視 | 受け手が冪等でない。イベントのスキーマが公開されていない | [5][20][22][28] |

「分散モノリス」の兆候（定義がないので、上の 3 つの文書からの**整理**として示す）：(1) 複数のサービスが同じ表を読み書きしている [4][5]、(2) 1 つの要求を返すのに同期呼び出しの連鎖が要る [28]、(3) スキーマや API の変更を複数のサービスで同時にデプロイしないと壊れる [4]、(4) 2 つのサービスが絶えず細かいやり取りをしている（境界の引き直しの合図）[5]。

### 6.5 共通データ基盤への取り込み

| 選択 | 得るもの | 失うもの | 根拠 |
| --- | --- | --- | --- |
| 定期の全件ダンプ（バッチ ETL） | 単純。正本への影響を時間帯で制御できる | 鮮度。削除の検出が難しい | [2][6] |
| ETL（宛先の前で変換） | 宛先に負荷をかけない。読み込み前の監査 | 変換エンジンの運用。生データが残らないと作り直せない | [6] |
| ELT（宛先で変換） | 生データを残せる。作り直せる。宛先と一緒に伸縮 | 宛先の計算費用。生データの統制（個人情報など） | [6] |
| CDC でログへ、ログから基盤へ | 鮮度。削除も届く。受け手を足せる | 3.1・3.3 の制限。内部スキーマの露出 | [12][20][22] |
| リバース ETL（基盤から業務系へ戻す） | 分析の結果を業務で使える | 派生データが業務系に入り、正本の境界が曖昧になる | [1][6] |

Kreps は、ETL が「抽出と整形」と「倉庫の都合に合わせた再構成」の 2 つを混ぜていることを問題とし、整ったフィードを出す責任は**データを作る側**にある、としている [20]。これは、共通データ基盤のチームが全サービスの内部スキーマを読み解く形（N 個の取り込みを 1 チームが抱える）を避ける根拠になる。

## 7. 設計レビューで問うこと（問い｜なぜ問うか｜危ない兆候）

| # | 問い | なぜ問うか | 危ない兆候 |
| --- | --- | --- | --- |
| 1 | この事実（注文・在庫・顧客…）の正本はどのサービスのどのストアか。1 つに決まっているか | 食い違ったときに「どちらが正しいか」を定義で決めるため [1] | 「場合による」「両方」「同期しているので同じ」 |
| 2 | 派生データ（キャッシュ・検索・集計・倉庫・学習済みモデル）を全部消したら、正本から作り直せるか。手順と所要時間は | 作り直せないなら、それは派生ではなく第 2 の正本 [1] | 作り直しの手順がない。派生側にしかない項目がある |
| 3 | 派生データが一斉に空になったとき、正本は再構築の負荷に耐えるか | Slack 2022-02-22 はここで自力で戻らなくなった [30] | キャッシュ前提の重い問い合わせ。全シャードを当たる問い合わせ |
| 4 | この表を読み書きするサービスはいくつか。権限で強制しているか | 共有は開発時と実行時の結合を生む [4][5] | 複数サービスが同じ表に書く。DB ユーザーが共通 |
| 5 | 1 つの処理で、DB と別のシステム（ブローカー・キャッシュ・検索・外部 API・メール）の両方に書いている箇所はどこか | 二重書き込みは片方だけ成功しうる [2][8] | `commit` の直後に `publish`。`try/catch` で握りつぶす再送 |
| 6 | 同じキーへの並行した更新が、2 つのシステムに同じ順序で届く保証は何か | エラーなしで恒久的に食い違う型がある [2][22] | 「タイムスタンプで後勝ち」「めったに起きない」 |
| 7 | アウトボックスの中継はポーリングかログ追尾か。順序はどう保証しているか | ポーリングは順序が難しい [10b] | 連番の順に読んで「既読位置」だけ覚える実装 |
| 8 | 受け手は同じイベントを 2 回受けても結果が変わらないか。何で重複を見分けるか | アウトボックスも CDC も Kafka も既定は at-least-once [8][12][24] | 「exactly-once なので不要」。イベントに ID がない |
| 9 | 外に出しているのは内部の表の形か、外向きに決めたイベントの形か | 表の CDC は内部スキーマを契約にしてしまう [3] | 列名の変更で下流が壊れる。下流が何を読んでいるか分からない |
| 10 | スキーマを変えるとき、DDL は下流へどう伝わるか | 論理デコードは DDL を流さない [12][17] | 「CDC が自動でやる」 |
| 11 | レプリケーションスロットの保持量を誰が監視し、上限はいくつか。消費が止まったら何が先に起きるか | 既定は無制限。正本のディスクが埋まる [16][18b] | `max_slot_wal_keep_size` が既定のまま。使っていないスロットがある |
| 12 | スロットが無効になった／落とされたとき、取りこぼしをどう検知し、どう埋めるか | 上限を付けると今度は「黙った欠落」の危険が出る [12] | 再スナップショットの手順と所要時間を誰も知らない |
| 13 | 正本の DB がフェイルオーバーしたとき、スロットは新しいプライマリにあるか | 15 以前は伝わらない。17 以降は設定が要る [12][16] | `slot.failover` も `sync_replication_slots` も既定のまま |
| 14 | 更新の少ない DB・表だけを取り込んでいないか。ハートビートは入れたか | 確認応答の機会がなく WAL が残る [12][33] | `heartbeat.interval.ms=0`（既定） |
| 15 | ログの保持期間は、受け手が止まって復旧するまでの最長時間より長いか | 既定は 7 日。削除の印は 24 時間で消える [24][25] | 受け手の最長停止時間を決めていない |
| 16 | コンパクションしたトピックを「全履歴」として使っていないか | コンパクションは最新値しか保証しない [24][26] | 監査・再計算に履歴が要るのに `compact` |
| 17 | 1 つの要求を返すのに、同期で何個のサービスを直列に呼ぶか | 連鎖は可用性と応答時間を悪くする [28] | 呼び先が落ちると自分も落ちる。タイムアウトの合計が上流より長い |
| 18 | 共通データ基盤へ出すデータの形と品質に、責任を持つのは作る側か、基盤側か | 整ったフィードの責任は作る側、という主張 [20]。BP 1.1 [27] | 基盤チームが各サービスの表を直接読んでいる |
| 19 | 分析系の結果を業務系へ戻す流れ（リバース ETL）はあるか。戻した値の正本はどこか | 派生が正本に紛れ込む [6] | 戻した値を業務側で上書きしている |
| 20 | 書いた直後に読む必要がある箇所はどこか。そこは非同期の流れを通っていないか | ログ中心の構成には、購読者をまたぐ分離性がない [22] | 画面が「保存したのに古い」。回避のための `sleep` |

## 8. ケーススタディで測れること・測れないこと

題材 A（基盤をまたぐデータ統合）で測れること：

- **二重書き込みの欠落・幽霊イベント・順序の入れ替わり**の件数。書き手 ID＋連番で、DB と Redpanda の両側を数える。障害は「DB のコミット後・発行前に強制終了」「発行後・コミット前に強制終了」「ブローカーへの経路を切断」の 3 点で入れる（[2][8][21] の 3 つの型に対応）
- **アウトボックス＋ポーリング**：連番順の読み取りで読み飛ばしが起きるか（6.3 の「記憶・要確認」を実測で決着させる）。長いトランザクションを 1 本混ぜる
- **アウトボックス＋Debezium（Outbox Event Router）**：Connect を強制終了したあとの重複の件数、`id` ヘッダーでの重複排除後の件数
- **表の CDC**：列の追加・改名・主キーの変更で、下流に何が届くか（題材 B と共有）
- **WAL の保持**：コネクタを止めて書き込みを続け、`pg_replication_slots` の保持量の伸びを測る。`max_slot_wal_keep_size` を付けたとき・`idle_replication_slot_timeout` を付けたときに、スロットが無効になる時点と、再開後の欠落件数
- **ハートビートなしの低頻度 DB**：同じインスタンスの別の DB だけに書き込み、取り込み対象側のスロットが進まないことを確かめる
- **Kafka 4.4 との照合**：Redpanda のコンパクションが「ベストエフォート」[26] であることが、再構築の一致率に影響するか

実機で先に決める設定（既定のままだと意図と違う動きをするもの）：`plugin.name=pgoutput`（既定は `decoderbufs`）、`publication.autocreate.mode=filtered`（既定は `all_tables`）、`heartbeat.interval.ms`（既定は 0）、`wal_level=logical`。

測れないこと：

- リージョンをまたぐフェイルオーバーでのスロットの同期（単一ホスト。手動昇格でスロットが失われることは測れるが、実際のネットワーク分断は再現しない）
- マネージドサービス（RDS・Cloud SQL・Aurora）でのスロットの自動引き継ぎ。公式文書の記述 [12] の比較のみ・未検証
- DynamoDB Streams・Cosmos DB の change feed を使うアウトボックス [7][8]。未検証
- 大規模な WAL の保持（テラバイト級）での復旧時間。小さく保つ方針のため相対比較のみ

## 9. 未確定・要確認

1. **AWS「Enabling data persistence in microservices」の発行日・改訂日**：取得したページに日付の表示が見つからなかった。改訂履歴のページは開いていない。
2. **Redpanda の保持の既定値**（`log_retention_ms` など）と `tombstone_retention_ms` の既定値：クラスタ設定のページが長く、該当箇所を取得できなかった。Kafka と同じ 7 日・24 時間だという前提で書かない。
3. **Debezium の文書の「`pgoutput` は生成列の値を取り込まない」**と、**PostgreSQL 18 の生成列の複製**（`publish_generated_columns`）の関係。Debezium 3.7 が publication のこのオプションを扱うかは未確認。実機で確かめる。
4. **Debezium 3.7 の `plugin.name` の既定が `decoderbufs`** である点は、文書の後半（設定の表）から要約ツール経由で読んだ値。着手時に文書の表を直接見て確かめ直す。
5. **Outbox Event Router の版固定 URL**（`/reference/3.7/...`）は開いていない。
6. **ポーリング方式の読み飛ばし**（6.3）：一次資料で直接は確認できていない。実測で決着させる。
7. **Kleppmann「Online Event Processing」**：CACM 版の PDF を本文で確認したが、読んだのは冒頭から New York Times の事例の途中（p.43〜48）まで。結論部は読んでいない。ACM Queue の HTML 版は 403 で開けなかった。
8. **Kafka 原論文**：3.3 節（配信保証）の途中まで本文で確認。4 節以降（LinkedIn での配備、性能、今後の課題としての複製）は読んでいない。
9. **Kreps「The Log」**：元の URL（engineering.linkedin.com）は 404。現行は linkedin.com/blog/engineering/ 配下で、本文はあるが、図が欠け、書式が崩れ、末尾が切れているように見える。引用するときは現行の URL と「図は欠落」を書く。
10. **AWS Data Analytics Lens の提案 4.5.4（CDC）**：検索の抜粋で見ただけ。BP 4.5 のページ本文は取得できなかった。
11. **Azure のアウトボックス（Cosmos DB）の記事** [7]：検索の抜粋のみ。日付も未確認。
12. **Google Cloud の指針**：今回は調べられていない。Google Cloud Architecture Center のサービス間通信・データ所有に関する文書は別途確認が要る。
13. **PostgreSQL 19 以降でのシーケンスの複製**：18.7 の文書では「複製されない」[17]。その後の版での変更は調べていない（記憶・要確認）。
14. **「Scaling Memcache at Facebook」（NSDI 2013）のリース**など、キャッシュと DB の競合を扱う原論文は今回開いていない。Part 6 でキャッシュを厚く扱うなら追加で確認する。
15. DDIA 2e の印刷ページ（p.10〜11、p.497〜498、p.504）は、手元の抽出テキストの索引と柱から読み取った値。書籍担当のノートと突き合わせる。

## 10. 結論（スライドに書くこと。箇条書き 15〜30 個、各項目に出典の番号）

1. 正本（記録のシステム）は「新しいデータが最初に書かれ、食い違ったら定義上こちらが正しい」場所。派生データは「失っても正本から作り直せる」もの [1]
2. 正本か派生かは製品の種類ではなく使い方で決まる。同じ PostgreSQL が、あるデータでは正本、別のデータでは派生になる [1]
3. 「system of record」「dual write」「outbox」「分散モノリス」に公的な標準の定義はない。ガイドでは、どの文書の定義を使うかを明示する [1][2][8]
4. AWS と Azure はどちらも「サービスごとにデータストアを持ち、データは API を通す」を勧める。ただし任意の指針で、規範ではない [4][5]
5. Azure は「同じ物理サーバーの共有は安全。問題は同じスキーマ・同じ表を読み書きすること」と注記している。分けるべきは所有であって、まずは機械ではない [5]
6. AWS は共有 DB を禁じず、条件つきの選択肢として挙げる。払うものは、開発時の結合（スキーマ変更の調整）と実行時の結合（ロックの巻き添え）[4]
7. サービスごとに DB を分けたら、サービスをまたぐ問い合わせとトランザクションのための別の仕組みが必ず要る。分けるだけでは設計は終わらない [4][9]
8. microservices.io は Chris Richardson 個人のサイト。用語の出どころとして参照し、根拠は AWS・Azure の文書に置く [9][10][11]
9. 二重書き込みの不整合は 2 つの型：(a) 片方だけ成功する（原子性の問題）、(b) 並行する更新が 2 つのシステムで逆順に届く（順序の問題）。(b) はエラーが 1 つも出ないまま恒久的に食い違う [2][22]
10. 書く順を入れ替えても、DB のトランザクションで包んでも、二重書き込みは直らない。不整合の種類が入れ替わるだけ [21]
11. 異種のシステムをまたぐ分散トランザクション（XA）は、参加側の対応が要り、障害を増幅する。検索索引やキャッシュは多くが非対応 [22]
12. アウトボックスは、2 つのシステムへの書き込みを「1 つの DB の 1 トランザクション」に畳む。送る処理は別のプロセスに任せる [3][8][10]
13. アウトボックスも CDC も Kafka も、既定の保証は「少なくとも 1 回」。受け手を冪等にし、イベントに ID を持たせるのは選択ではなく前提 [8][12][15][24]
14. 中継の方式は 2 つ。ポーリングはどの SQL DB でも動くが順序が難しい。ログ追尾はコミット順で届くが、スロットと Connect の運用を引き受ける [10b][12]
15. 表そのものを CDC で流すと、内部のスキーマが外向きの契約になる。アウトボックスは、内部のスキーマと外向きのイベントを分ける手段でもある [3][15]
16. PostgreSQL の論理レプリケーション・論理デコードは DDL を流さない。シーケンスの値もラージオブジェクトも流れない（18.7 の文書）[12][17]
17. レプリケーションスロットは、消費側が止まっていても WAL を保持し続ける。`max_slot_wal_keep_size` の既定は無制限。正本のディスクを派生側の都合が埋めうる [16][18b]
18. 上限を付ければ正本は守れるが、スロットが無効になり、取りこぼしと再スナップショットの危険に変わる。どちらを守るかを先に決める [12][18b]
19. PostgreSQL 18 は、使われていないスロットを時間で無効にする `idle_replication_slot_timeout` を加えた（既定は無効）。購読の `streaming` の既定は `parallel` になり、生成列の複製と競合のログも入った [18]
20. Debezium 3.7 は PostgreSQL 14〜18 に対応。既定値に注意：`plugin.name` は `decoderbufs`、publication は全テーブル、ハートビートは無効、フェイルオーバースロットは無効 [12][13]
21. フェイルオーバーでスロットが引き継がれるかは版で違う。15 以前は引き継がれず、17 以降は設定すれば同期される [12][16]
22. ログは「追記のみ・全順序」の列。同じ入力を同じ順序で受け取れば同じ結果になる、という原理が、複製にもデータ統合にも使える [20][22]
23. システムを 1 対 1 でつなぐと経路は N² に近づく。中央のログに出して各自の速さで読めば N 本で済む。整ったフィードを出す責任は作る側にある [20]
24. Kafka は最初から「受け手が位置を持ち、巻き戻して読み直せる」設計で、保持は時間（当初の例で 7 日）で切る。読み直せることが、派生データの作り直しを支える [23]
25. ログの保持は無限ではない。Kafka 4.4 の既定は 7 日、削除の印は 24 時間で消える。コンパクションは最新値しか保証せず、履歴の代わりにはならない [24][25][26]
26. ログ中心の構成の限界：書いた直後に読めるとは限らず、購読者をまたぐ読み取りに分離性がない。原著者自身が欠点として書いている [22]
27. データの流れは 3 形態。DB 経由は即時だが全員を結合する。同期の呼び出しは最新だが可用性と遅延を引き継ぐ。非同期は結合を切るが、結果整合・重複・順序を引き受ける [4][5][28]
28. 分散モノリスの兆候（定義はないので整理として）：同じ表を複数サービスが書く／同期呼び出しの連鎖／同時デプロイが要る／2 つのサービスが絶えず細かくやり取りする [4][5][28][29]
29. ETL と ELT の違いは、変換をどこで行うかだけ。生データを残す ELT は作り直しに向く。リバース ETL は派生データを業務系へ戻す流れで、正本の境界を曖昧にしやすい [6]
30. 事故の一次報告：派生データ（キャッシュ）が消えて正本が再構築の負荷に耐えられなかった Slack 2022-02-22 [30]、正本が 2 つになった GitHub 2018-10-21 [31]。**二重書き込みや WAL 肥大を原因と明記した大手事業者の事後報告は見つからなかった**（公式文書の警告と技術記事 [32][33] はある）

## 11. 出典（番号｜題名｜発行者｜版・日付｜URL｜確認の深さ）

| 番号 | 題名 | 発行者 | 版・日付 | URL | 確認の深さ |
| --- | --- | --- | --- | --- | --- |
| 1 | データ指向アプリケーションデザイン 第2版 1.1.2・1.1.3「記録のシステムと導出データ」（印刷 p.10〜11） | オライリー・ジャパン（Kleppmann・Riccomini 著、斉藤 訳） | 第2版 | 書籍（非公開の抽出テキストで確認） | 本文確認（該当節のみ） |
| 2 | 同 12.2.1 二重書き込み（印刷 p.497〜498、図 12-4） | 同上 | 第2版 | 書籍 | 本文確認（該当箇所のみ） |
| 3 | 同 12.2.2 チェンジデータキャプチャ、アウトボックスパターン（印刷 p.499〜504） | 同上 | 第2版 | 書籍 | 一部確認（索引と該当段落の検索結果のみ。前後は未読） |
| 4 | Enabling data persistence in microservices（Introduction／Database-per-service pattern／Shared-database-per-service pattern） | AWS Prescriptive Guidance（Tabby Ward、Balaji Mohan） | 日付の表示なし（2026-11-18 閲覧） | https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-data-persistence/introduction.html ほか `database-per-service.html`・`shared-database.html` | 本文確認（3 ページ。API composition・CQRS・Event sourcing・Saga の各ページは未読） |
| 5 | Data considerations for microservices | Microsoft Azure Architecture Center | ms.date 2022-07-26、更新 2026-09-29 | https://learn.microsoft.com/en-us/azure/architecture/microservices/design/data-considerations | 本文確認 |
| 6 | Extract, transform, load (ETL) | Microsoft Azure Architecture Center | ms.date 2025-09-15、更新 2025-10-30 | https://learn.microsoft.com/en-us/azure/architecture/data-guide/relational-data/etl | 本文確認 |
| 7 | Implement the Transactional Outbox pattern by using Azure Cosmos DB | Microsoft Azure Architecture Center | 日付未確認 | https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-outbox-cosmos | 題名のみ（検索の抜粋を読んだ） |
| 8 | Transactional outbox pattern（Cloud design patterns, architectures, and implementations） | AWS Prescriptive Guidance | 日付の表示なし（2026-11-18 閲覧） | https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html | 本文確認 |
| 9 | Pattern: Database per service | microservices.io（Chris Richardson 個人のサイト） | © 2026 | https://microservices.io/patterns/data/database-per-service.html | 本文確認 |
| 10 | Pattern: Transactional outbox | 同上 | © 2026 | https://microservices.io/patterns/data/transactional-outbox.html | 本文確認 |
| 10b | Pattern: Polling publisher | 同上 | © 2026 | https://microservices.io/patterns/data/polling-publisher.html | 本文確認（Transaction log tailing のページは未読） |
| 11 | Pattern: Shared database | 同上 | © 2026 | https://microservices.io/patterns/data/shared-database.html | 本文確認 |
| 12 | Debezium connector for PostgreSQL | Debezium（公式文書） | 3.7（stable）。2026-11-18 閲覧 | https://debezium.io/documentation/reference/stable/connectors/postgresql.html | 本文確認（長いページを 4 分割で要約ツール経由。設定表の一部は 9 節のとおり要再確認） |
| 13 | Debezium Release Series 3.7 | Debezium | 3.7.1.Final（2026-11-06） | https://debezium.io/releases/3.7/ | 本文確認 |
| 14 | Frequently Asked Questions | Debezium | 2026-11-18 閲覧 | https://debezium.io/documentation/faq/ | 本文確認 |
| 15 | Outbox Event Router | Debezium（公式文書） | 3.7（stable）。2026-11-18 閲覧 | https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html | 本文確認 |
| 16 | 47.2 Logical Decoding Concepts | PostgreSQL Global Development Group | 18.7 の文書 | https://www.postgresql.org/docs/18/logicaldecoding-explanation.html | 本文確認 |
| 17 | 29.8 Logical Replication — Restrictions | 同上 | 18.7 の文書 | https://www.postgresql.org/docs/18/logical-replication-restrictions.html | 本文確認 |
| 18 | E. Release Notes — Release 18 | 同上 | 18（2025-09-25） | https://www.postgresql.org/docs/18/release-18.html | 本文確認（複製に関する項目のみ） |
| 18b | 19.6 Replication（設定パラメータ） | 同上 | 18.7 の文書 | https://www.postgresql.org/docs/18/runtime-config-replication.html | 本文確認（該当パラメータのみ） |
| 19 | 29.1 Publication | 同上 | 18.7 の文書 | https://www.postgresql.org/docs/18/logical-replication-publication.html | 本文確認 |
| 20 | The Log: What every software engineer should know about real-time data's unifying abstraction | LinkedIn Engineering（Jay Kreps） | 2013-12-16 | https://www.linkedin.com/blog/engineering/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying （旧 URL の engineering.linkedin.com は 404） | 本文確認（図は欠落、書式崩れ、末尾欠けの疑い） |
| 21 | Understanding the Dual-Write Problem and Its Solutions | Confluent（Wade Waldron）。**ベンダーのブログ・自己申告** | 2024-05-29 | https://www.confluent.io/blog/dual-write-problem/ | 本文確認 |
| 22 | Online Event Processing: Achieving consistency where distributed transactions have failed | Kleppmann、Beresford、Svingen。Communications of the ACM 62(5), pp.43–49（ACM Queue 17(1) にも掲載） | 2019-05。doi:10.1145/3312527 | https://martin.kleppmann.com/2019/05/01/olep-cacm.html （PDF：https://martin.kleppmann.com/papers/olep-cacm.pdf ） | 本文確認（p.43〜48 の途中まで。結論部は未読。ACM Queue の HTML 版は 403） |
| 22b | Turning the database inside-out with Apache Samza | Martin Kleppmann（Strange Loop 2014 の講演の書き起こし） | 2015-03-04 | https://martin.kleppmann.com/2015/03/04/turning-the-database-inside-out.html | 本文確認 |
| 23 | Kafka: a Distributed Messaging System for Log Processing | Kreps、Narkhede、Rao。NetDB'11（Athens） | 2011-06-12 | http://pages.cs.wisc.edu/~akella/CS744/F17/838-CloudPapers/Kafka.pdf （大学の講義用の写し） | 本文確認（1〜3.3 節の途中まで） |
| 24 | Design（Log Compaction、Message Delivery Semantics、Replication） | Apache Kafka | 4.4 | https://kafka.apache.org/44/design/design/ | 本文確認 |
| 25 | Broker Configs | Apache Kafka | 4.4 | https://kafka.apache.org/44/configuration/broker-configs/ | 本文確認（前半のみ。該当の既定値は取得） |
| 26 | Compaction Settings | Redpanda | 26.2（v26.2.7） | https://docs.redpanda.com/current/manage/cluster-maintenance/compaction-settings/ | 本文確認（保持の既定値はこのページになし） |
| 27 | Data Analytics Lens — AWS Well-Architected Framework | AWS | 発行 2023-12-22 | https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/analytics-lens.html （目次：同ディレクトリの `llms.txt`） | 表紙と目次を本文確認。BP 6.2〜6.4 は検索の抜粋。BP 4.5 の本文は取得できず |
| 28 | Communication in a microservice architecture（.NET Microservices: Architecture for Containerized .NET Applications） | Microsoft | ms.date 2020-01-30、更新 2023-10-03 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/architect-microservice-container-applications/communication-in-microservice-architecture | 本文確認 |
| 29 | IntegrationDatabase | Martin Fowler（個人の記事） | 2004-05-25（2015-07-01 更新） | https://martinfowler.com/bliki/IntegrationDatabase.html | 本文確認 |
| 30 | Slack's Incident on 2-22-22 | Slack Engineering（Laura Nolan ほか）。事業者自身の事後報告 | 2022-04-26（2022-04-27 更新） | https://slack.engineering/slacks-incident-on-2-22-22/ | 本文確認 |
| 31 | October 21 post-incident analysis | GitHub（Jason Warner）。事業者自身の事後報告 | 2018-10-30 | https://github.blog/news-insights/company-news/oct21-post-incident-analysis/ | 本文確認 |
| 32 | Cache made consistent | Engineering at Meta（Lu Pan）。**技術記事・自己申告**（事後報告ではない） | 2022-06-08 | https://engineering.fb.com/2022/06/08/core-infra/cache-made-consistent/ | 本文確認 |
| 33 | Contributing to Debezium: Fixing Logical Replication at Scale（前編：Patching the PostgreSQL JDBC Driver、2023-11-09） | Zalando Engineering（Conor Gallagher／前編 Declan Murphy）。**技術記事・自己申告** | 2025-12-19 | https://engineering.zalando.com/posts/2025/12/contributing-to-debezium.html | 本文確認（前編は未読） |

事故を探すのに使った検索語（2026-11-18）：`postmortem replication slot WAL disk full outage Debezium logical replication incident report`／`post-incident review "replication slot" OR "logical replication" WAL disk full outage status page postmortem`／`Facebook "cache invalidation" incident OR "Cache made consistent"`／`"distributed monolith" microservices antipattern shared database synchronous coupling`（learn.microsoft.com・docs.aws.amazon.com・thoughtworks.com・cloud.google.com・martinfowler.com に限定）。
