# ファクトチェックの反映記録：deck/p03.js・p04.js・p05.js（S33〜S72）

- 作業日：2026-11-18
- 対象：`deck/p03.js`（S33〜S45）、`deck/p04.js`（S46〜S56）、`deck/p05.js`（S57〜S72）
- 拾った指摘：`A_standards.md`・`A_products.md`・`A_books.md` のうち S33〜S72 に当たるもの、`_quote_hits.txt` の S41・S49・S52・S61、`D_books.md` の #1・#15（S38・S39・S43・S45 への言及）。B・C の各ファイルに S33〜S72 への言及は無かった（スライド番号で grep）
- 結果：**全 31 行。直した 26、直さなかった 5**
- 確認：`node build_one.js p03／p04／p05` はエラーなし、refs 漏れ 0、ノート漏れ 0、LONG TITLE なし。`tools/quote_check.py` を 3 ファイルに 18 字でかけ、書籍の本文との 25 字以上の一致は 0（残るのは書名・製品名・用語の並びで、最長 24 字）
- 確かめ方：書籍は `research/books/text/<ISBN>.txt` の該当ページを自分で読んだ（PDF ページ = 印刷ページ + 18。『大規模データ管理 第2版』だけ + 26。ISBN 0006-5 の p.28〜32・130〜132・144〜146・149〜150・157〜159、0180-2 の p.63〜64・76〜77・98〜102・参考文献 [104]、0071-3 の p.40〜41・218〜220）。Web は WebFetch で開いた。Azure の 2 ページと AWS の 3 ページは本文をそのまま読めた。Mailchimp・Snowflake・pgvector・PostgreSQL・BigQuery は、小型モデルに原文の引用を抜き出させて読んだ（全文の通読ではない）

## Part 3 での『ハードパーツ』の DB 分解の手順の引き方（Part 15 の担当へ）

- S39 は、5 段階プロセス（6.2 節 p.149〜150、図 6-17）を図で示し、ノートで 4 段階目と 5 段階目を次のように引く：「スキーマを別のサーバーへ移す方法は 2 つ。バックアップしてリストアする方法は、通常、移すときに停止が要る。レプリケーションは停止が生じないが、設定と調整の作業が増える（6.2.4 節 p.157〜158）。接続先を切り替え、古いサーバーからスキーマを消す（6.2.5 節 p.159）」。根拠の行は「6.2 節 p.149〜150・6.2.4〜6.2.5 節 p.157〜159」
- S39 のノートは、これを「同じ製品の別のサーバーへ移す手順」と位置づけ、「別の製品へ、照合と切り戻しの窓を持って移す手順は Part 15」と送っている。D10 の文言と同じ切り分け
- S38 は 6.2.4 節 p.158 を「スキーマを分けても、単一のデータベースに依存する間は量子は 1 つ。スケーラビリティ・耐障害性・性能に悪い影響が出うる」という記述にだけ使う。節とページは本文で確かめた（6.2.4 節の見出しは p.157 の末尾、2 つの方法と量子の記述は p.158、6.2.5 節は p.159）

## 指摘ごとの対応

| 指摘の出どころ | スライド | 指摘の要点 | 自分で確かめた一次資料と結果 | 対応 | 直した後の文、または直さない理由 |
|---|---|---|---|---|---|
| A_standards #11 | S69 | HNSW 論文に年と掲載先が無い。「釣り合いがよい」は IVFFlat との比較 | DDIA 2e 参考文献 [104]：IEEE TPAMI 42 巻 4 号 pp.824–836、2020 年 4 月。pgvector README（master、v0.8.7）："It has better query performance than IVFFlat (in terms of speed-recall tradeoff)"。指摘どおり | 直した | 根拠の行「Malkov・Yashunin の HNSW 論文（arXiv:1603.09320、2016／IEEE TPAMI 2020）」。表「IVFFlat より、速さと再現率の釣り合いがよい。…」 |
| A_standards #12 | S50 | GQL の標準の番号が無い（指摘側は ISO の書誌を未確認） | ISO の書誌ページ（iso.org/standard/76120.html）：ISO/IEC 39075:2024、Edition 1、2024-04 発行。DDIA 2e p.89 の「2024 年に公開」と合う | 直した | ノートに「標準の番号は ISO/IEC 39075:2024 です」。根拠の行に「ISO/IEC 39075:2024（GQL。2024-04 発行。ISO の書誌を 2026-11 確認）」を足した。表のセルは行の高さの余裕が無いので変えていない |
| A_products #1（D15） | S67 | Snowflake「外部のクライアントは追記・削除できない」。同じ公式文書に、書き込めるとする記述もある | docs.snowflake.com の 2 ページを開いた。`tables-iceberg` に "Third-party clients can't append to, delete from, or upsert data to Iceberg tables that use Snowflake as the catalog." と、Horizon Catalog 経由の書き込みの留意点（CTAS 不可、equality delete 不可、タグとブランチ不可など）が並ぶ。専用ページは "You can read and write to Snowflake-managed Iceberg v2 and v3 tables from external engines"。どちらが現行かは文書から決められなかった | 直した（言い切りを外した） | 表「Snowflake：外部からの書き込みの可否は、文書内で記述が分かれ未確認」。ノートに、両方の記述があり確かめられなかったので未確認とした、と書いた |
| A_products #2、A_books #6（D13） | S66 | AWS PERF03-BP01 のページに「歴史的な参照用、廃止予定」の注記 | 旧ページ（performance-efficiency-pillar/perf_data_use_purpose_built_data_store.html）に注記があることを確認。現行の Framework の対応ページを見つけた：`wellarchitected/latest/framework/perf03.html`（Data management）と `framework/perf03-bp01.html`。注記なし。Common anti-patterns の 1 つ目は "Teams standardize on one database engine because they already know it and force every workload onto it."（旧ページの文言から変わっている） | 直した（現行ページに差し替え） | 根拠の行「Azure「Understand data models」／AWS Well-Architected Framework PERF03-BP01（2026-11 確認）」。注記「AWS：用途に合うデータストアを選ぶ。使い慣れているという理由で 1 つのエンジンに統一しない」。ノートも現行の文言に合わせた。S26・S31 の「DR objectives」は担当外 |
| A_products #3 | S62 | Mailchimp「監視の追加は未着手だった」は原文に無い | mailchimp.com/what-we-learned-from-the-recent-mandrill-outage/："In November of 2018, engineers on our Mandrill team identified the potential to reach wraparound"、"Our team determined wraparound was not an immediate threat, but we added a ticket to the backlog to set up additional monitoring."。チケットのその後は書かれていない。指摘どおり | 直した | 「2018-11 に兆候を把握し、差し迫っていないと判断して、監視の追加はバックログのチケットにしていた」。ノートに「そのチケットがどうなったかは報告に書かれていません」 |
| A_products #4 | S62 | 「autovacuum が遅れ」は、原文では推定 | 同上："The autovacuum process on shard4 likely fell behind due to the higher load, though it may have failed outright—we are unable to determine for certain which occurred."。指摘どおり | 直した | 「負荷が偏ったシャードで autovacuum が遅れたとみられ（失敗の可能性もあると報告は書く）、XID が上限に達して安全停止」。ノートにも、どちらかは特定できないと報告が書いている、と足した |
| A_products #6、A_books #3（D13） | S37・S51・S54・S65・S66・S70 | Azure の文書の日付が、記事の日付と更新日で混ざっている | CQRS と Understand data models の front matter を開き、`ms.date` と `updated_at` が別の値であることを確認。D13 に従い日付を書かない | 直した | S37 ノート「…どちらも 2026 年 11 月に確認しました」。S51「Azure Architecture Center「Event Sourcing」「CQRS」（2026-11 確認）」。S54「「Event Sourcing」（イベントの版。2026-11 確認）」。S65「「Materialized View pattern」（2026-11 確認）」。S70「「Understand data models」（2026-11 確認）」。S66 は上の行のとおり |
| A_products #7 | S55・S56 | 「入るのも出るのも高くつく」は Event Sourcing のページだけの記述。CQRS のページには無い | Azure「CQRS」の本文を全部読んだ。移行の費用の記述は無い。あるのは "it can introduce significant complexity into the application design, specifically when combined with the Event Sourcing pattern" と、向かない場面 2 つ。指摘どおり | 直した | S55 表「イベントソーシングは入るのも出るのも高くつく。CQRS も複雑さを増す」。S55 ノート「Azure の指針は、イベントソーシングについて、入るのも出るのも高くつくとしています。CQRS については、とくにイベントソーシングと組むと設計がかなり複雑になりうる、としています」。S56 ノートに、この記述はイベントソーシングについてのもの、と足した |
| A_products #8 | S69・S70 | 次元の上限は型を替えれば上がる（halfvec は 4,000 次元） | pgvector README：vector 2,000、halfvec 4,000、bit 64,000 次元まで索引できる。指摘どおり | 直した | S69 表「索引できるのは、vector 型で 2,000 次元まで（halfvec 型は 4,000 次元まで）」。S70 ノートに同じ内容を 1 文 |
| A_products #9 | S62 | 300 万未満でも、読み取り専用のトランザクションと VACUUM は続けられる | PostgreSQL 18 文書 24.1.5："any transactions already in progress can continue, but only read-only transactions can be started … The VACUUM command can still be run normally."。指摘どおり | 直した | 表「…300 万未満で新しい XID の割り当てを拒否（読み取りと VACUUM は可）」。ノートに、進行中のトランザクションは続けられ、読み取り専用は始められ、VACUUM も実行できる、と足した |
| A_products #10 | S62 | 領域を返す例外の条件が 1 つ落ちている | 同 24.1.2："except in the special case where one or more pages at the end of a table become entirely free and an exclusive table lock can be easily obtained"。指摘どおり | 直した | 表「…（末尾のページが空き、排他ロックをすぐ取れる場合を除く）」。ノートも同じ条件にした |
| A_products #11 | S62 | HOT の条件に「BRIN を除く」を足せる | 開いていない（指摘自身が「そのままでよい」） | 直さない | 行の幅に余裕が無く、設計の判断には響かない。指摘も実害は小さいとしている |
| A_products #12 | S67 | BigQuery 側の制限も書かないと、片方だけ制限があるように読める | docs.cloud.google.com/bigquery/docs/iceberg-tables（題は Apache Iceberg managed tables）："store data in storage buckets that you own"、"Modifying data files for Iceberg managed tables outside of BigQuery can cause query failure or data loss."。指摘どおり | 直した | 表「BigQuery：利用者のバケットに Parquet で置く。外からファイルを変えると失敗やデータ損失が起きうる」。ノートにも足した。行が 1 行分伸びるので、下の注記を y 5.8・h 0.7 に下げた |
| A_products #14 | S62 | Mailchimp の発生日（年は公開日からの読み取り）。そのままでよい | 原文："The outage began at 05:35 UTC on February 4, and we resolved the issue on February 5 at 22:09 UTC." | 直さない | 指摘が「そのままでよい」。日付は原文と合う |
| A_books #1（D14） | S51 | CQRS の訳語は「コマンドクエリ責務分離」 | DDIA 2e p.99：「コマンドクエリ責務分…（中略）」。指摘どおり | 直した | ノート「CQRS、コマンドクエリ責務分離です」。3 ファイルに「責任分離」は残っていない |
| A_books #2 | S51・S54 | 順序の保証は、DDIA では欠点の列ではなく「唯一の重要な要件」。ページは p.101 末から p.102 に続く | DDIA 2e p.101：欠点の箇条書きは 3 つ（外部の情報と決定性、不変性と個人データの削除、再処理の副作用）。その後の段落に「唯一の重要な要件は、…ログに現れる順序とま…（中略）」。位置づけの指摘は正しい。**ページの指摘は違っていた**：この段落は p.101 の中で終わり、p.102 は 3.4 節から始まる | 直した（ページは p.98〜101 のまま） | S51 カードの題「払うもの・要るもの（DDIA 2e p.101、Azure）」、3 行目「要件：全ビューが、ログと同じ順序で処理する保証」。S51 ノート「欠点として同書が挙げるのは 3 つです。…これとは別に、全ビューがログと同じ順序でイベントを処理する保証を、ただ 1 つの重要な要件として挙げています」。S54 ノート「DDIA 第 2 版はこれを欠点ではなく、重要な要件として書いています」 |
| A_books #5（D12）、_quote_hits S41 | S41 ノート | 書籍の文と 29 字が一致 | 『大規模データ管理 第2版』p.219 の本文と見比べた | 直した | 「アプリケーションオーナーが受け持つのは、アプリケーションの中核とそのインタフェース、それにアクセス制御です」 |
| A_books #5（D12）、_quote_hits S49 | S49 ノート | 25 字が一致 | DDIA 2e p.71 と見比べた | 直した | 「同書は、非正規化したデータは導出データの一種と見ると理解しやすい、とも書いています」 |
| A_books #5（D12）、_quote_hits S52 | S52 ノート | 36 字が一致 | DDIA 2e p.76 と見比べた | 直した | 「同書は、アナリストが扱いやすいのはスタースキーマのほうで、こちらが選ばれることが多い、と述べています」 |
| _quote_hits S61（D12） | S61 表 | 製品名の並び 25 字が一致 | DDIA 2e p.117：「RocksDB[7]、Cassandra、ScyllaDB、HBase[8]」 | 直した | 並びを「RocksDB、HBase、ScyllaDB、Cassandra」に替えた（製品名そのものは変えられないので、順序だけ） |
| A_books #7 | S38 題 | 『ハードパーツ』が共有を一律に否定しているように読める | 同書 p.130：「サービスベースアーキ…（中略）」。p.30：基準を満たさないのは「データベースのデプロ…（中略）」場合。p.158：悪影響を「及ぼす可能性がある」。指摘どおり | 直した | 題「共有 DB では、変更の調整と停止の影響が全サービスに及ぶ」。リード「1 つの DB に依存するサービス群は、壊す変更で全体の調整が要り、DB が止まれば一緒に止まる」。注記「…性能や耐障害性に響きうる。同書は共有を禁じてはいない。サービスベースの構成では共有してよいとする（p.130）」。ノートに同じ断りを足し、「共有は選択肢で、このスライドはその費用を示しています」と結んだ。根拠の行に p.130 を入れた |
| A_books #8 | S38 | 量子の定義を、デプロイの面だけに短くしている | 同書 p.28：「高度な機能的凝集、…（中略）が可能なアーティファクト」。指摘どおり | 直した | ノート「同書の定義には機能的な凝集と結合の条件も入っていますが、ここではデプロイの面だけを使います」。本文はそのまま |
| A_books #9 | S66 | Azure の文書の片側だけを引いている | Azure「Understand data models」冒頭："A single data store rarely satisfies all access patterns efficiently. Most production systems adopt polyglot persistence"。後半："Avoid premature fragmentation: Use one service when it still meets performance, scale, and governance objectives."。指摘どおり | 直した | 注記「Azure：多くの本番システムは複数のモデルを使うとしたうえで、早すぎる細分化を避け、1 つのサービスが性能・規模・統制の目標を満たすうちは 1 つを使う」。ノートも同じ順に書き直した |
| A_books #12 | S47 | 「重要な違いだと述べています」は原文より強い。根拠に p.77 が無い | DDIA 2e p.64：「それぞれ異なる用途に適しています」まで。一対多の木ならドキュメント、多対一・多対多はリレーショナル、は 3.1.5 節 p.77。指摘どおり | 直した | ノート「DDIA 第 2 版の 3 章は、モデルごとに得意な関係の形が違うことを示しています」。根拠の行に「3.1.5 節 p.77」を足した |
| A_books #13 | S7、Part 5 全体 | 「索引」「列指向」「転置索引」は DDIA 2e の訳語ではない | DDIA 2e は「インデックス」「カラム指向」。指摘どおり | 直さない | 指摘の直し先は S7 のノート（Part 0 の担当）。Part 5 の語は本ガイドの言い換えのままにした。S7 に断りが入らない場合は、S58 のノートに 1 文足す必要がある |
| A_books #14 | S41 | 共有されるシステムの所有は、先に挙がる方法が落ちている。節の開始は p.40 | 『大規模データ管理 第2版』p.40〜41：1 つ目はデータドメインごとに別のデータプロダクトを作る方法、もう 1 つは単一のデータプロダクトの中に所有を示す列を持たせる方法。2.3.2.4 節の見出しは p.40。指摘どおり | 直した | 注記「共有されるシステムでは、ドメインごとにデータプロダクトを分ける方法と、1 つの中に所有を示す列を持たせる方法がある（同書 p.40〜41）」。根拠の行も p.40〜41 |
| A_books #15 | S41 ノート | 本書はデータメッシュとは違う立場だと断っている | 同 p.219：「（データメッシュ理論…（中略）」。指摘どおり | 直した | ノート「本書は、データメッシュの理論では 1 つの役割にまとめる、と断ったうえで、まとめない理由を挙げます。ここでは 2 つを取り上げます」 |
| A_books #16 | S39 根拠の行 | 6.1.2 節の開始は p.144 | 『ハードパーツ』p.144 に 6.1.2 節の見出しと導入。指摘どおり | 直した | 「6.1.2 節 p.144〜146」。S19 は担当外 |
| A_books #17 | S39 表 | 「データベーストランザクション」は見出しの表記（箇条書きは「データトランザクション」） | p.145 の箇条書きは「データトランザクション」、p.146 の 6.1.2.2 の見出しは「データベーストランザクション」 | 直さない | 見出しの表記に合わせており誤りではない。指摘も「そのままでよい」 |
| D_books #1（D10） | S38・S39 | Part 15 が「手順は無い」と書く一方、Part 3 が同じ手順を引いている | 『ハードパーツ』p.157〜159 を読んだ（上の「Part 3 での引き方」） | 直した | S39 のノートに 2 つの方法と停止の有無、切り替えを書き、「同じ製品の別のサーバーへ移す手順」と位置づけた。根拠の行に「6.2.4〜6.2.5 節 p.157〜159」を足した |
| D_books #15 | S43・S45 | DDIA 13 章を Part 3 でも引いているが、S255 の対応表の行に Part 3 が無い | S43・S45 の根拠の行に 13.2.1.4 節 p.546〜547 があることを確認 | 直さない | 直す先は S255（Part 17 の担当）。Part 3 側に直す箇所は無い |

## 確かめて、指摘のほうが違っていた件

- A_books #2 のページ：順序の保証の段落は p.101 の中で終わる。p.102 には続かない。根拠の行は「p.98〜101」「p.100〜101」のままにした
- A_products #2 の「後継の文言は未確認」：現行のページは `wellarchitected/latest/framework/perf03-bp01.html` にあった（注記の案内先 `framework/welcome.html` は 404 のまま）。文言は旧ページから変わっているので、スライドの言い方を現行に合わせた

## 不確かな点・取りまとめ役への申し送り

- S67 の Snowflake：公式文書に両方の記述があることまでしか確かめていない。実機では試していない
- S38 の題を変えた。`deck/qa/slidemap.txt`、`research/deck_text_A.md`、ほかの Part がこの題を文字で引いていれば、合わせる必要がある（`deck/*.js` に旧題の引用は無かった）
- 見た目は確かめていない（PowerPoint を起動していない）。文字が増えた箱：S38 の注記、S41 の注記（1 行に収まるか境目）、S51 のカードの題、S62 の表の 2 行と事後報告の注記、S66 の注記、S67 の表の最後の行（4 行になる見込みで、下の注記を 0.1 下げた）、S69 の表。再書き出しのときに見てほしい
- S62 のノートは、但し書きを足したので 450 字を超えている
- Azure「Event Sourcing」「Materialized View pattern」「Data considerations」は、日付を外しただけで本文は開き直していない（ファクトチェック 2 本が内容の一致を確認済み）
