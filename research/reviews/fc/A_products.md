# ファクトチェック：範囲 A（S1〜S72）／観点「製品と事後報告」

確認日：2026-11-18。対象：`research/deck_text_A.md`（Part 0〜5）。

確かめ方：一次資料の URL を自分で開いた。取得は WebFetch（小型モデルが本文から該当箇所を抜き出す方式）で、**原文の引用を返させて照合**した。本文をそのまま返したページ（Azure Architecture Center の 6 ページ、AWS の 4 ページ、CrowdStrike の RCA の PDF 冒頭）は自分で直接読んだ。それ以外は「引用の抜き出し」を読んでおり、ページ全文の逐語の通読ではない。確信が持てない指摘には、その旨を書いた。

指摘の件数：誤り 0、不正確 7、補足 7（計 14）。

## 1. 指摘（重要な順）

| # | スライド | 問題の記述（短く） | 何が違うか・根拠（URL と節。自分で開いて確かめたか） | 直した文の案 | 重大度 |
|---|---|---|---|---|---|
| 1 | S67（表「各社の Iceberg の表」） | 「Snowflake：自社をカタログにした表へ、外部のクライアントは追記・削除できない」 | 引用元のページ https://docs.snowflake.com/en/user-guide/tables-iceberg には、確かに "Third-party clients can't append to, delete from, or upsert data to Iceberg tables that use Snowflake as the catalog." がある。しかし**同じページの**「External query engines through Snowflake Horizon Catalog」の節は "Reading and writing Iceberg v3 tables via the Horizon Iceberg REST Catalog API is supported … for customer-managed and Snowflake-managed storage" と書き、専用のページ https://docs.snowflake.com/en/user-guide/tables-iceberg-query-using-external-query-engine-snowflake-horizon は "You can read and write to Snowflake-managed Iceberg v2 and v3 tables from external engines"（図の説明に "Both Read and Write are Generally Available"）と書く。書き込みの制限として挙がるのは、equality delete 不可、外部エンジンからの CTAS 不可、タグとブランチ不可、共有された表・動的テーブルへの書き込み不可など。2 ページとも開いて確認（抜き出しによる）。公式文書の中で 2 つの記述が並んでおり、どちらがどの経路に当たるかをページは説明していない。スライドの言い切りは、条件が落ちているか、古い記述だけを拾っている可能性が高い（**どちらが現行の正かは断定できない**） | 「Snowflake：自社をカタログにした表は、Horizon の Iceberg REST カタログ経由なら外部エンジンから読み書きできるが、equality delete・CTAS・ブランチなどは不可（同じ文書に『第三者のクライアントは追記・削除できない』という記述も残る。未検証）」 | 不正確 |
| 2 | S66（根拠の行、右下の注記、ノート）、S26・S31（根拠の行） | 「AWS PERF03-BP01」「AWS Reliability Pillar『DR objectives』」を現行の指針として引いている | どちらのページも冒頭に "This whitepaper is for historical reference only and will be deprecated in the future. All updated guidance and best practices now live in the Well-Architected Framework whitepaper." と出る。PERF03-BP01：https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/perf_data_use_purpose_built_data_store.html 、DR objectives：https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/disaster-recovery-dr-objectives.html （2 ページとも本文を直接読んだ）。`verify_p05.md` は PERF03 の注記に気づいているが、スライドには書かれていない。**DR objectives のほうは書き手の記録にも無い**。内容（誤りの例「経験があるから 1 つに固執」、RTO・RPO の定義、可用性との区別）は原文と一致。後継：注記のリンク先 https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html は確認時 404。各 Pillar の入口は新しい構成になっており、Performance Efficiency は「Data management」（`perf03.html`）、Reliability は「Plan for Disaster Recovery (DR)」（`rel13.html`）へリンクしている（入口の 2 ページは本文を確認。リンク先 2 ページは本文を取得できず、**後継の文言は未確認**） | 根拠の行に「（廃止予定の注記があるページ。2026-11 確認）」を足す。可能なら後継の `perf03` と `rel13` の本文を開いて、同じ記述があるかを確かめてから差し替える | 不正確 |
| 3 | S62（事後報告の囲み） | Mailchimp「2018-11 に兆候を把握したが、監視の追加は未着手だった」 | 原文は "In November of 2018, engineers on our Mandrill team identified the potential to reach wraparound" と "we added a ticket to the backlog to set up additional monitoring" まで。チケットがその後どうなったか（未着手か、着手したか）は書かれていない。https://mailchimp.com/what-we-learned-from-the-recent-mandrill-outage/ （2019-03-26 公開。2 回開いて引用を確認）。「未着手だった」は原文に無い言い回し | 「2018-11 に兆候を把握し、差し迫った脅威ではないと判断して、監視の追加はバックログのチケットにした」 | 不正確 |
| 4 | S62（事後報告の囲み） | Mailchimp「書き込みが偏ったシャードで autovacuum が遅れ、安全停止」 | 原文は "The autovacuum process on shard4 likely fell behind due to the higher load, though it may have failed outright." で、遅れたのか失敗していたのかを特定していない。スライドは推定を断定にしている（同上の URL） | 「書き込みが偏ったシャードで autovacuum が遅れたとみられ（失敗していた可能性もあると報告は書く）、XID が上限に達して安全停止」 | 不正確 |
| 5 | S16（表・lead・ノート）、S19・S20 | 「変更・操作 13、故障 3、負荷の増加 2、潜在的な不具合 1」「設定・ルール・ポリシー 4／更新・機能の有効化 3」 | 19 件を 1 件ずつ開いた結果は下の 2 節。**合計の 13／3／2／1 は、書き手の規則のもとで成り立つ**。ただし「報告が最初に挙げる出来事」という規則を文字どおり当てると、境界が 3 つある。(a) Google Cloud 2025-06-12 は、報告が先に挙げるのは 5/29 の機能追加（"On May 29, 2025, a new feature was added to Service Control"）で、6/12 のポリシー変更はその次。規則どおりなら内訳は「設定・ルール・ポリシー 3／更新・機能の有効化 4」になる（合計 13 は不変）。(b) Cloudflare 2023-11-02 は、報告が最初に挙げるのが電力会社の "unplanned maintenance event" で、地絡（ground fault）はその約 3 時間後。GitHub 2018 を「保守作業＝変更・操作」に入れた基準と揃えるなら変更・操作 14／故障 2、逆に GitHub 2018 を「故障しかけた機器」と読めば 12／4 になる。(c) AWS DynamoDB 2015 の原文は "a brief network disruption" で、故障とも変更とも書いていない。lead の「機器・電源・ネットワークの故障が引き金だったのは 3 件」は、原文より踏み込んだ言い方 | S16 の「数え方と限界」に 1 文足す：「境界の判断で、変更・操作は 12〜14 件、故障は 2〜4 件の幅がある。Google Cloud 2025 は当日のポリシー変更で数えた（報告は先に 5/29 の機能追加を挙げる）」。lead は「故障や通信の途絶が引き金だったのは 3 件」 | 不正確 |
| 6 | S17（根拠の行・ノート）、S37（ノート） | Azure「Design for change」（2026-03）、「Data considerations for microservices」（更新 2026-09-29） | ページのメタデータを直接読んだ。Design for change は `ms.date: 2018-08-30`、`updated_at: 2026-03-06`。Data considerations は `ms.date: 2022-07-26`、`updated_at: 2026-09-29`。一方、S51 の Event Sourcing（2026-03-27）と CQRS（2025-02-20）、S65 の Materialized View（2026-09-21）、S66・S70 の Understand data models（2025-08-21）は `ms.date` を書いている（4 ページとも `updated_at` は別の日付）。**同じデッキの中で日付の基準が混ざっている**。`ms.date` が内容の日付なら、Design for change は 2018 年の文書で、「2026-03」は内容が新しい印象を与える。https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/design-for-evolution ほか | `ms.date` に揃える：S17「Azure『Design for change』（2018-08-30。2026-11 確認）」、S37「（2022-07-26。2026-11 確認）」。または全ページ「2026-11 確認」だけにする | 不正確 |
| 7 | S55（表 6 行目）、S56（「イベントで持つ」） | 「イベントソーシングと CQRS は…入るのも出るのも高くつく。一部に選んで使う」 | "It's costly to migrate to or from an event sourcing solution" と "For most systems and most parts of a system, traditional data management is sufficient" は **Event Sourcing のページだけ**の記述。CQRS のページは "it can introduce significant complexity into the application design, specifically when combined with the Event Sourcing pattern" と、向かない場面（ドメインが単純、CRUD で足りる）を書くにとどまる。S55・S56 のノートの「出典の補足：Azure Architecture Center『CQRS』」は、この主張の出典にならない。2 ページとも本文を直接読んだ。S51 は Event Sourcing に限って書いており問題ない | S55：「イベントソーシングは入るのも出るのも高くつく（Azure）。CQRS も、特にイベントソーシングと組むと複雑さが増す。一部に選んで使う」 | 不正確 |
| 8 | S70（表「ベクトル検索」の切り替えの合図）、S69（表「次元の上限」） | 「次元の上限」「索引できるのは、vector 型で 2,000 次元まで」 | README は vector 2,000 次元に続けて、halfvec は 4,000 次元、bit は 64,000 次元まで索引できると書く（https://github.com/pgvector/pgvector 。引用を確認）。S69 は「vector 型で」と限定しており正しいが、S70 で「次元の上限」を専用ストアへ切り替える合図にするなら、型を替える手があることが落ちている | S69 の表に「（halfvec は 4,000 次元まで）」を足す | 補足 |
| 9 | S62（表「XID の周回」、ノート「つまり書き込みが止まります」） | 300 万未満で新しい XID の割り当てを拒否 | 数字は一致。原文は続けて "any transactions already in progress can continue, but only read-only transactions can be started … The VACUUM command can still be run normally" と書き、復旧に postmaster の停止やシングルユーザーモードは要らないとしている（PostgreSQL 18 文書 24.1.5、ページ表示は 18.7。https://www.postgresql.org/docs/18/routine-vacuuming.html ）。Sentry（2015）と Mailchimp（2019）の「停止」は当時の版・構成の話で、18 のふるまいと同じとは限らない | ノートに「読み取り専用のトランザクションと VACUUM は続けられる（18 の文書）」を足す | 補足 |
| 10 | S62（表「領域」） | 「標準の VACUUM は、空いた領域を OS に返さない（表の末尾のページが空いた場合を除く）」 | 原文の例外は "one or more pages at the end of a table become entirely free **and an exclusive table lock can be easily obtained**"。条件が 1 つ落ちている（同上 24.1） | 「（表の末尾のページが空き、排他ロックをすぐ取れる場合を除く）」 | 補足 |
| 11 | S62（表「索引」） | 「索引の列を変えず、同じページに空きがあれば省ける（HOT）」 | 一致。原文は条件を "not including summarizing indexes"（コアでは BRIN だけ）とし、HOT でも "summary indexes may still need to be updated" と書く（66.7。https://www.postgresql.org/docs/18/storage-hot.html ）。スライドの範囲では実害は小さい | そのままでよい。足すなら「（BRIN を除く）」 | 補足 |
| 12 | S67（表「各社の Iceberg の表」BigQuery、ノート「開いた形式は置換性を上げます」） | 「BigQuery：利用者のバケットに Parquet で置く」 | 一致（"store data in storage buckets that you own"、`file_format = PARQUET`）。ページの現在の題は「Apache Iceberg managed tables」。同じページは "Modifying data files for Iceberg managed tables outside of BigQuery can cause query failure or data loss" と書き、書き込みは BigQuery 経由に限るよう勧める。他エンジン向けには "Export of Iceberg V2 snapshot" とあり、挙がっている版は V2 だけ（https://docs.cloud.google.com/bigquery/docs/iceberg-tables 。引用を確認。最終更新日はページから取れず）。Snowflake の行と対にするなら、BigQuery 側の制限も書かないと片方だけ制限があるように読める | 「BigQuery：利用者のバケットに Parquet で置く。BigQuery の外からデータファイルを変えると、問い合わせの失敗やデータ損失が起きうる」 | 補足 |
| 13 | S16（ノート）、Part 14 との整合 | 「故障は 3 件」の中身 | S16 の 3 件は DynamoDB 2015・Cloudflare 2023・Cloudflare 2020。調査ノート 09 の 4.3 節と結論 1 は、同じ「3 件」を Cloudflare 2023・2020 と **GitHub 2018** としている（`verify_p01.md` が修正の経緯を書いている）。範囲 D の S（Part 14）は 13／3／2／1 で S16 と数は合っている（`deck_text_D.md` を語句で確認）が、件名の一覧までは照合していない。ノート 09 を参照して書いた箇所が残っていれば食い違う | Part 14 の件名つきの表で、故障 3 件が S16 と同じ 3 件かを取りまとめ時に確かめる | 補足 |
| 14 | S62（根拠の行） | 「Sentry（2015-07-20 発生）／Mailchimp Mandrill（2019-02-04 発生）」 | 日付は一致。Mailchimp の原文は発生の文に年を書いておらず（"at 05:35 UTC on February 4"）、2019 年は公開日（2019-03-26）と返金期間の記述からの読み取り。また報告は「2/5 22:09 UTC に解決」と「2/6 01:00 UTC までに通常に戻った」の 2 つの時刻を書く。スライドの「2019-02-04〜05」は前者に沿っており問題ない | そのままでよい | 補足 |

## 2. Part 1（S16）の 19 件：一次報告を 1 件ずつ開いた結果

規則（スライドの記述）：「報告が最初に挙げる出来事で 1 件 1 分類」。下の「原文の語句」は、今回開いて抜き出させた引用。CrowdStrike は PDF を取得して冒頭 2 ページを直接読んだ。

| # | 件 | 原文が最初に挙げる出来事（引用） | スライドの分類 | 妥当か |
|---|---|---|---|---|
| 1 | GitLab 2017-01-31 | 年表の先頭は 17:20 UTC の LVM スナップショット取得（準備）。障害の始まりは 19:00 UTC "GitLab.com starts experiencing an increase in database load due to what we suspect was spam." 削除は "errantly thinking they were doing so on the secondary" | 負荷の増加 | 妥当（規則どおり。ノートが誤操作を断っている）。直接の原因で数えれば変更・操作 |
| 2 | AWS S3 2017-02-28 | "At 9:37AM PST, an authorized S3 team member using an established playbook executed a command" "one of the inputs to the command was entered incorrectly" | 変更・操作（コマンド） | 妥当 |
| 3 | GitHub 2018-10-21 | "At 22:52 UTC on October 21, routine maintenance work to replace failing 100G optical equipment resulted in the loss of connectivity" "restored in 43 seconds" | 変更・操作（保守作業） | 妥当。ただし交換の対象は "failing"（故障しかけ）の機器で、故障とも読める。#16 と基準を揃えること（指摘 5） |
| 4 | AWS DynamoDB 2015-09-20 | "On Sunday, at 2:19am PDT, there was a brief network disruption that impacted a portion of DynamoDB's storage servers." ページに年の表記は無い（9/20 の日曜） | 故障（ネットワーク） | おおむね妥当。原文は「故障」とも「変更」とも書かず、原因も述べない |
| 5 | AWS Kinesis 2020-11-25 | "The trigger, though not root cause, for the event was a relatively small addition of capacity that began to be added to the service at 2:44 AM PST, finishing at 3:47 AM PST." | 変更・操作（容量の追加） | 妥当 |
| 6 | AWS us-east-1 2021-12-07 | "At 7:30 AM PST, an automated activity to scale capacity of one of the AWS services hosted in the main AWS network triggered an unexpected behavior from a large number of clients" | 変更・操作（自動のスケール） | 妥当（人の変更ではなく自動の動作。#7 と同じ箱に入れる数え方もある） |
| 7 | AWS DynamoDB／DNS 2025-10-19〜20 | "The incident was triggered by a latent defect within the service's automated DNS management system" "Right before this event started, one DNS Enactor experienced unusually high delays"。展開・変更・機器の故障は引き金として書かれていない | 潜在的な不具合 | 妥当 |
| 8 | Facebook 2021-10-04 | "During one of these routine maintenance jobs, a command was issued with the intention to assess the availability of global backbone capacity, which unintentionally took down all the connections in our backbone network" | 変更・操作（コマンド） | 妥当 |
| 9 | Roblox 2021-10-28〜31 | 要約の原因："Enabling a relatively new streaming feature on Consul under unusually high read and write load"。有効化は "On October 27th at 14:00, one day before the outage"。年表の先頭は "On the afternoon of October 28th, Vault performance was degraded and a single Consul server had high CPU load." | 変更・操作（機能の有効化） | 妥当（要約の先頭で分類）。年表の先頭は症状で、原因には「高い負荷のもとで」という条件が付く |
| 10 | Atlassian 2022-04-05 | "There was a communication gap between the team that requested the deletion and the team that ran it." "the team provided the IDs of the entire cloud site" 削除は "between 07:38 UTC and 08:01 UTC" | 変更・操作（スクリプト） | 妥当 |
| 11 | Datadog 2023-03-08 | "on March 8, 2023, at 06:00 UTC, a security update to systemd was automatically applied to a number of VMs" | 変更・操作（ソフトウェアの更新） | 妥当 |
| 12 | CrowdStrike 2024-07-19 | "On July 19, 2024, two additional IPC Template Instances were deployed."（その前に、2024-02 のセンサー 7.11 でのテンプレート型の導入を述べる。どちらも変更） | 変更・操作（ルールの配布） | 妥当 |
| 13 | Google Cloud 2025-06-12 | 報告が先に書くのは "On May 29, 2025, a new feature was added to Service Control for additional quota policy checks."、次が "On June 12, 2025 at ~10:45am PDT, a policy change was inserted into the regional Spanner tables" | 変更・操作（ポリシーの変更） | 大分類は妥当。**内訳は規則どおりなら「更新・機能の有効化」**（指摘 5） |
| 14 | Cloudflare 2025-11-18 | "it was triggered by a change to one of our database systems' permissions" "That feature file, in turn, doubled in size." | 変更・操作（設定の変更） | 妥当 |
| 15 | Cloudflare 2024-11-14 | "On November 14, 2024, we made a change to support an additional dataset for Logpush." "A bug in this system resulted in a blank configuration being provided to Logfwdr." | 変更・操作（設定の変更） | 妥当 |
| 16 | Cloudflare 2023-11-02 | 08:50 UTC、電力会社が "had an unplanned maintenance event affecting one of their independent power feeds"。"At approximately 11:40 UTC, there was a ground fault on a PGE transformer at PDX-04." | 故障（電源） | おおむね妥当。**最初に挙がる出来事は第三者の「計画外の保守」**で、#3 と基準を揃える必要がある（指摘 5） |
| 17 | Cloudflare 2020-11-02 | "At 14:43, a network switch started misbehaving." "Six minutes later, the switch recovered without human intervention." | 故障（機器） | 妥当 |
| 18 | Slack 2021-01-04 | "On January 4th, one of our Transit Gateways became overloaded." "our TGWs did not scale fast enough"。当日の変更は巻き戻したが "turned out they weren't the issue" | 負荷の増加 | 妥当 |
| 19 | Slack 2022-02-22 | "The PBR step on February 22 updated Consul on 25% of the fleet." | 変更・操作（ソフトウェアの更新） | 妥当 |

集計：スライドの規則と書き手の判断のままなら 13／3／2／1（計 19）で一致。内訳 4・3・3・2・1 は、#13 の読み方で 3・3・4・2・1 に変わりうる。#3 と #16 の扱いで、変更・操作は 12〜14、故障は 2〜4 の幅がある。どの数え方でも、変更・操作が過半である点は変わらない。発生年の範囲「2015〜2025 年」は一致（#4 の年はページに無く、曜日からの読み取り）。

## 3. 確かめて一致した主な事実

1. PostgreSQL 18 の現行のマイナー版は 18.7（versioning のページ。2026-11-12 のリリース告知）。文書のページ表示も 18.7（S53・S62） — https://www.postgresql.org/support/versioning/
2. PostgreSQL 18 文書の節番号：13.1 Introduction（MVCC）、24.1 Routine Vacuuming、24.1.5 Preventing Transaction ID Wraparound Failures、66.7 Heap-Only Tuples、8.14 JSON Types、8.14.2 Designing JSON Documents、65.4 GIN Indexes、65.4.4.1 GIN Fast Update Technique、65.4.5 GIN Tips and Tricks（S53・S55・S62・S68・S70・S71）
3. MVCC：各 SQL 文はスナップショットを見る。"reading never blocks writing and writing never blocks reading"（13.1。S62）
4. XID は 32 ビット。残り 4,000 万（"forty million transactions from the wraparound point"）で警告、300 万未満で新しい XID の割り当てを拒否（24.1.5。S62）
5. jsonb：ある程度決まった構造を勧める／どの更新も行全体に行レベルのロック／扱える大きさに抑えて競合を減らす／それ以上分けて独立に更新できない単位が理想（8.14.2。S53・S55）
6. jsonb の GIN：既定の `jsonb_ops` はキーの存在演算子に対応、`jsonb_path_ops` は非対応だが "usually much smaller"、検索も "typically perform better"（8.14.4。S53）
7. GIN：1 行の挿入が多数の索引挿入になる／保留リストが大きいと検索が大幅に遅い／大量投入時は索引を落として作り直すことを勧める（65.4.4.1、65.4.5。S68）
8. Sentry：公開 2015-07-23。"On Monday, July 20th, Sentry was down for most of the US working day."。当時のしきい値は 100 万未満（S62 のノート「当時の版のしきい値は今と違う」と一致） — https://blog.sentry.io/transaction-id-wraparound-in-postgres/
9. Mailchimp Mandrill：05:35 UTC（2/4）に開始、2/5 22:09 UTC に解決。shard4 に負荷が偏った。VACUUM の見積もりは最長 40 日。ダンプとリストアは "still disastrously slow"。Search と Url の 2 表を切り捨て、VACUUM は約 1 時間後に完了（S62）
10. pgvector：README のインストール手順は v0.8.7（タグの日付 2026-10-01）。索引なしは厳密検索で再現率は完全。HNSW の既定は m=16、ef_construction=64、hnsw.ef_search=40。IVFFlat は構築が速く省メモリだが問い合わせ性能は劣る。条件が 10% なら既定で平均 4 行。iterative index scan は 0.8.0 から。vector の索引は 2,000 次元まで（S69・S70）
11. ClickBench：README に "created and used by the ClickHouse team"、単一の平らな表、99,997,497 行、43 本、1 本ずつ実行（各 3 回）、"take them with a grain of salt"（S71）
12. RocksDB Tuning Guide：3 つの増幅の定義は S61 の訳と一致。最終編集 2023-03-28（S61）
13. BigQuery：保存と計算の分離、独立に伸縮、表のデータは列形式（S67） — https://docs.cloud.google.com/bigquery/docs/storage_overview
14. Snowflake：Database storage・Compute・Cloud services の 3 層。読み込んだデータを内部の最適化・圧縮した列形式に直す（S67）
15. Iceberg の仕様："Versions 1, 2 and 3 … are complete and adopted"、"Version 4 is under active development and has not been formally adopted"。版は前方互換を壊す機能の追加で上がる。メタデータファイルの原子的な差し替えが直列化可能な分離の土台（S67）
16. Azure「Data considerations for microservices」："Two services shouldn't share a data store." と、注記 "Services can safely share the same physical database server. Problems occur when services share the same schema, or they read and write to the same set of database tables."（S37）
17. AWS Prescriptive Guidance「Shared-database-per-service pattern」：hot table を避ける、変更は後方互換、開発時と実行時の結合、選ぶ条件 5 つ。「Database-per-service pattern」：またぐ問い合わせには別のパターンが要る。どちらのページにも廃止予定の注記は無い（S37・S43）
18. Azure「Event Sourcing」（ms.date 2026-03-27）：複雑なパターン、入るのも出るのも高くつく、ほとんどのシステムでは従来のデータ管理で足りる、台帳や注文処理に選んで使う、ビューは結果整合、誤ったイベントも残る、イベントの版の扱い（S51・S54）
19. Azure「Materialized View」（ms.date 2026-09-21）：更新の合図が失われると "the view silently serves stale results"、新しさを監視（S65）。Azure「Understand data models」（ms.date 2025-08-21）："Use one service when it still meets performance, scale, and governance objectives."、"A search index becomes the primary data store" を antipattern に挙げる（S66・S70）
20. Azure「Design for change」に "Use fitness functions" の項がある。Thoughtworks Radar は 2017-11 と 2018-05 に Trial、"This blip is not on the current edition of the Radar."（S17）

## 4. 確かめなかった範囲

- **観点の外**：書籍（DDIA 2e、ハードパーツ、大規模データ管理）のページと要約、ISO/IEC 25010・JIS X 25010、IPA 非機能要求グレード、NIST 用語集、Google SRE 本・SRE Workbook（Chubby、エラーバジェットの例）、論文（Dean・Barroso、Stonebraker、HNSW、Krikorian の講演）。ほかの観点の担当に任せた
- **19 件の全文の通読**：18 件は抜き出させた引用で確かめた。停止時間・件数など、範囲 A のスライドに出ない数字は照合していない（Part 14 の担当範囲）。Datadog の第 2〜4 部は開いていない
- **AWS の後継ページの文言**：`perf03.html`・`rel13.html` と Framework 本体は本文を取得できなかった（404 または本文なし）。後継に同じ記述があるかは未確認
- **Snowflake の 2 つの記述のどちらが現行か**：公式文書の中の食い違いを見つけたところまで。実機では確かめていない
- **BigQuery・Snowflake のページの最終更新日**：取得できなかった
- **ClickHouse・DuckDB・Aurora**：範囲 A には製品のふるまいの記述が無い（ClickHouse と DuckDB はケーススタディの題材名、ClickHouse は ClickBench の運営者として出るだけ。Aurora は出てこない）。確かめる対象が無かった
- **PostgreSQL のマテリアライズドビュー**：範囲 A（S63）は DDIA に基づく一般論だけで、PostgreSQL の `REFRESH MATERIALIZED VIEW` のふるまいには触れていない。Part 12 の範囲
- **図の見た目**（`deck/qa/sNNN.png`）は開いていない
