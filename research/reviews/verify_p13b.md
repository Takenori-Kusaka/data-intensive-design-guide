# verify_p13b：Part 13 後半（認証・AI・セキュリティ基盤、共通の型、レビュー、まとめ）の確かめ直し

確認日：2026-11-18。対象：`deck/p13b.js`（12 枚）。Web は URL を開いて本文で確かめた（取得ツールの抽出経由。CrowdStrike の RCA、Sculley ほかの論文、NIST SP 800-53 は原ファイルを取得して該当箇所を直接読んだ）。書籍は `research/books/text/` の本文で確かめた。

| スライドの題 | 事実 | 出典（URL か書籍ページ） | 確かめ方 | 結果 |
| --- | --- | --- | --- | --- |
| 認証基盤：利用者・鍵・方針が正で、トークンは導出 | JWT のアクセストークンは、鍵を認可サーバーのメタデータの jwks_uri から得て、typ・iss・aud・署名・exp を検証する。2021-10、Proposed Standard | https://www.rfc-editor.org/rfc/rfc9068 §4 | 本文確認 | 一致 |
| 同上 | 検証側は知らない kid を見たら jwks_uri を取り直す | https://openid.net/specs/openid-connect-core-1_0.html §10.1.1（errata set 2、2023-12-15） | 本文確認 | 一致 |
| 同上 | OPA のバンドルは方針とデータを含み、定期取得、更新は結果整合 | https://www.openpolicyagent.org/docs/management-bundles | 本文確認 | 一致（OPA の版はページに表示なし。版は書かなかった） |
| 同上 | PIP の例に ID プロバイダーから得る利用者の属性。8.2.6 ID プロバイダー | 『大規模データ管理 第2版』p.241（PDF p.267） | 書籍本文で確認 | 一致 |
| 同上 | 「トークンは発行時点の写し」「RFC 9068 は失効を定めない」 | RFC 9068 | 本文確認 | 修正した。RFC に「写し」という文言は無い。「本ガイドの当てはめ」と注記した。「失効を定めない」は載せるのをやめた |
| 手元の検証は、止まらなさと失効の遅さの交換 | 応答はキャッシュしてよい（MAY）。性能と安全の釣り合いを考えなければならない（MUST）。exp を超えてキャッシュしてはならない。2015-10 | https://www.rfc-editor.org/rfc/rfc7662 §4 | 本文確認 | 一致 |
| 同上 | 新しい鍵を JWK Set に足す、kid を JOSE ヘッダーに入れる、退役した鍵は移行のため妥当な期間残す | OpenID Connect Core 1.0 §10.1.1 | 本文確認 | 一致 |
| 同上 | jwks_uri の応答に Cache-Control の max-age を付けるべき | 同 §10.2.1 | 本文確認 | 載せるのをやめた。10.2.1 は暗号化鍵の入れ替えの節で、署名鍵の検証側のキャッシュの根拠には使えない |
| 同上 | 「認証基盤が止まっても期限までは検証できる」 | — | — | 仕様の文言ではない。`L.note(s, 'add', …)` で本ガイドの整理と明示 |
| 同上 | NIST SP 800-204 の MS-SS-1（期限を短く）、方針のキャッシュ | NIST SP 800-204 | 未確認 | 載せるのをやめた（原文を開いていない） |
| 止まったとき拒否するか通すかは、選んで書く | Google 2020-12-14：本文の時系列は 03:46〜04:33（US/Pacific）、「47 分」。見出しは 04:07〜06:23。速報は 03:45〜04:35、50 分 | https://status.cloud.google.com/incident/zall/20013 | 本文確認 | 一致。スライドは本文の時系列を使い、ノートに食い違いを書いた |
| 同上 | User ID Service は安全のため古いデータを検出すると要求を拒む。割当が下がり Paxos のリーダーが書けず、読み取りの大半が古くなった。サポートの社内の道具が影響を受け、連絡が遅れた | 同上 | 本文確認 | 一致 |
| 同上 | failurePolicy は Ignore か Fail。既定は Fail。タイムアウトは既定 10 秒、1〜30 秒 | https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/ （v1.37 の文書） | 本文確認 | 一致（タイムアウトの値はスライドに載せていない） |
| 同上 | Entra：既存のセッションは開始時のデータで評価（既定で有効）。新規セッションとゲストは対象外。無効にすると、実時間で評価できなければ拒否。文書の日付 2026-03-24 | https://learn.microsoft.com/en-us/entra/identity/conditional-access/resilience-defaults | 本文確認 | 一致。「既存セッションは通す」は、要る制御を満たしていた場合などの条件つきなので、「開始時の情報で評価して通す」と書いた |
| 同上 | OPA：persist でディスクに保存し、バンドルサーバーに届かなくても直近に有効化したバンドルで起動できる。署名の検証に失敗したら今のバンドルを使い続ける | https://www.openpolicyagent.org/docs/management-bundles | 本文確認 | 一致 |
| 同上 | Cedar はポリシー言語、版 4.6 | https://docs.cedarpolicy.com/ | 本文確認（冒頭ページ） | 一致。評価の規則（既定で拒否など）とエンティティの渡し方は確かめておらず、載せていない |
| 同上 | AuthZEN Authorization API 1.0 は Final（2026-01-11）。PEP と PDP の間の API。ポリシー言語・構成・状態管理は範囲外 | https://openid.net/specs/authorization-api-1_0.html | 本文確認（末尾約 4% は未読） | 一致 |
| 特徴量・埋め込み・索引・モデルは導出データ | モデルは訓練データから導出され、推論の出力は入力とモデルから導出される | DDIA 2e p.548（PDF p.566） | 書籍本文で確認 | 一致 |
| 同上 | 不安定なデータ依存の対策は信号の版つきの写し。古くなる危険と複数の版を保つ費用がある | Sculley ほか NIPS 2015（https://papers.nips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf ）「Unstable Data Dependencies」 | PDF を取得して本文確認 | 一致 |
| 同上 | ML メタデータ：パイプラインと部品の版、引数、成果物への参照、前のモデルへの参照、評価指標 | https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning | 本文確認 | 一致（ページの日付は取得できず。確認月を書いた） |
| 同上 | 埋め込み空間は同じ埋め込みモデルの埋め込みで埋めたベクトル項目から成る。dimensions は埋め込みモデルによる | https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-create-index （2026-11-09） | 本文確認 | 一致 |
| 同上 | 特徴量の列に所有者と文書を付ける（#11） | https://developers.google.com/machine-learning/guides/rules-of-ml | 本文確認 | 一致 |
| 学習と推論のずれは、同じ定義と時点の正しさで防ぐ | ずれの定義（学習時と推論時の性能の差）と 3 つの原因。#29・#32・#37 の題 | 同上 | 本文確認 | 一致 |
| 同上 | 各行の時刻からさかのぼり、幅は TTL まで。TTL の基準は各行の時刻。既定では event timestamp だけで絞るので、後から埋め戻した値が返りうる | https://docs.feast.dev/getting-started/concepts/point-in-time-joins | 本文確認 | 一致 |
| 同上 | 既存の項目の変更・削除には、削除して全体を作り直すことが多い | Azure AI Search 文書（上記）「Update a vector index」 | 本文確認 | 一致 |
| 同上 | 埋め込みモデルを替えるとき、並行して作って切り替える | — | — | 一次資料なし。`L.note(s, 'add', …)` で明示 |
| 推論の入出力を記録し、AI なしの経路を決めておく | #29：推論時に使った特徴量を保存し、学習に使う。全件が無理なら一部でも | Rules of ML | 本文確認 | 一致 |
| 同上 | 監視の出発点：予測の偏り、行動の上限（達したら警告と人の調査） | Sculley ほか NIPS 2015「Monitoring and Testing」 | PDF を取得して本文確認 | 一致 |
| 同上 | 実験のたびに出力・パラメータ・メトリクス・アルゴリズムを記録し、保存した実験データで結果を再現する | 『大規模データ管理 第2版』11.5.2 節 p.328（PDF p.354） | 書籍本文で確認 | 一致。「規制当局への証明」は該当箇所を読み切っておらず、載せていない |
| 同上 | ゲートウェイは単一障害点になりうる。生の要求と応答が通り、法令対応の範囲に入る。遅延が増える。合意した SLO を危うくするなら入れるな。2026-04-30 | https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/azure-openai-gateway-guide | 本文確認 | 一致 |
| 同上 | プロンプトと応答の保存範囲、AI が使えないときのふるまいを定める標準 | — | — | 一次資料なし。`L.note(s, 'add', …)` で明示。NIST AI RMF の本文は開いておらず、引いていない |
| 同上 | Thoughtworks Radar の LiteLLM／agentgateway の位置 | — | 未確認 | 載せるのをやめた |
| 監査ログは記録のシステム。書けないときを決める | AU-5：監査ログの処理の失敗時に警告し、組織が定めた追加の行動を取る。例は最も古い記録の上書き、システムの停止、記録の生成の停止。警告だけの選択も可。AU-9：不正な参照・変更・削除から守る | NIST SP 800-53 Rev.5（5.2.0）の OSCAL 版カタログ（https://github.com/usnistgov/oscal-content ） | 原ファイルを取得して本文確認 | 修正した。ノート 08 は「書けないときの扱いを明示する一次資料なし」としていたが、AU-5 が該当する。どれを選ぶかの基準だけを「本ガイドの考え」とした |
| 同上 | ファイルごとのハッシュ（SHA-256）。1 時間ごとのダイジェスト。秘密鍵で署名。各ダイジェストは前のダイジェストの署名を含む | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html | 本文確認 | 一致 |
| 同上 | 自作の監査テーブルでは、監査ログと DB 状態の完全性の保証は依然として困難 | DDIA 2e 13.3.4.5 節 p.573（PDF p.591） | 書籍本文で確認 | 一致 |
| 同上 | 診断のログの「捨てて数える」（OTLP） | — | 未確認（前半 p13.js の担当） | 載せるのをやめた。「ログ基盤のスライド」への参照にした |
| 鍵の入れ替えは再暗号化ではない | ローテーションで替わるのは現在の鍵素材だけ。KMS キーは同じ論理的な資源。復号の鍵素材は KMS が自動で選ぶ。データは再暗号化されず、データキーも替わらない。漏れたデータキーの影響を緩和しない。周期は指定しなければ 365 日 | https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html | 本文確認 | 一致。365 日は「自動ローテーションを有効にし、周期を指定しないとき」の値なので、ノートにその条件で書いた |
| 同上 | DEK と KEK の定義。DEK は手元で生成、書き込みごとに新しく、データの近くに包んで保存。KEK は中央に置き、KMS の外に出ない | https://docs.cloud.google.com/kms/docs/envelope-encryption | 本文確認 | 一致（64KiB の上限は載せていない） |
| 同上 | ローテーションは暗号化済みのデータを再暗号化しない。不正使用が疑われるときは、復号 → 新しい主版で暗号化 → 古い版を無効化または破棄予約 | https://docs.cloud.google.com/kms/docs/re-encrypt-data | 本文確認 | 一致 |
| 分類は所有者が決め、製品の更新は段階的に配る | 分類の一覧は中央で管理し、増やしすぎない。ラベル 4 段（Highly Confidential〜Public）。分類から自動でラベルを付ける | 『大規模データ管理 第2版』8.2.3 節 p.236〜237（PDF p.262〜263） | 書籍本文で確認 | 一致 |
| 同上 | データオーナーは、品質・定義・分類・使用目的・ラベルなどを管理する | 同 p.219（PDF p.245） | 書籍本文で確認 | 修正した。ノート 08 は「分類の所有は一次資料なし」としていたが、書籍に記述がある |
| 同上 | ドメイン境界は信頼境界。PEP・PDP・PIP・PAP の 4 部品。PDP の訳語は「ポリシー定義点」 | 同 p.235〜236、p.241（PDF p.261〜262、p.267） | 書籍本文で確認 | 一致。「仕組みを基盤が持つ」は本ガイドの読み方で、ノートにそう書いた |
| 同上 | 04:09 UTC に配布、05:27 UTC に戻した。センサー 7.11 以降の Windows。Mac と Linux は影響なし。段階配布と顧客による制御 | https://www.crowdstrike.com/en-us/blog/falcon-content-update-preliminary-post-incident-report/ | 本文確認 | 一致 |
| 同上 | 型は入力 21 個、渡すのは 20 個。Content Validator は 21 個で検証。所見 6：段階的に配るべき。「設定データで、コードでもカーネルドライバーでもない」 | CrowdStrike RCA（2024-08-06）PDF | PDF を取得して本文確認 | 一致。影響した台数は RCA に無いので載せていない |
| 共通の型：先に配っておき、手元の情報で動く | 静的な安定性の定義。制御プレーンとデータプレーンの定義。データプレーンは制御プレーンが傷んでも今の状態を保つ。Mike Furr、2019-12-05 | https://builder.aws.com/content/3K9SiqiJ369TGkkGzqPM95BuYWI/static-stability-using-availability-zones | 本文確認 | 一致 |
| 同上 | 制御プレーンは複雑で依存が多い。データプレーンは意図して単純。広い障害はデータプレーンのほうが統計的に起きにくい | https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/control-planes-and-data-planes.html | 本文確認 | 一致。「復旧の経路を制御プレーンに依存させない」はこのページで確かめられず、載せていない |
| 同上 | フォールバックの代わり 4 つ。IAM ロールの認証情報は先に各インスタンスへ配られ、何時間も有効。Jacob Gabrielson、2019-12-05 | https://builder.aws.com/content/3EuS9Sakq7L3VLQIF3qzfMfke1Y/avoiding-fallback-in-distributed-systems | 本文確認 | 一致 |
| 同上 | Google 2020-12-14：既存のデータプレーンの構成は動き続け、変更の操作だけが影響を受けた | Google Cloud Incident #20013 | 本文確認 | 一致 |
| 同上 | 右端の列（この Part での例） | — | — | 本ガイドの当てはめ。表の見出しに明記 |
| 設計レビューで問うこと／まとめ | 新しい事実は無い（前のスライドの再掲） | — | — | — |

## ノートから使わなかったもの

- Azure AD 2021-03-15（暫定の転記だけが根拠）、Zanzibar の数値、Vault Agent のキャッシュ、PostgreSQL・BigQuery の行レベルの制御、NIST SP 800-207・800-204・800-92・800-57：原文を開いていないか、枚数に収まらないため載せていない
- Microsoft Entra の 2024-01・2025-02 の事後報告：Part 14 の担当
