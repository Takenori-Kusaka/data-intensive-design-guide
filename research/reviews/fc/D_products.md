# ファクトチェック：範囲 D（S205〜S256）／観点：製品と事後報告

調査日 2026-11-18。確かめ方：事後報告 25 本（Part 14 の 24 件＋GitHub 2021-11）と、AWS Builders' Library 2 本、Cloudflare「Code Orange」、製品の公式文書を、**要約ツールを通さずに原文の HTML／PDF を取得し、本文を語句で検索して該当箇所を読んだ**（URL は末尾）。verify_p14.md は URL の一覧としてだけ使い、事実は原文で確かめ直した。

結論：**事実と違う「誤り」は見つからなかった。** 日付・時刻・時間・件数・原因・対策は、24 件すべてで原文と一致した。計算で作った所要時間も見つからなかった（スライドの時間はどれも原文にある数字）。指摘は、分類と言い回しに関する「不正確」5 件と「補足」6 件。

## 1. 指摘（重要な順）

| # | スライド | 問題の記述（短く） | 何が違うか・根拠（自分で開いて確かめたか） | 直した文の案 | 重大度 |
|---|---|---|---|---|---|
| 1 | S209・S211 と S219・S248・S250 | 型②の問い。S209 の一覧表は「全体で 1 つしかないものは何か」、S219（設計レビュー）は「この基盤が 1 時間止まったら、どのサービスが止まるか。その一覧は誰が持つか」 | スライドどうしの食い違い。S209 のノートは「右端の問いは、最後の設計レビューのスライドでもう一度まとめます」、S244・S246 は「問いの文言は各 Part のまま」と書くが、型②だけ問いの中身が別物（「1 つしかないもの」を探す問い → 「止まったら何が止まるか・一覧の持ち主」を問う問い）。S211 の副題は S209 側（「全体で 1 つしかないもの…を探す」）、S248 の最終行は S219 側。他の型（①③④⑤⑥⑦⑧）は S209 が短縮形で S219 が同じ問いに 1 文を足した形で、中身は同じ | どちらかに揃える。例：S209 を「この基盤が止まったら、どのサービスが止まるか」に変える。または S219 を「全体で 1 つしかないものは何か。それが 1 時間止まったら、どのサービスが止まるか」とし、S248 も同じ文に | 不正確 |
| 2 | S217（S220 の「段階は範囲を限るが、検出はしない」も） | Cloudflare 2026-02-20 を段階配布の例に並べ、「段階は範囲を限ったが、検出はしなかった」 | 原文（確認済み）は "the configuration change was applied iteratively and not instantaneously across all BYOIP customers" と書くだけで、段階配布（staged／gradual rollout）とは呼んでいない。検出については "We were able to detect impact on one.one.one.one and revert the impacting change before more prefixes were impacted" と書いており、「検出はしなかった」は原文と噛み合わない（検出したのは順次適用の仕組みではなく別の監視、という読み取りなら本ガイドの解釈）。「25% が取り下げられた」「全顧客には及ばず」は原文どおり | 「変更は順に適用され、全顧客には及ばず／影響に気づいて戻すまでに、BYOIP のプレフィックスの 25% が取り下げられた／順に適用する仕組み自体は、異常を見て止まらなかった（本ガイドの読み取り）」 | 不正確 |
| 3 | S207 | Google Cloud 2025 を「変更：設定・ルール・ポリシーの変更と配布」に分類 | 数え方は「報告が最初に挙げる出来事」（S206）。原文（確認済み）が最初に挙げるのは "On May 29, 2025, a new feature was added to Service Control…This code change and binary release went through our region by region rollout" で、ソフトウェアの更新。ポリシーの投入は 6/12 で 2 番目の出来事。規則どおりなら「ソフトウェアの更新、機能の有効化」に入り、内訳が 4・3 → 3・4 になる。変更・操作の合計 13 件は変わらない。GitLab 2017 には同種の但し書きがあるが、この件には無い | 表の該当欄に「Google Cloud 2025（最初の出来事は 5/29 のコード配布。停止を起こしたのは 6/12 のポリシー投入）」と但し書きを足す。または規則どおり移す | 不正確 |
| 4 | S210 | 「同じ型」に Datadog 2023-03-08（自社の配布手順を通らない OS の自動更新） | 型①の定義は「挙動を決めるデータ（設定・ルール・ポリシー）が数秒で全体に届く」。原文（確認済み）は "a security update to systemd was automatically applied" で、配られたのはソフトウェアの更新。届いたのも「数秒」ではなく 06:00〜07:00 UTC の窓の中。「自社の段階配布を通らない経路」という点は原文どおり（"we do so region-by-region… However, the base OS image…had a legacy security update channel enabled"） | 「近い型：Datadog 2023-03-08（データではなく OS の更新だが、自社の段階配布を通らない経路で一斉に入った）」 | 不正確 |
| 5 | S231 | GitHub 2021-11-27「読み取り複製の多くがデッドロックし」 | 原文（確認済み）は "a significant portion of our MySQL read replicas entered a semaphore deadlock"。「多く」は過半とも読め、原文より強い | 「読み取り複製のかなりの部分がデッドロックし」 | 不正確 |
| 6 | S212・S219 | 「9 件で…壊れた基盤に依存していた」。スライドに名前が出るのは 8 件 | S212 の 3 つの箱に出るのは AWS 2021・Roblox・Slack 2021・S3 2017・Kinesis 2020・Google Cloud 2025・Meta 2021・Atlassian 2022 の 8 件。9 件目は verify_p14.md では Google 2020-12-14。原文（確認済み）の対策 3 に "Improve reliability of tools and procedures for posting external communications during outages that affect internal tools" があり、割り当て自体は妥当。ただし S212 の根拠の行にもノートにもこの件が無く、読者は 9 件を数えられない | 「状況を伝えられない」の箱か、ノートの出典の補足に「Google 2020-12-14：社内の道具に及ぶ停止のとき、外への掲示の道具と手順を改善すると報告」を足す | 補足 |
| 7 | S215 | Cloudflare 2026-02-20「検証環境のデータでは再現しなかった」 | 原文（確認済み）は "Our staging environment contains data that matches Production as closely as possible, but was not sufficient in this case and the mock data we relied on…was insufficient"。「再現しなかった」という言い回しは原文に無い（試して再現しなかった、とは書いていない） | 「検証環境のデータと模擬データが足りず、事前に見つけられなかった」 | 補足 |
| 8 | S212 | 対策「連絡先を製品の外にも持つ（Atlassian）」 | 原文（確認済み）は "we will improve the backup of key contacts and retrofit support tooling to enable customers without a valid URL or Atlassian ID to make direct contact with our technical support team"。「製品の外に」は原文に無い言い回し | 「主要な連絡先のバックアップを改善し、URL や ID が無くても問い合わせられるようにする（Atlassian）」 | 補足 |
| 9 | S213 | Cloudflare 2020-11-02 の対策が「作り直しの不具合を修正」だけ | 修正は原文どおり（"We've since fixed the bug in our cluster management system"）。原文にはもう 1 つ、型④に直結する対策がある："for at least one of our databases, the cure may be worse than the disease, and in fact we may not want to invoke the promotion process so quickly. Immediately after this incident we adjusted that configuration accordingly"（確認済み） | 「作り直しの不具合を修正。自動の昇格を急がない設定に変更」 | 補足 |
| 10 | S223 | Spanner の「同時実行の扱い」のセル：文書は「細かい同時実行制御」を非対応に挙げる | 文言は原文どおり（"Fine-grained concurrency control"。The PostgreSQL language in Spanner、Last updated 2026-11-12。確認済み）。ただしこれは非対応の一覧の 1 項目で、Spanner が競合をどう扱うかの記述ではない。ほかの 3 行（ロックで待つ／楽観的／再試行）と種類が違う。また「既定 Serializable」は正しい（"Serializable isolation is the default isolation level in Spanner"）が、同じページは Repeatable Read を選べるとし、他の DB から移すワークロードには Repeatable Read を勧めている（"we recommend configuring your application to use repeatable read isolation"。確認済み） | 既定の列：「Serializable（Repeatable Read も選べる。文書は移行時にこちらを勧める）」。同時実行の列は、非対応の一覧からの引用であることを明示するか、右の列へ移す | 補足 |
| 11 | S212 | 型③の該当に GitHub 2018 が入っていない | 9 件の割り当ては原文から妥当（下の照合表）。数え漏れの候補として、GitHub 2018 の原文（確認済み）に "We use GitHub Pages internally and all builds had been paused several hours earlier, so publishing this took additional effort"（状況を伝えるブログの公開が、止めていた自社の機能に依存）がある。入れるかどうかは書き手の判断 | 入れるなら「10 件」。入れないなら現状のままでよい（分類は書き手による、の断りは S206 にある） | 補足 |

## 2. 件ごとの照合表（Part 14 の 24 件＋GitHub 2021-11）

凡例：一致＝スライドの記述が原文にある。番号は verify_p14.md の順。すべて原文を取得して確認。

| # | 件 | スライドの記述（主なもの） | 原文との照合 | 型・引き金の割り当て |
|---|---|---|---|---|
| 1 | GitLab 2017-01-31 | 約 300 GB、pg_dump は 9.2 と 9.6 の不一致で失敗、通知メールは届かず、約 6 時間前の手動スナップショット、停止約 18 時間、対策 3 つ | 一致（"around 300 GB"、"roughly 6 hours before"、"down for about 18 hours"、DMARC で拒否、#1095・#1102・"Assign an owner for data durability"） | ⑥⑦ 妥当。引き金「負荷の増加」は "± 19:00 UTC…increase in database load due to what we suspect was spam" が最初の出来事で規則どおり |
| 2 | AWS S3 2017-02-28 | 入力の誤りで意図より多く外した、全面再起動は想定より長い、SHD 管理画面が S3 に依存、対策 | 一致（9:37AM PST、"entered incorrectly"、"longer than expected"、11:37AM まで SHD 更新不可、"remove capacity more slowly"、"minimum required capacity level"、SHD を複数リージョンで） | ③⑦ 妥当。コマンド |
| 3 | GitHub 2018-10-21 | 43 秒、24 時間 11 分、Orchestrator の昇格、設定どおり、バックアップから全体を作り直したことは無い、数テラバイトに数時間、対策 | 一致（"43 seconds"、"24 hours and 11 minutes"、"behaved as configured"、"never needed to fully rebuild an entire cluster from backup"、"multiple terabytes…take hours"）。機器は "failing 100G optical equipment" | ④⑥ 妥当（③の候補は指摘 11）。保守作業 |
| 4 | DynamoDB 2015-09-20 | 短いネットワーク障害、約 55% で推移、再試行で負荷が減らない、要求を止めて容量追加、分割 | 一致（2:19am PDT、"stabilizing at approximately 55%"、5:06am "pause requests"、7:10am 回復、"segmenting…many instances of the metadata service each serving only portions"）。原文に年の表記は無い（"Sunday, September 20"） | ②⑤ 妥当。故障 |
| 5 | Kinesis 2020-11-25 | Cognito はベストエフォート、バッファの不具合、投稿の道具が Cognito に依存、予備は使い慣れず遅れた、対策 | 一致（"trigger, though not root cause"、"designed to be best effort"、"latent bug in this buffering code"、"more manual and less familiar tool"、cellularization の加速、"a few large AWS services…to a separate, partitioned front-end fleet"、"regularly trained on the backup tool"） | ②③ 妥当。容量の追加 |
| 6 | AWS 2021-12-07 | 自動の容量調整、監視と展開が内部ネットワーク上、稼働中の EC2 と既存の DNS 応答は影響なし | 一致（7:30 AM PST "automated activity to scale capacity"、"running EC2 instances were unaffected"、"existing DNS entries and answers to DNS queries were not impacted"、サポートは 7:33 AM〜2:25 PM PST、複数リージョンのサポート基盤） | ③⑤ 妥当（⑤："a latent issue prevented these clients from adequately backing off"）。自動のスケール |
| 7 | AWS 2025-10-19〜20 | DNS 自動化の競合、掃除が現用の計画を消した、レコードが空、人手で復旧、DWFM が進めない、流入を絞り選んで再起動、自動化を全世界で停止、NLB の制限 | 一致（"latent race condition"、"incorrect empty DNS record"、"required manual operator intervention"、"congestive collapse"、4:14 AM "throttled incoming work and began selective restarts"、"disabled…automation worldwide"、"velocity control mechanism"） | ②④⑤⑦。④⑤は明確。⑦（削除の単位）は「掃除が現用の計画まで消した」「NLB が一度に外しすぎた」からの読み取りで、やや広い。潜在的な不具合 |
| 8 | Meta 2021-10-04 | コマンドで全接続を落とした、監査の道具の不具合、DNS が広告を取り下げ、現地へ、取引として価値がある、停止時間の記載なし | 一致（"a bug in that audit tool"、"declare themselves unhealthy and withdraw those BGP advertisements"、"sent engineers onsite"、"I believe a tradeoff like this is worth it"）。本文に停止時間の数字は無いことを確認 | ③④ 妥当。コマンド |
| 9 | Roblox 2021-10-28 | 73 時間、Consul の 4 用途、監視と Consul の循環、専用クラスタへ分割、拠点とゾーン | 一致（"73-hour outage"、"service discovery, health checks, session locking…and as a KV store"、"circular dependency between our telemetry systems and Consul"、"split some critical services into their own dedicated clusters"、"additional, geographically distinct data center"） | ②③ 妥当。機能の有効化（10/27 に streaming を有効化） |
| 10 | Atlassian 2022-04-05 | 883 サイト（顧客 775）、即時削除、API は ID の種類を確かめない、最長 14 日、連絡先の一部が消えた、RPO は満たし RTO は満たせず | 一致（07:38〜08:01 UTC、"up to 14 days"、"accepted both site and app identifiers and assumed the input was correct"、"missed our RTO but met our RPO"、soft delete、複数サイト復元の自動化）。対策の言い回しは指摘 8 | ③⑥⑦ 妥当。スクリプト |
| 11 | Datadog 2023-03-08 | 5 リージョン・クラウド 3 社、06:00〜07:00 UTC、直接の接続なし、対策 | 一致（"five distinct regions…three different cloud providers"、"window between 06:00 and 07:00 UTC"、"no direct network connection or coupling"、legacy channel を無効化、"audited"、"use the level of infrastructure disruption we saw to prove…degraded conditions"） | ⑧ 妥当。①は定義とずれる（指摘 4）。更新 |
| 12 | CrowdStrike 2024-07-19 | 定義 21 個・渡すのは 20 個、21 番目の条件が初めて、検証器は 21 個前提、設定データ、対策 3 つ | 一致（RCA PDF 2024-08-06："21 input parameter fields"、"non-wildcard matching criterion for the 21st input"、"Rapid Response Content is configuration data; it is not code or a kernel driver"、compile time の検査、runtime array bounds check、staged deployment） | ① 妥当。設定の配布 |
| 13 | Google Cloud 2025-06-12 | 空の項目、数秒で全世界、null 参照、us-central1 の過負荷、乱数つき指数バックオフ無し、最大約 2 時間 40 分、掲示は約 1 時間後、対策 | 一致（"unintended blank fields"、"replicated globally within seconds"、"herd effect"、"did not have the appropriate randomized exponential backoff"、"up to ~2h 40 mins"、"~1h after the start of the crashes"、"fail open"、"propagated incrementally"） | ①③⑤⑧。①③⑤は明確。⑧は「リージョン別の配置が、全世界に複製される 1 つの表を共有」からの読み取り。引き金の分類は指摘 3 |
| 14 | Cloudflare 2025-11-18 | 5 分ごとに生成、行が重複し 2 倍、上限 200、プロキシが落ちた、対策 2 つ | 一致（11:20 UTC、"every five minutes"、"doubled in size"、"limit is set to 200"、panic、"Hardening ingestion of Cloudflare-generated configuration files in the same way we would for user-generated input"、"more global kill switches"） | ① 妥当。設定の配布（最初の出来事は DB の権限変更） |
| 15 | Cloudflare 2024-11-14 | 空の設定、安全装置が全顧客分を送る、下流が応答不能 | 一致（"blank configuration"、"fail open"、"transmitting events for all customers"、"Buftee became unresponsive"、"roughly 3.5 hours"・"about 55% of the logs" はスライドに出していない） | ① 妥当。設定の配布 |
| 16 | Cloudflare 2023-11-02 | 高可用クラスタ上のサービスが、1 拠点にしか無い Kafka と ClickHouse に依存、対策 | 一致（"Kafka and ClickHouse — were only available in PDX-04"、"never tested fully taking the entire PDX-04 facility offline"、GA 製品は高可用クラスタ必須、"chaos testing…including the full removal of each of our core data center facilities"） | ⑤⑧ 妥当（⑤："thundering herd problem"）。故障（電源） |
| 17 | Cloudflare 2020-11-02 | スイッチの部分故障、etcd が読み取り専用、同期複製を昇格、全複製の作り直し、6 時間 33 分、認証の DB が過負荷 | 一致（"six hours and 33 minutes"、"partially operating state"、"made the cluster read-only"、"requires a rebuild of all database replicas"、"primary authentication database was overwhelmed"）。対策の抜けは指摘 9 | ④ 妥当。故障 |
| 18 | Slack 2021-01-04 | 休暇明け、CPU 低下で縮小、1,200 台、供給の仕組みが詰まった、ダッシュボードが別の VPC、対策 | 一致（"first working day of the year"、"drop in CPU utilization initially triggered some automated downscaling"、"add 1,200 servers…between 7:01am PST and 7:15am PST"、"different VPC from their backend databases"、"regularly load test provision-service"） | ③④ 妥当。負荷の増加 |
| 19 | Slack 2022-02-22 | 25% ずつ、前の週の 2 回は無事、ピークと重なり連鎖障害、空の予備に替わる、全シャードに散る問い合わせ、起動要求を絞る、問い合わせを直した | 一致（"updated Consul on 25% of the fleet. It followed two previous 25% steps the prior week, both of which had occurred without any incident"、"as we hit peak traffic for the day"、"scatter query"、"throttle client boot requests"、"read from Vitess only the data that was missing from memcached"、"do not normally return to a stable state without a significant reduction in load or increase in capacity"）。「3 回目」は原文の言葉ではないが、2 回＋当日で数え方は正しい。公開日 2022-04-26 一致 | ⑤ 妥当。更新 |
| 20 | Google 2020-12-14 | 47 分、OAuth、古いデータを検出すると拒む、使用量 0、猶予切れで自動引き下げ | 一致（"for a duration of 47 minutes"、03:46〜04:33 US/Pacific、"will reject requests when it detects outdated data"、"reported the usage…as 0"、"grace period…expired"） | ①③。③はスライドに根拠が出ていない（指摘 6） |
| 21 | Cloudflare 2025-12-05 | 段階配布をしない仕組みで数秒、旧プロキシが 500、約 25 分、約 28%、11 月の後の対策は未完、対策 | 一致（08:47〜09:12 UTC "~25 minutes"、"approximately 28% of all HTTP traffic"、"does not perform gradual rollouts, but rather propagates changes within seconds"、FL1、"we have not finished deploying them yet"、"default to a known-good state"） | ① 妥当 |
| 22 | Cloudflare 2026-02-20 | 値なしのフラグを全件と解釈、約 1,100、25%、約 300 は人手、6 時間 7 分、対策 | 一致（17:48 UTC、"6 hours and 7 minutes"、`pending_delete`、"~1,100"、"25% of BYOIP prefixes"、"~300…manually restored…at 23:03 UTC"、"API schema standardization"、"circuit breaker"）。言い回しは指摘 2・7 | ⑦ 妥当 |
| 23 | PagerDuty 2025-08-28 | 1% → 5% → 25% と設定で拡大、25% で 1 回目、気づかず 75% で 2 回目、Kafka の監視が薄く段階配布があっても防げなかった | 一致（"starting at 1% on Aug 21, moving to 5% on Aug 27 and then 25% by the end of the day on the 27th…raised to 75% on the 28th"、1 回目 03:53 UTC・2 回目 16:38 UTC、"increasing the feature's rollout from 25% to 75%"、"hadn't realized it was correlated"、"gradually enabled via configuration rather than a distinct deployment"、"previously minimal alerting on Kafka, allowed the incident to occur, despite having a gradual rollout process in place"）。「25% の段階で 1 回目」は原文の日付と整合 | ② 妥当（Kafka は "the backbone of our decoupled, async architecture"） |
| 24 | Azure 2024-01-21（NKRF-1TG） | Storage・Key Vault・Event Hubs・Service Bus が RBAC の方針を ARM から取得、キャッシュが切れて拒む、West Europe で 20 倍超、絞り込みを強めた | 一致（01:30〜08:58 UTC、"rely on ARM to download RBAC authorization policies"、"once the cached data expired these services failed, rejecting incoming requests"、"increased traffic in West Europe by over 20x"、"increased throttling"）。原文の表記は "Event Hub" | ②⑤ 妥当 |
| — | GitHub 2021-11-27（S231） | 2 時間 50 分、最後の rename の段、デッドロック、クラッシュ回復、破損なし、移行を一時停止、分割、余裕を増やす、原因は調査中 | 一致（"November 27 20:40 UTC (lasting 2 hours and 50 minutes)"、"no data corruption"、"paused schema migrations"、"canary mode on a single shard"、"increase the amount each cluster is over-provisioned"、"continuing to investigate"）。公開日 2021-12-01 一致。「多く」は指摘 5 | — |

### 型ごとの件数と引き金の件数（verify_p14.md の割り当てを数え直した）

- 型：① 7（3＋ほか 4）、② 6（3＋ほか 3）、③ 9（3＋ほか 6）、④ 5、⑤ 7、⑥ 3、⑦ 5、⑧ 3。S209 の「ほか n 件」とすべて一致。
- 引き金（指定の 19 件）：設定の配布 4、コマンド・スクリプト 3、更新・有効化 3、容量・スケール 2、保守作業 1（計 13）、故障 3、負荷 2、潜在的な不具合 1。合計 19。S207・S220・S250・S253 の数字と一致。境目は指摘 3（Google Cloud 2025）。
- 事業者の数 13（GitLab、AWS、GitHub、Meta、Roblox、Atlassian、Datadog、CrowdStrike、Google、Cloudflare、Slack、PagerDuty、Microsoft）、年の幅 2015〜2026 も一致。

## 3. 確かめて一致した主な事実（製品・文書）

1. Aurora DSQL：分離レベルは固定（"The transaction isolation level is fixed at PostgreSQL Repeatable Read"）。OCC で、衝突はコミット時に直列化エラー（SQLSTATE 40001）。ユーザーガイドの concurrency control／migration のページ。
2. Aurora DSQL：トリガー・PL/pgSQL・一時表・TRUNCATE は使えない（"not procedural languages like PL/pgSQL"、"No temporary tables"、"Use DELETE FROM table_name instead of TRUNCATE"）。
3. Aurora DSQL のクォータ：1 トランザクションで変更できる行は 3,000、接続の最長は 60 分（ほかにトランザクション 5 分、10 MB）。CHAP_quotas。
4. Spanner（PostgreSQL インターフェース）：非対応の一覧は Triggers／SERIAL／Fine-grained concurrency control／SAVEPOINT／Transactional DDL／Partial indexes／Extensions／Foreign data wrappers／User-defined data types, functions and operators。スライドの列挙と一致（Last updated 2026-11-12）。
5. Spanner：既定は Serializable（isolation-levels のページ）。
6. CockroachDB：v26.4 は実在（Regular、2026-10-26）。既定は SERIALIZABLE。非対応に range types・XA syntax・Column-level privileges・Foreign data wrappers。整数の割り算は decimal（`//` で切り捨て）。
7. PostgreSQL 18 文書 29.8 Restrictions：スキーマと DDL は複製されない、シーケンスのデータは複製されない、切り替え先にするならシーケンスを最新の値に進める。節番号も一致。
8. PostgreSQL 18 文書 24.1（Routine Vacuuming）：UPDATE・DELETE は古い行の版をすぐには取り除かない、VACUUM が取り除き再利用に回す。
9. Kafka 4.4 Design：キーと null のペイロードが削除（トゥームストーン）、delete.retention.ms（既定 24 時間）より遅れた受け手は削除の印を見逃しうる、書き込み中のセグメントはコンパクションされない、max.compaction.lag.ms は "not a hard guarantee"。
10. ClickHouse DELETE：軽量 DELETE は印を付けるだけ、物理的な削除は次のマージ、"for an unspecified period"、期限が要るなら min_age_to_force_merge_seconds か ALTER TABLE … DELETE。
11. Debezium 3.7 PostgreSQL コネクタ：tombstones.on.delete の既定は true、削除イベントの後にトゥームストーン。
12. AWS Builders' Library 2 本：どちらも Published Dec 5, 2019。静的な安定性の定義、フォールバックは試しにくい・それ自体が失敗する・読めない負荷、IAM ロールの認証情報は "proactively pushed to every instance and remain valid for many hours"。
13. Cloudflare「Code Orange: Fail Small」：2025-12-19 公開。"Require controlled rollouts for any configuration change that is propagated to the network, just like we do today for software binary releases"。
14. Stripe「Online Migrations at Scale」：2017-02-02、4 段階（二重書き込み → 読みの切替 → 書きの切替 → 旧データの削除）、Scientist による読みの照合。
15. S223・S238 の「未検証」「公式文書の記述（2026-11 確認）」の印は付いている。S206・S254 の「自己申告」の印も付いている。

## 4. 確かめなかった範囲

- 書籍（DDIA 2e、『プラットフォームエンジニアリング』『ハードパーツ』『大規模データ管理』）の章・ページ、法と機関（Data Act、GDPR、EDPB、個人情報保護委員会、NIST、Datatilsynet、Deutsche Wohnen、DPC、EU AI 規則）。別の観点の担当範囲。
- 事後報告の図・グラフの中の数字（本文の文字だけを検索した）。verify_p14.md の「28 件のうち原文を開けた件」という内部の数。
- PostgreSQL 18 文書 13.2（既定 Read Committed）は今回は開いていない（広く知られた既定値）。Aurora PostgreSQL の「固有のページを確かめられず」という主張の再検索もしていない。
- 製品の実機でのふるまい（文書の記述だけ）。Part 17 は新しい事実を足していないので、Part 14〜16 との数字・問いの文言の整合だけを見た。

## 5. 開いた原文（主なもの）

verify_p14.md の 24 件の URL（すべて取得できた。CrowdStrike は PDF）に加えて：
- https://github.blog/news-insights/company-news/github-availability-report-november-2021/
- https://aws.amazon.com/builders-library/static-stability-using-availability-zones/ ／ https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/
- https://blog.cloudflare.com/fail-small-resilience-plan/
- https://docs.aws.amazon.com/aurora-dsql/latest/userguide/ （working-with-postgresql-compatibility-unsupported-features、CHAP_quotas、working-with-concurrency-control）
- https://cloud.google.com/spanner/docs/reference/postgresql/overview ／ https://cloud.google.com/spanner/docs/isolation-levels ／ https://cloud.google.com/spanner/docs/postgresql-interface
- https://www.cockroachlabs.com/docs/v26.4/postgresql-compatibility ／ /docs/v26.4/transactions ／ /docs/releases/
- https://www.postgresql.org/docs/18/logical-replication-restrictions.html ／ https://www.postgresql.org/docs/18/routine-vacuuming.html
- https://kafka.apache.org/44/design/design/
- https://clickhouse.com/docs/sql-reference/statements/delete
- https://debezium.io/documentation/reference/3.7/connectors/postgresql.html
- https://stripe.com/blog/online-migrations
