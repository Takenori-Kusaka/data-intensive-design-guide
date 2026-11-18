# Part 9「正しさの水準を決める」事実の確かめ直し

確認日：2026-11-18。対象：`deck/p09.js`（扉 1 枚＋本文 14 枚）。

確かめ方の凡例：「本文確認」＝URL を取得して原文（HTML をテキスト化したもの、PDF は pdftotext）を自分で検索して読んだ。「本文確認（要約経由）」＝取得ツールの要約モデルに原文の引用を出させた。「書籍本文で確認」＝`research/books/text/0180-2.txt` の該当ページを検索して読んだ（印刷ページ＝PDF ページ − 18）。

## 1. スライドごとの事実

| スライドの題 | 事実 | 出典（URL か書籍ページ） | 確かめ方 | 結果 |
| --- | --- | --- | --- | --- |
| トランザクションは失敗と並行の後始末を肩代わりする | トランザクションは自然法則ではなく、プログラミングモデルを簡素化するための仕組み | DDIA 2e p.271–272 | 書籍本文で確認 | 一致 |
| 同上 | 再試行の落とし穴（応答が届かなかった成功の二重実行、DB の外の副作用） | DDIA 2e p.282–283 | 書籍本文で確認 | 一致 |
| ACID の 4 文字は製品で意味が違う | ACID の語は 1983 年（Härder・Reuter）。「ACID 準拠」では保証が分からない | DDIA 2e p.273 | 書籍本文で確認 | 一致（原論文は未確認。本書の記述として使った） |
| 同上 | 一貫性は不変条件のことでアプリケーション固有。CAP の一貫性は線形化可能性 | DDIA 2e p.274–275 | 書籍本文で確認 | 一致 |
| 同上 | 分離性は教科書ではシリアライザブル。多くの製品はそれより弱い | DDIA 2e p.276 | 書籍本文で確認 | 一致 |
| 同上 | Aurora DSQL は 1 トランザクションで変更 3,000 行まで | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-postgresql-compatibility-unsupported-features.html | 本文確認 | 一致（未検証と明記） |
| 同上 | DynamoDB は 1 回の API 呼び出しに最大 100 操作 | ノート 05 [27] | 確かめていない | 載せるのをやめた |
| 同上 | MySQL は `innodb_flush_log_at_trx_commit=0` で応答済みの書き込みを失う（Jepsen） | ノート 05 [9] | 該当箇所を確かめていない | 載せるのをやめた（永続性は Part 8 へ送った） |
| 読み取りの異常 | リードスキューの語、ノンリピータブルリードの一例、困る場面（バックアップ、分析・整合性の検査） | DDIA 2e p.288–289 | 書籍本文で確認 | 一致。図と数値（倉庫 A・B の在庫）は自作 |
| 同上 | リードコミッテッドはダーティリードを防ぐ | DDIA 2e p.284–285 | 対応表＋書籍の見出しで確認 | 一致 |
| 書き込みの異常 | 当直医の例（最低 1 人は当直）。本書の例であることをノートに明記し、スライドは配達員の例に置き換えた | DDIA 2e p.298 | 書籍本文で確認 | 一致 |
| 同上 | ライトスキューは、ロストアップデートの自動検出では防げない。防ぐには真のシリアライザブルか明示的なロック | DDIA 2e p.299 | 書籍本文で確認 | 一致 |
| 分離レベルは「どの異常を許すか」の約束 | SQL-92 草案 4.28 節：4 水準、既定は SERIALIZABLE、表 9 は P1〜P3 の 3 列 | http://www.contrib.andrew.cmu.edu/~shadow/sql/sql1992.txt | 本文確認 | 一致。現行の ISO/IEC 9075 の条文は未確認とスライドに明記。「既定は SERIALIZABLE」はノートから削り、スライドには載せていない |
| 同上 | Hermitage：PostgreSQL の read committed＝monotonic atomic view、repeatable read＝snapshot isolation、serializable＝serializable。G1・P4・G-single・G2-item の結果 | https://raw.githubusercontent.com/ept/hermitage/master/README.md | 本文確認 | 一致 |
| 同上 | Hermitage は証明ではない。防ぎ方と性能は示さない | 同上 | 本文確認 | 一致 |
| 同上 | Berenson ほか（1995）がロストアップデート・リードスキュー・ライトスキュー・スナップショット分離を定義に加えた | ノート 05 [3]（ノートの著者が原文で確認） | この回では原文を開いていない | ノートの記述のまま使用。表 4 は載せていない |
| 同じ名前の分離レベルが製品で別のものを指す | PostgreSQL 18：既定 Read Committed、Repeatable Read はスナップショット分離、Serializable は SSI | https://www.postgresql.org/docs/18/transaction-iso.html | 本文確認 | 一致 |
| 同上 | MySQL 8.4 InnoDB：既定 REPEATABLE READ。SERIALIZABLE は autocommit 無効時に SELECT を FOR SHARE に変える | https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html | 本文確認（要約経由。直接の取得は 403） | 一致 |
| 同上 | MySQL の repeatable read：Hermitage では monotonic atomic view、P4 を防がない | Hermitage README | 本文確認 | 一致 |
| 同上 | Oracle：既定 READ COMMITTED。水準は read committed・serializable・read-only。ORA-08177 | https://docs.oracle.com/en/database/oracle/oracle-database/26/cncpt/data-concurrency-and-consistency.html | 本文確認 | 一致。製品名は「Oracle AI Database」とだけ書き、「26ai」は載せていない |
| 同上 | Oracle の serializable：Hermitage では snapshot isolation、G2-item を防がない | Hermitage README、DDIA 2e p.276・p.293 | 本文確認／書籍本文で確認 | 一致 |
| 同上 | SQL Server：既定 READ COMMITTED。REPEATABLE READ は共有ロックを終了まで保持し、新しい行の挿入は防がない | https://raw.githubusercontent.com/MicrosoftDocs/sql-docs/live/docs/t-sql/statements/set-transaction-isolation-level-transact-sql.md （ms.date 2025-09-26） | 本文確認 | 一致 |
| 同上 | SQL Server の SERIALIZABLE はキー範囲ロック | ノート 05 [17] | 該当箇所を確かめていない | 載せるのをやめた（Hermitage の結果だけにした） |
| 同上 | SQL Server の SNAPSHOT の競合エラー番号（3960） | ノート 05（記憶・要確認） | 確かめていない | 載せるのをやめた |
| 同上 | CockroachDB：既定 SERIALIZABLE、文書は水準を 2 つと書く、40001 | https://www.cockroachlabs.com/docs/stable/transactions | 本文確認 | 一致。stable の版番号（v26.4）は確かめきれず、載せていない |
| 同上 | CockroachDB：Hermitage には repeatable read（snapshot isolation）の行がある | Hermitage README | 本文確認 | 一致。文書との食い違いは「未確認」とセルに書いた |
| 同上 | Spanner：既定 serializable（外部整合性）、repeatable read はスナップショット分離でライトスキューが起こりうる | https://docs.cloud.google.com/spanner/docs/isolation-levels | 本文確認 | 一致 |
| 同上 | Spanner の repeatable read の一般提供日（2026-04-17） | ノート 05 [24]（題名のみ） | 確かめていない | 載せるのをやめた |
| 同上 | Aurora DSQL：PostgreSQL の Repeatable Read に固定、スナップショット分離 | 上記 DSQL の 2 ページ | 本文確認 | 一致 |
| 同上 | YugabyteDB・DynamoDB・MongoDB の行 | ノート 05 | 確かめていない | 載せるのをやめた（指定の 7 製品だけ） |
| DB を入れ替えると、既定の正しさの水準が変わる | SQL Server：READ_COMMITTED_SNAPSHOT は SQL Server の既定が OFF、Azure SQL Database の既定が ON | 上記 SQL Server の文書 | 本文確認 | 一致 |
| 同上 | Aurora DSQL：ロックを取らず、競合はコミット時に SQLSTATE 40001（OC000）。再試行と冪等な設計を勧める。スナップショットは BEGIN の時点 | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-concurrency-control.html | 本文確認 | 一致 |
| 同上 | PostgreSQL の Repeatable Read は競合した更新を失敗させる（could not serialize access due to concurrent update） | PostgreSQL 18 文書 13.2.2 | 本文確認 | 一致 |
| 同上 | 既定がリードコミッテッドの製品（Oracle・PostgreSQL・SQL Server） | DDIA 2e p.286 | 書籍本文で確認 | 一致 |
| MySQL の既定はロストアップデートを防がない | Jepsen MySQL 8.0.34（2023-12-19）：健全な 1 台で、成功した 9,048 件中にロストアップデート 198 件 | https://jepsen.io/analyses/mysql-8.0.34 （3.3 節） | 本文確認 | 修正した。原文は「9,048 件の成功したトランザクションのうち、446 件が 198 件のロストアップデートに関与」。「9,048 件中 198 件が失われた」と読める書き方を避け、「1 回の試験で、9,048 件の中に 198 件」と書いた |
| 同上 | Jepsen：monotonic atomic view も満たさない | 同上 | 本文確認 | 一致（ノートを短くする際に削った。スライドには載せていない） |
| 同上 | Jepsen の勧め（Serializable、または Read Committed＋FOR UPDATE） | ノート 05 | 原文で該当の文を見つけられなかった | 載せるのをやめた |
| 同上 | ACIDRain 脚注 6：MySQL の Repeatable Read でロストアップデートが起きた | http://www.bailis.org/papers/acidrain-sigmod2017.pdf | 本文確認 | 一致 |
| 同上 | MySQL/InnoDB のリピータブルリードはロストアップデートを検出しない。PostgreSQL のリピータブルリードは検出する | DDIA 2e p.296 | 書籍本文で確認 | 一致 |
| 分離レベルより先に、トランザクションの範囲を問う | EC アプリ 12 本、脆弱性 22 件、うち 17 件はトランザクションの使い方の誤りで、最も強い保証のもとでも成立 | ACIDRain 1 節 | 本文確認 | 一致 |
| 同上 | 内訳：在庫 9・ギフト券 8・カート 5 | ACIDRain 4 節 | 本文確認 | 一致 |
| 同上 | Feral Concurrency Control（Rails 67 本） | ノート 05 [30] | 確かめていない | 載せるのをやめた |
| 同上 | Flexcoin（2014-03-02） | ACIDRain 1 節（引用どまり） | 取引所の発表は未確認 | 載せるのをやめた |
| ロストアップデートの防ぎ方は 5 つ | アトミックな更新が通常は最良。ORM は読んで書き戻す形を書かせやすい | DDIA 2e p.294 | 書籍本文で確認 | 一致 |
| 同上 | 明示的なロックは付け忘れやすい。デッドロックのリスク | DDIA 2e p.295 | 書籍本文で確認 | 一致 |
| 同上 | バージョン列による条件付き書き込み（楽観的ロック） | DDIA 2e p.296 | 書籍本文で確認 | 一致 |
| 同上 | Aurora DSQL の SELECT ... FOR UPDATE は、先にコミットした相手がいると OC000 で失敗する | 上記 DSQL の文書 | 本文確認 | 一致（発表者ノートを短くする際に削った。入れ替えのスライドの表に「競合はコミット時に 40001」とだけ残した） |
| 同上 | 制約は「ロストアップデートそのもの」を検出しない、という整理 | — | 一次資料なし | 本ガイドの整理として、表の中で限界を明記した |
| Serializable の実装は 3 つ | 3 つの実装（逐次実行、2 相ロック、SSI） | DDIA 2e p.303 | 書籍本文で確認 | 一致 |
| 同上 | 逐次実行：VoltDB・Redis、スループットは 1 コアに制限 | DDIA 2e p.304 | 書籍本文で確認 | 一致 |
| 同上 | 2PL：MySQL/InnoDB と SQL Server のシリアライザブル。高パーセンタイルの遅延 | DDIA 2e p.308–310 | 書籍本文で確認 | 一致 |
| 同上 | SSI：2008 年に発表。PostgreSQL、CockroachDB。読み書きトランザクションは短く | DDIA 2e p.312、p.317 | 書籍本文で確認 | 一致 |
| 同上 | 直列化の失敗は SQLSTATE 40001。判断のロジックも含めトランザクション全体を再試行。PostgreSQL は自動の再試行を提供しない | https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html （13.5） | 本文確認 | 修正した。ノート 05 は 40001 の出典を 13.2 としていたが、13.2 のページに 40001 の記載は無く、13.5 にある。根拠の行を 13.5 にした |
| 必要な箇所だけ強くし、受け入れる異常は理由を残す | PostgreSQL の文書：全書き込みと一貫した読み取りに Serializable を使えば、ほかの工夫は要らない。保護はホットスタンバイと論理レプリカに及ばない | https://www.postgresql.org/docs/18/applevel-consistency.html （13.4） | 本文確認 | 一致 |
| 同上 | 判断の手順と、宅配注文サービスへの当てはめ | — | 一次資料なし | 「本ガイドの考え」の注記を付けた |
| 設計レビューで問うこと | Jepsen が、利用者自身の負荷で不変条件を試験するよう勧めている | ノート 05 5 節 | MySQL 8.0.34 の報告では該当の文を確かめきれなかった | 載せるのをやめた |

## 2. 確かめ直しで直した点（ノートとの差）

1. SQLSTATE 40001 の出典：PostgreSQL 18 文書の 13.2 ではなく 13.5「Serialization Failure Handling」。
2. Jepsen の数字の書き方：「9,048 件中 198 件」は、成功したトランザクション 9,048 件の 1 回の試験の中で見つかったロストアップデートの件数（関与したトランザクションは 446 件）。
3. CockroachDB の文書の URL：`docs.cockroachlabs.com` ではなく `www.cockroachlabs.com/docs/stable/` で取得できた。版番号は載せていない。
4. PostgreSQL の文書の版：ページは 18 系。最新のマイナーは 18.7（2026-11-12 公開の告知をページで確認）。スライドには「PostgreSQL 18 文書」と書いた。

## 3. 載せなかったもの・未確認のまま残るもの

- SQL 標準の現行版（ISO/IEC 9075-2:2023）の条文。スライドは「SQL-92 草案」「現行版は未確認」と明記。
- Berenson ほか（1995）と Adya ほか（2000）の原文は、この回では開いていない（ノート 05 の著者が原文で読んだ記述に依る）。Adya の G0〜G2 の定義はスライドに載せていない。
- MySQL 8.4・9 系で Jepsen 8.0.34 と同じ結果になるか。スライドに「確認できていない」と明記し、題材 D で測ると書いた。
- CockroachDB の repeatable read（Hermitage に行があり、公式文書は 2 水準と書く）が現行の版でどう有効になるか。
- Hermitage が各製品を試した版（README に無い）。
- Spanner の repeatable read の提供段階、Oracle の文書の正確な版の表示（URL は /26/、ページに「Release 26」）。
- クラウド製品（Spanner・Aurora DSQL）と Oracle・SQL Server・CockroachDB の挙動は、公式文書と Hermitage の記述で、本ガイドでは未検証。
