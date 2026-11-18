# Part 7「動かしたまま変える契約」事実の確かめ直し

確認日：2026-11-18。Web の一次資料は、ページの本文を取得して該当の文を検索・目視した（要約ツールは使っていない）。書籍は `research/books/text/<ISBN>.txt` の該当ページを読んだ。枚数：16（扉 1＋本文 15）。

## 確かめた事実

| スライドの題 | 事実 | 出典（URL か書籍ページ） | 確かめ方 | 結果 |
| --- | --- | --- | --- | --- |
| 逐次更新の間は、新旧の版が同時に動く | 逐次更新（rolling upgrade）は数ノードずつ配る。新旧のコードとデータが共存する | DDIA 2e p.155〜156 | 書籍本文で確認 | 一致 |
| 同上 | 「データはコードより長生きする」。5 年前の値が元の形式で残る | DDIA 2e 5.2.1.1 節 p.172 | 書籍本文で確認 | 一致（引用 14 字。Part 内の引用はこの 1 か所） |
| 同上 | 「Part 2 で用語を出した」という発表者ノートの一文 | — | ほかの Part の原稿が無く確かめられない | 載せるのをやめた |
| 後方互換と前方互換：向きが更新の順序を決める | 後方＝新しいコードが古いデータを読める、前方＝その逆 | DDIA 2e p.156 | 書籍本文で確認 | 一致 |
| 同上 | BACKWARD は消費者を先、FORWARD は生産者を先、FULL は独立に更新できる | https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html （Confluent Platform 8.4） | 本文確認 | 一致 |
| 同上 | サーバーが先・クライアントが後と仮定でき、リクエストに後方互換、レスポンスに前方互換だけが要る。組織をまたぐと更新を強制できない | DDIA 2e 5.2.2.4 節 p.179〜180 | 書籍本文で確認 | 一致 |
| 同上 | 古いコードが未知のフィールドを落とすと値が消える | DDIA 2e p.156〜157（図 5-1） | 書籍本文で確認 | 一致 |
| 形式ごとに、新旧を対応づける規則が違う | Avro：フィールドは名前で対応。読み手に無いフィールドは無視、書き手に無いフィールドは読み手の既定値、無ければエラー | https://avro.apache.org/docs/1.12.0/specification/ （Schema Resolution） | 本文確認 | 一致 |
| 同上 | Avro の版 | 文書サイトの仕様は 1.12.0 が最新（1.12.1・1.12.2 の仕様ページは 404）。GitHub のリリースとダウンロードページは 1.12.2（2026-08-23） | 本文確認、GitHub API | 修正した（ノート 03 は「1.12.0 が最新か未確認」。スライドは「Avro 仕様 1.12.0」と書き、1.12.2 のリリースは載せていない） |
| 同上 | Protobuf：番号で対応。変更を Wire-unsafe／Wire-safe／Wire-compatible に分ける。未知のフィールドを保持する | https://protobuf.dev/programming-guides/proto3/ （Updating A Message Type、Unknown Fields） | 本文確認 | 一致 |
| 同上 | Protobuf：書き手に無いフィールドは型の既定値（空文字列、0）で埋まる。名前は変えられるが番号は変えられない | DDIA 2e 5.1.3.1 節 p.164〜165 | 書籍本文で確認 | 一致 |
| 同上 | JSON Schema Draft 2020-12 の本文に、版の間の互換の規則が無い | https://json-schema.org/draft/2020-12/json-schema-core | 本文確認（「compatib」7 件はどれも別の文脈） | 一致 |
| 同上 | Confluent の文書も「JSON Schema does not explicitly define compatibility rules」と書く | Confluent Platform 8.4 文書（上と同じページ） | 本文確認 | 一致 |
| 同上 | additionalProperties を省略すると空のスキーマと同じ（未知のプロパティを通す） | JSON Schema Core §10.3.2.3、DDIA 2e p.160 | 本文確認、書籍本文で確認 | 一致 |
| 同上 | JSON Schema の「書き手が書いていないフィールド」は required で決まる | Validation の仕様は開いていない | — | 載せるのをやめた（セルは「スキーマの書き方しだい」にした） |
| 同上 | 同時に使うスキーマ形式の数は最小限に | DDIA 2e 5.1.5 節 p.171 | 書籍本文で確認 | 一致 |
| 両方向に安全な変更は、既定値つきの追加と削除 | Avro：既定値なしの追加は後方互換を、既定値なしの削除は前方互換を壊す。改名は別名で後方互換だが前方互換でない | DDIA 2e 5.1.4.2 節 p.168〜169 | 書籍本文で確認 | 一致 |
| 同上 | Avro の別名の利用は実装の任意（may optionally）。昇格は int→long/float/double など | Avro 仕様 1.12.0（Aliases、Schema Resolution） | 本文確認 | 一致 |
| 同上 | Avro・Protobuf とも、既定値つきフィールドの追加・削除は完全に互換 | Confluent Platform 8.4 文書 | 本文確認 | 一致 |
| 同上 | Protobuf：追加・削除は Wire-safe。削除した番号は「must reserve」。再利用は解析エラー、PII の漏えい、破損につながる | protobuf.dev proto3（Deleting Fields、Consequences of Reusing Field Numbers） | 本文確認 | 一致 |
| 同上 | Protobuf：型の変更は値が切り捨てられることがある | protobuf.dev（Wire-compatible）、DDIA 2e p.165 | 本文確認、書籍本文で確認 | 一致 |
| 同上 | Protobuf：JSON（ProtoJSON）では安全な変更の範囲が違う | protobuf.dev proto3（Updating A Message Type の Note） | 本文確認 | 修正した（下書きの「JSON にすると安全でない」は原典より強い。「規則が変わる」にした） |
| 同上 | 「名前と型の変更はどの形式でも片方向にしか安全でない」 | — | Protobuf のバイナリでは改名は両方向に安全 | 修正した（リードを「形式と向きで変わる」にした） |
| 互換性モードは、向きと比べる範囲の 2 軸で選ぶ | 7 つのモード。非 TRANSITIVE は最新の版とだけ、TRANSITIVE は登録済みのすべての版と比べる | Confluent Platform 8.4 文書、https://docs.redpanda.com/current/manage/schema-reg/schema-reg-api/ （26.2） | 本文確認 | 一致 |
| 同上 | ブローカーと並べてスキーマレジストリを置き、互換性を検査するのが一般的 | DDIA 2e 5.2.4.1 節 p.184、5.1.4.3 節 p.169 | 書籍本文で確認 | 一致 |
| 既定は直前の版とだけ比べ、古いデータは守らない | Confluent の既定は BACKWARD（非推移）。Protobuf には BACKWARD_TRANSITIVE を勧める。全版を読むなら BACKWARD_TRANSITIVE | Confluent Platform 8.4 文書 | 本文確認 | 一致 |
| 同上 | Redpanda の既定は BACKWARD。文書の版は 26.2（タグ v26.2.7） | Redpanda 26.2 文書 Schema Registry API | 本文確認 | 一致 |
| 同上 | Apicurio：全体の規則が無ければ何も適用しない。AsyncAPI・GraphQL は互換性の規則が None | https://www.apicur.io/registry/docs/apicurio-registry/3.3.x/getting-started/assembly-intro-to-registry-rules.html 、同 assembly-rule-reference.html | 本文確認 | 修正した（ノート 03 は 3.0.x／3.2.x。文書の最新の系列は 3.3.x で、同じ記述を 3.3.x で確かめて版を直した） |
| 同上 | v1→v2→v3 の例（既定値つきで足し、次に既定値を外す） | Avro の規則からの帰結。事例としての出典は無い | — | 発表者ノートに例として書き、結果は題材 B で測ると明記 |
| 契約の強制は、書き手側と CI に置く | ブローカーは通常データモデルを強制しない | DDIA 2e p.184 | 書籍本文で確認 | 一致 |
| 同上 | スキーマのデータベースがあれば、デプロイ前に互換性を検査できる | DDIA 2e 5.1.5 節 p.171 | 書籍本文で確認 | 一致 |
| 同上 | Redpanda のサーバー側スキーマ ID 検証は企業版のライセンスが要る。ID が登録済みかだけを見て、ペイロードは検査しない | https://docs.redpanda.com/current/manage/schema-reg/schema-id-validation/ 、https://docs.redpanda.com/current/get-started/licensing/overview/ | 本文確認 | 一致 |
| 同上 | Confluent 互換のシリアライザは既定で自動登録。共有・本番では事前登録と auto.register.schemas=false を勧める | Redpanda 26.2 文書 Schema Registry API | 本文確認 | 一致 |
| 同上（ノート） | Confluent のスキーマ規則は Enterprise と Confluent Cloud に限る | https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html | 本文確認 | 一致 |
| API とイベントの仕様は、互換の規則までは決めない | OpenAPI 3.2.1（2026-09-10）。Schema Object は JSON Schema Draft 2020-12 の上位集合。info.version は記述文書の版 | https://spec.openapis.org/oas/latest.html | 本文確認 | 一致 |
| 同上 | AsyncAPI の最新は 3.1.0（リリース 2026-01-31）。「does not assume any kind of software topology, architecture or pattern」 | https://www.asyncapi.com/docs/reference/specification/latest 、GitHub API | 本文確認 | 一致 |
| 同上 | OpenAPI・AsyncAPI は API の版の間の互換規則を定めない | 両仕様の本文を「compatib」「breaking」で検索。仕様自体の版の互換の記述だけだった | 本文確認（無いことの確認） | 一致 |
| 同上 | CloudEvents 1.0.2（2022-02-06）。必須は id・source・specversion・type。data の型は制限しない | https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md 、GitHub API | 本文確認 | 一致 |
| 同上 | 版づけは生産者に任せる。非互換の変更では type を変え、新旧の両方をしばらく出す（非規範） | CloudEvents Primer（main、1.0.3-wip）「Versioning of CloudEvents」 | 本文確認 | 一致 |
| 同上 | 厳格なコントラクトは名前・型・順序まで一致を求め、もろさの原因になる。コンシューマー駆動コントラクトは受け手が必要な項目をまとめ、出し手がビルド時に検証する | 『ハードパーツ』13.1 節 p.367、13.1.2.2 節 p.374 | 書籍本文で確認 | 一致 |
| データ契約は、スキーマに品質と条件を足した合意 | 提供者と消費者が、どのデータを何の目的で使うかを正式に合意すること。技術面と業務面。互換性・SLA・品質・版。テストのひな形として破壊的な変更を見つける | 『大規模データ管理 第2版』8.1.5 節 p.229〜231 | 書籍本文で確認 | 一致 |
| 同上 | 「A schema is only one element of a data contract」 | Confluent Platform 文書 Data Contracts | 本文確認 | 一致 |
| 同上 | ODCS v3.2.0（2026-09-08）。YAML。Bitol は LF AI & Data の Graduated | https://github.com/bitol-io/open-data-contract-standard （README、GitHub API）、https://bitol.io/ | 本文確認 | 一致 |
| 同上 | Radar：ODCS は Adopt（2026-11-04 公開）。Data Contract CLI は Trial（2025-11。現行の号には非掲載） | https://www.thoughtworks.com/en-us/radar/languages-and-frameworks/open-data-contract-standard-odcs 、…/radar/tools/data-contract-cli | 本文確認 | 一致 |
| 同上 | 標準化団体による規範的な定義は見つからなかった | ノート 03 の調査結果 | 再調査はしていない | スライドに「本調査では見つからなかった」と限定して書いた |
| 同上 | 「データ契約」の語の出どころ（Andrew Jones、PayPal） | 二次情報のみ | — | 載せるのをやめた |
| expand/contract：非互換の変更を 3 段階に分ける | expand→migrate→contract。contract をやり残すと始める前より悪い状態になりうる。2014-05-13、Danilo Sato | https://martinfowler.com/bliki/ParallelChange.html | 本文確認 | 一致 |
| PostgreSQL の DDL は、ロックと書き換えを調べる | 明記がなければ ACCESS EXCLUSIVE。非 volatile の DEFAULT は書き換えなし、volatile な DEFAULT と型変更は表と索引を書き換え。NOT VALID は外部キー・CHECK・NOT NULL。VALIDATE は SHARE UPDATE EXCLUSIVE | https://www.postgresql.org/docs/18/sql-altertable.html | 本文確認 | 一致 |
| 同上 | 通常の索引作成は書き込みを止め読み取りは可。CONCURRENTLY は失敗すると INVALID の索引が残る | https://www.postgresql.org/docs/18/sql-createindex.html | 本文確認 | 一致 |
| 同上 | lock_timeout の既定は 0（無効）。節は 19.11 | https://www.postgresql.org/docs/18/runtime-config-client.html | 本文確認 | 一致 |
| 同上 | ACCESS EXCLUSIVE だけが SELECT を止める。ロックは解放まで無期限に待つ | https://www.postgresql.org/docs/18/explicit-locking.html （13.3） | 本文確認 | 一致 |
| 同上 | 待っている ACCESS EXCLUSIVE が後続の読み書きを待たせる（ロックの行列） | 公式文書に明記が見つからない | — | 載せるのをやめた（「題材 B で実測する」とだけ書いた） |
| 同上 | SET NOT NULL、ADD PRIMARY KEY USING INDEX、virtual の生成列の行 | ノート 03 の表 | 枚数の都合 | 載せるのをやめた |
| 設定やルールもデータで、契約と段階配布が要る | CrowdStrike：型の定義は 21 入力、センサーのコードは 20。範囲外の読み取り。対策に入力数の検査、境界検査、段階配布（所見 1・2・6） | CrowdStrike RCA（2024-08-06）PDF をテキスト化 | 本文確認 | 一致。発生時刻（04:09 UTC）と台数は RCA で確かめられず載せていない |
| 同上 | Google Cloud：2025-05-29 に機能を追加。エラー処理もフラグも無い。2025-06-12 に空欄を含むポリシーが数秒で全世界に複製。コードは地域ごとに配ったが問題の経路は実行されなかった | https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW | 本文確認 | 一致（ノート 03 で「記憶・要確認」だった最後の点を原文で確認）。影響時間は表記が分かれるので載せていない |
| 同上 | Cloudflare：ファイルが倍になり、上限 200 個を超えた。5 分ごとに生成され全体へ。対策の 1 番目は自社生成の設定の取り込みを利用者入力と同じに堅くする | https://blog.cloudflare.com/18-november-2025-outage/ | 本文確認 | 一致。時刻（11:20、14:30、17:06 UTC）は一致を確かめたが、Part 14 の担当なので載せていない |
| 未知の入力の扱いは、寛容さに頼らず仕様に書く | RFC 9413 は IAB、Informational、2023-06。「no longer considered best practice in all scenarios」（§2）、§2.2、§3、§4.1、§5.1 の要旨 | https://www.rfc-editor.org/rfc/rfc9413.txt | 本文確認 | 一致。3 枚のカードへの当てはめは「本ガイドの考え」と明示した |

## ノートにあって載せなかったもの

- Pact、Knight Capital（SEC の命令）、Cloudflare 2025-12-05、GitHub 2021-11-27、Stripe 2019-07-10、pgroll・gh-ost：枚数の都合。Part 14・15 の担当と重なる
- Confluent の JSON Schema の内容モデルごとの判定表：ページ後半を読み切っていない
- Redpanda の 30 日の試用ライセンス：本文で確認したが、設計の判断に関わらないので省いた

## 不確かな点

- Confluent と Apicurio のふるまいは文書の比較だけで、未検証（スライドに明記）。Redpanda は題材 B で測る
- 「OpenAPI・AsyncAPI・JSON Schema は互換の規則を定めない」「データ契約の規範的な定義が無い」は、無いことの確認で、検索した範囲に限る
- v1→v2→v3 が段ごとに通り全体では壊れる例は、規則からの帰結。題材 B で実測するまで結果として書かない
- PowerPoint での見た目（はみ出し・重なり）は未確認。表のセルは 2〜3 行に収まる字数にしてある
