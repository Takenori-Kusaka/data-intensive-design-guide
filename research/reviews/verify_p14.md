# Part 14 事実の確かめ直し

確認日：2026-11-18。確かめ方：事業者の一次報告の URL を curl で取得し、HTML（CrowdStrike は PDF）を手元でテキスト化して、書き手が該当の文を直接読んだ（要約ツールは通していない）。短い報告（S3、Meta 2021、Cloudflare 2025-12）は全文、ほかは事実ごとに該当の文を検索して読んだ。書籍は `research/books/text/0141-3.txt` の本文で確認。

## 1. 開いた事後報告と、確かめた事実（件ごと）

「指定」は計画で指定された 19 件。引き金の分類は Part 1 と同じ数え方（報告が最初に挙げる出来事で 1 件 1 分類）。

| # | 件（発生日） | URL | 原文で確かめた事実（スライドに使ったもの） | 型 | 引き金の分類 |
| --- | --- | --- | --- | --- | --- |
| 1 | GitLab 2017-01-31（指定） | https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ | ±19:00 UTC に負荷増（スパムと推測）。二次側のつもりで一次側の DB ディレクトリを消去、約 300 GB。pg_dump は 9.2 のバイナリで 9.6 に対して動き失敗。cron の通知メールは DMARC 未設定で拒否。約 6 時間前の手動 LVM スナップショットから復元。「down for about 18 hours」。対策：バックアップの監視、復元の自動テスト、データ耐久性の責任者 | ⑥⑦ | 負荷の増加（Part 1 に合わせた） |
| 2 | AWS S3 2017-02-28（指定） | https://aws.amazon.com/message/41926/ | 9:37 PST、手順書に沿ったコマンドの入力の誤りで意図より多くのサーバーを外した。索引と配置のサブシステムが全面再起動。大きなリージョンでは長年全面再起動をしておらず想定より長い。13:54 PST 復旧。SHD の管理画面が S3 に依存し 11:37 まで個別の更新不可。対策：外す速度を落とす、最低容量を割る操作を防ぐ、SHD 管理画面を複数リージョンで | ③⑦ | 変更：コマンド |
| 3 | GitHub 2018-10-21（指定） | https://github.blog/news-insights/company-news/oct21-post-incident-analysis/ | 故障しかけた 100G 光機器を交換する定例の保守作業で 43 秒の切断。Orchestrator が西海岸へ昇格。劣化 24 時間 11 分。「Orchestrator's actions behaved as configured」。バックアップからクラスタ全体を作り直したことは無く、数テラバイトの復元に数時間。対策：リージョンをまたぐ昇格を防ぐ設定 | ④⑥ | 変更：保守作業 |
| 4 | AWS DynamoDB 2015-09-20（指定） | https://aws.amazon.com/message/5467D2/ | 2:19 PDT の短いネットワーク障害。担当範囲（membership）をメタデータサービスに取り直し、時間切れ→再試行で高負荷が続く。エラー率は約 55% で安定。5:06 にメタデータサービスへの要求を止め、容量を足した。7:10 回復。対策：メタデータサービスの分割ほか。**ページの記載は「Sunday, September 20」で年が無い**（2015 年 9 月 20 日は日曜） | ②⑤ | 故障 |
| 5 | AWS Kinesis 2020-11-25（指定） | https://aws.amazon.com/message/11201/ | 引き金は少量の容量追加（「trigger, though not root cause」）。全サーバーが OS のスレッド数上限を超過。Kinesis の全面回復は 10:23 PM PST。Cognito は Kinesis への送信がベストエフォートの設計で、バッファの潜在不具合で Web サーバーが塞がった。SHD の投稿の道具が Cognito に依存、予備の道具は手作業が多く使い慣れず遅れた。対策：セル分割の前倒し、大口サービスを別の群へ、予備の道具の定期訓練 | ②③ | 変更：容量の追加 |
| 6 | AWS 2021-12-07（指定） | https://aws.amazon.com/message/12721/ | 7:30 PST、自動の容量調整が内部ネットワーク側のクライアントに想定外の挙動を起こし、接続の急増で機器が混雑。監視と展開の仕組みが内部ネットワーク上。稼働中の EC2 は影響なし、Route 53 は変更 API のみ不調で既存の応答は影響なし。サポートの問い合わせ作成が 7:33〜14:25 不可。対策：サポートの仕組みを複数リージョンで | ③⑤ | 変更：自動のスケール |
| 7 | AWS 2025-10-19〜20（指定） | https://aws.amazon.com/message/101925/ | DNS 管理の自動化の潜在的な競合。遅れた Enactor が古い計画を上書きし、別の Enactor の掃除がその計画を削除、入口の DNS レコードが空に。人手の介入が必要。DWFM が「congestive collapse」、4:14 に流入を絞り選択的に再起動。NLB はヘルスチェック失敗で自動の AZ フェイルオーバー。対策：自動化を全世界で停止、NLB に velocity control | ②④⑤⑦ | 潜在的な不具合 |
| 8 | Meta 2021-10-04（指定） | https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/ | 保守作業中のコマンドがバックボーンの全接続を落とした。監査の道具の不具合で止まらず。DNS サーバーは DC に届かないと BGP 広告を取り下げる作り。社内の道具が使えず現地へ。防御が復旧を遅らせたが価値のある取引と記載。**停止時間の記載なし**（全文を読み、hours／minutes の語が無いことを確認） | ③④ | 変更：コマンド |
| 9 | Roblox 2021-10-28（指定） | https://about.roblox.com/newsroom/2022/01/roblox-return-to-service-10-28-10-31-2021 | 73 時間の停止。Consul をサービス発見・ヘルスチェック・ロック・KV に使用。10/27 にトラフィック経路のサービスで streaming を有効化。BoltDB の freelist。監視と Consul の循環依存。対策：監視を監視対象に依存させない、重要サービスを専用クラスタへ、拠点とゾーンの追加 | ②③ | 変更：機能の有効化 |
| 10 | Atlassian 2022-04-05（指定） | https://www.atlassian.com/blog/how-we-build/post-incident-review-april-2022-outage | 07:38〜08:01 UTC に 883 サイト（顧客 775）を即時削除。API はサイト ID もアプリ ID も受け、種類を確かめない。最長 14 日。顧客の連絡先の一部が消え通常の問い合わせ不可。「missed our RTO but met our RPO」。対策：ソフトデリートを全体に、複数サイトの復元の自動化、連絡先のバックアップ | ③⑥⑦ | 変更：スクリプト |
| 11 | Datadog 2023-03-08（指定） | https://www.datadoghq.com/blog/2023-03-08-multiregion-infrastructure-connectivity-issue/ | 06:00 UTC、systemd の自動セキュリティ更新。5 リージョン、クラウド 3 社。OS 既定の更新窓 06:00〜07:00 UTC。数万ノード。リージョン間に直接の接続なし。対策：旧い更新経路を無効化、同種を監査、同規模の劣化を試験に | ①⑧ | 変更：更新 |
| 12 | CrowdStrike 2024-07-19（指定） | https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf | 定義は入力 21 個、渡すのは 20 個。21 番目に非ワイルドカードの条件が初めて入り範囲外読み取り。検証器は 21 個前提で通した。「Rapid Response Content is configuration data; it is not code or a kernel driver」。対策：コンパイル時の項目数検査、境界検査、段階配布 | ① | 変更：設定の配布 |
| 13 | Google Cloud 2025-06-12（指定） | https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW | 5/29 に Service Control へ新機能（機能フラグなし）。6/12 に空の項目を含むポリシーが Spanner に入り数秒で全世界に複製、null 参照で再起動の繰り返し。us-central1 は herd effect、乱数つき指数バックオフなし、解消まで最大約 2 時間 40 分。状況ページの最初の掲示は約 1 時間後。対策：fail open、全世界複製データの段階的な伝搬 | ①③⑤⑧ | 変更：設定の配布 |
| 14 | Cloudflare 2025-11-18（指定） | https://blog.cloudflare.com/18-november-2025-outage/ | 11:20 UTC 開始、14:30 大部分回復、17:06 全面回復。ClickHouse の権限変更で特徴量ファイルの行が重複し 2 倍に。5 分ごとに生成。上限 200 個を超えて panic。対策：自社生成の設定を利用者入力と同等に検査、全体の停止スイッチ | ① | 変更：設定の配布 |
| 15 | Cloudflare 2024-11-14（指定） | https://blog.cloudflare.com/cloudflare-incident-on-november-14-2024-resulting-in-lost-logs/ | 約 3.5 時間、ログの約 55% を失った。空の設定→「fail open」の安全装置が全顧客分を送る。Buftee が応答不能。保護の仕組みは設定されていなかった | ① | 変更：設定の配布 |
| 16 | Cloudflare 2023-11-02（指定） | https://blog.cloudflare.com/post-mortem-on-cloudflare-control-plane-and-analytics-outage/ | 拠点 PDX-04 の電源喪失。高可用クラスタ上のサービスが PDX-04 にしか無い Kafka と ClickHouse に依存。拠点丸ごとの停止は未試験。対策：GA の製品は高可用クラスタ必須、拠点を丸ごと外すカオス試験 | ⑤⑧ | 故障 |
| 17 | Cloudflare 2020-11-02（指定） | https://blog.cloudflare.com/a-byzantine-failure-in-the-real-world/ | スイッチの部分故障。etcd が読み取り専用に。同期複製を自動昇格、昇格で全複製の作り直しが要る不具合。API とダッシュボードが 6 時間 33 分劣化。不具合は修正済みと記載 | ④ | 故障 |
| 18 | Slack 2021-01-04（指定） | https://slack.engineering/slacks-outage-on-january-4th-2021/ | 休暇明け最初の営業日。Transit Gateway の過負荷。CPU 使用率の低下で自動の縮小、その後 7:01〜7:15 に 1,200 台の追加を試み provision-service が詰まった。ダッシュボードは DB と別の VPC。対策：同じ VPC に置く、provision-service の定期的な負荷試験 | ③④ | 負荷の増加 |
| 19 | Slack 2022-02-22（指定） | https://slack.engineering/slacks-incident-on-2-22-22/ | Consul エージェントの更新を 25% ずつ。前週の 2 回の 25% は無事。その日のピークで連鎖障害。全シャードに散る問い合わせ、時間切れでキャッシュを埋め直せない。クライアントの起動要求を絞った | ⑤ | 変更：更新 |
| 20 | Google 2020-12-14 | https://status.cloud.google.com/incident/zall/20013 | 47 分（03:46〜04:33 US/Pacific）、OAuth を要する顧客向けサービスが利用不能。旧い割当の仕組みが使用量 0 と報告、猶予切れで自動の割当引き下げ、Paxos リーダーが書けず。古いデータを検出すると要求を拒む作り | ①③ | （19 件の外） |
| 21 | Cloudflare 2025-12-05 | https://blog.cloudflare.com/5-december-2025-outage/ | 08:47〜09:12 UTC、約 25 分、HTTP 通信の約 28%。バッファ拡大は段階配布、試験用ルールの停止は数秒で全体に届く仕組み。11/18 後の対策は未完と記載。対策：設定にも健全性の確認と巻き戻し、既知の良い状態で続ける | ① | （同上） |
| 22 | Cloudflare 2026-02-20 | https://blog.cloudflare.com/cloudflare-outage-february-20-2026/ | 17:48 UTC 開始、全体 6 時間 7 分。値なしの `pending_delete` を API が全件と解釈。BYOIP 4,306 のうち約 1,100（25%）を取り下げ（17:56〜18:46）。約 800 は 20:20 ごろ、約 300 は 23:03 に人手で復旧。変更は順に適用。対策：API スキーマの標準化、遮断器 | ⑦ | （同上） |
| 23 | PagerDuty 2025-08-28 | https://www.pagerduty.com/eng/august-28-kafka-outages-what-happened-and-how-were-improving/ | 1 回目 03:53 UTC、2 回目 16:38 UTC。要求ごとに Kafka プロデューサを生成。1%（8/21）→ 5%・25%（8/27）→ 75%（8/28）。「despite having a gradual rollout process in place」 | ② | （同上） |
| 24 | Microsoft Azure 2024-01-21（NKRF-1TG） | https://azure.status.microsoft/en-us/status/history/?trackingId=NKRF-1TG | 01:30〜08:58 UTC。Storage・Key Vault・Event Hub・Service Bus は RBAC の方針を ARM から取得し、キャッシュが切れると要求を拒んだ。West Europe は再試行の嵐で通信が 20 倍超、絞り込みを強めて回復 | ②⑤ | （同上） |

事後報告以外に開いた一次資料：

| 資料 | URL | 確かめた事実 |
| --- | --- | --- |
| AWS Builders' Library「Static stability using Availability Zones」（2019-12-05） | https://aws.amazon.com/builders-library/static-stability-using-availability-zones/ | 静的な安定性の定義（依存先が傷んでも、していたことが動き続ける）。データプレーンは既存の状態を保ちコントロールプレーンの障害時も動く。公開日 |
| 同「Avoiding fallback in distributed systems」（2019-12-05） | https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/ | フォールバックは試しにくい・それ自体が失敗する・読めない負荷をかける。代替（主経路の信頼性、呼び出し側に誤りを返す、先に配る、フェイルオーバーに変える）。IAM ロールの認証情報は先に配られ何時間も有効 |
| Cloudflare「Code Orange: Fail Small」（2025-12-19） | https://blog.cloudflare.com/fail-small-resilience-plan/ | ネットワークに配る設定変更に、ソフトウェアのリリースと同じ管理された段階配布を求める |
| 『プラットフォームエンジニアリング』p.145〜146 | research/books/text/0141-3.txt | 基盤はステートフルな傾向があり変更管理が前提。脚注：カナリアは安全機構でありテスト機構ではない |

## 2. スライドごとの確認

| スライドの題 | 事実 | 出典 | 確かめ方 | 結果 |
| --- | --- | --- | --- | --- |
| 事後報告 24 件を原文で読み、型に分けた | 24 件、13 事業者、2015〜2026 年 | 上表 #1〜24 | 本文確認 | 一致（数え直した） |
| 同 | Meta 2021 の報告に停止時間が無い | #8 | 本文確認（全文） | 一致 |
| 同 | Cloudflare は 2025-12 に、11/18 後の対策が未完と書いた | #21 | 本文確認 | 一致 |
| 引き金は、19 件のうち 13 件が変更や操作だった | 変更・操作 13（4・3・3・2・1）、故障 3、負荷 2、潜在不具合 1 | #1〜19 | 本文確認。Part 1 の数え方と数に揃えた | **修正した**（ノート 09 の「故障 3 件＝Cloudflare 2023・2020、GitHub 2018、残りは変更」は原文と合わない。§3 参照） |
| 同 | 43 秒、24 時間 11 分 | #3 | 本文確認 | 一致 |
| 同 | 基盤は状態を持ち変更管理が前提 | 『プラットフォームエンジニアリング』p.145〜146 | 書籍本文で確認 | 一致 |
| 全体が止まる条件は… | Google 2020 の 47 分、古いデータを拒む作り | #20 | 本文確認 | 一致（ノートの「47 分／50 分」の揺れは、報告本文の 47 分を採った） |
| 同 | Azure 2024 のキャッシュ切れで拒否 | #24 | 本文確認 | 一致 |
| 同 | AWS 2021 で稼働中の EC2 と既存の DNS 応答は影響なし | #6 | 本文確認 | 一致 |
| 型①… | CrowdStrike・Google 2025・Cloudflare 2 件の各欄 | #12・13・14・21 | 本文確認 | 一致 |
| 型②⑧… | Roblox 73 時間、DynamoDB 約 55%、Kinesis→Cognito、Datadog、Cloudflare 2023 | #9・4・5・11・16 | 本文確認 | 一致。ノートの「61 時間」は使わず |
| 同 | PagerDuty の利用分析の新機能 | #23 | 本文確認 | 一致。「本流と同じ Kafka を共有」という言い方は原文で確かめていないので書かなかった |
| 型③… | 9 件 | #2・5・6・8・9・10・13・18・20 | 本文確認 | **修正した**（ノートは 10 件。PagerDuty の状況ページが障害側に依存していたことは原文で確かめられず、外した） |
| 型④… | 各欄 | #3・17・7・18・8 | 本文確認 | 一致 |
| 型⑤… | 各欄。Azure の 20 倍超、Google の約 2 時間 40 分 | #4・13・19・24・7 | 本文確認 | 一致 |
| 型⑥⑦… | GitLab、Atlassian、S3、Cloudflare 2026、GitHub 2018 | #1・10・2・22・3 | 本文確認 | 一致。GitLab の「変更約 6 時間分を失った」は、報告の要約が「17:20〜00:00 UTC」と書くので載せるのをやめた |
| 設定やルールもデータ… | 5 件の食い違い、CrowdStrike の位置づけ、Cloudflare の計画 | #12・14・15・22・20、Fail Small | 本文確認 | 一致 |
| 段階配布は万能ではない… | Slack 2022 の 25% × 3、PagerDuty の段階 | #19・23 | 本文確認 | **修正した**（ノートは「1%→75% の途中」。原文は 25% で 1 回目、75% に上げて 2 回目） |
| 同 | Cloudflare 2026 は順に適用、25% | #22 | 本文確認 | 一致 |
| 同 | カナリアは安全機構 | 『プラットフォームエンジニアリング』p.145 脚注 | 書籍本文で確認 | 一致（言い換え。引用にしていない） |
| 対策の軸は静的な安定性… | 定義、IAM の例、フォールバックの危険 | Builders' Library 2 本 | 本文確認 | 一致 |
| 設計レビューで問うこと… | 中央の列の各事例 | 上表 | 本文確認 | 一致。「危ない兆候」は本ガイドの整理（ノートに明記） |

## 3. Part 1 と食い違う件／調査ノートと食い違う件

引き金の分類は Part 1 の数（13・3・2・1）に揃えた。Part 1 は件ごとの割り当てを載せていないので、Part 14 の表の割り当ては書き手の推定。突き合わせが要る点：

| 件 | Part 14 の表の置き場所（Part 1 に合わせた推定） | 書き手が原文を読んだ見立て |
| --- | --- | --- |
| GitLab 2017 | 負荷の増加 | 報告の時系列は、17:20 の手動スナップショット（作業の準備）→ 19:00 の負荷増 → 23:00 の複製の遅れ → 誤削除。停止とデータ損失の直接の原因は人の操作。「人の操作」に入れる数え方もありうる（その場合 変更・操作 14、負荷 1） |
| AWS 2025 | 変更を伴わない潜在的な不具合 | 異論なし。ただし型④（自動化の誤動作）にも入れている |
| AWS 2021 | 変更：容量の追加・自動のスケール | 人の変更ではなく自動の動作。分類の名前どおりで異論なし |
| GitHub 2018 | 変更：保守作業 | 「故障しかけた機器の交換」。ノート 09 はこれを故障に数えていた |
| DynamoDB 2015 | 故障 | ノート 09 は故障に数えていなかった（原文は「brief network disruption」） |
| Slack 2021 | 負荷の増加 | ノート 09 は「変更」側に入れていた |

ほかの注意：

- ノート 09 の表は内容のある行が 29 行ある（指定 19＋追加 10。うち SRE 本の 2 行は書籍）。スライドは outline の「28 件」をそのまま書いた。数え方を取りまとめ側で確かめてほしい
- 使わなかった件（原文を開いていない）：Facebook 2010-09-23、GitHub 2021-11-27、Azure 2026-09 の 2 件、SRE 本 26 章の Gmail・Music、未確認の 3 件
- DynamoDB の件の年（2015）は AWS のページに無い
- Slack 2022 の開始時刻、PagerDuty の「95% を 38 分」、Roblox の「61 時間」は原文にあるが、スライドには載せていない
- メタステーブル障害の原論文（Bronson ほか、HotOS 2021）は開いていない。スライドには載せず、Slack 2022 の報告が引いていることも書いていない（Part 10 への参照のみ）
