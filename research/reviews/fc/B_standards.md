# ファクトチェック：範囲 B（S73〜S137）× 観点「標準と論文」

調査日 2026-11-18。対象は `research/deck_text_B.md`。原典は自分で取得して本文を読んだ（要約ツールは検索の入口にだけ使用）。取得した原典：Hermitage README（raw）、SQL-92 草案（X3H2-92-154/DBL CBR-002、1992-07）、Berenson ほか 1995（MSR-TR-95-51 の PDF）、ACIDRain（SIGMOD 2017 の PDF）、Jepsen「MySQL 8.0.34」、RFC 9413（txt）、Avro 仕様 1.12.0、protobuf.dev proto3 ガイド、JSON Schema 2020-12（Core・Validation）、OpenAPI 3.2.1（GitHub の 3.2.1.md）、AsyncAPI 3.1.0（asyncapi.md）、CloudEvents 1.0.2（spec.md・primer.md）、ODCS のリリース一覧と README、LF AI & Data の Bitol ページ、Thoughtworks Radar の 2 つの blip、Confluent「Schema Evolution」（current）、CockroachDB 文書（stable）、ParallelChange、Zalando の技術記事 2 本。

件数：**誤り 0／不正確 5／補足 9**。

## 指摘（重要な順）

| # | スライド | 問題の記述（短く） | 何が違うか・根拠（自分で開いて確かめたか） | 直した文の案 | 重大度 |
|---|---|---|---|---|---|
| 1 | S128（本文「標準の定義の限界」、NOTE） | 「標準の表を満たしても、ロストアップデートとライトスキューを防ぐとは限らない。Berenson ほかがこの欠けを指摘した」「ロストアップデートは標準の表からは読めない」 | 条件が 2 つ落ちている。(a) SQL-92 草案 4.28 節は、表 9 の直前の本文で「The four isolation levels guarantee that ... no updates will be lost」と書いている。つまり標準は**本文では**ロストアップデートを 4 水準すべてで防ぐと述べ、表（P1〜P3）にはその列が無い。(b) Berenson ほか 1995 の主張は水準ごとに違う。P4 は「possible at the READ COMMITTED isolation level」だが「forbidding P2 also precludes P4」（3 章末〜4.1 節）。A5A・A5B も「P2 が排除されていれば起きない」。一方、厳密な解釈（A1〜A3 の禁止）ではスナップショット分離が「ANOMALY SERIALIZABLE」を満たしてしまい、A5B（ライトスキュー）を許す（Remark 9・10）。草案と論文 PDF を開いて確認。なお表 9 の注記は、SERIALIZABLE で 3 現象が起きないのは「直列化可能であることの帰結」としており、SERIALIZABLE は 3 現象の排除で定義されているわけではない | 「草案の本文は『更新は失われない』と書くが、表 9 にあるのは 3 つの現象だけ。Berenson ほか（1995）は、現象の定義が曖昧で、READ COMMITTED ではロストアップデート（P4）が起こりうること、現象を狭く読むとスナップショット分離が SERIALIZABLE の表を満たしたままライトスキュー（A5B）を許すことを示した」 | 不正確 |
| 2 | S131（本文・NOTE）、関連 S136 | 「1 回の試験で、成功した 9,048 件の中にロストアップデートが 198 件」 | 単位が混ざっている。Jepsen 3.3 節の原文は「Out of 9,048 successful transactions in this test, our new checker found 446 distinct transactions involved in 198 instances of lost update. Only 47 of those instances appeared in some cycle.」。9,048 はトランザクション数、198 は異常の**事例数**で、関わったトランザクションは 446 件。「9,048 件中 198 件」と読むと約 2% に見えるが、関与したトランザクションは約 5%。リスト追記（list-append）の負荷での 1 回の結果である点も落ちている。原文を開いて確認（日付 2023-12-19、対象 8.0.34、3.3 節は一致） | 「1 回の試験（リスト追記の負荷）で、成功した 9,048 トランザクションのうち 446 件が、198 件のロストアップデートに関わっていた」 | 不正確 |
| 3 | S129（MySQL の行）、S131（「Hermitage：実際の水準は monotonic atomic view」「3 つの報告が一致」） | MySQL の Repeatable Read の「実際の水準」を monotonic atomic view とだけ書く | Hermitage README の表は確かに「monotonic atomic view」（PMP と G-single は R/O、P4 は —）。しかし同じスライドで引く Jepsen の報告は 3.5 節「Non-Monotonic View」と要旨で、MySQL の Repeatable Read は **Monotonic Atomic View も破る**（健全な 1 台でも）と報告し、3.4 節では内部整合性の異常（9,048 件中 126 件）も示す。3 つの報告が一致するのは「ロストアップデートを防がない」点だけで、「実際の水準」は一致していない。`verify_p09.md` 46 行目は「ノートを短くする際に削った」と記すが、削った結果、Hermitage の水準名が確定した事実のように読める。両方の原文を開いて確認 | S131 の Hermitage の枠か条件の枠に 1 行足す：「Jepsen（2023-12）は、書き込みを含む場合は monotonic atomic view も満たさないと報告している。Hermitage の水準名は手作業の試験の範囲での分類」。「3 つの報告が一致」は「ロストアップデートについては 3 つの報告が一致」に | 不正確 |
| 4 | S126（最下行・NOTE 末尾） | 「リードスキューを防ぐにはスナップショット分離以上が要る」 | スライドが出典に挙げる Berenson ほか 1995 では、A5A（Read Skew）は「P2 が排除されている履歴では起きない」ので、ロックによる REPEATABLE READ でも防がれる（Table 4：REPEATABLE READ の A5A は Not Possible）。しかも同論文 Remark 9 は REPEATABLE READ とスナップショット分離を**比較不能**としており、「以上」という一列の順序は原典に無い。論文 PDF を開いて確認。（Hermitage では SQL Server の repeatable read の G-single は「some」で、実装によって差がある） | 「リードスキューは、スナップショット分離か、読んだ行のロックを最後まで持つ Repeatable Read で防がれる。リードコミッテッドでは防がれない」 | 不正確 |
| 5 | S86（サブタイトル・「本ガイドの考え」・NOTE） | 「分散モノリスに権威ある定義は見つからなかった」 | 再検索した。標準・規格・クラウド各社の指針には定義が見当たらない（この点は一致）。ただし書籍には明示の定義がある。Sam Newman『Monolith to Microservices』（O'Reilly、2019）1 章「The Distributed Monolith」：「A distributed monolith is a system that consists of multiple services, but for whatever reason the entire system has to be deployed together.」。これは S86 の兆候 3（同時に出さないと壊れる）と同じ内容。確認方法：出版社経由で配布されている PDF の抜粋を検索結果で確認（書籍の現物とページ番号は未確認）。「権威ある」の意味しだいだが、広く引かれる著者の定義を無いことにするのは言い過ぎ | 「標準や公的な指針による定義は見つからなかった。書籍では Newman（2019）が『複数のサービスからなるが、全体を一緒にデプロイしなければならないシステム』と定義している。本ガイドは、指針にある兆候を 4 つに整理する」 | 不正確 |
| 6 | S85（「見つかったもの」・NOTE） | Zalando の記事を「更新の少ない DB でスロットが進まず、WAL が溜まる問題」「障害の規模は書かれていません」とだけ紹介 | 「大手事業者の事後報告は見つからなかった」は再検索しても覆らなかった（下の「再検索の記録」）。ただし Zalando の記事は帰結まで書いている。2025-12-19 の記事：「causing WAL to pile up until disk space ran out」。その前段の 2023-11-09 の記事（Patching the PostgreSQL JDBC Driver）：WAL が「consume all of the available disk space on the database node resulting in demotion of the node to read-only」。事後報告ではなく、日時・影響範囲も無いが、「ディスクが尽き、ノードが読み取り専用に降格した」ことは自己申告されている。両記事を開いて確認。ほかに利用者・個人の報告はある（Qlik Community 2024-01-18 の投稿「FULL database outage」、個人ブログ複数。いずれも事業者の事後報告ではない） | 「Zalando の技術記事（2023-11-09、2025-12-19）：更新の少ない DB でスロットが進まず、WAL がディスクを使い切ってノードが読み取り専用に降格する問題と、その修正。日時や影響範囲は書かれていない」。見つからなかったものの 2 行目は「…とする**事業者の**事後報告」と限定を付ける | 補足 |
| 7 | S93（名前の変更・Avro） | 「別名で後方互換にはなる」 | Avro 仕様 1.12.0 の Aliases 節は「An implementation **may optionally** use aliases to map a writer's schema to the reader's」。別名の解決は実装の任意の機能で、仕様が保証するものではない。仕様を開いて確認 | 「別名に対応した実装なら後方互換になる（別名の利用は仕様上は任意）。前方互換にはならない」 | 補足 |
| 8 | S92（Protobuf「未知のフィールドとして保持する」）、S102 | 保持を無条件に書いている | protobuf.dev の「Unknown Fields」は保持と明記するが、直後の「Retaining Unknown Fields」で、JSON への直列化と、フィールドを 1 つずつ写す処理では未知のフィールドが失われると書く。S91 の「読んで書き戻すと値が消える」の話と直結する。開いて確認 | 表のセルに「（バイナリの場合。JSON に直すと失われる）」を足す | 補足 |
| 9 | S102（位置づけの枠） | 「実装を更新できる環境が前提（§3）」 | §3 の 1 文目は「The guidance in this document is intended for protocols that are deployed to the Internet」。対象はインターネットに配備されるプロトコルで、社内のデータ契約への当てはめは類推になる（スライドは「本ガイドの解釈」と明記済み）。ほかの引用（§2「no longer considered best practice in all scenarios」、§2.2「not a good strategy for extensibility」、§4.1 の定着、§5.1 の致命的エラー、IAB・Informational・2023-06・標準化過程の文書ではない）はすべて原文と一致 | 「IAB の Informational 文書で、標準ではない。対象はインターネットのプロトコルで、実装を更新できることが前提（§3）」 | 補足 |
| 10 | S126（NOTE「リードスキューはノンリピータブルリードの一例」） | 出典に Berenson（A5A）を挙げつつ、包含の向きが論文と逆 | Berenson ほか 4.2 節は「Fuzzy Reads (P2) is a degenerate form of Read Skew where x=y」。つまり論文ではノンリピータブルリード（ファジーリード）のほうがリードスキューの特殊な場合。「一例」は DDIA の言い方と思われる（書籍の担当の確認事項） | 「DDIA は、リードスキューをノンリピータブルリードの一例として扱う」と主語を付ける | 補足 |
| 11 | S128（「現行版の条文は未確認」） | 現行版について材料が無いまま | 二次資料だが、Jepsen「MySQL 8.0.34」1.1 節が「The same ambiguous, incomplete definitions are still present in the 2023 revision of the standard」と書いている。ISO/IEC 9075 の条文そのものは有償で、今回も未確認 | NOTE に「Jepsen（2023-12）は、同じ定義が 2023 年版にも残ると書いている（二次資料）」を足せる | 補足 |
| 12 | S98（調査の限界） | 「標準化団体による規範的な定義は見つからなかった」 | 再検索しても、採択済みの規範的な定義は見つからなかった（主張は維持できる）。策定中の動きはある：W3C ODRL Workshop（2026-07）の JPMorgan Chase の意見書が「dprod-contracts specification (EKGF/OMG track, v0.7)」に `DataContract` クラスがあると記す。v0.7 の草案段階で、OMG の採択仕様ではない（意見書の該当箇所だけ確認。仕様本体は未確認）。ODCS v3.2.0（2026-09-08）、Bitol が LF AI & Data の Graduated（LF のページは 2026-06、Radar は 2026-07 と記載）、Radar Vol.35（2026-11）で ODCS が Adopt、Data Contract CLI は 2025-11 の Trial で現行号に非掲載、はすべて一致 | 「…見つからなかった。OMG／EKGF で策定中の草案はある（2026-11 時点で未採択）」 | 補足 |
| 13 | S92・S93（「Avro 仕様 1.12.0」） | 版 | Apache Avro のリリースは 1.12.2 まで出ている（GitHub のタグで確認）。1.12.0 の文書の Schema Resolution・Aliases の内容はスライドと一致。1.12.1・1.12.2 の仕様との差分は未確認 | 「Avro 仕様 1.12.0（最新のリリースは 1.12.2。差分は未確認）」 | 補足 |
| 14 | S129（CockroachDB の行） | 「文書は水準を 2 つと書くが、Hermitage には行がある（食い違い。未確認）」 | 両方とも確認した。CockroachDB 文書（stable、Transactions）：「offers two transaction isolation levels: SERIALIZABLE and READ COMMITTED」。Hermitage README：CockroachDB に "repeatable read"＝snapshot isolation の行がある。食い違いは事実。理由は今回も特定できず（試験した版が README に無い）。スライドの書き方のままでよい | 変更不要。「（2026-11 時点でも食い違いを確認）」と足せる | 補足 |

## 再検索の記録（「無い」「見つからなかった」の主張）

- **S85 事後報告**：検索語は「postmortem / incident report × replication slot × WAL × disk full」「inactive replication slot × outage × status page」「dual write × postmortem × root cause」「CDC / Debezium lag × customer-facing × post-incident review」（Tavily 3 回、WebSearch 2 回）。大手事業者が原因と明記した事後報告は見つからず。見つかったのは、技術記事（Zalando、Gunnar Morling、AWS のブログとナレッジ）、製品の解説、個人・利用者の報告。主張は維持できる（指摘 6 の限定を付ける）。網羅的な検索ではない
- **S86 分散モノリス**：標準・指針の定義は見つからず。書籍の定義が 1 つ（指摘 5）。「Martin Fowler の定義」とする記事があったが、出典が示されておらず確認できなかった
- **S98 データ契約**：ISO・IEEE・W3C・OMG・DAMA で検索。採択済みの規範的な定義は見つからず（指摘 12）
- **S92 JSON Schema に互換規則が無い**：Draft 2020-12 の Core と Validation を全文検索（compatib・evol）。版の間のスキーマ互換を定める記述は無い（一致）

## 確かめて一致した主な事実

1. SQL-92 草案の分離レベルは 4.28 節「SQL-transactions」、表は Table 9「SQL-transaction isolation levels and the three phenomena」。4 水準 × P1〜P3 のセルは S128 の表と全部一致（草案の txt）
2. Berenson ほか 1995：P4（Lost Update）、A5A（Read Skew）、A5B（Write Skew）、Snapshot Isolation の名前と定義。SIGMOD 95、MSR-TR-95-51。「Snapshot Isolation does not permit P4 or A5A」「allow A5B」（PDF）
3. Hermitage の PostgreSQL 3 行：read committed＝monotonic atomic view（P4・G-single・G2-item は —）、repeatable read＝snapshot isolation（P4・G-single は ✓、G2-item は —）、serializable＝全部 ✓。3 水準とも G1a・G1b・G1c は ✓。S128 の 9 セルを 1 つずつ照合して一致
4. Hermitage の S129 のセル：MySQL repeatable read＝monotonic atomic view・P4 は —／Oracle serializable＝snapshot isolation・G2-item は —／SQL Server serializable＝serializable（snapshot は別の行）／CockroachDB serializable＝serializable。README に試験した版の記載は無い。「試験の集まりで証明ではない」「防ぎ方と性能は示さない」は Caveats と一致
5. Jepsen「MySQL 8.0.34」：2023-12-19、3.3 節が Lost Update at Repeatable Read、ほぼすべての結果が健全な 1 台で発生（2 節）
6. ACIDRain：Warszawski・Bailis、SIGMOD'17。自前運用の EC アプリ 12 本、脆弱性 22 件、在庫 9・ギフト券 8・カート 5、範囲の誤り（scope-based）17 件と水準（level-based）5 件、17 件は最も強い分離でも成立（1 節・4.2 節）。脚注 6 が MySQL の Repeatable Read でのロストアップデート
7. RFC 9413：IAB、Informational、2023-06、「not an Internet Standards Track specification」。§2・§2.2・§3・§4.1・§5.1 の節番号と内容
8. Avro 1.12.0 Schema Resolution：フィールドは名前で対応、書き手だけにあるフィールドは無視、読み手だけにあるフィールドは既定値、無ければエラー。昇格は int→long・float・double など
9. protobuf.dev proto3：変更を Wire-unsafe／Wire-safe／Wire-compatible（Conditionally Safe）に分ける。追加と削除は安全、消した番号は reserve が必須（must）、再利用の帰結に解析エラー・PII の漏えい・データ破損、int32↔int64 は切り捨てがありうる
10. Confluent「Schema Evolution」：「JSON Schema does not explicitly define compatibility rules」、既定は BACKWARD で非推移、Protobuf には BACKWARD_TRANSITIVE を勧める、全版を読むなら BACKWARD_TRANSITIVE（current のページ。8.4 かどうかは未確認）
11. OpenAPI 3.2.1：GitHub のリリース 2026-09-10。Schema Object は JSON Schema Draft 2020-12 の上位集合。info.version は OpenAPI 文書の版で、API の版とは別
12. AsyncAPI 3.1.0（リリース 2026-01-31）：「does not assume any kind of software topology, architecture or pattern」。互換の規則の記述は無い
13. CloudEvents 1.0.2：必須は id・source・specversion・type。Primer（non-normative）：版づけは出す側が決める、互換の変更は type を保つ、非互換なら type を変え新旧をしばらく両方出す
14. ODCS v3.2.0 は 2026-09-08 リリース。Bitol は LF AI & Data の Graduate 段階
15. ParallelChange：Danilo Sato、2014-05-13、expand・migrate・contract、縮めないと始める前より悪くなりうる
16. Zalando の記事の日付 2025-12-19

## 確かめなかった範囲

- 指示にあった **Adya の論文、Jepsen の PostgreSQL 12.3 と RDS for PostgreSQL 17.4、Dynamo 論文、DynamoDB 2022 年論文、Kreps「The Log」は、S73〜S137 の本文・根拠・ノートに出てこない**（全文検索で確認）。照合の対象が無いので未確認。S79（ログ）と S114（リーダーレス）は書籍だけを出典にしている
- ISO/IEC 9075 の現行版の条文（有償）
- Hermitage の個別の試験ファイル（README の表だけ照合）。Jepsen の付属データ
- Newman の書籍の現物とページ番号、OMG/EKGF の dprod-contracts 仕様の本体
- Avro 1.12.1・1.12.2 の仕様との差分、Confluent のページの版（8.4 か）。同ページには JSON Schema の `compatibilityPolicy`（LENIENT・STRICT）と LOGICAL という設定の記述があった。S94 の「7 つのモード」との関係は製品の担当の確認事項
- 製品の既定値・設定名、事後報告の数字、書籍のページと訳語（別の観点の担当）。Meta の 2022-06-08 の記事、Thoughtworks 以外の指針
