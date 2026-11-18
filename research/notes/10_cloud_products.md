# 10 クラウドのマネージド製品の公式文書に基づく比較

調査日：2026-11-18

> **このノートの位置づけ**：ここに書くクラウド製品のふるまいは、すべて**公式文書に基づく・未検証**である。実機では測っていない。公称値（SLA・設計目標・「typically」と書かれた値）は実績ではない。ガイドに載せるときは各表に「公式文書に基づく・未検証（確認日 2026-11-18）」と明記する。
>
> 読み取りの方法の限界：ページの取得には要約つきの取得ツールを使った。AWS と Microsoft Learn は本文がそのまま返ったので「本文確認」。Google Cloud・Snowflake・PostgreSQL・CockroachDB は、ツールが本文から抜き出した要約と短い引用を読んだので「本文確認（抜粋）」と書き分ける。後者は数値の読み違いがありうるので、スライドに載せる数値はファクトチェックで原ページを開き直す。

## 1. 問い（このノートが答えること。対応する Part）

- Part 5：OLTP と分析を 1 つの製品で兼ねない理由を、製品の作り（行と列、計算とストレージの分離、料金の軸）で示せるか
- Part 8：複製は同期か非同期か、何台・何ゾーンに書いてから応答するか。フェイルオーバーで何を失うと製品自身が書いているか。分割は自動か、キー設計に何を要求するか
- Part 9：既定の分離レベルと読み取りの整合性は、製品ごとにどう違うか。「PostgreSQL 互換」は分離レベルまで互換か
- Part 12：変更の取り出し（CDC）と分析基盤への取り込みで、「厳密に 1 回」はどの範囲の保証か
- Part 13：共通基盤に据えたとき、離れるときに残る依存は何か（置換性）
- 実機（PostgreSQL 18・CockroachDB）で測ることと、クラウド製品の公式文書の記述を、1 つの表で対応づけられるか

## 2. 標準・定義（節番号）

このノートは製品の比較が主題で、標準の本文は開いていない。定義は他のノート（分離レベル、複製、SLO）に依る。

| 用語 | このノートでの意味 | 出典・確認の深さ |
| --- | --- | --- |
| 分離レベル | SQL 標準の 4 水準（Read Uncommitted／Read Committed／Repeatable Read／Serializable）。製品の「Repeatable Read」は多くがスナップショット分離で、標準の定義と一致しない | ISO/IEC 9075-2 の節番号は未確認（記憶・要確認）。PostgreSQL 18 の文書が自製品の実装をそう説明している [68] |
| 外部整合性 | Spanner の用語。トランザクションが直列に走ったかのようにふるまい、その順序がコミットの観測順と矛盾しない。文書は線形化可能性より強い性質だと説明する | [27] |
| RPO／RTO | RPO＝失ってよいデータの量（時間で測る）。RTO＝復旧までの時間 | Aurora の文書の定義 [4]、BigQuery の文書の定義 [39] |
| SLA | **返金（サービスクレジット）の条件**であって、可用性の実績でも設計目標でもない。各社とも未達時の救済をクレジットに限っている | [7][16][25][35][43] |
| 厳密に 1 回 | 製品ごとに範囲が違う。「ストリーム内でレコードが 1 回だけ現れる」「オフセットが一致したときだけ追記する」「確認応答の後に再配信しない」は別の保証 | [21][37][48][62] |

## 3. 製品ごとの違い（表。公式文書の URL・版・日付）

ページの最終更新日は、AWS の文書と Google Cloud の文書では取得した本文に表示がなかった（確認日 2026-11-18）。SLA のページと Microsoft Learn は日付を記録した。

### 3.1 データモデル・API・整合性

| 製品 | データモデルと API | 読み取りの整合性（選択肢と既定） | 分離レベル（既定） | トランザクションの範囲と上限 |
| --- | --- | --- | --- | --- |
| Aurora PostgreSQL | リレーショナル。PostgreSQL のワイヤプロトコルと SQL | ライターは最新。リーダー（Aurora Replica）は非同期で遅れる [2]。ローカル書き込み転送のセッションでは `SESSION`（既定）／`EVENTUAL`／`GLOBAL` を選ぶ [9] | Aurora のユーザーガイドに Aurora PostgreSQL 専用の分離レベルのページは見つからなかった。AWS の移行プレイブックは既定を Read Committed と書く [10]（検索の抜粋のみ）。書き込み転送のセッションでは Serializable は使えない [9] | PostgreSQL と同じ対話的トランザクション。クラスタは 1 リージョン・ライター 1 台。上限はクラスタボリュームの大きさ（128 TiB、新しい版は 256 TiB）と表の大きさ 32 TiB [6] |
| Aurora Global Database | 同上。プライマリのリージョン 1 つ＋読み取り専用のセカンダリが最大 10 リージョン [3] | セカンダリは非同期で遅れる。文書は遅延を「typically under a second」と書く [3] | 同上 | 書き込みはプライマリのリージョンだけ。書き込み転送でセカンダリから送れる [3] |
| Aurora DSQL | リレーショナル。PostgreSQL 16 互換をうたう。単一リージョンとマルチリージョンのどちらも active-active [11] | 強整合。文書は読み手が常に同じデータを見ると書く [11][15] | **PostgreSQL の Repeatable Read に固定**（スナップショット分離）。変更できない [14]。楽観的並行性制御で、衝突はコミット時に SQLSTATE 40001 で返る [12] | 1 トランザクションで変更できるのは 3,000 行・10 MiB まで、長さ 5 分まで。DDL と DML は別トランザクション、DDL は 1 トランザクションに 1 文。接続は 60 分で切れる [13][14] |
| DynamoDB | キー・バリュー／ドキュメント。独自の HTTP API（`GetItem`・`Query` など）。パーティションキー（＋ソートキー）が必須 [24] | **既定は結果整合**。`ConsistentRead=true` で強整合（表とローカルセカンダリ索引だけ。グローバルセカンダリ索引とストリームは常に結果整合）[18] | 単発の操作は read-committed。`TransactWriteItems`／`TransactGetItems` と単発の書き込み・`GetItem` の間は serializable。`Query`・`Scan`・`BatchGetItem`（全体として）とは read-committed [19] | 1 トランザクションに 100 操作・合計 4 MB まで。同じアカウント・同じリージョンの表に限る。索引には使えない。対話的なトランザクションではなく、1 回の API 呼び出し。冪等トークンは 10 分有効 [19] |
| Spanner | リレーショナル（強い型つけ）。GoogleSQL と PostgreSQL の 2 つの方言 [33][34] | **既定は strong 読み取り**。bounded staleness・exact staleness を選べる。古い読み取りの上限は版の保持期間（既定 1 時間、最長 1 週間）[36] | **既定は Serializable**（外部整合性）。Repeatable Read（スナップショット分離）も選べる [26][27]。Repeatable Read の提供段階（GA かプレビューか）はページに書かれていなかった | 表・行・リージョンをまたぐ読み書きトランザクション。1 コミットあたり 80,000 ミューテーション・100 MiB まで（索引と変更ストリームを含む）[30] |
| BigQuery | 列指向の分析用。GoogleSQL。計算とストレージが別々に伸縮する [45] | クエリは開始時点のスナップショット。タイムトラベルは過去 7 日 [39] | 複数文トランザクションはスナップショット分離。衝突したトランザクションは取り消される [38] | 複数の表・データセット・プロジェクトにまたがれる。1 トランザクションで変更できる表は 100 個、パーティションの変更は 100,000 回まで。恒久的なオブジェクトの DDL は入れられない。変更中は表のロックを持つ [38] |
| Snowflake | 列指向の分析用。独自の SQL 方言。ストレージ・計算（仮想ウェアハウス）・クラウドサービスの 3 層 [50] | 文は開始前にコミットされたデータだけを見る [46] | **Read Committed だけ**（通常の表）[46] | 複数文・複数表。DDL は自動でコミットし、巻き戻せない。`UPDATE`／`DELETE`／`MERGE` は互いに並行できないロックを取る。ロック待ちの既定は 43,200 秒。ハイブリッド表は行単位のロック [46] |

### 3.2 複製・フェイルオーバー・マルチリージョン

| 製品・構成 | 複製の方式（何に書いてから応答するか） | フェイルオーバーの公称値（RPO／RTO） | マルチリージョンの整合性 |
| --- | --- | --- | --- |
| Aurora（1 リージョン） | ストレージ層が 3 つの AZ の 6 つのストレージノードへ**同期**で複製する。DB インスタンスの数とは無関係 [1][2]。「6 つのうち 4 つで書き込みが成立する」という定足数は、読んだ公式文書には書かれておらず、論文 [81] の設計の説明（記憶・要確認）。リーダーインスタンスへの反映は非同期 [2] | リーダーがあれば昇格。文書は「typically restored in less than 60 seconds」と書く。リーダーがなければ同じ AZ で作り直し、「typically takes less than 10 minutes」[2]。AZ 障害ではデータを失わないと書く [2] | — |
| Aurora Global Database | リージョン間は**非同期** [2][3] | 計画的な切り替え（switchover）は同期を待つので RPO 0。障害時のフェイルオーバーは RPO が秒単位の 0 でない値、RTO は分の単位 [4]。Aurora PostgreSQL は `rds.global_db_rpo`（20 秒以上）で上限を決められるが、どのセカンダリも上限内にないとプライマリのコミットを止める [4] | セカンダリは読み取り専用で遅れる。フェイルオーバーでは複製されていない書き込みを失いうる。旧プライマリへの書き込み遮断は最善努力で、文書自身が split-brain の可能性を書く [4] |
| Aurora DSQL | コミットしたログを 3 つの AZ のストレージ複製へ**同期**で複製。マルチリージョンは 2 つのリージョン＋ログだけを持つ証人リージョン [15] | 「フェイルオーバー」という操作がない。文書は複製の遅れによるデータ損失のおそれがないと書く [15]。公称の可用性は単一リージョン 99.99%、マルチリージョン 99.999% [11][15] | どちらのリージョンの端点でも読み書きでき、強整合。マルチリージョンは同じ大陸のリージョンの組に限る [11] |
| DynamoDB（1 リージョン） | パーティションは複数の AZ へ自動で複製 [24]。HTTP 200 は「durably persisted」を意味する [18]。何台に書いてから応答するかは、読んだページには書かれていなかった（論文 [80] の設計の説明に依る。記憶・要確認） | 公称の RPO／RTO は読んだページに見つからなかった | — |
| DynamoDB global tables（MREC・既定） | リージョン間は**非同期**。文書は「typically within a second or less」と書く [20] | RPO は複製の遅れに等しい（通常は数秒）[20] | 同じ項目を複数のリージョンで書くと **last writer wins**。「強整合の読み取り」も、他のリージョンで更新された項目については古い値を返しうる。トランザクションは呼び出したリージョンの中でだけ原子的 [20] |
| DynamoDB global tables（MRSC） | 書き込みは、応答する前に少なくとももう 1 つのリージョンへ**同期**で複製 [20] | RPO 0 をうたう [20] | ちょうど 3 リージョン（複製 3、または複製 2＋証人 1）。強整合の読み取りはどの複製でも最新を返す。**トランザクション API・TTL・ローカルセカンダリ索引は使えない**。他のリージョンで変更中の項目への書き込みは `ReplicatedWriteConflictException` で失敗する。作成後に整合性モードは変えられない [20] |
| Spanner（リージョナル） | Paxos による**同期**複製。投票権のある複製の過半数が合意してコミット。読み書き複製 3 つを別々のゾーンに置く [28][29] | 公称の RPO／RTO は読んだページに見つからなかった。SLA は 99.99% 以上 [35] | — |
| Spanner（デュアルリージョン・マルチリージョン） | 同じ Paxos。定足数がリージョンをまたぐので書き込みの遅延が増える [29] | デュアルリージョンは RPO 0 と書く。手動のフェイルオーバーは「usually completes within one minute」、自動は最長 45 分かかりうると書く [29]。SLA は 99.999% 以上 [35] | 外部整合性はリージョンをまたいでも同じ。既定のリーダーリージョンが書き込みを受ける [29] |
| BigQuery | データを 2 つのゾーンへ**同期**で書く。ゾーン障害では 1 分以内に別のゾーンへ回すと書く [39] | リージョンの障害では、そのリージョンのデータを失いうる。別リージョンへの自動バックアップはない。「マルチリージョン」というロケーションはリージョン間の冗長性を意味しない [39] | リージョン間のデータセット複製と、マネージド災害復旧は別の機能として選ぶ [39] |
| Snowflake | リージョン内の耐久性について、読んだ複製のページには記述がなかった [51] | アカウントやデータベースの複製は予定された更新（非同期）。障害時の遅れは最大で更新間隔の 2 倍と書く [51]。明示の RPO／RTO の目標値は書かれていない | フェイルオーバーとクライアントの付け替えは Business Critical 以上の版が必要 [51] |
| AlloyDB（比較用） | プライマリは別ゾーンに待機ノード。リージョン間のセカンダリクラスタへは非同期 [60] | フェイルオーバーの所要時間は概要のページに書かれていなかった | — |
| Cosmos DB（比較用） | リージョン内は 4 つの複製のうち 3 つ（ローカルの過半数）に書く。Strong だけは全リージョンで同期（グローバルの過半数）[57] | リージョン障害の RPO：Strong は 0、Bounded staleness は K と T（複数リージョンの最小は 100,000 回または 300 秒）、Session・Consistent prefix・Eventual は 15 分未満 [57][59] | **5 つの整合性レベル**（Strong／Bounded staleness／Session／Consistent prefix／Eventual）。複数リージョン書き込みでは Strong を選べない [57]。衝突は衝突フィードと解決方針で扱う [59] |

### 3.3 分割の方式と主要な制限値

| 製品 | 分割 | キー設計の制約とホットキーへの対処 | 主な制限値 |
| --- | --- | --- | --- |
| Aurora PostgreSQL | 分割しない（ライター 1 台、共有ストレージ）。水平分割は別機能の Aurora Limitless Database | — | クラスタボリューム 128 TiB（PostgreSQL 17.5・16.9・15.13 以降は 256 TiB）、表 32 TiB、リーダー 15 台 [6] |
| Aurora DSQL | 主キーの範囲とアクセスの形で自動に分割・統合する [15] | ランダムな主キーを勧める。単一のキーや狭い範囲への集中を避ける [12][14] | 行 2 MiB、列 1 MiB、主キーの合計 1 KiB、1 トランザクション 3,000 行・10 MiB・5 分、表 1,000 個、スキーマ 10 個、データベース 1 個、ストレージは既定 10 TiB（申請で 256 TiB）、接続 10,000 [13] |
| DynamoDB | パーティションキーのハッシュで自動に分割。容量かスループットが足りなくなると増える [24] | パーティション 1 つあたり毎秒 3,000 読み取り単位・1,000 書き込み単位が設計上の上限。キーをまたいで一様な負荷になるよう設計する。書き込みシャーディングを勧める [23] | 項目 400 KB [19]、表あたりの既定のスループット枠は読み書きとも 40,000 単位（引き上げ可）、グローバルセカンダリ索引 20、ローカルセカンダリ索引 5 [22] |
| Spanner | 主キーの範囲で分割。大きさと負荷で分割点を自動で足す [33] | 単調に増えるキーはホットスポットを作る。ハッシュ、キーの列の入れ替え、UUID v4、ビット反転を勧める。インターリーブは後から外せない [33] | セル 10 MiB、キー 8 KiB、表 5,000、列 1,024、索引は表あたり 128、ノードあたり 10 TiB、変更ストリームはデータベースあたり 10 [30] |
| BigQuery | 利用者がパーティション（日付など）とクラスタ化を宣言する | — | 行 100 MB、列 10,000、パーティション 10,000、同じ表で同時に走る変更系 DML は 2、待ち行列は 20 [44] |
| Snowflake | マイクロパーティション（非圧縮で 50〜500 MB）へ自動で分ける。利用者は分割を定義しない。クラスタリングキーは任意 [56] | — | 読んだページに行や表の上限値はなかった |
| Cosmos DB（比較用） | パーティションキーで論理パーティションに分ける | 論理パーティション 20 GB、パーティションあたり 10,000 RU/s。超えるなら階層パーティションキーへ作り直す [58] | 項目 2 MB、トランザクションバッチは 100 操作・同じパーティションキーに限る [58] |

スロットリングは、DynamoDB（スループット枠・パーティションの上限）、Cosmos DB（RU の超過、Bounded staleness の遅れ超過で書き込みを絞る [57]）、BigQuery（DML の待ち行列 [44]）、Aurora の `rds.global_db_rpo`（コミットを止める [4]）のように、**整合性や遅れの上限を守るために書き込みを止める**形でも現れる。

### 3.4 変更の取り出し（CDC）と取り込み

| 製品・機能 | しくみ | 保持・順序・配信の保証（文書の言葉） | 注意 |
| --- | --- | --- | --- |
| DynamoDB Streams | 項目単位の変更を時系列に記録 | 保持は 24 時間。各レコードはストリームに「exactly once」現れ、項目ごとに変更の順で並ぶ。順序の保証は項目（主キー）単位で、パーティション全体ではない [21] | 「1 回だけ現れる」はストリームの中の話で、読み手の処理が 1 回という意味ではない。トランザクションの変更は別々の時点に現れ、他のトランザクションと混ざる。読み手は原子性を仮定できない [19]。シャードの同時読み手は 2 まで [21][22] |
| Aurora PostgreSQL 論理レプリケーション | PostgreSQL の論理レプリケーション（`pgoutput`、`wal2json` など）[8] | PostgreSQL と同じ（スロット。障害後に重複しうる [71]） | PostgreSQL 16 のリードレプリカからの論理デコードは Aurora では使えない [8]。Global Database の切り替え後はスロットの管理が要る [4] |
| Aurora ゼロ ETL 統合 | Aurora から Redshift／SageMaker のレイクハウスへ、AWS が管理するパイプラインで複製 [5] | 「near real-time」としか書かれていない。配信の保証の語はない [5] | 同じリージョン内だけ。主キーのない表は失敗状態になる。DDL で表の再同期が走り、その間は問い合わせできない。Global Database のフェイルオーバーで統合は無効になり、作り直す。初期の投入に 20〜25 分以上 [5] |
| Aurora DSQL の CDC | 行の変更を Kinesis Data Streams へ送る | 本文は開いていない。検索結果の要約によれば 2026-07-08 に一般提供、レコードは行の最終状態 [17] | クォータの表に「CDC streams per cluster 5」がある [13]。詳細は未確認 |
| Spanner change streams | 表・列を指定して変更を流す。Dataflow（Beam）、Kafka コネクタ、API、Datastream で読む [31] | 保持は 1〜30 日、既定 7 日と読めた [31]。配信の保証と順序の語は読んだページになかった | 保持日数は古い資料（1〜7 日）と違う。原ページで再確認する。変更ストリームの書き込みはコミットの大きさの上限に数えられる [30] |
| BigQuery Storage Write API | gRPC のストリームで取り込む。既定・committed・pending・buffered の 4 種 [37] | **既定のストリームは at-least-once**。「厳密に 1 回」は、アプリが作ったストリームで**オフセットを指定したとき**に、次の追記位置と一致した場合だけ書くことで実現する [37] | CDC の取り込み（`_CHANGE_TYPE` の `UPSERT`／`DELETE`）は既定のストリームを使い、主キーの宣言が要るが、**主キーは強制されない**。一意性は送り手の責任 [41] |
| Snowflake Streams | 表のオフセットを持ち、版の履歴から変更を返す | オフセットは、ストリームを DML トランザクションで消費してコミットしたときだけ進む。「exactly-once」という語は使っていない [47] | 保持期間を過ぎるとストリームは stale になり作り直し（延長は既定で最大 14 日）。読み手ごとに別のストリームを作る [47] |
| Snowpipe Streaming | 行を直接、表へ流し込む | Elastic Channels は at-least-once で順序の保証なし。Named Channels はオフセットトークンで、チャネル内は順序つき・「exactly-once」[48] | 遅延「as low as 5 seconds」やスループットは設計目標で保証ではないとページ自身が書く [48] |
| Snowflake Dynamic Tables | 問い合わせの結果を保持し、自動で更新 | 目標の遅れは最小 60 秒。下流の表は入力の一貫したスナップショットを映す [49] | 60 秒より新しいデータが要る用途には向かないと書く [49] |
| Pub/Sub（比較用） | メッセージ配信 | 既定は at-least-once・順序の保証なし [63]。厳密に 1 回の配信は pull 購読だけ、同じリージョンで接続したときだけ。push と export は対象外 [62] | 「確認応答に成功した後は再配信しない」という定義で、処理の副作用が 1 回という意味ではない [62] |
| Event Hubs（比較用） | パーティションつきの追記ログ。Kafka プロトコル（1.0 以降）で読み書きできる [65] | 保持は Standard で最長 7 日、Premium・Dedicated で 90 日。チェックポイントの保存は読み手の責任 [65] | Standard はパーティション数を後から変えられない [65] |
| Kinesis Data Streams／MSK（比較用） | Kinesis は 3 つの AZ へ同期で複製、保持は既定 24 時間・最長 365 日。MSK は Kafka のリーダー・フォロワー複製、MSK Replicator はクラスタ間の非同期 [66][67] | 検索の抜粋のみ | MSK Replicator は非同期なので、切り替え先で重複しうると AWS のブログが書く（自己申告）[67] |

### 3.5 スキーマ変更のふるまい

| 製品 | 文書の記述 | 出典 |
| --- | --- | --- |
| Aurora PostgreSQL | PostgreSQL と同じ（ロックの水準は PostgreSQL の文書に依る）。Aurora 固有の記述は調べていない。ゼロ ETL 統合があると DDL が再同期を起こす | [5] |
| Aurora DSQL | DDL は 1 トランザクションに 1 文、DML と混ぜられない。索引は `CREATE INDEX ASYNC` で作る。DDL は他のセッションに SQLSTATE 40001（OC001）を起こしうる。`TRUNCATE`・一時表・トリガ・PL/pgSQL は使えない | [12][14] |
| DynamoDB | キー以外の属性にスキーマがない。キーのスキーマは作成時に決まる。後から足せるのはグローバルセカンダリ索引（調べた範囲で、キーの変更手順の記述は未確認） | [22][24] |
| Spanner | スキーマ更新は停止を要しないと書く。`NOT NULL` の追加などは既存データの検証が走り、数分から何時間もかかりうる。その間も読み書きは続けられる | [32] |
| BigQuery | 列の追加（`NULLABLE`／`REPEATED` だけ）、`REQUIRED` の緩和、列名の変更、一部の型の拡張はその場でできる。厳しくする変更・途中への挿入・その他の型変更は表の作り直し | [40] |
| Snowflake | 列の削除はメタデータだけの操作。DDL は自動コミットで巻き戻せない。読み込み時のスキーマ進化（`ENABLE_SCHEMA_EVOLUTION`、既定は無効、1 回の読み込みで足せる列は既定 100）がある | [46][55] |

### 3.6 SLA（返金条件。実績ではない）

| 製品 | 公称値と条件 | ページの日付 | 出典 |
| --- | --- | --- | --- |
| Aurora | 2 つ以上の AZ にインスタンスがあるクラスタは 99.99%、単一 AZ は 99.9%。Global Database と DSQL はこの SLA に出てこない | 2025-03-12 | [7] |
| Aurora DSQL | 単一リージョン 99.99%、マルチリージョン 99.999% | 2025-05-27 | [16] |
| DynamoDB | 標準 99.99%、Global Tables 99.999%。可用性は 5 分ごとのエラー率（500・503）で測る。Global Tables の SLA は、リージョン内の表がすべてグローバル表であること、障害時に切り替えを試みることが条件 | 2025-05-14 | [25] |
| Spanner | マルチリージョン・デュアルリージョン 99.999% 以上、リージョナル 99.99% 以上（ストックホルムは 99.95%） | 日付は取得できず | [35] |
| BigQuery | 99.99%（Standard edition は 99.9%）。抜粋から読めた範囲 | 日付は取得できず | [43] |
| Snowflake | SLA のページは 403 で開けなかった。検索の抜粋では、月間可用性とエラー率のしきい値の組でクレジットを決める表がある | 未確認 | [54] |
| AlloyDB | 高可用性を有効にしたインスタンスで 99.99%（ストックホルムは 99.95%）。停止の定義は「接続要求がすべて失敗する」 | 日付は取得できず | [61] |
| Cosmos DB | 読んだ信頼性のページに数値は見つからなかった。SLA の本文は未確認 | — | [59] |
| MSK | マルチ AZ の構成で 99.9% | 検索の抜粋のみ | [67] |
| Pub/Sub | 抜粋では数値の欄が空で読めなかった。停止の定義は「発行の要求が 1 つも成功しない」 | 未確認 | [64] |

- どの SLA も、未達のときの救済はクレジット（将来の請求からの減額）で、損害の補償ではない。Google の SLA は「sole and exclusive remedy」と書く [35][43]
- 停止の定義が狭い（「すべての接続が失敗」「発行が 1 つも成功しない」）ものがあり、部分的な劣化は数えられない [61][64]
- 文書の本文にある「99.99%」（DSQL の概要など [11]）は設計上の公称値で、SLA の条件とは別に書かれている

### 3.7 置換性：標準への互換と、離れるときに残る依存

| 製品 | 標準への互換 | 非互換・独自の前提（離れるときに残るもの） |
| --- | --- | --- |
| Aurora PostgreSQL | PostgreSQL のエンジンそのものに近い。論理レプリケーション・`pglogical` が使える [8] | ストレージ層と Global Database、ゼロ ETL、書き込み転送の整合性モードは Aurora 固有。分離レベルはライターとリーダーで前提が違いうる（下の Jepsen の項） |
| Aurora DSQL | PostgreSQL 16 のワイヤプロトコルと SQL の一部 [11] | 分離レベルが Repeatable Read 固定、楽観的並行性制御で再試行が前提、3,000 行・5 分の上限、トリガ・PL/pgSQL・一時表・`TRUNCATE` なし、データベースは 1 個、照合順序は `C` だけ [13][14]。**PostgreSQL 向けに書いたアプリは、ロック待ちを前提にした箇所と大きなバッチを書き直す** |
| DynamoDB | 標準の問い合わせ言語に準拠しない独自 API | キー設計（アクセスの形を先に決める）、結果整合が既定、100 操作のトランザクション、Streams の 24 時間。MRSC ではトランザクション API が使えないので、**整合性モードを変えると使える API が変わる** [19][20] |
| Spanner | GoogleSQL、または PostgreSQL 方言（PostgreSQL の SQL の一部）[34] | PostgreSQL インターフェースは拡張・ユーザー定義型・ストアドプロシージャを支えない。移行には手直しが要ると文書自身が書く [34]。インターリーブ、ミューテーションの上限、外部整合性（TrueTime）を前提にした設計は他へ持ち出せない |
| BigQuery | GoogleSQL。Iceberg のマネージド表は、利用者のバケットに Parquet と Iceberg のメタデータで置き、他のエンジンから読める [42] | 通常の表は独自の保存形式。Iceberg のマネージド表にも制限がある（パーティション進化なし、同時の変更系 DML は 1、メタデータの出力は別操作で直近 90 分のストリーム分を含まないことがある）[42] |
| Snowflake | 独自の SQL 方言。Iceberg 表（Snowflake がカタログ、または外部カタログ）を持てる [52] | 通常の表は Snowflake が管理する保存先にあり独自形式 [50]。Snowflake をカタログにした Iceberg 表へは、外部のクライアントから追記・削除・upsert ができない [52]。Streams・Dynamic Tables・タスクは独自機能 |
| Cosmos DB | NoSQL の独自 API のほか、MongoDB・Cassandra などのワイヤプロトコル互換 API [57] | 整合性レベルと RU の考え方、20 GB の論理パーティション |
| Event Hubs | Kafka プロトコル互換（1.0 以降）[65] | チェックポイントやパーティション数の扱いは Kafka と同じではない。互換の範囲の一覧は未確認 |

### 3.8 料金の決まり方の軸（数値は書かない）

| 製品 | 軸 | 出典 |
| --- | --- | --- |
| Aurora | インスタンス（プロビジョニングまたはサーバーレス）＋ストレージ（使った分）＋I/O（Standard は要求数に課金、I/O-Optimized は I/O 込み）。2 つの構成は切り替えられる | [1] |
| Aurora DSQL | サーバーレス。CDC は流したバイト数と Kinesis の料金（検索の要約のみ） | [17] |
| DynamoDB | オンデマンド（要求単位）かプロビジョニング（容量単位）。強整合の読み取りは結果整合の 2 倍、トランザクションは項目ごとに 2 倍の読み書き。グローバル表は複製先でも書き込みを消費する | [18][19][20] |
| Spanner | 計算容量（ノード／処理ユニット）＋ストレージ。構成（リージョナル／マルチリージョン）で変わる。料金のページは未確認 | [29]（構成のみ） |
| BigQuery | 問い合わせはスキャン量課金（オンデマンド）か容量（スロット、エディション）。ストレージは別。料金のページは取得できず、この行は記憶・要確認 | 記憶・要確認 |
| Snowflake | 計算はクレジット（仮想ウェアハウスは秒課金、起動ごとに最低 60 秒）、ストレージは TB あたりの定額、クラウドサービス層は日次でウェアハウス使用量の 10% を超えた分、リージョン外への転送 | [53] |
| Event Hubs | パーティション数ではなく、スループット単位・処理単位・容量単位 | [65] |

### 3.9 OSS の実機製品との対応（公式文書の記述のみ。未検証）

| 項目 | PostgreSQL 18 | CockroachDB（文書は v26.4） | Aurora PostgreSQL | Aurora DSQL | Spanner | DynamoDB |
| --- | --- | --- | --- | --- | --- | --- |
| 既定の分離レベル | Read Committed。Repeatable Read はスナップショット分離、Serializable は SSI で 40001 の再試行が要る [68] | Serializable。Read Committed も選べる。Serializable では 40001 をクライアントが再試行する [72] | Aurora 固有のページは見つからず。AWS の移行プレイブックは Read Committed と書く [10]（抜粋のみ） | PostgreSQL の Repeatable Read に固定。衝突は 40001 [12][14] | Serializable（外部整合性）。Repeatable Read も選べる [26] | 単発の操作は read-committed。トランザクション API は serializable（相手の操作による）[18][19] |
| 読み取りの整合性 | プライマリは最新。スタンバイは既定で非同期のため遅れる [69] | 既定はリースホルダーからの強整合。follower reads（exact／bounded staleness）は古いデータを読む。exact は 4.2 秒以上前 [74] | ライターは最新、リーダーは非同期で遅れる。書き込み転送で `SESSION`／`EVENTUAL`／`GLOBAL` [2][9] | 強整合（どの AZ・リージョンの端点でも）[15] | 既定は strong。bounded／exact staleness を選べる [36] | 既定は結果整合。`ConsistentRead` で強整合（表とローカルセカンダリ索引だけ）[18] |
| 複製 | ストリーミング複製は既定で非同期。`synchronous_standby_names` と `synchronous_commit`（`remote_write`／`on`／`remote_apply`）で同期。`FIRST n`（優先順）と `ANY n`（定足数）[69] | Raft。レンジごとに複製の定足数が合意してからコミット。3 が定足数を作れる最小の数 [73] | ストレージ層が 3 AZ・6 ノードへ同期。リーダーへは非同期。リージョン間（Global Database）は非同期 [1][2][3] | 3 AZ へ同期。マルチリージョンも同期（証人リージョンつき）[15] | Paxos で同期。投票複製の過半数 [28] | 複数 AZ へ自動複製。台数の記述は読んだページになし。グローバル表は MREC が非同期、MRSC が同期 [20][24] |
| フェイルオーバー | 昇格は `pg_ctl promote`／`pg_promote()` で明示に行う。自動フェイルオーバーの記述は読んだページ（27.2 相当）になし。非同期では未送の WAL を失う [69] | リースの移動は「within a few seconds」。数値の一部は社内テストに基づくと書く（自己申告）[73] | リーダーがあれば通常 60 秒未満、なければ通常 10 分未満と書く。Global Database は RPO が秒単位、RTO が分単位 [2][4] | フェイルオーバーの操作がない。自動で健全な側へ回すと書く [11][15] | リージョナルの RPO／RTO は公式文書に記述なし（2026-11-18、読んだ範囲）。デュアルリージョンは RPO 0 [29] | 単一リージョンの RPO／RTO は公式文書に記述なし（2026-11-18、読んだ範囲）。MREC の RPO は複製の遅れ、MRSC は 0 [20] |
| CDC | 論理デコードとレプリケーションスロット。通常は各変更を 1 回流すが、障害後は重複しうる。使われないスロットは WAL を溜める。スロットをスタンバイへ同期できる [71] | changefeed。行の変更を at-least-once で届ける。同じキーの最初の送出は時刻順 [75] | PostgreSQL の論理レプリケーション、ゼロ ETL 統合 [5][8] | Kinesis Data Streams への CDC（検索の要約のみ）[17] | change streams。保持 1〜30 日（既定 7 日と読めた）[31] | DynamoDB Streams。保持 24 時間、項目単位の順序 [21] |
| 主な制限 | 表 32 TB、フィールド 1 GB、列 1,600、行は 8 KB のページに収める（大きな値は TOAST）[70] | 行の大きさのガードレール（記録 64 MiB、エラー 512 MiB）、ロック追跡のバイト数の既定 4 MiB。検索の要約のみで、版による違いあり [76] | クラスタ 128 TiB（新しい版は 256 TiB）、表 32 TiB、リーダー 15 台 [6] | 1 トランザクション 3,000 行・10 MiB・5 分、行 2 MiB、接続 60 分 [13] | 1 コミット 80,000 ミューテーション・100 MiB、セル 10 MiB、キー 8 KiB [30] | 項目 400 KB、トランザクション 100 操作・4 MB、パーティションあたり毎秒 3,000 読み取り・1,000 書き込み単位 [19][23] |

### 3.10 Jepsen の分析と論文の扱い

- **Amazon RDS for PostgreSQL 17.4（Jepsen、2025-04-29、追記 2025-05-03）**[77]：対象は RDS for PostgreSQL の**マルチ AZ クラスタ**（13.15〜17.4）で、**Aurora ではない**。障害は注入していない。健全な状態でも数分おきに Long Fork などの異常が出て、スナップショット分離を満たさなかった。異常はリーダー端点（セカンダリ）への読み取り専用の問い合わせを含む。Jepsen は、より弱い Parallel Snapshot Isolation に当たる可能性を述べている。追記によれば原因は、プライマリがトランザクションを見えるようにする順序と、セカンダリが WAL の順で見えるようにする順序のずれで、PostgreSQL の側のしくみに由来する。勧めは、重要な読み取りをライター端点に寄せること、不変条件を実験で確かめること。報告自身が「粗い調査」で不具合の不在は証明できないと書く
  - このノートでの使い方：**「レプリカを足すと、分離レベルの保証は 1 台のときと同じではない」**ことの、マネージド製品での例。Aurora に同じ異常があるかは、この報告からは言えない
- Jepsen の一覧 [78] に、Aurora・Aurora DSQL・DynamoDB・Spanner・Snowflake・BigQuery・Cosmos DB の分析は**ない**（2026-11-18 時点）。CockroachDB は beta-20160829（2017-02-16）、PostgreSQL は 12.3（2020-06-12）で、どちらも古い版なので結論の唯一の根拠にしない
- 論文は**設計の説明**として扱い、現行の製品のふるまいの根拠にしない（本ノートでは本文を開き直していない。題名と発表の場は記憶・要確認）
  - Spanner（OSDI 2012）[79]：TrueTime と外部整合性の設計
  - DynamoDB（USENIX ATC 2022）[80]：現行のサービスの設計と運用の説明
  - Aurora（SIGMOD 2017・2018）[81][82]：ストレージ層の 6 複製と定足数の設計。「4/6 で書き込み成立」はここに依る
  - Snowflake（SIGMOD 2016）[83]：ストレージと計算の分離の設計

## 4. 事故・失敗例（一次報告）

このノートでは事業者の事後報告は調べていない（Part 14 のノートに任せる）。公式文書が自分で書いている「失いうるもの」を、事故の型の予告として拾う。

| 文書が書いている失敗の形 | 製品 | 出典 |
| --- | --- | --- |
| フェイルオーバーで、複製されていない書き込みを失う。旧プライマリへの書き込み遮断は最善努力で、split-brain がありうる | Aurora Global Database | [4] |
| RPO の上限を設定すると、遅れが上限を超えたときにプライマリのコミットが止まる | Aurora Global Database（PostgreSQL） | [4] |
| 同じ項目を複数リージョンで書くと、後の書き込みが勝ち、前の書き込みは黙って消える。他のリージョンでは、トランザクションの途中の状態が見える | DynamoDB global tables（MREC） | [20] |
| リージョンの障害で、そのリージョンのデータを失いうる。「マルチリージョン」のロケーションは冗長性ではない | BigQuery | [39] |
| DDL で表の再同期が走り、複製先の表が問い合わせ不能になる。フェイルオーバーで統合が無効になる | Aurora ゼロ ETL 統合 | [5] |
| 保持期間を過ぎるとストリームが stale になり、作り直しになる（取りこぼした変更は取り戻せない） | Snowflake Streams | [47] |
| ストリームの保持は 24 時間。読み手がそれ以上止まると変更を失う | DynamoDB Streams | [21] |
| 主キーを宣言しても強制されない。重複は送り手の責任 | BigQuery の CDC 取り込み | [41] |

## 5. 権威の推奨と位置づけ（規範か任意か）

- このノートで読んだのは製品の公式文書（優先順位 3）と Jepsen の分析（優先順位 4）で、Well-Architected などの権威の文書は開いていない。製品の文書の中の「We recommend」は、**その製品を使う人に向けたベンダーの任意の推奨**であって、規範ではない
- 文書の中の推奨の例：Aurora はリーダーを 2 つ以上の AZ に置く [2]。DynamoDB はトランザクションを必要なときだけ小さく使う [19]。DSQL はランダムな主キーと冪等な再試行を勧める [12]。Spanner は単調増加のキーを避ける [33]
- Jepsen の勧め（重要な読み取りはライター端点へ、不変条件は実験で確かめる）[77] は、独立した検証者の助言で、任意

## 6. 設計判断の分かれ目（何を選ぶと何を得て何を失うか。表）

| 判断 | 選ぶもの | 得るもの | 失うもの | 根拠 |
| --- | --- | --- | --- | --- |
| リージョン間の複製 | 非同期（Aurora Global Database、DynamoDB MREC） | 書き込みが速い。遠いリージョンも組める | 障害時に秒単位の書き込みを失う。MREC は同時更新が黙って上書きされる | [4][20] |
| リージョン間の複製 | 同期（Spanner マルチリージョン、DSQL マルチリージョン、DynamoDB MRSC、Cosmos DB Strong） | RPO 0 をうたえる。どこで読んでも最新 | 書き込みの遅延がリージョン間の往復に比例。DSQL は同じ大陸だけ、MRSC は 3 リージョン固定でトランザクション API なし、Cosmos DB は複数リージョン書き込みと両立しない | [11][20][29][57] |
| 分離レベルの既定 | 弱い既定（PostgreSQL・Aurora の Read Committed、Snowflake の Read Committed） | 再試行がいらない。既存のアプリがそのまま動く | 書き込みスキューなどの異常を、アプリ側で防ぐ | [46][68] |
| 分離レベルの既定 | 強い既定（Spanner・CockroachDB の Serializable） | 異常を DB が防ぐ | 競合時の中断と再試行をアプリが実装する | [26][72] |
| 並行性の制御 | 楽観的（DSQL、Spanner の既定の読み取り） | ロック待ちとデッドロックがない | 競合はコミット時に失敗する。再試行と冪等性が前提。DSQL は `SELECT FOR UPDATE` も「待つ」のではなく「後で失敗する」 | [12][26] |
| 「PostgreSQL 互換」 | Aurora PostgreSQL | 互換の幅が広い | ライター 1 台。リージョン間は非同期 | [2][3] |
| 「PostgreSQL 互換」 | Aurora DSQL／Spanner の PostgreSQL 方言 | 水平に伸び、同期で複製 | 互換は一部。分離レベル・上限・使えない機能が違い、移行に手直しが要る | [14][34] |
| CDC の取り出し口 | 製品の組み込み（DynamoDB Streams、ゼロ ETL、Snowflake Streams） | 運用が軽い | 保持が短い、行き先が固定、障害時に作り直し。保証の語が文書にないものがある | [5][21][47] |
| CDC の取り出し口 | 標準に近い口（PostgreSQL の論理レプリケーション＋ Debezium、Kafka コネクタ） | 行き先を選べる。置換しやすい | スロットや重複の扱いを自分で持つ | [8][71] |
| 分析の保存形式 | 製品の独自形式 | 機能が全部使える | 離れるときに全量の書き出しが要る | [50] |
| 分析の保存形式 | Iceberg（BigQuery・Snowflake のマネージド表） | 利用者の保存先に開いた形式で残り、他のエンジンから読める | 書き込みは実質その製品経由。機能に制限がある | [42][52] |
| 料金の軸 | スキャン量・要求数に課金（オンデマンド） | 使わなければ払わない | 負荷と費用が直結し、ホットキーや全走査が請求に出る | [18][53] |
| 料金の軸 | 容量を確保（プロビジョニング、スロット、ウェアハウス） | 費用が読める | 余りを払う。足りないとスロットリング | [20][22] |

## 7. 設計レビューで問うこと（問い｜なぜ問うか｜危ない兆候）

| # | 問い | なぜ問うか | 危ない兆候 |
| --- | --- | --- | --- |
| 1 | この製品の既定の分離レベルは何で、設計はそれを前提にしているか | 既定は製品ごとに違い、同じ名前でも中身が違う [26][46][68] | 「トランザクションだから安全」とだけ書いてある |
| 2 | 「PostgreSQL 互換」のどの範囲に依存しているか。非互換の一覧を読んだか | DSQL は分離レベル固定・3,000 行・5 分、Spanner は拡張やストアドなし [14][34] | 互換の根拠が製品ページの見出しだけ |
| 3 | 読み取りはどこから読み、どれだけ古くてよいか | 既定が結果整合の製品がある（DynamoDB）。レプリカは遅れる [2][18] | 書いた直後に読む処理が、リーダー端点や索引を読んでいる |
| 4 | レプリカを読む処理に、分離レベルの保証を仮定していないか | RDS のマルチ AZ クラスタで、リーダーを含む読み取りがスナップショット分離を破った [77] | 不変条件の検査をリーダー側で走らせている |
| 5 | 応答済みの書き込みは、何台・何ゾーン・何リージョンに書かれているか | 同期か非同期かで、失うものが決まる [1][4][20][28] | 「マルチリージョンだから安全」とだけ書いてある |
| 6 | フェイルオーバーの RPO／RTO は、文書の「typically」か、契約の SLA か、自分で測った値か | 3 つは別物。SLA は返金条件 [2][4][7] | SLA の数字を可用性の設計目標として引用している |
| 7 | 障害時の切り替えで、旧プライマリへの書き込みを誰が止めるか | 遮断は最善努力だと文書が書く製品がある [4] | 切り替え手順にアプリの停止や DNS の TTL がない |
| 8 | マルチリージョンで同じ項目を 2 か所から書くと、どうなるか | last writer wins は黙って上書きする [20] | 「衝突は起きない前提」と書いてある |
| 9 | 整合性のモードを変えると、使える API や機能が変わらないか | MRSC ではトランザクション API・TTL・ローカルセカンダリ索引が使えない。後から変えられない [20] | モードを後で切り替える計画になっている |
| 10 | キー設計はアクセスの形から決めたか。最も熱いキーの負荷は上限の何割か | パーティションあたりの上限がある。単調増加のキーは偏る [23][33][58] | 主キーが連番・時刻。上限との比較がない |
| 11 | 1 トランザクション・1 項目・1 コミットの上限に、最大のバッチは収まるか | 100 操作・4 MB、3,000 行・10 MiB、80,000 ミューテーションなど [13][19][30] | 夜間バッチの件数が上限と比べられていない |
| 12 | 再試行は誰が書き、冪等か | 強い分離レベルや楽観的制御は 40001 を返す [12][72] | 40001 を汎用のエラーとして扱っている |
| 13 | CDC の保持期間より長く読み手が止まったら、どう復旧するか | 24 時間（DynamoDB Streams）、stale（Snowflake Streams）[21][47] | 再構築の手順がなく、ストリームを正にしている |
| 14 | 「厳密に 1 回」は、どの区間の、どの条件での保証か | オフセット指定のとき、同じリージョンの pull のとき、チャネル内、など条件つき [37][48][62] | 既定の設定のまま「重複なし」と書いてある |
| 15 | 取り込み先は主キーの一意性を強制するか | BigQuery の CDC は強制しない [41] | 重複の検査が下流にない |
| 16 | DDL を流すと、複製・CDC・派生の表に何が起きるか | 再同期や検証で、長く使えなくなりうる [5][32] | スキーマ変更の手順に下流の確認がない |
| 17 | SLA の条件（構成、停止の定義、除外）を満たす構成か | 単一 AZ では値が下がる。停止の定義が狭い [7][25][61] | SLA の値だけを書き、条件を書いていない |
| 18 | この製品をやめるとき、何を書き直すか。データは開いた形式で取り出せるか | 独自 API・独自の整合性の前提・独自の保存形式が残る [20][34][42][52] | 出口の手順と費用がどこにもない |
| 19 | 費用は何に比例するか（スキャン量、要求数、確保した容量、I/O） | 軸が違うと、同じ負荷でも請求の出方が違う [1][18][53] | 見積もりが平均の負荷だけで、最悪の問い合わせがない |
| 20 | この比較の根拠は、公式文書か、ベンダーのブログか、自分の実測か | 公称値と実績を混ぜると判断を誤る | 性能の数字の出どころが書かれていない |

## 8. ケーススタディで測れること・測れないこと

| 区分 | 内容 |
| --- | --- |
| 測れる（題材 D） | PostgreSQL 18 の分離レベルごとの異常、同期・非同期の複製で昇格時に失う応答済みコミットの件数、スタンバイでの古い読み取り。3.9 の表の PostgreSQL 18 の列を実測で裏づけられる |
| 測れる（題材 D） | CockroachDB の既定（Serializable）での再試行の回数、follower reads の古さ。3.9 の表の CockroachDB の列（文書は v26.4。実機の版を着手時に合わせて確かめる） |
| 測れる（題材 A・B） | PostgreSQL の論理デコード＋ Debezium での重複・欠落・順序。スロットが WAL を溜めるふるまい。CDC の保持を超えて読み手が止まったときの再構築 |
| 類推にとどまる | 「レプリカを読むと分離レベルの保証が変わる」ことは、PostgreSQL のプライマリ＋スタンバイで Jepsen と同じ型の検査を小さく再現できる可能性がある。ただし RDS のマルチ AZ クラスタそのものではない |
| 測れない | Aurora のストレージ層、Aurora Global Database・DynamoDB global tables・Spanner マルチリージョンのリージョン間のふるまい、DSQL の楽観的制御、BigQuery・Snowflake の取り込みの保証、SLA の実績、料金。**すべて「公式文書に基づく・未検証」と書く** |
| 測れない | 単一ホストなので、時計のずれとリージョンをまたぐ障害。Spanner の外部整合性や DynamoDB の last writer wins のふるまいは再現できない |

## 9. 未確定・要確認

- **Aurora PostgreSQL の分離レベル**：Aurora ユーザーガイドに PostgreSQL 版の専用ページを見つけられなかった（Aurora MySQL にはある）。既定が Read Committed という記述は移行プレイブックの検索抜粋だけ。リーダーインスタンスで使える分離レベルも未確認
- **Aurora の定足数（4/6 で書き込み、3/6 で読み取り）**：読んだ公式文書には「6 ノードへ同期」としかない。数は論文の記憶で、原文を開き直す
- **DynamoDB の 1 リージョン内の複製の台数と、応答までに書く数**：公式文書に記述を見つけられなかった。論文の記憶では 3 複製のうち過半数（要確認）
- **Spanner change streams の保持（1〜30 日、既定 7 日）**：要約ツール経由の読み取り。原ページで再確認する
- **Spanner の Repeatable Read の提供段階**、**Spanner の PostgreSQL 方言の非互換の一覧**（既知の問題のページは開いていない）
- **Spanner デュアルリージョンの「自動フェイルオーバーは最長 45 分」**：要約ツール経由。原文の条件を確かめる
- **Snowflake の SLA**：ページが 403 で開けず、公称の可用性の値を確かめられなかった。**Cosmos DB・Pub/Sub・Event Hubs・Kinesis の SLA** も本文は未確認
- **Snowflake のリージョン内の耐久性（複数 AZ）**：読んだページに記述なし
- **BigQuery・Spanner の料金の軸**：料金のページを取得できなかった
- **Aurora DSQL の CDC**：検索の要約だけ。本文（cdc-streams.html）は未読
- **CockroachDB の制限値**：既知の制限のページが 404。検索の要約によれば、ロック追跡の既定値は版によって 256 KiB と 4 MiB の 2 つの記述があり、実機の版で確かめる。CDC・follower reads のライセンス条件は読んだページに記述なし
- **PostgreSQL 18 の自動フェイルオーバー**：読んだ節には記述なし。「本体は障害の検知と切り替えのしくみを持たない」という記述があるはずの節（フェイルオーバーの節）は未読（記憶・要確認）
- **ページの最終更新日**：AWS の文書と Google Cloud の文書は、取得した本文に日付がなかった。スライドには「確認日 2026-11-18」と書く
- **論文 5 本**：本文は開いていない。題名・発表の場・年は記憶
- Jepsen の報告が、同じ異常を自前で運用する PostgreSQL のレプリカで確かめたわけではない点。原因が PostgreSQL のしくみにあるという追記と、Aurora への当てはまりは別の問い

## 10. 結論（スライドに書くこと。箇条書き 15〜30 個、各項目に出典の番号）

1. クラウド製品の比較は、このガイドでは**公式文書に基づく・未検証**。公称値・SLA・実測を同じ表に混ぜない [7][25][35]
2. SLA は返金の条件であって実績ではない。構成の条件（複数 AZ、全表がグローバル表など）と、停止の定義の狭さを読む [7][25][61]
3. 既定の分離レベルは製品で違う：PostgreSQL と Snowflake は Read Committed、Spanner と CockroachDB は Serializable、Aurora DSQL は Repeatable Read（スナップショット分離）に固定 [14][26][46][68][72]
4. DynamoDB の既定の読み取りは結果整合。強整合は表とローカルセカンダリ索引だけで、グローバルセカンダリ索引とストリームは常に結果整合 [18]
5. DynamoDB のトランザクションは 1 回の API 呼び出しで、100 操作・4 MB・同じリージョンまで。`Query` や `Scan` との間は read-committed [19]
6. 「PostgreSQL 互換」は 1 つの意味ではない。Aurora PostgreSQL、Aurora DSQL、Spanner の PostgreSQL 方言は、互換の幅も分離レベルも上限も違う [8][14][34]
7. Aurora DSQL はロックを取らず、衝突をコミット時に 40001 で返す。`SELECT FOR UPDATE` も待たずに後で失敗する。再試行と冪等性が設計の前提になる [12]
8. Aurora DSQL の 1 トランザクションは 3,000 行・10 MiB・5 分まで。大きなバッチは分割する [13]
9. Aurora は 3 つの AZ の 6 つのストレージノードへ同期で書く。リーダーインスタンスとリージョン間（Global Database）は非同期 [1][2][3]
10. Aurora Global Database のフェイルオーバーは、秒単位の書き込みを失いうる。書き込みの遮断は最善努力で、文書自身が split-brain を書いている [4]
11. RPO に上限を設けると、遅れたときにコミットが止まる。整合性の上限は、可用性と引き換えになる [4][57]
12. DynamoDB global tables の既定（MREC）は非同期で last writer wins。強整合モード（MRSC）は 3 リージョン固定で RPO 0 だが、トランザクション API が使えない [20]
13. Spanner は Paxos で過半数に同期で書き、既定の読み取りは strong。マルチリージョンでは書き込みの遅延と引き換えになる [28][29][36]
14. Cosmos DB は整合性を 5 段階から選ぶ。Strong だけが全リージョンへ同期で、複数リージョン書き込みとは両立しない [57]
15. BigQuery は 2 つのゾーンへ同期で書くが、リージョンの障害ではデータを失いうる。「マルチリージョン」は冗長性の名前ではない [39]
16. 分割は自動でも、キー設計は利用者の責任。DynamoDB はパーティションあたりの上限、Spanner は単調増加キーのホットスポット、Cosmos DB は 20 GB の論理パーティション [23][33][58]
17. 「厳密に 1 回」は条件つき：BigQuery はオフセットを指定したストリームだけ（既定は at-least-once）、Pub/Sub は同じリージョンの pull だけ、Snowpipe Streaming は Named Channels の中だけ [37][48][62]
18. DynamoDB Streams の「1 回だけ現れる」はストリームの中の話。保持は 24 時間で、トランザクションの原子性は流れてこない [19][21]
19. 組み込みの CDC と取り込みは、運用が軽い代わりに、保持・行き先・DDL・フェイルオーバーに制約がある（ゼロ ETL は DDL で再同期、切り替えで作り直し）[5][47]
20. BigQuery の CDC 取り込みは主キーを強制しない。重複を防ぐのは送り手 [41]
21. スキーマ変更は「オンライン」でも無料ではない：Spanner は検証に数分から何時間、BigQuery は厳しくする変更で作り直し、DSQL は DDL を 1 文ずつ [14][32][40]
22. Iceberg への対応は置換性を上げるが、書き込みは実質その製品経由で、機能の制限がある [42][52]
23. 離れるときに残るのは、独自 API だけでなく**独自の整合性の前提**（結果整合が既定、楽観的制御、外部整合性、last writer wins）[12][18][20][27]
24. レプリカを足すと、分離レベルの保証は 1 台のときと同じとは限らない。Jepsen は RDS for PostgreSQL 17.4 のマルチ AZ クラスタで、リーダーを含む読み取りがスナップショット分離を破ることを示した（2025-04-29。Aurora は対象外）[77]
25. Aurora・DSQL・DynamoDB・Spanner・Snowflake・BigQuery・Cosmos DB に、Jepsen の公開された分析はない（2026-11-18 時点）。独立した検証がない保証は、文書の言葉として読む [78]
26. 論文（Spanner 2012、Aurora 2017・2018、Snowflake 2016、DynamoDB 2022）は設計の説明で、現行の製品の保証ではない。数値は現行の公式文書で確かめ直す [79][80][81][82][83]
27. 料金は軸で比べる：要求数・スキャン量に比例するか、確保した容量に比例するか、ストレージと計算が分かれているか。強い整合性とトランザクションは、同じ操作でも多く課金される製品がある [1][18][19][53]
28. 実機の PostgreSQL 18 と CockroachDB で測れるのは、分離レベル・複製・フェイルオーバー・CDC の**型**。クラウド製品の値そのものは測れないので、対応表は文書の記述として示す [68][69][71][72]

## 11. 出典（番号｜題名｜発行者｜版・日付｜URL｜確認の深さ）

確認日はすべて 2026-11-18。「本文確認（抜粋）」は、取得ツールが本文から抜き出した要約と短い引用を読んだもの。

| 番号 | 題名 | 発行者 | 版・日付 | URL | 確認の深さ |
| --- | --- | --- | --- | --- | --- |
| 1 | Amazon Aurora storage | AWS | Aurora User Guide。日付の表示なし | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.StorageReliability.html | 本文確認 |
| 2 | High availability for Amazon Aurora | AWS | 同上 | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html | 本文確認 |
| 3 | Using Amazon Aurora Global Database | AWS | 同上 | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html | 本文確認 |
| 4 | Using switchover or failover in Amazon Aurora Global Database | AWS | 同上 | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html | 本文確認 |
| 5 | Aurora zero-ETL integrations | AWS | 同上 | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/zero-etl.html | 本文確認 |
| 6 | Quotas and constraints for Amazon Aurora | AWS | 同上 | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_Limits.html | 本文確認 |
| 7 | Amazon Aurora Service Level Agreement | AWS | 最終更新 2025-03-12 | https://aws.amazon.com/rds/aurora/sla/ | 本文確認（抜粋） |
| 8 | Overview of PostgreSQL logical replication with Aurora | AWS | Aurora User Guide。日付の表示なし | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Replication.Logical.html | 本文確認 |
| 9 | Configuring Aurora PostgreSQL for Local write forwarding | AWS | 同上 | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-postgresql-write-forwarding-configuring.html | 検索の抜粋のみ |
| 10 | Transactions（SQL Server to Aurora PostgreSQL Migration Playbook） | AWS | 日付の表示なし | https://docs.aws.amazon.com/dms/latest/sql-server-to-aurora-postgresql-migration-playbook/chap-sql-server-aurora-pg.tsql.transactions.html | 検索の抜粋のみ |
| 11 | What is Amazon Aurora DSQL? | AWS | Aurora DSQL User Guide。日付の表示なし | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/what-is-aurora-dsql.html | 本文確認 |
| 12 | Concurrency control in Aurora DSQL | AWS | 同上 | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-concurrency-control.html | 本文確認 |
| 13 | Cluster quotas and database limits in Amazon Aurora DSQL | AWS | 同上 | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/CHAP_quotas.html | 本文確認 |
| 14 | Migrating from PostgreSQL to Aurora DSQL（互換性の考慮点を含む） | AWS | 同上 | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-postgresql-compatibility-unsupported-features.html | 本文確認（開いた URL は移行ガイドの内容を返した） |
| 15 | Resilience in Amazon Aurora DSQL | AWS | 同上 | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/disaster-recovery-resiliency.html | 本文確認 |
| 16 | Amazon Aurora DSQL Service Level Agreement | AWS | 最終更新 2025-05-27 | https://aws.amazon.com/rds/aurora/dsql/sla/ | 本文確認（抜粋） |
| 17 | Change data capture streams（Aurora DSQL） | AWS | 検索の要約では 2026-07-08 に一般提供 | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/cdc-streams.html | 題名のみ（検索の要約を読んだ） |
| 18 | DynamoDB read consistency | AWS | DynamoDB Developer Guide。日付の表示なし | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html | 本文確認 |
| 19 | Amazon DynamoDB Transactions: How it works | AWS | 同上 | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html | 本文確認 |
| 20 | How DynamoDB global tables work | AWS | 同上（グローバル表 2019.11.21 版） | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html | 本文確認 |
| 21 | Change data capture for DynamoDB Streams | AWS | 同上 | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html | 本文確認 |
| 22 | Quotas in Amazon DynamoDB | AWS | 同上 | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html | 本文確認 |
| 23 | Best practices for designing and using partition keys effectively in DynamoDB | AWS | 同上 | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html | 本文確認 |
| 24 | Partitions and data distribution in DynamoDB | AWS | 同上 | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.Partitions.html | 本文確認 |
| 25 | Amazon DynamoDB Service Level Agreement | AWS | 最終更新 2025-05-14 | https://aws.amazon.com/dynamodb/sla/ | 本文確認（抜粋） |
| 26 | Isolation levels（Spanner） | Google Cloud | 日付の表示なし | https://docs.cloud.google.com/spanner/docs/isolation-levels | 本文確認（抜粋） |
| 27 | TrueTime and external consistency | Google Cloud | 同上 | https://docs.cloud.google.com/spanner/docs/true-time-external-consistency | 本文確認（抜粋） |
| 28 | Replication（Spanner） | Google Cloud | 同上 | https://docs.cloud.google.com/spanner/docs/replication | 本文確認（抜粋） |
| 29 | Instance configurations（Spanner） | Google Cloud | 同上 | https://docs.cloud.google.com/spanner/docs/instance-configurations | 本文確認（抜粋） |
| 30 | Quotas and limits（Spanner） | Google Cloud | 同上 | https://docs.cloud.google.com/spanner/quotas | 本文確認（抜粋） |
| 31 | Change streams overview（Spanner） | Google Cloud | 同上 | https://docs.cloud.google.com/spanner/docs/change-streams | 本文確認（抜粋） |
| 32 | Make schema updates（Spanner） | Google Cloud | 同上 | https://docs.cloud.google.com/spanner/docs/schema-updates | 本文確認（抜粋） |
| 33 | Schemas overview（Spanner） | Google Cloud | 同上 | https://docs.cloud.google.com/spanner/docs/schema-and-data-model | 本文確認（抜粋） |
| 34 | PostgreSQL interface（Spanner） | Google Cloud | 同上 | https://docs.cloud.google.com/spanner/docs/postgresql-interface | 本文確認（抜粋） |
| 35 | Cloud Spanner Service Level Agreement (SLA) | Google Cloud | 日付は取得できず | https://cloud.google.com/spanner/sla | 本文確認（抜粋。クレジットの表は未読） |
| 36 | Timestamp bounds（Spanner） | Google Cloud | 日付の表示なし | https://docs.cloud.google.com/spanner/docs/timestamp-bounds | 本文確認（抜粋） |
| 37 | Introduction to the BigQuery Storage Write API | Google Cloud | 同上 | https://docs.cloud.google.com/bigquery/docs/write-api | 本文確認（抜粋） |
| 38 | Multi-statement transactions（BigQuery） | Google Cloud | 同上 | https://docs.cloud.google.com/bigquery/docs/transactions | 本文確認（抜粋） |
| 39 | Understand reliability（BigQuery） | Google Cloud | 同上 | https://docs.cloud.google.com/bigquery/docs/reliability-intro | 本文確認（抜粋） |
| 40 | Modify table schemas（BigQuery） | Google Cloud | 同上 | https://docs.cloud.google.com/bigquery/docs/managing-table-schemas | 本文確認（抜粋。末尾約 1 万字は未読） |
| 41 | Stream table updates with change data capture（BigQuery） | Google Cloud | 同上 | https://docs.cloud.google.com/bigquery/docs/change-data-capture | 本文確認（抜粋） |
| 42 | Apache Iceberg managed tables（BigQuery） | Google Cloud | 同上 | https://docs.cloud.google.com/bigquery/docs/iceberg-tables | 本文確認（抜粋） |
| 43 | BigQuery Service Level Agreement (SLA) | Google Cloud | 日付は取得できず | https://cloud.google.com/bigquery/sla | 本文確認（抜粋。表の一部が欠けていた） |
| 44 | Quotas and limits（BigQuery） | Google Cloud | 日付の表示なし | https://docs.cloud.google.com/bigquery/quotas | 本文確認（抜粋。末尾約 4.5 万字は未読） |
| 45 | BigQuery overview | Google Cloud | 同上 | https://docs.cloud.google.com/bigquery/docs/introduction | 本文確認（抜粋） |
| 46 | Transactions（Snowflake） | Snowflake | 日付の表示なし | https://docs.snowflake.com/en/sql-reference/transactions | 本文確認（抜粋） |
| 47 | Introduction to streams | Snowflake | 同上 | https://docs.snowflake.com/en/user-guide/streams-intro | 本文確認（抜粋） |
| 48 | Snowpipe Streaming（overview） | Snowflake | 同上 | https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview | 本文確認（抜粋） |
| 49 | Dynamic tables | Snowflake | 同上 | https://docs.snowflake.com/en/user-guide/dynamic-tables-about | 本文確認（抜粋） |
| 50 | Key concepts and architecture | Snowflake | 同上 | https://docs.snowflake.com/en/user-guide/intro-key-concepts | 本文確認（抜粋） |
| 51 | Introduction to replication and failover across multiple accounts | Snowflake | 同上 | https://docs.snowflake.com/en/user-guide/replication-intro | 本文確認（抜粋） |
| 52 | Apache Iceberg tables（Snowflake） | Snowflake | 同上 | https://docs.snowflake.com/en/user-guide/tables-iceberg | 本文確認（抜粋） |
| 53 | Understanding overall cost | Snowflake | 同上 | https://docs.snowflake.com/en/user-guide/cost-understanding-overall | 本文確認（抜粋） |
| 54 | Support Policy and Service Level Agreement | Snowflake | 未確認 | https://www.snowflake.com/en/legal/addenda/support-policy-and-service-level-agreement | 未確認（403。検索の抜粋でクレジットの表だけ見た） |
| 55 | ALTER TABLE | Snowflake | 日付の表示なし | https://docs.snowflake.com/en/sql-reference/sql/alter-table | 本文確認（抜粋。末尾約 1 万字は未読） |
| 56 | Micro-partitions & Data Clustering | Snowflake | 同上 | https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions | 本文確認（抜粋） |
| 57 | Consistency level choices - Azure Cosmos DB | Microsoft | ms.date 2025-09-03、更新 2026-04-27 | https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels | 本文確認 |
| 58 | Service Quotas and Default Limits - Azure Cosmos DB | Microsoft | ms.date 2025-09-03、更新 2026-08-25 | https://learn.microsoft.com/en-us/azure/cosmos-db/concepts-limits | 本文確認 |
| 59 | Reliability in Azure Cosmos DB | Microsoft | ms.date 2026-05-06、更新 2026-11-12 | https://learn.microsoft.com/en-us/azure/reliability/reliability-cosmos-db | 本文確認（RPO の表と衝突の節だけ） |
| 60 | AlloyDB overview | Google Cloud | 日付の表示なし | https://docs.cloud.google.com/alloydb/docs/overview | 本文確認（抜粋） |
| 61 | AlloyDB Service Level Agreement (SLA) | Google Cloud | 日付は取得できず | https://cloud.google.com/alloydb/sla | 本文確認（抜粋） |
| 62 | Exactly-once delivery（Pub/Sub） | Google Cloud | 日付の表示なし | https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery | 本文確認（抜粋） |
| 63 | Subscription overview（Pub/Sub） | Google Cloud | 同上 | https://docs.cloud.google.com/pubsub/docs/subscription-overview | 本文確認（抜粋） |
| 64 | Pub/Sub Service Level Agreement (SLA) | Google Cloud | 日付は取得できず | https://cloud.google.com/pubsub/sla | 本文確認（抜粋。Pub/Sub 本体の数値は読めず） |
| 65 | Event Hubs features and terminology | Microsoft | ms.date 2026-01-12、更新 2026-02-13 | https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-features | 本文確認 |
| 66 | Amazon Kinesis Data Streams Features／Amazon Kinesis（Big Data Analytics Options on AWS） | AWS | 日付の表示なし | https://aws.amazon.com/kinesis/data-streams/features ／ https://docs.aws.amazon.com/whitepapers/latest/big-data-analytics-options/amazon-kinesis.html | 検索の抜粋のみ |
| 67 | Amazon MSK Service Level Agreement／Amazon MSK FAQs／AWS Big Data Blog（MSK Replicator。自己申告） | AWS | 日付の表示なし | https://aws.amazon.com/msk/sla ／ https://aws.amazon.com/msk/faqs | 検索の抜粋のみ |
| 68 | 13.2. Transaction Isolation | PostgreSQL Global Development Group | PostgreSQL 18（ページの表示は 18.7） | https://www.postgresql.org/docs/18/transaction-iso.html | 本文確認（抜粋） |
| 69 | 26.2. Log-Shipping Standby Servers | PostgreSQL Global Development Group | PostgreSQL 18 | https://www.postgresql.org/docs/18/warm-standby.html | 本文確認（抜粋） |
| 70 | Appendix K. PostgreSQL Limits | PostgreSQL Global Development Group | PostgreSQL 18 | https://www.postgresql.org/docs/18/limits.html | 本文確認（抜粋） |
| 71 | 47.2. Logical Decoding Concepts | PostgreSQL Global Development Group | PostgreSQL 18 | https://www.postgresql.org/docs/18/logicaldecoding-explanation.html | 本文確認（抜粋） |
| 72 | Transactions | Cockroach Labs | stable（リンクは v26.4） | https://docs.cockroachlabs.com/docs/stable/transactions | 本文確認（抜粋） |
| 73 | Replication Layer | Cockroach Labs | stable（v26.4） | https://docs.cockroachlabs.com/docs/stable/architecture/replication-layer | 本文確認（抜粋） |
| 74 | Follower Reads | Cockroach Labs | stable（v26.4） | https://docs.cockroachlabs.com/docs/stable/follower-reads | 本文確認（抜粋） |
| 75 | Change Data Capture Overview | Cockroach Labs | stable（v26.4） | https://docs.cockroachlabs.com/docs/stable/change-data-capture-overview | 本文確認（抜粋） |
| 76 | Cluster Settings | Cockroach Labs | v26.1 | https://docs.cockroachlabs.com/docs/v26.1/cluster-settings | 題名のみ（検索の要約を読んだ） |
| 77 | Amazon RDS for PostgreSQL 17.4 | Jepsen（Kyle Kingsbury） | 2025-04-29、追記 2025-05-03。対象は RDS for PostgreSQL マルチ AZ クラスタ 13.15〜17.4 | https://jepsen.io/analyses/amazon-rds-for-postgresql-17.4 | 本文確認（抜粋。2 回読んだ） |
| 78 | Analyses（一覧） | Jepsen | 確認日 2026-11-18 | https://jepsen.io/analyses | 本文確認（抜粋） |
| 79 | Spanner: Google's Globally-Distributed Database | Corbett ほか | OSDI 2012 | — | 未確認（記憶・要確認） |
| 80 | Amazon DynamoDB: A Scalable, Predictably Performant, and Fully Managed NoSQL Database Service | Elhemali ほか | USENIX ATC 2022 | — | 未確認（記憶・要確認） |
| 81 | Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases | Verbitski ほか | SIGMOD 2017 | — | 未確認（記憶・要確認） |
| 82 | Amazon Aurora: On Avoiding Distributed Consensus for I/Os, Commits, and Membership Changes | Verbitski ほか | SIGMOD 2018 | — | 未確認（記憶・要確認） |
| 83 | The Snowflake Elastic Data Warehouse | Dageville ほか | SIGMOD 2016 | — | 未確認（記憶・要確認） |
