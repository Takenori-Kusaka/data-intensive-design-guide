# 05 トランザクションと分離レベル、サービスをまたぐ整合性（どの水準の正しさを、どこに求めるか）

調査日：2026-11-18

確認の深さの書き方：出典の表（11 節）の「確認の深さ」は、指示どおり「本文確認」「題名のみ」「未確認」の 3 段階。本文確認のうち、ページを要約ツール（WebFetch の要約モデル）経由で読んだものは「本文確認（要約経由）」、PDF や生のテキストを自分で読んだものは「本文確認（原文）」と書き分けた。要約経由の数値・版・日付は、スライドに載せる前に原文で見直すこと（9 節）。

## 1. 問い（このノートが答えること。対応する Part）

対応する Part：9（ステップ 7「どの水準の正しさを、どこに求めるか」）、11（ステップ 7 続き「サービスをまたぐ整合性をどう保つか」）。

1. 「ACID」「分離レベル」という言葉は、標準・論文・製品で同じ意味か。違うなら、何で比べればよいか（Part 9）
2. 製品の既定の分離レベルは何で、名前と中身はどこで食い違うか（Part 9）
3. 実務で起きる異常（更新の消失、書き込みスキュー、ファントム、読み取りスキュー）を、どの手段で、いくら払って防ぐか（Part 9）
4. 弱い分離レベルは、実際のアプリケーションで害になった証拠があるか（Part 9）
5. 1 つの DB を出たとき（サービスをまたぐとき）、原子性と分離性は何に置き換わるか。2 相コミット・XA、サーガ、耐久実行、冪等性の位置づけ（Part 11）
6. 「厳密に 1 回」は何を保証し、何を保証しないか（Part 11）

## 2. 標準・定義（節番号）

### 2.1 ACID の各文字と、製品によって意味が違うこと

| 文字 | 意味（DDIA 2e 8.1.1 の整理 [48]） | 製品で違う点 |
| --- | --- | --- |
| A 原子性 | 途中で失敗したら書き込みを全部捨てられること。並行性の話ではない。本書は「アボート可能性」と言い換える（p.274） | DynamoDB は 1 回の API 呼び出しに入る最大 100 個の操作だけが対象 [27]。Aurora DSQL は 1 トランザクション 3,000 行まで [26] |
| C 一貫性 | 不変条件を守ること。DB 単体の性質ではなく、アプリケーションの使い方に依存する（p.274–275）。CAP の「一貫性」（線形化可能性）とは別物 | Azure の Saga のページは「有効な状態から有効な状態へ」と書く [33]。意味は同じだが、誰が守るかは書いていない |
| I 分離性 | 並行するトランザクションが互いに邪魔しないこと。教科書ではシリアライザブルだが、製品の既定はそれより弱い（p.275–276） | 3 節の表のとおり、既定も名前も製品ごとに違う |
| D 永続性 | コミット後は失われないという約束。単一ノードでは fsync と先行書き込みログ、複製のある DB では一定数のノードへのコピー（p.276–277） | MySQL は `innodb_flush_log_at_trx_commit=0` で応答済みの書き込みを失うことを Jepsen が確認 [9] |

- 「ACID」という語の初出は Härder と Reuter（1983 年）。本書 p.273 による。原論文は未確認（記憶・要確認）
- 本書は「ACID 準拠」という表示だけでは保証の中身が分からない、と述べる（p.273–274）[48]。このノートでは、分離性を「どの異常を防ぐか」で比べる

### 2.2 SQL 標準の分離レベル（現象 P1〜P3 による定義）

確認できた範囲：**SQL-92 の公開草案**（X3H2-92-154/DBL CBR-002「Proposed revised text of DIS 9075」）の 4.28 節「SQL-transactions」と表 9 を原文で読んだ [1]。**現行の ISO/IEC 9075-2:2023 の条文は有料で、ISO のページも 403 で開けなかった**。現行版の節番号と文言は未確認 [2]。Jepsen は同じ定義を SQL:1999 の文書から引いている [7]。

草案 4.28 節の内容 [1]：

- 分離レベルは READ UNCOMMITTED、READ COMMITTED、REPEATABLE READ、SERIALIZABLE の 4 つ。**草案では既定は SERIALIZABLE**
- SERIALIZABLE は「何らかの直列実行と同じ効果を生む実行」と定義される。P1〜P3 が起きないことは、その帰結として注記されている
- 3 つの現象：
  - P1（ダーティリード）：T1 が行を変更し、T1 がコミットする前に T2 がそれを読む。T1 がロールバックすると、T2 は存在しなかった行を読んだことになる
  - P2（ノンリピータブルリード）：T1 が行を読み、T2 がその行を変更・削除してコミットする。T1 が読み直すと値が変わっているか、行が消えている
  - P3（ファントム）：T1 が検索条件に合う行の集合を読み、T2 が条件に合う行を作る。T1 が同じ条件で読み直すと別の集合になる
- 表 9：

| レベル | P1 | P2 | P3 |
| --- | --- | --- | --- |
| READ UNCOMMITTED | 起こりうる | 起こりうる | 起こりうる |
| READ COMMITTED | 起きない | 起こりうる | 起こりうる |
| REPEATABLE READ | 起きない | 起きない | 起こりうる |
| SERIALIZABLE | 起きない | 起きない | 起きない |

- 草案は、4 つのレベルすべてで「更新は失われない」と書いている（4.28 節）。これが現行版に残っているかは未確認

標準の定義に無いもの：ダーティライト、更新の消失、読み取りスキュー、書き込みスキュー、スナップショット分離。これが 2.3 の批判の出発点になる。

### 2.3 Berenson ほか「A Critique of ANSI SQL Isolation Levels」（1995）

MSR-TR-95-51（1995 年 6 月）。SIGMOD 95、pp.1–10 [3]。原文を読んだ。

- **解釈が 2 通りある**（2.2 節）。P1 の英文は T1 のアボートを要求していない。実際に異常が起きた履歴だけを禁じる「厳密な解釈」（A1・A2・A3）と、異常につながりうる並びを禁じる「広い解釈」（P1・P2・P3）に分かれる。論文は広い解釈が正しいとする（Remark 4）
- **標準は不完全**（3 節）。ダーティライト P0（`w1[x]...w2[x]`）を禁じていない。全レベルで P0 を禁じるべき（Remark 3）。ほかにも異常が残る（Remark 5）
- **P0〜P3 による定義は、ロックの定義の言い換え**（Remark 6）。これが後に Adya の批判点になる（2.4）
- 追加の異常（4 節）：

| 記号 | 名前 | 履歴 | 節 |
| --- | --- | --- | --- |
| P4 | 更新の消失（Lost Update） | `r1[x]...w2[x]...w1[x]...c1` | 4.1 |
| P4C | カーソルでの更新の消失 | `rc1[x]...w2[x]...w1[x]...c1` | 4.1 |
| A5A | 読み取りスキュー（Read Skew） | `r1[x]...w2[x]...w2[y]...c2...r1[y]...(c1 or a1)` | 4.2 |
| A5B | 書き込みスキュー（Write Skew） | `r1[x]...r2[y]...w1[y]...w2[x]...(c1 and c2 occur)` | 4.2 |

- **スナップショット分離の定義**（4.2 節）：各トランザクションは開始時点（Start-Timestamp）のコミット済みデータのスナップショットを読む。読み取りは止められない。コミット時に、自分の実行区間内にコミットした別のトランザクションが同じデータを書いていたらアボートする（First-committer-wins）。これが P4 を防ぐ
- **スナップショット分離の位置**（4.2 節）：
  - READ COMMITTED より強い（Remark 8）。A5A は READ COMMITTED で起こり、スナップショット分離では起きない
  - REPEATABLE READ とは**比べられない**（Remark 9）。スナップショット分離は A3 を防ぐが A5B を許し、REPEATABLE READ はその逆
  - 厳密な解釈の A1・A2・A3 はすべて防ぐ（Remark 10）。つまり、標準の表を厳密に読むと、スナップショット分離は「SERIALIZABLE」を名乗れてしまう。しかし書き込みスキューを許すので直列化可能ではない
  - 広い解釈の P3 は防げない。例：「作業時間の合計が 8 時間以下」という条件を 2 つのトランザクションが別々の行の挿入で破る
- **Oracle の Read Consistency**（4.3 節）：文ごとにスナップショットを取り直す方式。P4C は防ぐが、P4 と A5A は許す
- **用語への苦言**（5 節）：「Repeatable Read」という名前は二重に不適切。繰り返し読んでも同じ結果にならず、業界ではすでに別の意味（直列化可能）で使われていた
- **表 4**（分離の種類ごとに起こりうる異常）。PDF から抽出した表は列がずれて読めなかった。下の表は、本文（4.1・4.2 節と Remark 8〜10）と、ずれた抽出結果を突き合わせて組み直したもので、**原紙の表との一字ずつの照合はしていない（要確認）**

| 分離の種類 | P0 | P1 | P4C | P4 | P2 | P3 | A5A | A5B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| READ UNCOMMITTED | × | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| READ COMMITTED | × | × | ○ | ○ | ○ | ○ | ○ | ○ |
| Cursor Stability | × | × | × | △ | △ | ○ | ○ | △ |
| REPEATABLE READ | × | × | × | × | × | ○ | × | × |
| Snapshot | × | × | × | × | × | △ | × | ○ |
| SERIALIZABLE | × | × | × | × | × | × | × | × |

（○＝起こりうる、×＝起きない、△＝場合による）

### 2.4 Adya の一般化（G0〜G2）

Adya・Liskov・O'Neil「Generalized Isolation Level Definitions」（ICDE 2000）[4]。CMU の講義ページの写しで原文を読んだ（MIT の配布元は 403）。

- 批判：標準の定義は曖昧で、Berenson ほかの修正版はロックの言い換えなので、楽観的な方式とマルチバージョンの方式を締め出してしまう（1 節・3 節）
- 方法：トランザクション間の依存（書き込み依存、読み取り依存、反依存＝読んだものを後から書き換えられる）を辺にした直列化グラフ（DSG）を作り、**禁じる閉路の種類**でレベルを定義する（5 節）

| 現象 | 定義 | 節 |
| --- | --- | --- |
| G0（Write Cycles） | 書き込み依存の辺だけでできた閉路 | 5.1 |
| G1a（Aborted Reads） | コミットした T2 が、アボートした T1 の書いた値を読んだ | 5.2 |
| G1b（Intermediate Reads） | コミットした T2 が、T1 の最終でない途中の値を読んだ | 5.2 |
| G1c（Circular Information Flow） | 書き込み依存と読み取り依存の辺だけでできた閉路 | 5.2 |
| G2（Anti-dependency Cycles） | 反依存の辺を 1 つ以上含む閉路 | 5.3 |
| G2-item | 項目の反依存の辺を 1 つ以上含む閉路（述語の反依存は数えない） | 5.4 |

| レベル | 禁じる現象 | 対応する ANSI の名前 |
| --- | --- | --- |
| PL-1 | G0 | READ UNCOMMITTED |
| PL-2 | G1（G1a・G1b・G1c） | READ COMMITTED |
| PL-2.99 | G1、G2-item | REPEATABLE READ |
| PL-3 | G1、G2 | SERIALIZABLE |

- PL-3 は競合直列化可能性を与える（5.3 節）
- Hermitage と Jepsen は、この Adya の定義（と Bailis ほかの拡張）を物差しに使っている [5][6][7]。G-single（反依存の辺がちょうど 1 つの閉路＝読み取りスキュー）、G-nonadjacent、OTV、PMP は Adya の学位論文と Bailis ほかの拡張による。**学位論文（MIT-LCS-TR-786）は未読**

### 2.5 Jepsen の整合性モデルの図

jepsen.io/consistency/models [6]。図は画像だが、ページの本文が矢印の関係を文章で説明している。それを読んだ。

- 図は Bailis ほか（VLDB 2014）と Viotti・Vukolić の図を作り直したもの。矢印は「強いモデルは弱いモデルを含意する」。色は非同期ネットワーク上での可用性
- 複数オブジェクト（トランザクション）の系統：strict serializable → serializable → repeatable read と snapshot isolation。両者 → monotonic atomic view。repeatable read → cursor stability。cursor stability と monotonic atomic view → read committed → read uncommitted
- 単一オブジェクトの系統：strict serializable → linearizable → sequential → causal → writes follow reads と PRAM → monotonic reads・monotonic writes・read your writes
- 可用性：cursor stability・snapshot isolation・sequential 以上は、非同期ネットワークでは完全には可用にできない。read your writes 以上は「スティッキー可用」まで。それより弱いものは完全に可用にできる
- 同じページの注意：スナップショット分離と repeatable read は**比べられない**（前者は A5B を許し、後者は述語の G-single を許す）
- スナップショット分離のページ [7]：スナップショット分離は実時間の順序も、同じクライアントの中の順序も要求しない。論文によって定義の厳しさが違い、Jepsen は「G-nonadjacent を禁じる」という緩い定義を採る
- serializable は実時間の順序を要求しない。実時間の順序まで求めるのが strict serializable。Spanner はこれを「外部整合性」と呼ぶ（3 節）[23]

## 3. 製品ごとの違い（表。公式文書の URL・版・日付）

### 3.1 既定の分離レベルと、名前と中身の食い違い

| 製品（文書の版） | 既定 | 名前と中身 | 競合時のふるまい | 出典 |
| --- | --- | --- | --- | --- |
| PostgreSQL 18（文書は 18.7） | Read Committed | 4 つの名前を受けつけるが実装は 3 つ。Read Uncommitted は Read Committed と同じ。**Repeatable Read＝スナップショット分離**（ファントムも起きない。直列化異常は起こりうる）。**Serializable＝SSI**（述語ロックは止めない監視。`pg_locks` に `SIReadLock`） | Repeatable Read：`could not serialize access due to concurrent update`。Serializable：`...due to read/write dependencies among transactions`。直列化失敗は SQLSTATE 40001。**トランザクション全体を最初から再試行**する | [11] |
| MySQL 8.4 / 9.7 InnoDB | REPEATABLE READ | 通常の SELECT は最初の読み取りで作ったスナップショットを読む。**ロックを取る読み取り・UPDATE・DELETE は最新のコミット済みの状態を見る**（ギャップロック・ネクストキーロック）。文書は両者を混ぜることを勧めず、その場合は SERIALIZABLE がふつう望ましいと書く。Hermitage では実体は「monotonic atomic view」、更新の消失を防がない [5]。Jepsen（8.0.34）はそれより弱いと報告 [9] | 更新の消失は検出されない（エラーにならない）。SERIALIZABLE は autocommit 無効時に通常の SELECT を `SELECT ... FOR SHARE` に変える（2 相ロック） | [14] |
| Oracle AI Database 26ai（Concepts。/23/ の URL は /26/ へ転送された） | Read Committed | 提供するのは Read Committed・Serializable・読み取り専用の 3 つ。**Serializable はトランザクション開始時点のコミット済みデータだけを見る方式**で、文書はダーティリード・ファジーリード・ファントムが起きないと書く。書き込みスキューへの言及は無い。Hermitage では実体は「snapshot isolation」[5] | 開始後に他がコミットした行を更新・削除しようとすると ORA-08177（serialize できない旨） | [16] |
| SQL Server（2017〜2025 と Azure SQL Database に適用。ms.date 2025-09-26） | READ COMMITTED | READ COMMITTED の中身が DB オプション `READ_COMMITTED_SNAPSHOT` で変わる。OFF（SQL Server の既定）は共有ロック、ON（**Azure SQL Database と Fabric の SQL データベースの既定**）は文ごとのスナップショット。REPEATABLE READ は共有ロックを最後まで保持（ファントムは起こる）。SNAPSHOT は別レベル（`ALLOW_SNAPSHOT_ISOLATION` が必要）。SERIALIZABLE はキー範囲ロック | ロック待ちとデッドロック。SNAPSHOT は更新の競合でエラー（番号は未確認） | [17] |
| CockroachDB v26.4（stable） | SERIALIZABLE | 文書は「分離レベルは 2 つ」と書く：SERIALIZABLE と READ COMMITTED。`sql.txn.read_committed_isolation.enabled` は既定で true。false にすると READ COMMITTED の指定は SERIALIZABLE に引き上げられる。READ UNCOMMITTED は READ COMMITTED に引き上げ。READ COMMITTED は文ごとのスナップショットで、更新の消失・書き込みスキュー・ファントムを許す | SERIALIZABLE：SQLSTATE 40001、文言に「restart transaction」。**クライアント側の再試行が必要**（単文と、結果が既定 16KiB のバッファに収まるバッチは自動再試行）。READ COMMITTED は直列化エラーの再試行が不要。結果不明は 40003 | [18][19] |
| YugabyteDB（YSQL。stable の文書） | 名前の上は Read Committed。中身は設定しだい | `yb_enable_read_committed_isolation` が false のあいだ、**Read Committed の指定はスナップショット分離で動く**。v2025.2 以降、yugabyted・YugabyteDB Anywhere・Aeon で作る新しいユニバースは true が既定。手動で組んだものは false のまま。Repeatable Read＝スナップショット分離。Serializable あり | （このノートでは未調査） | [21] |
| Spanner | serializable | serializable（外部整合性つき）と repeatable read の 2 つ。**repeatable read＝スナップショット分離**で、書き込みスキューを許すと文書が明記（当直医の例）。既定は楽観的で、読み取りはロックを取らない。`SELECT ... FOR UPDATE` を付けた読み取りはコミット時に検証される。リリースノートでは repeatable read は 2026-04-17 に一般提供 | serializable は競合でアボート。repeatable read は書き込みの競合をコミット時に検出（first-committer-wins） | [22][23][24] |
| Aurora DSQL | Repeatable Read（固定） | **分離レベルは PostgreSQL の Repeatable Read に固定**（＝スナップショット分離）。変えられない。ロックを取らない楽観的並行性制御。スナップショットは `BEGIN` の時点（PostgreSQL は最初の文の時点） | コミット時に競合を判定し、SQLSTATE 40001 を返す。OC000（データの競合）と OC001（スキーマの競合）。`SELECT ... FOR UPDATE` はロックではなく「書いたものとして判定する」印。再試行を前提に、処理を冪等に作ることを勧める。制限：DDL と DML は別トランザクション、1 トランザクション 3,000 行まで | [25][26] |
| DynamoDB | （分離レベルを選ぶ仕組みは無い） | `TransactWriteItems`・`TransactGetItems` は最大 100 操作・合計 4MB・同一アカウント同一リージョン。**相手の操作によって分離が違う**：単一項目の Put／Update／Delete／GetItem と他のトランザクションに対しては serializable、Query・Scan・BatchGetItem に対しては read-committed。BatchWriteItem は単位としては serializable でない。グローバルテーブルではリージョンをまたぐ ACID は無い | 競合は `TransactionCanceledException`（SDK は再試行しない）。単一項目の書き込み側は `TransactionConflictException`。`ClientRequestToken` で 10 分間冪等。各項目の読み書き容量を 2 回分消費 | [27] |
| MongoDB（Manual の表示は 9.0 Current） | トランザクションの read concern はクライアントの既定（プライマリでは `local`）。write concern の既定は 5.0 以降 `majority` | 複数文書のトランザクションはレプリカセットで FCV 4.0 以上、シャードクラスタで FCV 4.2 以上。文書は「分離レベル」という言葉で名づけていない。スナップショット分離が要るなら read concern `snapshot` を使えと書く。`snapshot` は `majority` でコミットしたときだけ、過半数にコミット済みのデータを読んだ保証になる | 文書は「スキーマ設計の代わりにしない」と注意する。実行時間の上限（60 秒）は記憶・要確認 | [28] |

読み方の注意：

- 「Repeatable Read」の中身は 4 通りある。PostgreSQL・YugabyteDB・Spanner・Aurora DSQL はスナップショット分離、SQL Server は共有ロックの保持（Adya の PL-2.99 に近い）、MySQL はどれにも当てはまらない（3.3）
- 「Serializable」という名前でも、Oracle は書き込みスキューを許す [5]
- 既定が Serializable なのは、調べた範囲では CockroachDB と Spanner だけ。Aurora DSQL は最強でもスナップショット分離
- 名前が同じ Read Committed でも、CockroachDB は自分の実装が PostgreSQL より強い（単文の中の異常を防ぐ）と書く [19]

### 3.2 Hermitage の結果表（製品 × 異常）

出典：github.com/ept/hermitage の README [5]。**最新コミットは 2026-01-23（f029bec、リンクの修正）**。その前は 2024-10-14（VeloxDB へのリンク）、2024-07-01（Memgraph の追加）。各製品をどの版で試したかは README の表には無い（製品ごとの .md にある。未読）。

○＝防ぐ、×＝防がない、R/O＝読み取り専用のときだけ防ぐ、一部＝場合による。★＝その製品の既定。

| 製品 | 製品が呼ぶ名前 | 実際の分離 | G0 | G1a | G1b | G1c | OTV | PMP | P4 | G-single | G2-item | G2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PostgreSQL | read committed ★ | monotonic atomic view | ○ | ○ | ○ | ○ | ○ | × | × | × | × | × |
| PostgreSQL | repeatable read | snapshot isolation | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | × | × |
| PostgreSQL | serializable | serializable | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| MySQL/InnoDB | read uncommitted | read uncommitted | ○ | × | × | × | × | × | × | × | × | × |
| MySQL/InnoDB | read committed | monotonic atomic view | ○ | ○ | ○ | ○ | ○ | × | × | × | × | × |
| MySQL/InnoDB | repeatable read ★ | monotonic atomic view | ○ | ○ | ○ | ○ | ○ | R/O | × | R/O | × | × |
| MySQL/InnoDB | serializable | serializable | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| Oracle DB | read committed ★ | monotonic atomic view | ○ | ○ | ○ | ○ | ○ | × | × | × | × | × |
| Oracle DB | serializable | snapshot isolation | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | × | 一部 |
| SQL Server | read uncommitted | read uncommitted | ○ | × | × | × | × | × | × | × | × | × |
| SQL Server | read committed（ロック）★ | monotonic atomic view | ○ | ○ | ○ | ○ | ○ | × | × | × | × | × |
| SQL Server | read committed（スナップショット） | monotonic atomic view | ○ | ○ | ○ | ○ | ○ | × | × | × | × | × |
| SQL Server | repeatable read | repeatable read | ○ | ○ | ○ | ○ | ○ | × | ○ | 一部 | ○ | × |
| SQL Server | snapshot | snapshot isolation | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | × | × |
| SQL Server | serializable | serializable | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| FDB SQL Layer | serializable ★ | serializable | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| CockroachDB | read committed | monotonic atomic view | ○ | ○ | ○ | ○ | ○ | × | × | × | × | × |
| CockroachDB | repeatable read | snapshot isolation | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | × | × |
| CockroachDB | serializable ★ | serializable | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| YugabyteDB | read committed ★ | monotonic atomic view | ○ | ○ | ○ | ○ | ○ | × | × | × | × | × |
| YugabyteDB | repeatable read | snapshot isolation | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | × | × |
| YugabyteDB | serializable | serializable | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| Memgraph | snapshot isolation ★ | snapshot isolation | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | × | × |
| Memgraph | read committed | read committed | ○ | ○ | ○ | ○ | ○ | × | ○ | × | × | × |
| Memgraph | read uncommitted | read uncommitted | ○ | × | × | × | ○ | × | ○ | × | × | × |

異常の名前（README の凡例）：G0＝ダーティライト、G1a・G1b・G1c＝ダーティリードの 3 種、OTV＝見えたトランザクションが消える、PMP＝述語の読み取りで複数の時点が混ざる、P4＝更新の消失、G-single＝読み取りスキュー、G2-item＝別々の行を読んだ書き込みスキュー、G2＝述語の読み取りによる書き込みスキュー。

README 自身が書く限界：

- 試験の集まりであって証明ではない。手で順に実行するので、速いタイミングに依存する問題は見つからない
- 表は「防ぐかどうか」だけで、防ぎ方（待たせるかアボートするか）と性能は示さない
- チェックの数が多いほどよいとは限らない（得るものと失うものの比較）

Hermitage と公式文書・Jepsen の食い違い（未解決。9 節）：

- CockroachDB：Hermitage には「repeatable read＝スナップショット分離」の行があるが、v26.4 の公式文書は分離レベルを 2 つと書く [18]。設定で有効にする機能かどうかは未確認
- MySQL の REPEATABLE READ：Hermitage は monotonic atomic view、Jepsen（8.0.34）はそれも満たさないと報告 [9]

### 3.3 Jepsen の分析の要点

| 対象 | 日付 | 要点 | 出典 |
| --- | --- | --- | --- |
| PostgreSQL 12.3（9.5.22・10.13・11.8 も） | 2020-06-12 | (1) Serializable で G2-item が出た（通常運用の単一ノードで、2 分の試験で 6 件）。原因は、並行する 3 つのトランザクションでの競合検出の誤り。修正コミットは 5940ffb で、次のマイナーリリース（8 月 13 日予定）に入ると報告。(2) Repeatable Read は実際にはスナップショット分離で、G2-item を許す。標準を厳密に解釈すれば準拠、広く解釈すれば非準拠。文書に明記するよう勧告。(3) Read Committed に G0・G1a・G1b は無かった | [8] |
| MySQL 8.0.34（MariaDB 10.11.3 も） | 2023-12-19 | 障害を入れない単一ノードの REPEATABLE READ で、G2-item、G-single、**更新の消失**（成功した 9,048 件中 198 件）、同じトランザクションの中で読み取りが変わる例（126 件）、monotonic atomic view の違反が出た。結論は、スナップショット分離でも PL-2.99 でも monotonic atomic view でもなく、正体がはっきりしない、というもの。勧め：繰り返し読める保証が要るなら Serializable、または Read Committed で `SELECT ... FOR UPDATE`。ORM の読んで書くパターンは黙って更新を失いうる。別件：RDS の Multi-AZ DB クラスターは Serializable でも直列化可能性を破った（`replica_preserve_commit_order` が既定で OFF） | [9] |
| Amazon RDS for PostgreSQL 17.4（13.15〜17.4 の Multi-AZ クラスター） | 2025-04-29（5 月 3 日に追記） | 障害を入れない健全なクラスターで、Long Fork と G-nonadjacent が数分ごとに出た。**スナップショット分離を満たさない**。Parallel Snapshot Isolation に当てはまる可能性。原因（追記）：プライマリはメモリ上の順序でトランザクションを見せ、セカンダリは WAL の順序で見せるので、ノード間で順序が食い違う。単一インスタンスは試験していない。勧め：読み取り専用エンドポイントでの読み取りを含む設計を見直す、大事な処理は書き込みエンドポイントに寄せる | [10] |

設計への意味：**分離レベルの保証は、読み取りをレプリカに逃がした時点で変わる**。PostgreSQL の公式文書も、Serializable の保護はホットスタンバイと論理レプリカにはまだ及ばないと書いている [12]。

## 4. 事故・失敗例（一次報告）

事業者自身の事後報告として読めたものは無い。以下は査読論文と Jepsen の報告。

| 事例 | 内容 | 出典の性質 |
| --- | --- | --- |
| Flexcoin（2014-03-02） | ビットコイン取引所。利用者間の送金のコードの欠陥を突かれ、数千の同時リクエストで、残高が更新される前に口座が貸越になるまで移され、保管していた全コインを失い閉鎖した | ACIDRain 論文 1 節が、取引所の発表を引用 [29]。**取引所の発表そのものは未確認** |
| ACIDRain（Warszawski・Bailis、SIGMOD 2017） | 自前で運用する型の EC アプリ 12 本（4 言語。合わせて 200 万を超えるサイトで使用と記載）を、SQL のログから異常を探す手法（2AD）で調べ、**22 件の脆弱性**を見つけて攻撃を確かめた。内訳は在庫 9・ギフト券 8・カート 5。**22 件のうち 17 件は、トランザクションの範囲の誤り**（処理をトランザクションで囲んでいない、または分けてしまっている）で、分離レベルを Serializable に上げても防げない。残りが分離レベルに由来。脚注 6：MySQL の Repeatable Read で更新の消失が起きた | 原文で確認 [29] |
| Feral Concurrency Control（Bailis ほか、SIGMOD 2015） | Rails のオープンソースアプリ **67 本**を調査。1 モデルあたりトランザクション 0.13、ロック 0.01 に対して、バリデーション 1.80、アソシエーション 3.19。バリデーションはトランザクションの 13.6 倍、アソシエーションは 24.2 倍。**アプリ側の検査（feral）は DB の制約の代わりにならない**：一意性と外部キーにあたる検査は、並行実行で重複や孤児を作りうる。使用数で最大 86.9% は安全、残りは破損しうる | 原文で確認 [30] |
| PostgreSQL 12.3 | Serializable が直列化可能でなかった（上の表） | Jepsen の報告 [8] |
| RDS for PostgreSQL 17.4 | 読み取りレプリカを含めるとスナップショット分離が崩れる | Jepsen の報告 [10] |

本書が挙げる事例（英国郵便局 Horizon、ビットコイン取引所の破綻、監査人の調査）は、本書 p.272・p.283 の引用どまりで、原典は未確認 [48]。

読み取れること：

1. 害の多くは「弱い分離レベル」より先に、**トランザクションの範囲の取り方**で起きている（22 件中 17 件）
2. 低い同時実行では表に出ない。API を公開すると、攻撃者が同時実行を作れる [29]
3. ORM と枠組みは、読んで判断して書くパターンと、アプリ側の検査を書かせやすい [30][9]

## 5. 権威の推奨と位置づけ（規範か任意か）

| 出どころ | 推奨 | 位置づけ |
| --- | --- | --- |
| PostgreSQL 公式文書 13.4 [12] | 業務ルールは Read Committed では守りにくい。Serializable を全書き込みと一貫した読み取りに使い、直列化失敗を自動で再試行する仕組みを共通に持つ。使えないなら `SELECT FOR UPDATE`・`LOCK TABLE` で明示的に守る | 製品の文書。任意 |
| PostgreSQL 公式文書 13.2 [11] | Serializable の性能のために：読み取り専用を宣言、接続数を抑える、トランザクションを短く、アイドルのまま開いたトランザクションを残さない、不要な明示ロックを外す | 製品の文書。任意 |
| CockroachDB 公式文書 [19] | SERIALIZABLE でうまく動いているなら READ COMMITTED に変えることは勧めない。READ COMMITTED は、移行元が READ COMMITTED 前提のアプリや、再試行を減らしたい高い同時実行向け | 製品の文書。任意 |
| Jepsen [8][9][10] | 文書に分離レベルの実体を明記せよ。利用者は自分の負荷で不変条件を試験せよ | 第三者の分析。任意 |
| AWS Prescriptive Guidance（saga choreography／orchestration）[32] | サービスごとに DB を持つ構成では 2 相コミットは選べないとして、サーガを示す。注意点：複雑さ、結果整合性、**参加者の冪等性**、**分離が無い（セマンティックロックを勧める）**、可観測性、遅延、オーケストレータの単一障害点、コレオグラフィでは二重書き込み（トランザクショナル・アウトボックスで解く）と循環依存 | クラウド事業者の設計指針。任意。利用者は設計者・テックリード |
| Azure Architecture Center「Saga」（ms.date 2025-02-25）[33] | 取引を補償可能・ピボット（引き返せない点）・再試行可能の 3 種に分ける。異常（更新の消失、ダーティリード、ファジーリード）と対策（セマンティックロック、可換な更新、悲観的ビュー、値の再読、バージョンファイル、リスクに応じた並行性制御）を挙げる | 同上。任意 |
| Azure Architecture Center「Compensating Transaction」（ms.date 2026-04-16）[34] | 補償は元の状態に戻すとは限らない。補償自体が失敗しうるので、各ステップを冪等にし、進み具合を記録して再開できるようにする。逆順とは限らない。引き返せない点を決め、取り消せない操作は検証が全部済んでから行う。まず再試行、補償は最後の手段。判断が重いときは人を入れる。一時的な不整合を許せないなら強い整合性かアトミックなトランザクションを使う | 同上。任意 |
| Kafka 公式文書（4.4、Design）[38] | 既定の保証は少なくとも 1 回。外部システムへの厳密に 1 回は相手の協力が要る。2 相コミットより、**出力と同じ場所にオフセットを保存する**ことを勧める | 製品の文書。任意 |
| IETF「Idempotency-Key」ヘッダー [36] | 草案（-08、2026-10-22 付、httpapi WG、Standards Track を目指す、2027-04-25 に失効）。**RFC ではない** | 草案。結論の唯一の根拠にしない |

規範（守らないと違反になるもの）は、この論点には見つからなかった。SQL 標準は製品の適合性を定めるが、利用者に分離レベルの選び方を課してはいない。

## 6. 設計判断の分かれ目（何を選ぶと何を得て何を失うか。表）

### 6.1 異常と、防ぐ手段（1 つの DB の中）

| 異常 | 実務での例 | 効く手段 | 効かない手段 |
| --- | --- | --- | --- |
| 更新の消失（P4） | 在庫数・ポイント残高を読んで、計算して、書き戻す。2 人が同時に同じ注文を編集する | アトミックな更新（`SET stock = stock - 1`）。`SELECT ... FOR UPDATE`。バージョン列による条件付き更新（楽観ロック）。スナップショット分離の自動検出（PostgreSQL の Repeatable Read、SQL Server の SNAPSHOT など）。Serializable | Read Committed のままの読んで書く処理。**MySQL の REPEATABLE READ**（検出しない）[5][9] |
| 読み取りスキュー（A5A） | 送金の途中で 2 口座の合計を読むと足りない。バックアップや集計が半端な状態を写す | スナップショット分離以上。1 文にまとめる | Read Committed |
| 書き込みスキュー（A5B、G2-item） | 「当直は最低 1 人」を 2 人が同時に外れる。残高の合計が正であることを 2 口座から別々に引き出す | Serializable。前提にした行を `SELECT ... FOR UPDATE` で明示的にロック。制約（表せる場合） | スナップショット分離（PostgreSQL の Repeatable Read、Oracle の Serializable、Aurora DSQL、Spanner の repeatable read）。更新の消失の自動検出 |
| ファントムによる書き込みスキュー（G2） | 会議室・配達枠の二重予約。ユーザー名の重複。「まだ無いこと」を確かめてから挿入する | Serializable。**一意性制約・排他制約**。ロックする行をあらかじめ作る（競合の実体化。最後の手段）[48] | `SELECT ... FOR UPDATE`（無い行はロックできない）。CockroachDB も、READ COMMITTED のロック読み取りは新しい行のファントムを防がないと書く [19] |

### 6.2 手段ごとの得るものと失うもの

| 選択 | 得るもの | 失うもの・費用 |
| --- | --- | --- |
| アトミックな更新 | 最も安い。待ちも再試行もほぼ無い | 1 文で書ける更新に限る。ORM が読んで書く形を生成すると使えない |
| `SELECT ... FOR UPDATE`（悲観ロック） | 読んで判断して書く処理を安全にする | 付け忘れを機械が見つけてくれない。ロック待ちで高パーセンタイルの遅延が延びる。デッドロック。無い行は守れない。Aurora DSQL と Spanner（楽観的）では「待つ」ではなく「コミット時に落ちる」に変わる [25][22] |
| バージョン列（楽観ロック） | DB の種類やトランザクションの有無に依存しない。API 越しでも使える（ETag と同じ考え方） | 競合時の再試行を呼び出し側が書く。競合が多いと再試行が増える。条件付き更新の正しさは製品の実装による（本書 p.296 の注意）[48] |
| Serializable（SSI。PostgreSQL・CockroachDB） | アプリのコードを読まなくても、分離に由来する異常が無いと言える。読み手と書き手は互いを止めない | **40001 の再試行を全経路に実装する**必要がある。アボート率は競合と実行時間で上がる。トランザクションを短くする必要。PostgreSQL ではスタンバイに保護が及ばない [12]。再試行される処理の中の外部への副作用（メール、他サービスの呼び出し）は取り消されない |
| Serializable（2 相ロック。MySQL・SQL Server） | 同じ保証 | 読み手と書き手が互いを止める。スループットと高パーセンタイルの遅延が悪化。デッドロック |
| 制約（一意性・外部キー・CHECK・排他） | 分離レベルに関係なく DB が守る。コードを通らない書き込みにも効く | 表せる不変条件が限られる。サービスをまたぐ不変条件には使えない。アプリ側の検査だけでは代わりにならない [30] |
| 弱い分離のまま受け入れる | 再試行の実装が要らず、性能が読みやすい | どの異常が起こりうるかを処理ごとに説明できる必要がある。攻撃者が同時実行を作れる API では、不具合ではなく脆弱性になる [29] |

### 6.3 サービスをまたぐとき

| 選択 | 得るもの | 失うもの・費用 |
| --- | --- | --- |
| 1 つの DB の 1 トランザクションに収める（サービスの境界を引き直す） | 原子性と分離性が DB から来る | サービスの独立性。共有 DB は置換性を失う（Part 3） |
| 異なる技術をまたぐ 2 相コミット（XA） | 複数の資源にまたがる原子性 | コーディネータが落ちると、準備済みの参加者は決められず、**ロックを持ったまま待つ**。PostgreSQL は、準備済みのまま長く置くとロックの保持、VACUUM の妨げ、最悪はトランザクション ID の周回防止で停止に至ると警告し、外部のトランザクションマネージャを書くのでなければ使うなと書く [13]。MySQL は準備済みの XA トランザクションが明示の `XA COMMIT`／`XA ROLLBACK` まで残る（`XA RECOVER` で探す）[15]。分離性は与えない |
| 分散 SQL の内部のトランザクション（CockroachDB・Spanner・YugabyteDB・Aurora DSQL） | 複数ノードにまたがる原子性と分離性を、1 つの製品が受け持つ。コーディネータの状態が複製されるので、コーディネータの障害で人手が要らない。CockroachDB は書き込みインテントとトランザクションレコードを使い、ハートビートが止まったレコードを他のトランザクションが中断・回復できる [20] | その製品の中だけ。別のサービスの DB、メッセージブローカー、外部 API は含まれない |
| サーガ（補償つきのローカルトランザクションの列） | 各サービスは自分の DB でコミットし、長いロックを持たない | **分離性が無い**（途中の状態が他から見える）。補償を全部書く。補償は失敗しうる。取り消せない操作がある |
| 冪等な受け手＋少なくとも 1 回の配信 | 分散トランザクション無しで「実質 1 回」。処理済み ID の記録と業務の書き込みを同じ DB トランザクションに入れる（本書 8.4.4、p.328–330）[48] | 冪等キーの設計、保存期間、同じキーで中身が違う要求の扱いを決める必要 |
| 耐久実行（Temporal、Step Functions、Durable Functions、Restate） | オーケストレータの状態（どこまで進んだか）を失わない。再試行・タイマー・補償の呼び出しを基盤が持つ | 分離性は与えない。呼び出される側の冪等性は依然として必要。ワークフローのコードに決定性の制約。基盤そのものが新しい共通の依存先になる（Part 14） |
| 謝罪を設計に入れる（Helland） | 可用性と疎結合。在庫の引当などを「暫定→確定／取消」で扱える | 業務側に、過剰引当・取り消し・人の対応の手順が要る |

### 6.4 サーガの原論文が言ったこと、言っていないこと

Garcia-Molina・Salem「Sagas」（SIGMOD 1987）[31]。コーネル大学の講義ページの写し（スキャンに OCR の文字層）で読んだ。OCR の誤字が多く、節番号は見出しから拾った。

- 動機は、**長く生きるトランザクション（LLT）が DB の資源を長く握る**問題。対象は 1 つの集中型の DBMS で、分散は紙幅の都合で扱わないと断っている（1 節の末尾）。マイクロサービスのための提案ではない
- 定義：LLT が、他のトランザクションと交互に実行できる一連のトランザクション T1…Tn に書けるとき、それがサーガ。各 Ti に補償トランザクション Ci を用意する。システムは、T1…Tn が全部終わるか、途中までの T1…Tj と補償 Cj…C1 が実行されるかを保証する
- **分離性は無い**と最初から書いてある：他のトランザクションはサーガの途中の結果を見ることがあり、補償を走らせても、それを見た側には知らせもアボートもしない
- 回復は 2 種類：後ろ向き（補償）と前向き（セーブポイントから残りを実行）。利用者による中断を禁じれば前向きだけで足り、補償を書かなくて済む
- 補償の限界：補償トランザクション自体が誤りで完了できないと、システムは行き詰まる。対策として挙げるのは、別の実装への切り替えと**人手の介入**。「美しくはないが実用的」と書く
- 取り消せない操作の例としてミサイルの発射を挙げる。補償を書くのは一般に難しいが、多くの業務では元の処理を書くのと同程度、とも書く
- 設計の助言：DB を疎結合な部品に分けておくと、LLT が自然にサブトランザクションに分かれる

オーケストレーションとコレオグラフィという分け方は原論文には無い（原論文にあるのは saga execution component という実行役）。この 2 分法は AWS と Azure の指針にある [32][33]。

| | オーケストレーション | コレオグラフィ |
| --- | --- | --- |
| 進め方 | 中央の調整役が各サービスに指示し、状態を持つ | 各サービスがイベントを出し、それを受けて次が動く |
| 向く場面 | 手順が複雑、参加者が増える | 参加者が少なく単純 |
| 弱点 | 調整役が障害点になる。調整のロジックを作る必要 | 流れが追いにくい。循環依存。結合試験が難しい。タイムアウトや再試行を全体でそろえにくい。DB 更新とイベント発行の二重書き込み |

### 6.5 耐久実行の位置づけ

耐久実行は、サーガの「調整役の状態を失わない」部分を基盤に任せる道具で、分散トランザクションの代わりではない。

| 製品 | 仕組み（公式文書の記述） | 保証の言い方 | 出典 |
| --- | --- | --- | --- |
| Temporal | コマンドをイベント履歴に記録し、障害後は履歴と突き合わせながら再実行して続きから再開。ワークフローのコードに決定性の制約 | ワークフローは「effectively once」で最後まで実行。アクティビティは失敗すると再試行されるので、冪等に書くことを勧める | [44] |
| AWS Step Functions | Standard は状態遷移ごとに状態を保存。最長 1 年 | Standard は「厳密に 1 回」（ASL で Retry を指定しないかぎり、タスクと状態は 2 回以上実行されない）。Express（最長 5 分）は非同期が少なくとも 1 回、同期が多くとも 1 回 | [45] |
| Azure Durable Functions／Durable Task | イベントソーシング。追記専用の履歴に行動を記録し、再開のたびに関数を最初から再実行して履歴で状態を組み直す。オーケストレータのコードは決定的でなければならない | アクティビティの実行回数の保証は、読んだページには書かれていなかった（少なくとも 1 回という理解は記憶・要確認） | [46] |
| Restate | 副作用のある操作とその結果をジャーナルに記録し、障害後は済んだステップを飛ばして再開。冪等キーをヘッダーに付けると重複した要求は元の結果を返す | 呼び出しは障害があっても「exactly once」で走ると書く。クラスタの合意には過半数が要る | [47] |

注意：どの製品の「1 回」も、**基盤が記録した範囲の中**の話。アクティビティが外部の API を呼んで、結果を記録する前に落ちれば、再試行で外部には 2 回届く。だから呼ばれる側の冪等キーが要る（2.x の端から端までの議論と同じ形）。

### 6.6 冪等性と「厳密に 1 回」

**冪等キー**

- Stripe の API [35]：`Idempotency-Key` ヘッダー。API v1 は、同じキーの最初の要求の**状態コードと本文を保存**し、再試行には保存した応答を返す（500 も含む）。キーは最長 255 文字、V4 UUID などを勧める。24 時間以上たったキーは消されうる。同じキーでパラメータが違えばエラー。保存されるのはエンドポイントの実行が始まってから（検証エラーや同時実行の競合は保存されず、再試行できる）。POST が対象で、GET と DELETE は定義上冪等。API v2 は挙動が違う（成功した操作は繰り返さず、失敗した部分を完了まで進める）
- IETF の草案 [36]：draft-ietf-httpapi-idempotency-key-header-08（2026-10-22 付、2027-04-25 失効、httpapi WG、状態は I-D Exists）。ヘッダーの値は Structured Field の文字列。キーは一意で、別の中身に使い回してはならない。同じキーの再試行には完了済みとして一貫した応答、処理中の重複には 409、同じキーで中身が違えば 422、必須なのに無ければ 400（いずれも SHOULD）。資源側は失効の方針を含む仕様を公開する。**草案であり RFC ではない**
- DynamoDB [27]：`ClientRequestToken` は 10 分間有効。同じトークンでパラメータを変えると `IdempotentParameterMismatch`
- Helland [43]：要求に「uniquifier」を付けるか、同じ働きをする工夫を入れる（2.2 節、7.5 節）

**Kafka の「厳密に 1 回」**（公式文書 4.4 と 4.0 の更新ノート）

| 項目 | 確認した内容 | 出典 |
| --- | --- | --- |
| `enable.idempotence` | 既定 `true`。条件は `max.in.flight.requests.per.connection` ≤ 5、`retries` > 0、`acks=all`。明示せずに条件と矛盾する設定をすると無効になり、明示していれば `ConfigException` | [37] |
| `acks` | 既定 `all` | [37] |
| `retries`／`delivery.timeout.ms` | 既定 2147483647／120000（2 分）。再試行の制御は後者で行うよう勧める | [37] |
| `max.in.flight.requests.per.connection` | 既定 5 | [37] |
| `transactional.id`／`transaction.timeout.ms` | 既定 null／60000（1 分）。設定すると冪等性が前提になる。既定ではブローカーが 3 台以上要る | [37] |
| `transaction.two.phase.commit.enable` | 既定 false。true にすると、クライアントが 2 相コミットに参加することをブローカーに伝え、そのトランザクションは期限切れにならない | [37] |
| 冪等プロデューサの仕組み | 0.11.0.0 から。ブローカーがプロデューサに ID を割り当て、メッセージごとの連番で重複を除く | [38] |
| トランザクション | 複数のトピックパーティションへの書き込みと、コンシューマのオフセットの更新をアトミックに行える。読む側は `isolation.level=read_committed` と `enable.auto.commit=false` が要る。**既定の `read_uncommitted` は中断されたトランザクションのメッセージも返す** | [38] |
| KIP-890 | 状態は承認済み。問題：中断されたトランザクションの遅れて届いたメッセージが次のトランザクションに紛れ込む、止まったままのトランザクションが LSO を進めなくする。対策：トランザクションごとにプロデューサのエポックを上げる、最初の produce でパーティションを暗黙に追加する（トランザクションのプロトコルの版 TV2）。古いクライアントにはブローカー側の検証 | [40] |
| 4.0 での扱い | 4.0 の更新ノートは、KIP-890 が強化されたトランザクションのプロトコルを 4.0 にもたらし、4.0 への更新を確定（`kafka-features.sh upgrade --release-version 4.0`）すると有効になると書く。4.0 のプロデューサではエポックがトランザクションごとに上がる。4.0 では、`max.in.flight...` が 5 を超えたときに冪等性が黙って外れる挙動も無くなった | [39] |

- 「TV2」という名前と「新しいクラスタでは既定で有効」という点は、更新ノートの要約からは確かめられなかった（9 節）
- **Kafka の「厳密に 1 回」が指すもの**：Kafka から読んで Kafka に書く処理（読む・処理する・書く・オフセットを進める）がアトミックになること。公式文書は「exactly-once」の主張は誤解を招く場合があるので細部を確かめよ、と自分で書く。外部システムへの厳密に 1 回は相手の協力が要り、2 相コミットではなく、出力と同じ場所にオフセットを保存する方法を勧める [38]
- したがって、DB に書く受け手は、Kafka のトランザクションを有効にしても冪等にする必要がある

**端から端までの議論**（Saltzer・Reed・Clark「End-to-End Arguments in System Design」）[41]。MIT の公開版を原文で読んだ。掲載誌と年（ACM TOCS、1984 年）は記憶・要確認。

- 主張：ある機能を完全に正しく実装できるのが、通信の両端にいるアプリケーションの知識と助けがあるときだけなら、その機能を下の層の機能として提供しても完全にはならない。下の層の仕組みは**性能の向上**としてだけ正当化される
- 「重複メッセージの抑制」の節：ネットワークが重複を消しても、アプリケーション自身が再試行で重複を作る（応答が無いので利用者がもう一度操作する、相手が落ちたのか応答が遅れただけか区別できない）。その重複はアプリケーションにしか見分けられない
- 当てはめ：ブローカーの「厳密に 1 回」や TCP の再送は、利用者の二重クリックや、タイムアウト後のクライアントの再試行による重複を消せない。**冪等キーは、要求を出した端から、最終的に状態を変える端まで通す**

### 6.7 制約の強制と「謝罪」

**Helland「Life beyond Distributed Transactions: an Apostate's Opinion」**（CIDR 2007）[42]。原文で読んだ（ACM Queue の 2016 年版は 403 で未確認）。

- 出発点：大規模なアプリケーションの開発者は、分散トランザクションを前提にせず作っている、という観察
- 「エンティティ」：一意なキーを持つデータのまとまりで、1 つの直列化可能性の範囲に収まる。**アトミックなトランザクションはエンティティをまたげない**（再分割で別のマシンに移りうるから）
- メッセージは少なくとも 1 回届く前提。受け手は処理済みであることを覚えて、繰り返しを無害にする（冪等）
- 「アクティビティ」：相手ごとのやり取りの状態。エンティティの中に持つ
- 合意は**暫定の操作**で作る：取り消しの権利を残して約束を求め、後で確定するか取り消す。不確かさは、ロックではなく業務の意味の中に持つ。「これは単なるワークフローだ」と書く

**Helland・Campbell「Building on Quicksand」**（CIDR 2009、arXiv:0909.1788）[43]。原文で読んだ。

- 複製を非同期にすると、プライマリが約束したことは確率的になる。業務ルールの強制も確率的になる（5.2 節）
- 計算は「記憶・推測・謝罪」に分けられる（5.7 節）。手元の知識だけで動く以上、行動は推測で、間違えたら謝罪する。謝罪は人に回してもよいし、業務のコードにしてもよい
- 「同期のチェックポイントか、謝罪か」（5.8 節）。絶対に謝らない設計は、受けたい取引を断ることになる（7 節）
- 過剰予約と過剰引当、座席予約のパターン（空き→購入保留→購入済み）、一意な識別子の重要性（7.1〜7.5 節）
- 可換な操作なら順序に依存しない。記憶装置への WRITE は可換でない（5.3 節）
- 在庫が 1 冊だけの本がフォークリフトに轢かれる例：計算機が完全でも、業務には謝罪が要る（7 節）

設計への意味：サービスをまたぐ不変条件（在庫を超えて売らない、二重に請求しない）は、DB の制約では強制できない。選べるのは、(a) 1 つのエンティティ（1 つのサービスの 1 つの DB）に寄せて制約で守る、(b) 暫定→確定／取消の手順にする、(c) 破れることを認めて検出と謝罪（返金・取り消し・人の対応）を設計する、のどれか。

## 7. 設計レビューで問うこと（問い｜なぜ問うか｜危ない兆候）

| # | 問い | なぜ問うか | 危ない兆候 |
| --- | --- | --- | --- |
| 1 | この DB の既定の分離レベルは何か。その名前の中身（どの異常を防ぐか）を、製品の文書か実測で言えるか | 既定も名前の意味も製品で違う [5][11][14] | 「ACID だから大丈夫」「Repeatable Read だから更新は消えない」 |
| 2 | 守りたい不変条件を、処理ごとに 1 文で書けるか（在庫 ≥ 0、枠は 1 件まで、など） | 分離レベルは不変条件に対して選ぶ。不変条件が無ければ選べない | 不変条件がコードの if 文にしか無い |
| 3 | 読んで、判断して、書く処理はどこにあるか。それは 1 文の更新に直せるか | 更新の消失と書き込みスキューの共通の形 [48] | ORM で読み込んで属性を変えて保存、が既定の書き方 |
| 4 | 「まだ無いこと」を確かめてから挿入する処理は、一意性制約か排他制約で守られているか | ファントムは行ロックで防げない [48][19] | アプリ側の重複チェックだけ [30] |
| 5 | トランザクションの範囲は、1 つの業務操作全体を囲んでいるか | ACIDRain の 22 件中 17 件は範囲の誤り [29] | 1 つの API 呼び出しの中に複数の自動コミットの文 |
| 6 | Serializable や楽観的な DB を使うなら、40001 の再試行はどこに、何回、どんな間隔で実装されているか | SSI・Aurora DSQL・CockroachDB は再試行が前提 [11][18][25] | 再試行が無い。再試行の中にメール送信や外部 API の呼び出しがある |
| 7 | 再試行の対象はトランザクション全体か。途中の文だけをやり直していないか | PostgreSQL は全体を最初からやり直すよう求める [11] | 例外を握って同じ接続で続行 |
| 8 | 読み取りをレプリカに逃がしている処理で、一貫した読み取りを前提にしていないか | レプリカを含めると保証が変わる [10][12] | 判断のための読み取りがレプリカ、書き込みがプライマリ |
| 9 | 同時実行を外から作れる API（残高、クーポン、在庫）で、並行に叩いたときの試験があるか | 低い同時実行では出ない。攻撃者は作れる [29] | 並行の試験が無い。負荷試験が正常系だけ |
| 10 | 2 相コミット・XA を使うなら、コーディネータが落ちたとき、準備済みのトランザクションを誰がどう片づけるか | 準備済みはロックを持ち続ける [13][15] | 手順書が無い。`max_prepared_transactions` を理由なく有効化 |
| 11 | 「分散トランザクション」と言うとき、同じ製品の中の話か、異なる技術をまたぐ話か | 前者は製品が受け持ち、後者は XA の問題を抱える [48][20] | 分散 SQL の保証を、ブローカーや他サービスまで及ぶと見なしている |
| 12 | サーガの各ステップの補償は書かれているか。補償が失敗したらどうなるか | 補償は失敗しうる。原論文の答えは人手 [31][34] | 補償が「TODO」。失敗時の通知先が無い |
| 13 | サーガの途中の状態を他の処理が読んだとき、何が起きるか | サーガに分離性は無い [31][32][33] | 「保留中」の状態が無く、途中の値がそのまま見える |
| 14 | 取り消せない操作（送金、発送、メール）は、どの時点で実行するか | 引き返せない点は検証の後に置く [33][34] | 最初のステップが外部への送金 |
| 15 | 受け手は冪等か。冪等キーは誰が作り、どこまで通し、いつまで保存するか | 少なくとも 1 回の配信と再試行が前提 [35][38][41] | キーをサーバー側で作る。保存期間が再試行の最大間隔より短い |
| 16 | 同じ冪等キーで中身が違う要求、処理中の重複は、どう応答するか | 決めないと誤用が黙って通る [35][36] | 最初の応答を無条件に返す |
| 17 | 「厳密に 1 回」と書いてある箇所は、何から何までの範囲の話か | Kafka の保証は Kafka の中。外部は相手の協力が要る [38] | 「Kafka が exactly-once だから DB 側は重複を考えない」 |
| 18 | Kafka を読む側の `isolation.level` は何か | 既定は中断されたトランザクションのメッセージも読む [38] | トランザクションで書いているのに、読む側が既定のまま |
| 19 | 耐久実行の基盤を使うなら、呼ばれる側（アクティビティ）は冪等か。基盤が止まったら業務はどうなるか | 基盤の「1 回」は記録の範囲内 [44][45] | 「ワークフローエンジンがあるから補償も冪等性も要らない」 |
| 20 | サービスをまたぐ不変条件が破れたとき、どう検出し、誰がどう謝るか | 強制できないものは、検出と謝罪を設計する [43] | 突き合わせ（照合）のバッチも、取り消しの手順も無い |

## 8. ケーススタディで測れること・測れないこと

題材 D（整合性の異常を再現）と題材 A（基盤をまたぐデータ統合）に対応。

測れること（WSL の Docker、PostgreSQL 18・CockroachDB・Kafka 4.x／Redpanda）：

- PostgreSQL 18 の Read Committed／Repeatable Read／Serializable で、更新の消失・書き込みスキュー・ファントムによる二重予約の**発生件数**（決まった順序で 2 接続を進める Hermitage 型と、並行に多数流す型の両方）
- 各手段（アトミックな更新、`SELECT ... FOR UPDATE`、バージョン列、Serializable、一意性制約・排他制約）を 1 つずつ足したときの、異常の件数・40001 の件数・再試行の回数・所要時間
- 再試行を実装しない場合に、正規の処理がどれだけ失敗として返るか（基準を厳しくした代償）
- CockroachDB の既定（SERIALIZABLE）と READ COMMITTED で同じ試験。40001 と再試行の回数
- PostgreSQL のスタンバイからの読み取りで、プライマリと違う状態が見えること（複製遅延）
- 冪等キーなし／ありで、障害を入れたときの重複件数（題材 A と共通）
- Kafka のトランザクションで書き、`read_uncommitted` と `read_committed` で読んだときの見え方の違い
- PostgreSQL の `PREPARE TRANSACTION` で準備済みのまま放置したとき、ロックが残り、他の更新が待たされること（XA の in-doubt の最小の再現）

測れないこと（未検証と明記する）：

- Oracle、SQL Server、Spanner、Aurora DSQL、DynamoDB、MongoDB、YugabyteDB の挙動（公式文書と Hermitage に基づく比較のみ）
- MySQL の REPEATABLE READ の挙動（計画の実機に MySQL は無い。足すなら Jepsen [9] の更新の消失を最小構成で再現できる）
- RDS のマルチ AZ クラスターで出た Long Fork [10]（素の PostgreSQL のストリーミング複製で同じ形が出るかは、手で順序を作れば試せる可能性があるが、再現できる保証は無い）
- 時計のずれに由来する異常、リージョンをまたぐ障害（単一ホスト）
- Jepsen のような網羅的な履歴の検査（Elle は使わない。手で作った場面と件数の集計にとどまる）
- 耐久実行の基盤（Temporal ほか）の実測。組むなら別題材
- SSI の性能の一般的な結論（同一環境内の相対比較だけ）

## 9. 未確定・要確認

1. **ISO/IEC 9075-2:2023 の条文は未確認**。ISO のページは 403。節番号（SQL-92 草案では 4.28、表 9）が現行版でどこか、既定が SERIALIZABLE という記述と「更新は失われない」という記述が残っているかは分からない
2. Berenson ほかの表 4 は、抽出結果が崩れていたので本文から組み直した。原紙と照合する
3. Adya の学位論文（G-single、G-nonadjacent の原定義）は未読。Hermitage と Jepsen のページ経由の理解
4. 要約ツール経由で読んだページの数値・版・日付は、原文で見直す：PostgreSQL 文書が 18.7 であること、MongoDB の Manual が「9.0 (Current)」であること、CockroachDB の stable が v26.4 であること、IETF 草案が -08（2026-10-22 付、2027-04-25 失効）であること、Kafka の文書が 4.4 であること、Jepsen の件数（198／9,048 など）
5. CockroachDB の READ COMMITTED が入った版（プレビュー v23.2、一般提供 v24.1 というのは記憶・要確認。v24.1 のリリースノートは長く、該当箇所まで読めなかった）。Hermitage にある「repeatable read」の行が、現行の版でどう有効になるのかも未確認
6. Spanner の repeatable read の一般提供日（2026-04-17）は、リリースノートの検索結果の抜粋で見ただけ。ページ全体は開いていない
7. Kafka：「transaction.version=2（TV2）」という機能名と、新規の 4.0 クラスタで既定で有効かどうかは、4.0 の更新ノートの要約からは確かめられなかった。KIP-890 の本文には TV2 の記述がある。KIP-939（2 相コミットへの参加。`transaction.two.phase.commit.enable` の由来と思われる）は未読
8. MySQL 9.x：9.7 の文書で既定が REPEATABLE READ であることだけ確認。Jepsen の 8.0.34 の結果が 8.4・9.x でも同じかは**一次資料に見つからなかった**
9. Oracle：/23/ の URL が /26/ に転送された。23ai の文書と文言が同じかは未確認。文書は書き込みスキューに触れていない。「Oracle の Serializable はスナップショット分離」は Hermitage と Berenson ほか・本書による
10. SQL Server の SNAPSHOT の更新競合のエラー番号（3960 は記憶・要確認）
11. MongoDB の `transactionLifetimeLimitSeconds` の既定 60 秒、`TransientTransactionError` での再試行は、読んだページに無かった（記憶・要確認）
12. Flexcoin の事故は ACIDRain 論文の引用どまり。取引所自身の発表は確認していない
13. ACIDRain の表（DB ごとに、既定と最大の分離レベルで許される異常の数）は抽出が崩れ、読めなかった
14. Azure Durable Functions のアクティビティが少なくとも 1 回であること、Temporal のアクティビティの既定の再試行方針は、読んだページに明記が無かった
15. Saltzer ほかの掲載誌・巻号、Härder・Reuter（1983）は原典未確認
16. Helland「Life beyond Distributed Transactions」は CIDR 2007 版を読んだ。ACM Queue の 2016 年の改訂版は 403 で開けなかった。差分は未確認
17. YugabyteDB の stable の版番号、Aurora DSQL の文書の日付は、ページに表示が無かった
18. 事業者自身による「分離レベルが原因」の事後報告は、**一次資料に見つからなかった**（探した範囲は ACIDRain の引用と Jepsen）

## 10. 結論（スライドに書くこと。箇条書き 15〜30 個、各項目に出典の番号）

Part 9

1. ACID の 4 文字のうち、C は DB ではなくアプリケーションが守る性質で、I は製品の既定ではシリアライザブルではない。「ACID 準拠」という表示からは保証の中身は分からない [48]
2. SQL 標準は分離レベルを 3 つの現象（P1 ダーティリード、P2 ノンリピータブルリード、P3 ファントム）で定義する。確認できたのは SQL-92 の公開草案の 4.28 節と表 9 で、現行の条文は有料のため未確認 [1][2]
3. 標準の定義には、ダーティライト、更新の消失、読み取りスキュー、書き込みスキュー、スナップショット分離が無い。Berenson ほか（1995）がこれを補い、定義の文言が 2 通りに読めることも示した [3]
4. スナップショット分離は Read Committed より強く、Repeatable Read とは比べられない。標準の表を厳密に読むと「Serializable」を名乗れてしまうが、書き込みスキューを許す [3]
5. Adya（2000）は、依存グラフの閉路（G0・G1・G2）で分離レベルを定義し直し、ロックにも楽観的方式にもマルチバージョンにも当てはまる物差しにした。Hermitage と Jepsen はこの物差しを使う [4][5][6]
6. 既定の分離レベルは製品で違う：PostgreSQL・Oracle・SQL Server は Read Committed、MySQL は REPEATABLE READ、CockroachDB と Spanner は Serializable、Aurora DSQL は Repeatable Read に固定 [11][14][16][17][18][22][26]
7. 「Repeatable Read」の中身は少なくとも 4 通りある。PostgreSQL・YugabyteDB・Spanner・Aurora DSQL ではスナップショット分離、SQL Server ではロックの保持、MySQL ではどちらでもない [5][9][11][21][22][26]
8. 「Serializable」も同じではない。PostgreSQL と CockroachDB は SSI、MySQL と SQL Server は 2 相ロック、Oracle はスナップショット分離で書き込みスキューを防がない [5][11][16][17]
9. MySQL の既定（REPEATABLE READ）は更新の消失を防がない。Hermitage、Jepsen（8.0.34）、ACIDRain の脚注が一致して示す [5][9][29]
10. 同じ名前の設定でも、DB オプションで中身が変わる。SQL Server の Read Committed は `READ_COMMITTED_SNAPSHOT` で、YugabyteDB の Read Committed は `yb_enable_read_committed_isolation` で別物になる [17][21]
11. 異常ごとに効く手段が違う。更新の消失はアトミックな更新・行ロック・バージョン列で防げるが、書き込みスキューは Serializable か前提の行のロック、「まだ無いこと」を前提にする処理は制約か Serializable でしか防げない [48][12][19]
12. Serializable（SSI）と楽観的な DB の費用は再試行。PostgreSQL・CockroachDB・Aurora DSQL は SQLSTATE 40001 を返し、トランザクション全体のやり直しを求める。再試行の実装を共通部品にする [11][18][25]
13. 再試行される処理の中に、DB の外への副作用を置かない。置くなら冪等にする [48][25]
14. 分離レベルの保証は、読み取りをレプリカに逃がすと変わる。PostgreSQL は Serializable の保護がスタンバイに及ばないと書き、RDS のマルチ AZ クラスターではスナップショット分離が崩れた [12][10]
15. 製品の「Serializable」にも不具合はあった（PostgreSQL 12.3 以前の G2-item）。大事な不変条件は自分の負荷で試験する [8]
16. 弱い分離は実害になる。EC アプリ 12 本から 22 件の脆弱性が見つかった。ただし 17 件は分離レベルではなく、トランザクションの範囲の誤り [29]
17. アプリ側の検査（バリデーション）は DB の制約の代わりにならない。Rails アプリ 67 本の調査で、トランザクションより 1 桁以上多く使われ、一部は並行実行で破れる [30]
18. 進め方：不変条件を書き出す → 制約で守れるものは制約 → 1 文の更新に直せるものは直す → 残りは Serializable（再試行つき）か明示ロック → 受け入れる異常は理由を書く [12][48]

Part 11

19. 「分散トランザクション」は 2 種類ある。同じ製品のノード間（分散 SQL の内部）は製品が原子性と分離性を受け持つ。異なる技術をまたぐもの（XA）は別物 [48][20]
20. XA・2 相コミットの弱点は、コーディネータが落ちたとき、準備済みの参加者がロックを持ったまま決められないこと。PostgreSQL は、トランザクションマネージャを書くのでなければ `PREPARE TRANSACTION` を使うなと書く [13][15][48]
21. サーガは 1987 年に、1 つの DB の中の長いトランザクションを分ける方法として提案された。最初から分離性は無く、補償が失敗したときの答えは人手だった [31]
22. サーガの費用：補償を全部書く、途中の状態が見える、取り消せない操作の置き場所を決める、参加者を冪等にする。AWS と Azure の指針はこれらを注意点として並べる（任意の推奨）[32][33][34]
23. 補償は元に戻すことではない。逆順とは限らず、失敗しうるので、記録して再開できるようにし、まず再試行、補償は最後の手段にする [34]
24. 耐久実行（Temporal、Step Functions、Durable Functions、Restate）は、調整役の状態を失わない道具。分離性は与えず、呼ばれる側の冪等性は依然として要る [44][45][46][47]
25. 冪等キーは、要求を出した端が作り、状態を変える端まで通す。保存期間、同じキーで中身が違う要求、処理中の重複の扱いを決める。Stripe は 24 時間・パラメータ不一致はエラー、DynamoDB は 10 分 [35][27]
26. `Idempotency-Key` ヘッダーの IETF の文書は草案（-08）で、RFC ではない。設計の参考にはなるが、標準として引用しない [36]
27. Kafka 4.x の既定は `enable.idempotence=true`・`acks=all`。これは 1 つのプロデューサのセッション内の重複を消すだけで、既定の配信保証は少なくとも 1 回 [37][38]
28. Kafka の「厳密に 1 回」は Kafka の中（読む・処理する・書く・オフセット）の話。外部の DB への厳密に 1 回は相手の協力が要り、公式文書は出力と一緒にオフセットを保存する方法を勧める。読む側は `read_committed` にしないと中断されたメッセージも読む [38]
29. KIP-890 は、トランザクションごとにプロデューサのエポックを上げ、遅れて届いたメッセージが次のトランザクションに紛れ込むのを防ぐ。4.0 への更新を確定すると有効になる [39][40]
30. 下の層の「1 回」は、端の重複（利用者の再操作、タイムアウト後の再試行）を消せない。重複の抑制は端から端までで設計する（Saltzer ほか）[41]
31. サービスをまたぐ不変条件は DB の制約で強制できない。1 つのサービスに寄せるか、暫定→確定／取消の手順にするか、破れることを認めて検出と謝罪を設計する（Helland）[42][43]

## 11. 出典（番号｜題名｜発行者｜版・日付｜URL｜確認の深さ）

| 番号 | 題名 | 発行者 | 版・日付 | URL | 確認の深さ |
| --- | --- | --- | --- | --- | --- |
| 1 | Database Language SQL（Proposed revised text of DIS 9075）4.28 節、表 9 | ANSI X3H2／ISO（草案の写し） | X3H2-92-154/DBL CBR-002、1992 年。**草案** | http://www.contrib.andrew.cmu.edu/~shadow/sql/sql1992.txt | 本文確認（原文。4.28 節のみ） |
| 2 | ISO/IEC 9075-2:2023 Information technology — Database languages SQL — Part 2: Foundation | ISO/IEC | 2023 年版 | https://www.iso.org/standard/76584.html | 未確認（403。条文は有料） |
| 3 | A Critique of ANSI SQL Isolation Levels | Berenson・Bernstein・Gray・Melton・E. O'Neil・P. O'Neil（Microsoft Research） | MSR-TR-95-51、1995 年 6 月。SIGMOD 95、pp.1–10 | https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-95-51.pdf | 本文確認（原文。表 4 は抽出が崩れた） |
| 4 | Generalized Isolation Level Definitions | Adya・Liskov・O'Neil | ICDE 2000（2000 年 3 月） | https://www.cs.cmu.edu/~15721-f24/papers/Generalized_Isolation_Levels_Definitions.pdf （配布元 pmg.csail.mit.edu は 403） | 本文確認（原文。5 節を中心に） |
| 5 | Hermitage: Testing transaction isolation levels（README） | Martin Kleppmann ほか | 最新コミット f029bec、2026-01-23 | https://github.com/ept/hermitage | 本文確認（原文。製品ごとの .md は未読） |
| 6 | Consistency Models | Jepsen | 日付の表示なし（2026-11-18 閲覧） | https://jepsen.io/consistency/models | 本文確認（原文。図そのものは画像で、本文の説明を読んだ） |
| 7 | Phenomena／Snapshot Isolation／Repeatable Read | Jepsen | 日付の表示なし（2026-11-18 閲覧） | https://jepsen.io/consistency/phenomena 、https://jepsen.io/consistency/models/snapshot-isolation 、https://jepsen.io/consistency/models/repeatable-read | 本文確認（原文） |
| 8 | Jepsen: PostgreSQL 12.3 | Jepsen（Kyle Kingsbury） | 2020-06-12 | https://jepsen.io/analyses/postgresql-12.3 | 本文確認（要約経由） |
| 9 | Jepsen: MySQL 8.0.34 | Jepsen（Kyle Kingsbury・Peter Alvaro） | 2023-12-19 | https://jepsen.io/analyses/mysql-8.0.34 | 本文確認（要約経由） |
| 10 | Jepsen: Amazon RDS for PostgreSQL 17.4 | Jepsen | 2025-04-29（2025-05-03 追記） | https://jepsen.io/analyses/amazon-rds-for-postgresql-17.4 | 本文確認（要約経由） |
| 11 | PostgreSQL 18 Documentation 13.2 Transaction Isolation | PostgreSQL Global Development Group | 18（表示は 18.7） | https://www.postgresql.org/docs/18/transaction-iso.html | 本文確認（要約経由） |
| 12 | PostgreSQL 18 Documentation 13.4 Data Consistency Checks at the Application Level | 同上 | 18 | https://www.postgresql.org/docs/18/applevel-consistency.html | 本文確認（要約経由） |
| 13 | PostgreSQL 18 Documentation: PREPARE TRANSACTION | 同上 | 18（表示は 18.7） | https://www.postgresql.org/docs/18/sql-prepare-transaction.html | 本文確認（要約経由） |
| 14 | MySQL Reference Manual 17.7.2.1 Transaction Isolation Levels | Oracle | 8.4。9.7 は既定の一文のみ確認（/9.6/ の URL は 9.7 の表示） | https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html | 本文確認（要約経由） |
| 15 | MySQL 8.4 Reference Manual 15.3.8.3 Restrictions on XA Transactions | Oracle | 8.4 | https://dev.mysql.com/doc/refman/8.4/en/xa-restrictions.html | 本文確認（要約経由） |
| 16 | Oracle AI Database Concepts: Data Concurrency and Consistency | Oracle | 26ai（/23/ の URL から /26/ へ転送） | https://docs.oracle.com/en/database/oracle/oracle-database/26/cncpt/data-concurrency-and-consistency.html | 本文確認（要約経由） |
| 17 | SET TRANSACTION ISOLATION LEVEL (Transact-SQL) | Microsoft | ms.date 2025-09-26、SQL Server 2017〜2025・Azure SQL Database ほか | https://learn.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver17 | 本文確認（原文） |
| 18 | Transactions | Cockroach Labs | stable＝v26.4（2026-11-18 閲覧） | https://docs.cockroachlabs.com/docs/stable/transactions | 本文確認（要約経由） |
| 19 | Read Committed Transactions | Cockroach Labs | stable＝v26.4 | https://docs.cockroachlabs.com/docs/stable/read-committed | 本文確認（要約経由） |
| 20 | Transaction Layer | Cockroach Labs | stable＝v26.4 | https://docs.cockroachlabs.com/docs/stable/architecture/transaction-layer | 本文確認（要約経由） |
| 21 | Transaction isolation levels | Yugabyte | stable（版の表示は未確認。v2025.2 への言及あり） | https://docs.yugabyte.com/stable/architecture/transactions/isolation-levels/ | 本文確認（要約経由） |
| 22 | Isolation levels overview | Google Cloud（Spanner） | 日付の表示なし（2026-11-18 閲覧） | https://docs.cloud.google.com/spanner/docs/isolation-levels | 本文確認（要約経由） |
| 23 | TrueTime and external consistency | Google Cloud（Spanner） | 日付の表示なし | https://docs.cloud.google.com/spanner/docs/true-time-external-consistency | 本文確認（要約経由） |
| 24 | Spanner release notes（2026-04-17 の項） | Google Cloud | 2026-04-17 | https://docs.cloud.google.com/spanner/docs/release-notes | 題名のみ（検索結果の抜粋で該当の項を見た） |
| 25 | Concurrency control in Aurora DSQL | AWS | 日付の表示なし（2026-11-18 閲覧） | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-concurrency-control.html | 本文確認（原文） |
| 26 | Migrating from PostgreSQL to Aurora DSQL（Considerations の節） | AWS | 日付の表示なし | https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-postgresql-compatibility-unsupported-features.html | 本文確認（原文） |
| 27 | Amazon DynamoDB Transactions: How it works | AWS | 日付の表示なし | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html | 本文確認（原文） |
| 28 | Transactions（MongoDB Manual） | MongoDB | 表示は 9.0 (Current) | https://www.mongodb.com/docs/manual/core/transactions/ | 本文確認（要約経由） |
| 29 | ACIDRain: Concurrency-Related Attacks on Database-Backed Web Applications | Warszawski・Bailis（Stanford） | SIGMOD 2017（2017-05） | http://www.bailis.org/papers/acidrain-sigmod2017.pdf | 本文確認（原文。付録の表は未読） |
| 30 | Feral Concurrency Control: An Empirical Investigation of Modern Application Integrity | Bailis・Fekete・Franklin・Ghodsi・Hellerstein・Stoica | SIGMOD 2015（2015-05/06） | http://www.bailis.org/papers/feral-sigmod2015.pdf | 本文確認（原文。要旨と 3〜4 節） |
| 31 | Sagas | Garcia-Molina・Salem（Princeton） | SIGMOD 1987 | https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf | 本文確認（原文。スキャンの OCR） |
| 32 | Saga choreography pattern／Saga orchestration pattern | AWS Prescriptive Guidance（Cloud design patterns） | 日付の表示なし（2026-11-18 閲覧）。saga.html は入門ページに転送された | https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-choreography.html 、https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html | 本文確認（原文） |
| 33 | Saga design pattern | Microsoft（Azure Architecture Center） | ms.date 2025-02-25 | https://learn.microsoft.com/en-us/azure/architecture/patterns/saga | 本文確認（原文） |
| 34 | Compensating Transaction pattern | Microsoft（Azure Architecture Center） | ms.date 2026-04-16 | https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction | 本文確認（原文） |
| 35 | Idempotent requests（API reference） | Stripe | 日付の表示なし（2026-11-18 閲覧） | https://docs.stripe.com/api/idempotent_requests | 本文確認（原文） |
| 36 | The Idempotency-Key HTTP Header Field | IETF httpapi WG（Jena・Dalal・Tishkin） | draft-ietf-httpapi-idempotency-key-header-08、2026-10-22、**草案** | https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | 本文確認（要約経由） |
| 37 | Producer Configs | Apache Kafka | 4.4 | https://kafka.apache.org/44/configuration/producer-configs/ | 本文確認（要約経由） |
| 38 | Design（Message Delivery Semantics、Using Transactions） | Apache Kafka | 4.4 | https://kafka.apache.org/44/design/design/ | 本文確認（要約経由） |
| 39 | Upgrading（4.0 の Notable changes） | Apache Kafka | 4.0 | https://kafka.apache.org/40/getting-started/upgrade/ | 本文確認（要約経由） |
| 40 | KIP-890: Transactions Server-Side Defense | Apache Kafka（Confluence） | 承認済み、最終更新 2025-02-13 | https://cwiki.apache.org/confluence/display/KAFKA/KIP-890%3A+Transactions+Server-Side+Defense | 本文確認（要約経由） |
| 41 | End-to-End Arguments in System Design | Saltzer・Reed・Clark（MIT） | ACM TOCS、1984 年（巻号は記憶・要確認） | https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf | 本文確認（原文） |
| 42 | Life beyond Distributed Transactions: an Apostate's Opinion | Pat Helland | CIDR 2007 | https://www.cidrdb.org/cidr2007/papers/cidr07p15.pdf | 本文確認（原文。ACM Queue 2016 年版は 403） |
| 43 | Building on Quicksand | Pat Helland・David Campbell | CIDR 2009、arXiv:0909.1788（2009-09-09） | https://arxiv.org/abs/0909.1788 | 本文確認（原文） |
| 44 | Workflow Execution／Activities | Temporal Technologies | 日付の表示なし（2026-11-18 閲覧） | https://docs.temporal.io/workflow-execution 、https://docs.temporal.io/activities | 本文確認（要約経由） |
| 45 | Choosing workflow type in Step Functions | AWS | 日付の表示なし | https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html | 本文確認（原文） |
| 46 | Durable Orchestrations Overview | Microsoft | ms.date 2026-04-22 | https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-orchestrations | 本文確認（原文） |
| 47 | Durable Execution（Concepts） | Restate | 日付の表示なし | https://docs.restate.dev/concepts/durable_execution | 本文確認（要約経由） |
| 48 | データ指向アプリケーションデザイン 第2版 8 章（8.1.1、8.2〜8.5） | Kleppmann・Riccomini 著、斉藤太郎 訳、オライリー・ジャパン | ISBN 978-4-8144-0180-2。p.271–332 | （書籍。対応表は research/books/notes/_parts/ch08.md） | 対応表経由（担当の読書ノート。本文は直接読んでいない） |
