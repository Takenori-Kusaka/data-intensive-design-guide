# ファクトチェックの反映：deck/p06.js・p07.js（S73〜S104）

反映日 2026-11-18。編集したのは `deck/p06.js`、`deck/p07.js` とこの記録だけ（`p11.js` は読んだだけ）。`node build_one.js p06`／`p07` はどちらもエラーなし、content slides 15、without refs 0、without notes 0。PowerPoint は起動していない（配置は AUTHORING.md 3 節の数値で計算しただけで、PNG では見ていない）。

- 反映 29 件（指摘 27 件＋決定だけに基づくもの 2 件：D8、D13）
- 直さなかった 2 件（B_books #17、D_books #8。どちらも「変更不要」の補足）
- 指摘のほうが一部違っていた 1 点（B_books #4・#20。下の表）

自分で開いた一次資料：『大規模データ管理 第2版』p.188・196〜201、DDIA 2e p.159・169〜170・184・199・496・504（`research/books/text/`）。Web は 2026-11-18 に `curl` で取得して本文を検索：Google Cloud 事後報告（ow5i3PPK96RduMcb1SsW）、Cloudflare 2025-11-18 の事後報告、AWS Prescriptive Guidance の Shared-database-per-service と Transactional outbox、Azure Data considerations for microservices、.NET Microservices（communication-in-microservice-architecture）、Avro 仕様 1.12.0、protobuf.dev proto3、RFC 9413、Debezium 3.7 PostgreSQL コネクタ、PostgreSQL 18 ALTER TABLE、Confluent Data Contracts、Zalando 2023-11-09。Zalando 2025-12-19、Avro のタグ一覧、W3C ワークショップの意見書は、ファクトチェック担当が取得した本文ファイルを読んだ。

## 指摘ごとの対応

| 指摘の出どころ | スライド | 指摘の要点 | 自分で確かめた一次資料と結果 | 対応 | 直した後の文、または直さない理由 |
|---|---|---|---|---|---|
| B_books #1／D9 | S75（副題・表・注記・ノート） | 同書 p.199 の 2 点は、データ流通の中で運び方を選ぶ考慮点。コピーか直接かの軸ではない | 『大規模データ管理 第2版』p.199「データ流通パターンを…（中略）」。速さが要る場合は「リアルタイムに近いパターン」（API・イベント）。アプリケーション統合の条件は p.200「スピードと強一貫性が必要不可欠な場合」。指摘どおり | 直した | 副題「コピーか直接かは、許せる遅れと照合の要否で決める（本ガイドの考え）」。表の見出し「コピーの運び方を選ぶときの考慮点（同書 p.199）」、1 行目「…数分〜数秒以内なら、API かイベントの運び方を検討する」。注記（本ガイドの考え）「同書の 2 点は、コピーの運び方を選ぶときの考慮点。『その遅れを許せないなら、正を直接呼ぶ』と、コピーか直接かの判断に使うのは本ガイドの考え。同期の API で呼んでも…」。ノートも同じ切り分けに書き直し、「持ち主に負荷をかけずに」は同書の該当箇所に無いので外した。配置：カード h 2.1→1.85、表 y 4.2→3.95、注記 y 5.36・h 1.12 |
| B_books #1／D9 | S88（カード・ノート） | 同上 | 同上 | 直した | カード「コピーか正かは、許せる遅れと照合の要否で決める（本ガイドの考え）」。ノート「…で決める、というのが本ガイドの考えです」 |
| B_books #4 | S75 ノート | 「『強一貫性』を定義なしで使う」は言い過ぎ。p.188 に説明がある | p.188（6.4.1 節）にストリーミングの一貫性レベルとしての説明あり（指摘どおり）。**ただし指摘の案「7 章で説明なしで使う」も正確でない**：7 章 p.197 に「強一貫性の（正確な）データ」と言い添えがある | 直した（案を修正して採用） | 「同書は 7 章で『強一貫性』を、『正確な』と言い添えるだけで使います。6.4.1 節（p.188）の説明は、ストリーミングの順序と伝搬の話で、読み出しが最新であることの定義ではありません」 |
| B_books #20 | S75 カード | 「速さと正確さ」は同書の語「スピードと強一貫性」より広い | p.200 は「スピードと強一貫性」。**指摘の「言い換えで広く読める」は一部違う**：同書自身が p.197 で強一貫性に「（正確な）」と言い添えている。ただしノートと語を揃えるほうが食い違わない | 直した | 「向く：速さと『強一貫性』（同書の語）が欠かせない場合」 |
| B_books #8 | S75 根拠の行 | 節とページ | 7.1.1 は p.196、7.1.2 は p.197、7.1.3 は p.198、7.1.4 は p.200〜201。指摘どおり | 直した | 「『大規模データ管理 第2版』7.1.2〜7.1.4 節 p.197〜201（運び方の考慮点 2 つは p.199）」 |
| B_books #12 | S74 ノート | 「規範ガイダンス」は資料の名前 | AWS の 2 ページを開いた。拘束力の記述は無い。案内ページは開いていない | 直した | ノートに「『規範ガイダンス』は AWS の資料の名前で、一事業者の推奨です。標準や規制という意味の規範ではありません」 |
| D13 | S74・S86 根拠の行 | Azure の文書は日付を書かず確認月だけ | AWS の 2 ページに「歴史的な参照用、廃止予定」の注記は無い（本文検索で 0 件）。差し替え不要 | 直した | S74「AWS 規範ガイダンス Shared-database-per-service／Azure Data considerations（2026-11 確認）」。S86 も同じ形。.NET Microservices（Microsoft Learn）の「2020-01-30」も同じ理由（ms.date）で外した |
| B_books #17 | S76 | 表 10-1〜10-4 の要約。現状のままでよい | 開いていない（変更なしの補足） | 直さない | 指摘自体が「現状のままでよい」 |
| D_books #8 | S77・S78 | Part 16 の S226 と節の表記が食い違う | p.496 に 12.2 節、二重書き込みは 12.2.1 節（p.497〜） | 直さない | Part 6 は既に「12.2.1 節」。直すのは S226 の側 |
| B_books #13 | S78 根拠の行 | 図 12-4 と同じ型。置き換えを断る | 値と題材は自前の例。書籍の図そのものは見ていない（本文テキストだけ） | 直した | 「DDIA 2e 12.2.1 節 p.498（図 12-4 の考え方を、宅配注文の例に置き換え）」。S126 は担当外 |
| B_books #14 | S80 ノート | 引用の直後の文も原文に近い | p.504「両方の書き込みを同じ…（中略）…単一のトランザクションにまとめる」。指摘どおり | 直した | 「…と認めています。それでも二重書き込みの問題を避けられるのは、書き込み先がどちらも同じ DB で、1 つのトランザクションで済むからです」 |
| B_books #11 | S81 表・ノート | ポーリングの順序。AWS は順序を保つ設計と書く | AWS Transactional outbox："preserves the order of messages and events by using timestamps and sequence numbers"、別に Issues に "Order of notification"。指摘どおり。microservices.io は開いていない | 直した | 表「AWS は、時刻と連番で順序を保つ設計だと書く。microservices.io は難しいとする（食い違う）」。ノートも同じ |
| B_products #8 | S82 表・ノート | publication.autocreate.mode は pgoutput のときだけ効く | Debezium 3.7："This setting applies only when the connector streams changes by using the pgoutput plug-in"。指摘どおり | 直した | 「pgoutput のときだけ効く。publication が無ければ全テーブルを対象に作る。絞るなら filtered」 |
| D8 | S83（カード・参照の注記・ノート）、S87 表 | 冪等の説明を Part 11 に揃え、参照する短い形に | `p11.js` の定義「1 回実行しても、何回実行しても、効果が同じになること」 | 直した | カードの題「冪等：1 回実行しても、何回実行しても、効果が同じになること」。注記「冪等の説明、冪等な受け手の作り方、『厳密に 1 回』が成り立つ範囲は Part 11」。ノートは同じ定義＋「受け手で言えば、同じイベントが 2 回届いても、効果は 1 回分です」。S87「受け手は冪等か。同じイベントが 2 回届いても、効果は 1 回分か」 |
| B_books #19 | S84 ノート・根拠の行 | DDIA p.199 に、この読みを支える記述がある | p.199「ログを保持する（リー…（中略）…」。指摘どおり | 直した | ノートに 1 文を足し、根拠の行に「／6.1.3.1 節 p.199（ログの保持）」 |
| B_standards #6 | S85（副題・カード・注意・ノート・根拠の行） | Zalando の記事は帰結まで書く。「事業者の」と限定を付ける | 2023-11-09："At times … WAL would consume all of the available disk space on the database node resulting in demotion of the node to read-only"。2025-12-19："causing WAL to pile up until disk space ran out"。指摘どおり。再検索はしていない | 直した | 副題「…大手事業者の事後報告は見つからなかった」（「無かった」を改めた）。見つからなかったもの 3 行に「事業者の」。見つかったもの「Zalando の技術記事（2023-11-09、2025-12-19）：…WAL がディスクを使い切る問題と修正」。注意「…技術記事には、WAL がディスクを使い切り、ノードが読み取り専用に降格することがあった、という自己申告がある（Zalando 2023-11-09。日時と影響範囲の記載は無い）」。配置：カード h 2.65→2.5、注意 y 4.6・h 1.0 |
| B_standards #5／D15 | S86（副題・注記・ノート） | 「権威ある定義は見つからなかった」は言い過ぎ | Newman の書籍は開いていない（決定 D15 の文言に従う） | 直した | 副題「標準や公的な指針に定義は見当たらない。指針にある兆候を、本ガイドが 4 つに整理した」。注記「標準や公的な指針に定義は見当たらない。書籍に定義の例がある（Newman『Monolith to Microservices』。本ガイドは現物を確かめていない）。上の 4 つは…」（ラベルは「本ガイドの整理」）。定義の中身は、現物を確かめていないので載せていない |
| B_books #5 | S86 表 3 行目・ノート | 「独立したデプロイ」は AWS ではなく Azure。AWS は条件つきの選択肢として載せる | AWS：「All your database changes must also be backward-compatible」「development time coupling」「runtime coupling」「long-running … transactions can lock」「You should consider using this pattern if」。deploy の語は無い。Azure："preserves the agility of independent deployments"。指摘どおり | 直した | 表「AWS（後方互換が条件）、Azure（独立したデプロイ）」。ノートに AWS と Azure の記述を分けて書き、「AWS は共有 DB を、既存のコードを大きく作り替えたくない場合などの選択肢として載せていて、禁じてはいません」 |
| B_books #9 | S88 根拠の行 | 12.2 節の見出しは p.496 | p.496 で確認。指摘どおり | 直した | 「DDIA 2e 5.2 節・12.2.1〜12.2.2 節（p.497〜504）／『大規模データ管理 第2版』p.197〜201」 |
| B_books #7 | S92 根拠の行 | 5.1.2 節は p.159 から、5.1.4 節は p.170 まで | p.159 に 5.1.2、p.169 に 5.1.4.4、p.170 に 5.1.5 の見出し。指摘どおり | 直した | 「DDIA 2e 5.1.2〜5.1.4 節 p.159〜170」 |
| B_standards #8 | S92 表・ノート、S102 カード・ノート | Protobuf の未知のフィールドは、JSON にすると失われる | protobuf.dev「Retaining Unknown Fields」："Serialize a proto to JSON" と "Iterate over all of the fields … to populate a new message" で失われる。指摘どおり | 直した | S92「未知のフィールドとして保持する（バイナリの場合。JSON に直すと失われる）」。S102「Avro は無視、Protobuf は保持（バイナリ）」。ノートにも 1 文 |
| B_standards #13 | S92 ノート | Avro のリリースは 1.12.2 まで | GitHub のタグ一覧に release-1.12.2。仕様の差分は未確認 | 直した | ノート「リリースは 1.12.2 まで出ていますが、仕様の差分は確かめていません」。根拠の行は確かめた版 1.12.0 のまま |
| B_standards #7 | S93 表・ノート | Avro の別名は実装の任意 | Avro 1.12.0："An implementation may optionally use aliases"。指摘どおり | 直した | 「別名に対応した実装なら後方互換（仕様上は任意）。前方互換にはならない」 |
| D12（_quote_hits S96） | S96 ノート | DDIA p.184 と 26 字が一致 | p.184「メッセージブローカー…（中略）」 | 直した | 「ブローカーはふつう、流れるデータの形を決めて守らせることはしません。ブローカーから見れば、メッセージの中身はバイト列です」。スライドの注意「ブローカーは通常、データモデルを強制しない」は一致が 15 字未満なのでそのまま |
| B_products #10 | S96 ノート | Confluent Cloud 側は条件つき | Confluent Data Contracts："only available on Confluent Enterprise and Confluent Cloud with the Stream Governance Advanced package"。指摘どおり | 直した | 「Enterprise と、Stream Governance の Advanced パッケージを付けた Confluent Cloud に限る」 |
| B_standards #12 | S98 注記・ノート | 策定中の草案がある | W3C ワークショップの意見書に "The dprod-contracts specification (EKGF/OMG track, v0.7)"。仕様の本体、採択の状態は未確認 | 直した（確かめた範囲だけ） | 注記「策定中とされる仕様はある（EKGF／OMG 系統の dprod-contracts v0.7。本体は未確認）」。「未採択」とは書いていない |
| B_books #16 | S99 根拠の行 | 個人サイトの印、DDIA は考え方 | 記事は開いていない（表記の補足） | 直した | 「Danilo Sato『ParallelChange』martinfowler.com（個人サイトの記事、2014-05-13）」「DDIA 2e 5.2.1 節 p.172〜173（考え方）」 |
| B_products #7 | S100 表・ノート | 外部キーは SHARE ROW EXCLUSIVE。書き換えの無い列の追加も ACCESS EXCLUSIVE | PostgreSQL 18 ALTER TABLE："ADD FOREIGN KEY requires only a SHARE ROW EXCLUSIVE lock … also … on the referenced table"。指摘どおり | 直した | 表「…更新は待たされる。外部キーのロックは SHARE ROW EXCLUSIVE」「そのまま実行できる（ロックは ACCESS EXCLUSIVE）」。「短く取る」は文書に無いので書いていない |
| B_products #2／D2 | S101 表・ノート | 「空欄を含むポリシー」「割り当てポリシー」 | Google の報告："This policy data contained unintended blank fields."。指摘どおり | 直した | 表「Google Cloud 2025-06-12（ポリシーのデータ）」「意図しない空のフィールド（blank fields）を含むポリシーのデータ」。ノートも同じ |
| B_products #3／D2 | S101 表・ノート | 「適切な」が落ちている | "did not have appropriate error handling nor was it feature flag protected"。指摘どおり | 直した | 表「読むコードに適切なエラー処理が無く、フラグの保護も無かった」。ノート「適切なエラー処理が無く、フィーチャーフラグでも保護されていませんでした」 |
| B_products #4／D3 | S101（副題・表・注記・ノート）、S103 表、S89 扉のノート | 「両方が原因」は本ガイドのまとめ。Cloudflare は段階配布を対策に挙げていない | Cloudflare の対策の列挙は 4 つ（設定ファイルの取り込みの強化、global kill switches、core dump、failure modes の見直し）で、段階配布は無い。Google は "data replication needs to be propagated incrementally"。CrowdStrike の RCA は開いていない（ファクトチェック担当の確認に依る） | 直した | 副題「3 件とも、書き手と読み手の想定がずれたデータが、短時間で全体に届いた（本ガイドの整理）」。表の列を「全体への届き方」「事業者が挙げた対策と、段階配布の有無」にし、各行に「段階配布：挙げた／挙げていない」。注記「3 件を同じ型にまとめるのは本ガイドの整理：…段階配布を対策に挙げたのは CrowdStrike と Google で、Cloudflare は挙げていない…」。S103「事故 3 件に共通するのは、全体への速い配布と読み手の検査の不足（本ガイドの整理）」。扉のノート「設定やルールのデータが引き金になった事故 3 件」 |
| B_standards #9 | S102 注記・ノート | §3 の対象はインターネットのプロトコル | RFC 9413 §3："intended for protocols that are deployed to the Internet"、"depends on an ability to update and deploy implementations"。指摘どおり | 直した | 「IAB の Informational 文書で、標準ではない。対象はインターネットに配備されるプロトコルで、実装を更新できることが前提（§3）」。ノートに「社内のデータ契約への当てはめは類推です」 |

## 残る不確かな点

- Newman『Monolith to Microservices』は現物を見ていない（スライドにもそう書いた）
- dprod-contracts は意見書での言及だけを確かめた。仕様の本体と採択の状態は未確認
- CrowdStrike の RCA（所見 6）、microservices.io、Meta 2022-06-08、ParallelChange は、今回は開き直していない
- D13 を .NET Microservices（Microsoft Learn）にも当てはめたのは担当の判断
- S75・S86・S101 のノートは 450 字を超えた（590〜640 字）
- S75・S85・S101 は箱の位置と高さを変えた。計算では収まるが、PNG での確認が要る
