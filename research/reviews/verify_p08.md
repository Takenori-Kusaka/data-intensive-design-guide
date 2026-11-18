# Part 8「複製と分割」事実の確かめ直し

確認日：2026-11-18。書き手が原典を開いて確かめた結果。Web の一次資料は、ページの HTML を取得して本文を文字列検索で照合した（要約ツールは使っていない）。書籍は `research/books/text/0180-2.txt`（DDIA 2e。印刷ページ＝PDF ページ − 18）の該当ページを読んだ。

結果の凡例：一致／修正した（ノートの記述から変えた）／載せるのをやめた／未確認と表示（スライドのセルに「未確認」と書いた）

| スライドの題 | 事実 | 出典（URL か書籍ページ） | 確かめ方 | 結果 |
| --- | --- | --- | --- | --- |
| 複製の目的は可用性・読み取りの拡張・近さの 3 つ | 複製の理由は 3 つ（近さ、障害時の継続、読み取りのスケールアウト） | DDIA 2e p.191 | 書籍本文で確認 | 一致 |
| 同上 | 複製はバックアップの代わりにならない。削除も複製先へ伝わる | DDIA 2e p.192（コラム） | 書籍本文で確認 | 一致 |
| 同上 | GitLab は、複製を主にフェイルオーバー用で災害復旧用ではないと書く | https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ | 本文確認（"primarily used for failover purposes and not for disaster recovery"） | 一致 |
| シングルリーダー：書き込みは 1 か所、変更を順に配る | リーダーだけが書き込みを受け、フォロワーは同じ順序で適用。別名（プライマリ・ソース／リードレプリカ・セカンダリ・ホットスタンバイ） | DDIA 2e p.193 | 書籍本文で確認 | 一致。訳語は本書の「シングルリーダー」に合わせた（依頼文の「単一リーダー」から変更） |
| 同上 | Raft などの合意もシングルリーダーが土台で、交代を自動で行う | DDIA 2e p.194 | 書籍本文で確認 | 一致 |
| 同上 | PostgreSQL の呼び名はプライマリとスタンバイ | https://www.postgresql.org/docs/18/warm-standby.html | 本文確認 | 一致 |
| 非同期では、応答済みの書き込みも失われうる | 同期の利点と欠点、1 台だけ同期（準同期）、過半数の例は 5 台中 3 台、完全非同期では完了を返した書き込みも永続性が保証されない、遅れは通常 1 秒以内だが保証なし・数分以上もある | DDIA 2e p.194–195 | 書籍本文で確認 | 一致 |
| synchronous_commit = on でも既定は非同期 | `synchronous_commit` の有効な値と既定（on）。`synchronous_standby_names` が空なら意味のある値は on と off だけで、ほかは on と同じ手元の同期 | https://www.postgresql.org/docs/18/runtime-config-wal.html （19.5） | 本文確認 | 一致 |
| 同上 | 表 19.1 の各値の保証（remote_apply は 4 項目、on は 3、remote_write は 2、local は 1、off は 0） | 同上（Table 19.1） | 本文確認 | 一致。ノートの表の「off：直近の分を失うことがある」は、表 19.1 の表記に合わせて「—」にした |
| 同上 | off で失いうる範囲は最大で `wal_writer_delay` の 3 倍。DB の不整合は起きない | 同上 | 本文確認 | 一致 |
| 同上 | `synchronous_standby_names` の既定は空で、同期の複製は無効。`ANY num (…)`・`FIRST num (…)` の書き方 | https://www.postgresql.org/docs/18/runtime-config-replication.html （19.6.2） | 本文確認 | 一致 |
| 同上 | ストリーミングレプリケーションは既定で非同期 | https://www.postgresql.org/docs/18/warm-standby.html （26.2.5・26.2.8） | 本文確認 | 一致 |
| 同上 | 文書の版の表示は PostgreSQL 18（告知欄は 18.7、2026-11-12 公開） | 同上 | 本文確認 | 一致。スライドは「PostgreSQL 18 文書（2026-11 確認）」とした |
| 損失ゼロの設定は、別の止まり方を持ち込む | 同期スタンバイのどれかが落ちるとコミットが完了しないことがある（"may never be completed"）。対策は候補を複数名指し。足りなければ数を減らすか無効にして再読み込み | https://www.postgresql.org/docs/18/warm-standby.html （26.2.8.4） | 本文確認 | 一致。ノートの「タイムアウトはない」は文書に明文が無いので載せるのをやめた |
| 同上 | 待つ間も資源は使わないがロックは保持。待ち時間の下限は往復時間。読み取り専用とロールバックは待たない | 同上（26.2.8・26.2.8.3） | 本文確認 | 一致 |
| 同上 | 待っている最中にプライマリが再起動すると、待っていたトランザクションはコミット済みになる | 同上（26.2.8.4） | 本文確認 | 一致 |
| 同上 | 題材 D の測定項目（同期スタンバイ停止時の待ち、昇格で失われた応答済みコミット） | research/outline.md 題材 D | 計画の記述と照合 | 一致。結果の数字は書いていない |
| フェイルオーバーは検知・昇格・遮断を誰が決めるか | フェイルオーバーの 3 段階、タイムアウトの例 30 秒、最新のデータを持つフォロワーを選ぶ、スプリットブレインとフェンシングの定義、手動を好む運用チームがある | DDIA 2e p.199–201 | 書籍本文で確認 | 一致 |
| 同上 | PostgreSQL は障害を検知して知らせるソフトウェアを提供しない。STONITH。定期的な切り替えは試験になる。手順の文書化を勧める。昇格は `pg_ctl promote`／`pg_promote()` | https://www.postgresql.org/docs/18/warm-standby-failover.html （26.3） | 本文確認 | 一致 |
| フェイルオーバーの事故は、取り決めの欠陥で起きた | GitHub：2018-10-21 22:52 UTC、43 秒の接続断、劣化 24 時間 11 分、Orchestrator が西海岸へ切り替え、最も忙しいクラスタで未複製の書き込み 954 件、対策にリージョンをまたぐ昇格の防止、最終的に利用者のデータは失われなかった、公開 2018-10-30 | https://github.blog/news-insights/company-news/oct21-post-incident-analysis/ | 本文確認 | 一致 |
| 同上 | DDIA に GitHub 2018-10 の事例は無い（p.200 の GitHub の事例は MySQL と Redis の不整合で別件） | DDIA 2e p.200 | 書籍本文で確認 | 一致。この件の根拠は事後報告（inst）だけにした |
| 同上 | GitLab：2017-01-31、WAL アーカイブ未使用、セカンダリのつもりでプライマリのデータを削除（約 300 GB）、pg_dump は 9.2 のバイナリで失敗、通知メールは届かず、約 6 時間前の手動の LVM スナップショットから復元、コピーに約 18 時間、プロジェクト約 5,000・コメント約 5,000・ユーザー約 700（見積もり）、公開 2017-02-10 | https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ | 本文確認 | 一致。損失の時間帯は報告の中で 17:20〜00:00 と 17:20〜23:30 の 2 通りがあるので、時刻は載せず「約 6 時間前のスナップショット」とだけ書いた |
| 同上 | Cloudflare 2020-11-02 の件（ノート 04 の 4.3） | — | 今回は原文を開いていない | 載せるのをやめた（Part 10・14 の担当範囲でもある） |
| 複製の遅れは、読み取りに 3 つの異常を起こす | 結果整合性、遅れは通常 1 秒未満だが数秒〜数分、リードアフターライト整合性・モノトニックリード・一貫した順序での読み取りの定義と対策、遅れが数分や数時間になったときを考える | DDIA 2e p.203–209 | 書籍本文で確認（p.204・205・209 の本文、6.1.5.2・6.1.5.3 の節の位置） | 一致 |
| 同上 | `remote_apply` は適用まで待ち、スタンバイの問い合わせに見える。コミットの遅れはほかの値よりずっと大きい | https://www.postgresql.org/docs/18/runtime-config-wal.html | 本文確認（"much larger commit delays"） | 一致 |
| 同上 | RDS for PostgreSQL のマルチ AZ クラスタで順序が食い違う異常（Jepsen 2025）、CockroachDB の follower reads の 4.2 秒、Spanner の stale read の推奨値 | ノート 04 | 今回は原文を開いていない | 載せるのをやめた |
| マルチリーダーとリーダーレスはコンフリクトを引き受ける | マルチリーダーは制約（残高、一意性）を守れない。可能なら避ける領域とみなされることが多い | DDIA 2e p.212 | 書籍本文で確認 | 一致 |
| 同上 | 最終書き込み優先（LWW）は、正常に処理された書き込みを暗黙のうちに破棄し、データ損失を伴う | DDIA 2e p.218–219 | 書籍本文で確認 | 一致。ノートの「黙って捨てる」は本書の表現「暗黙のうちに破棄」に直した |
| 同上 | クォーラム条件 w + r > n。それでも古い値が返る場合が 6 つあり、絶対的な保証と受け取らない | DDIA 2e p.226–229 | 書籍本文で確認 | 一致 |
| 同上 | Dynamo 論文の数値（99.94% が 1 版など）、sloppy quorum、DynamoDB が Multi-Paxos であること | ノート 04 | 今回は原文を開いていない | 載せるのをやめた |
| クラウド製品も、構成ごとに失う量と止まり方が違う | Aurora：複数 AZ の 6 つのストレージノードへ同期で複製。レプリカがあれば通常 60 秒未満、無ければ通常 10 分未満 | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html | 本文確認 | 一致 |
| 同上 | Aurora のレプリカの遅れは通常 100 ミリ秒よりずっと小さい | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Replication.html | 本文確認 | 一致 |
| 同上 | Aurora Global Database：リージョン間は非同期、RPO は通常は秒単位、RTO は分単位、計画的な切り替えは RPO 0、書き込みの遮断は最善努力でスプリットブレインがありうる | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html ／ 上記の高可用性のページ | 本文確認 | 一致 |
| 同上 | Aurora の「6 つのうち 4 つで書き込みが成立」 | — | 公式文書に記述を確認できず | 載せるのをやめた |
| 同上 | DynamoDB（1 リージョン）：応答の前の複製数、公称の RPO・RTO | — | 読んだページに記述なし | 未確認と表示 |
| 同上 | DynamoDB：読み取りの既定は結果整合。強整合の読み取りはテーブルと LSI だけ（GSI は不可） | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html | 本文確認 | 一致 |
| 同上 | DynamoDB global tables：MREC は非同期（通常 1 秒以内）、最終書き込み優先、RPO は複製の遅れに等しい（通常は数秒）。MRSC は少なくとももう 1 つのリージョンへ同期、RPO 0、ちょうど 3 リージョン、TTL・LSI・トランザクション操作は不可 | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html | 本文確認 | 一致 |
| 同上 | Spanner：リージョナルは読み書きレプリカ 3 つのうち 2 つで書き込みのクォーラム、SLA 99.99% 以上。デュアルリージョンは RPO 0、手動のフェイルオーバーは通常 1 分以内、自動は最長 45 分 | https://docs.cloud.google.com/spanner/docs/instance-configurations | 本文確認 | 一致 |
| 同上 | Spanner（リージョナル）の公称の RPO・RTO | — | 読んだページに記述なし | 未確認と表示 |
| 同上 | Spanner のマルチリージョンの SLA 99.999%、Aurora DSQL、Cosmos DB、BigQuery、Snowflake の行 | ノート 10 | 表を 7 行に絞るため | 載せるのをやめた |
| 分割は、1 台で足りなくなってから選ぶ重い手段 | シャーディングは重量級の解決策。1 台で足りるならシングルシャードのまま。パーティションキーの選択、全シャード検索、方式の変更が困難、分散トランザクションが要る | DDIA 2e p.247–248 | 書籍本文で確認 | 一致 |
| キー範囲は走査に、ハッシュは分散に強い | キー範囲の利点と欠点、mod N はほとんどのキーが移動、固定数のシャードとリシャーディング、ハッシュ範囲 | DDIA 2e p.250–257 | 書籍本文で確認（p.250・253・254・255 の該当行） | 一致 |
| 同上 | ホットキーの対策（専用のシャード、乱数の付加と読み取りの結合）。均一なのはキーの分布で負荷ではない | DDIA 2e p.258 | 書籍本文で確認 | 一致 |
| 同上 | DynamoDB の 1 パーティションの上限（3,000 RCU／1,000 WCU）、CockroachDB の range の大きさ（512 MiB／128 MiB） | ノート 04 | 今回は原文を開いていない | 載せるのをやめた |
| Kafka のパーティションは増やせるが、減らせない | Kafka はパーティション数を減らすことをサポートしない。増やすと `hash(key) % number_of_partitions` の対応が変わり、同じキーが別のパーティションへ行きうる。既存のデータは自動で再配置しない | https://kafka.apache.org/44/operations/basic-kafka-operations/ | 本文確認（版の一覧の先頭は 4.4） | 一致 |
| 同上 | Redpanda：`rpk topic add-partitions` で増やせる。既存のデータは新しいパーティションへ再配置されない | https://docs.redpanda.com/current/reference/rpk/rpk-topic/rpk-topic-add-partitions/ | 本文確認 | 一致 |
| 同上 | Redpanda はパーティションを減らせない | — | 読んだページ（add-partitions、トピックの設定）に記述なし | 未確認と表示。題も「Kafka の」に限定した |
| 同上 | Redpanda の版番号（ノートは 26.2） | — | 読んだページで版の表示を確かめられず | 載せるのをやめた（「Redpanda 文書（2026-11 確認）」とだけ書いた） |
| 同上 | Redpanda の開発モードは write caching が既定で有効で、fsync も省く。本番モードは write caching が既定で無効 | https://docs.redpanda.com/current/reference/rpk/rpk-redpanda/rpk-redpanda-mode/ ／ https://docs.redpanda.com/current/develop/manage-topics/config-topics/ | 本文確認 | 一致 |
| セカンダリ索引は、ローカルかグローバルかを選ぶ | ローカルは書き込みが 1 シャード、キーが分からない検索は全シャード。グローバルは索引の値で分割、書き込みが複数シャード、DynamoDB は非同期に反映 | DDIA 2e p.262–265 | 書籍本文で確認 | 一致 |
| 同上 | CockroachDB のセカンダリ索引が同期に更新されること | ノート 04（記憶・要確認） | 確かめていない | 載せるのをやめた |
| テナントの分離は、費用と分離の強さの交換 | 分割をテナントの分離に使う利点（資源・権限の分離、セルベース、テナントごとのバックアップなど）と課題 3 つ | DDIA 2e p.248–249 | 書籍本文で確認（見出しの位置） | 一致 |
| 同上 | サイロ・プール・ブリッジの 3 つの型 | https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/silo-pool-and-bridge-models.html | 本文確認 | 一致 |
| 同上 | セルはパーティションキーで振り分け、状態を共有しない。セルルーターという層を持つ | https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/what-is-a-cell-based-architecture.html | 本文確認 | 一致 |
| 同上 | 共有データベースはノイジーネイバーに注意。1 テナントだけの復元は別の資源へ戻して選び出す必要がありうる | https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/storage-data | 本文確認 | 一致。ノートの ms.date（2026-08-21）は本文から確かめられず、載せるのをやめた |
| 同上 | 「スキーマ分離」の行の得失、「見直しの合図」の列 | — | 一次資料なし | スライドに「本ガイドの整理（一次資料なし）」と明記した |
| 設計レビューで問うこと：複製と分割 | 各行の根拠は上の各スライドと同じ | 上記 | 上記 | 一致 |
| まとめ | 上の各スライドの再掲 | 上記 | 上記 | 一致 |

## 不確かな点（取りまとめ役への申し送り）

- 題材 D と題材 A の「実測する」という注記は、outline の計画に合わせた。パーティション数を増やしたときのキーの行き先は outline の題材に入っていないので、実測の注記は付けていない
- Kafka 4.4 の文書は `https://kafka.apache.org/44/…` を読んだ。`/documentation/` はリダイレクト用のページで本文が無い
- AWS・Google Cloud の文書はページに更新日の表示が無い。確認月（2026-11）だけを書いた
- 「フェイルオーバーの事故は取り決めの欠陥」という当てはめは本ガイドの整理で、各社の公式な結論の言い換えではない。スライドの注記に明記した
- GitLab の件はフェイルオーバーそのものの事故ではなく、複製の作り直しと復元の事故。スライドの題は outline の結論の文に合わせたが、リードで「復元を確かめる取り決め」と範囲を補った
- 見た目（はみ出し・重なり）は PowerPoint で確かめていない。文字数と行の高さから計算で合わせた。表の行が多いのはクラウド製品の表（8 行、10.5pt）とマルチテナントの表（5 行、10.5pt）
