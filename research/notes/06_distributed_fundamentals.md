# 06 分散システムの基礎と合意（何が信用できないか、線形化可能性の代償、合意が要る場面と要らない場面）

調査日：2026-11-18

出典は末尾の番号 [n] で示す。「記憶・要確認」と付けた記述は、今回の調査で本文を開いて確かめていない。

## 1. 問い（このノートが答えること。対応する Part）

対応する Part：10（基礎：分散システムでは何が信用できないか）、14 の一部（調整サービスが単一障害点になる型）。DDIA 2e では 9 章（p.359–）と 10 章（p.415–）に当たる [50]。

答える問い：

1. ネットワーク・時計・プロセスの停止の 3 つについて、「信用できない」とは具体的に何が起きることか。数字で言えるか
2. 線形化可能性とは何で、直列化可能性と何が違い、得るために何を払うか。CAP 定理は正確には何を言っているか
3. 合意（コンセンサス）が要るのはどの場面で、要らないのはどの場面か
4. ZooKeeper・etcd・Consul のような調整サービスは何を引き受け、どう全体を止めるか
5. ID の生成（UUIDv4・UUIDv7・Snowflake 方式・連番）は何を選ぶと何を失うか
6. 分散システムの正しさは、どんな手法で確かめられているか
7. テックリーダーは合意の理論をどこまで知れば、製品の選定とレビューができるか

## 2. 標準・定義（節番号）

### 2.1 部分障害と故障の種類

- **部分障害**：一部だけが壊れ、残りは動いている状態。壊れたのか遅いだけなのかを、相手からは区別できない（DDIA 9.1、p.359）[50]
- **gray failure**：Huang ほか（HotOS 2017）は、現れ方が微妙で、素早く確定的に検知できない部品の故障を指してこう呼ぶ。例は深刻な性能低下、散発的なパケット損失、不安定な I/O など（§1）。中心の性質は differential observability で、障害の影響を受ける側（アプリ）と、検知・復旧を担う側（障害検知器）とで見え方が違うこと（§1・§3.2）。要求処理は詰まっているのにハートビートは返る、という例を挙げる（§1）[2]
- **metastable failure**：Bronson ほか（HotOS 2021）の定義。きっかけ（trigger）で悪い状態に入り、**きっかけを取り除いても悪い状態が続く**障害。有効な処理量（goodput）が使えないほど低くなり、それを維持する仕組み（sustaining effect。多くは作業の増幅）がある。状態は stable → vulnerable → metastable の 3 つ。根本原因はきっかけではなく、維持する側の帰還ループだとする（§1・§2・§3）。抜け出すには、再起動や負荷の大幅な削減のような強い修正が要る（§1）[3]

### 2.2 時計

- **NTP の精度**：RFC 5905（NTPv4、2010-06）§1 は、一次サーバーで数十マイクロ秒、高速な LAN 上の二次サーバーとクライアントで数百マイクロ秒、ポーリング間隔が最長 36 時間の場合は数十ミリ秒としている。条件つきの値であり、保証ではない [9]
- **うるう秒**：RFC 5905 §7.3 の Leap Indicator が、月の最終分が 61 秒か 59 秒かを予告する [9]。Google は 24 時間（UTC の正午から正午）の線形の smear を提案・運用しており、その間の進み方の変化は約 11.6 ppm [12]。AWS は NTP 経路では smear し、PTP ハードウェアクロックは smear しないため、smear するものとしないものを混ぜるなと書いている。第 27 回国際度量衡総会の決議 4 は 2035 年までにうるう秒を廃止する方針 [10]
- **単調時計と実時間時計**：実時間時計（wall-clock）は NTP の補正やうるう秒で飛ぶ・戻ることがある。経過時間は単調時計で測る（DDIA 9.3.1、p.373）[50]。OS・言語ごとの API 名（`CLOCK_MONOTONIC` など）は記憶・要確認
- **TrueTime**：Spanner 論文（OSDI 2012）§3。`TT.now()` は時刻の点ではなく区間 [earliest, latest] を返す。誤差の幅 ε は、ポーリング間隔 30 秒・想定ドリフト 200 マイクロ秒/秒のもとで、約 1〜7 ms の鋸歯状、平均 4 ms（論文執筆時点の本番値）。時刻の源は GPS と原子時計。書き込みは、区間が過ぎるまで待つ commit wait（§4.1.2）で、タイムスタンプの順序と実時間の順序を一致させる。評価の節では、時計の不良より CPU の不良のほうが 6 倍多いと報告している [5]
- **ハイブリッド論理時計（HLC）**：Kulkarni ほか（2014、Buffalo 大学 Tech Report 2014-04）。論理時計の因果の性質を保ちつつ、値を物理時計（NTP）の近くに保ち、64 ビットの NTP タイムスタンプの形に収める。TrueTime のような専用ハードウェアや待ちを要らなくする提案 [8]
- **LWW（last write wins）**：タイムスタンプの大きい書き込みを勝ちとする解決。時計がずれると、後から行った書き込みが黙って捨てられる（DDIA 9.3.3、p.376）[50]

### 2.3 プロセスの停止、リース、フェンシングトークン

- プロセスは GC・VM の一時停止・ディスク待ちなどで任意の時点で止まりうる。止まっていた本人は気づかない（DDIA 9.3.4、p.380）[50]
- **リース**：期限つきのロック。持ち主が止まっているあいだに期限が切れ、別の持ち主が現れることがある
- **フェンシングトークン**：Kleppmann（2016-02-08）の定義。ロックを取るたびにロックサービスが増やす番号。クライアントは書き込みに番号を付け、**資源の側**が、これまでに見た最大より小さい番号の書き込みを拒む。期限の確認と書き込みのあいだで止まりうるので、クライアント側の確認だけでは防げない [14]。先行例として、Chubby 論文（OSDI 2006）§2.4 の sequencer がある [44]
- Kleppmann は、ロックの目的を「効率」（重複した作業を避ける）と「正しさ」（同時の更新による破損を防ぐ）に分け、後者には合意に基づく仕組みとフェンシングが要るとした [14]

### 2.4 線形化可能性、直列化可能性

- **線形化可能性（linearizability）**：Herlihy・Wing（ACM TOPLAS 12(3)、1990）。並行する各操作が、呼び出しから応答までのあいだのどこか 1 点で瞬時に効いたように見えること（要旨）。局所的（オブジェクトごとに成り立てば全体でも成り立つ）で、非ブロッキングな性質（§3）。論文自身が、線形化可能性は「トランザクションを 1 つのオブジェクトへの 1 つの操作に限った、厳密な直列化可能性の特別な場合」と見なせると書いている（§3.3 付近。節番号は要確認）[18]
- **直列化可能性（serializability）**：複数の操作をまとめたトランザクションが、何らかの直列の順で実行したのと同じ結果になること。実時間の順序は問わない。両方を満たすのが厳密な直列化可能性（strict serializability）[18]
- 使い分け：線形化可能性は「1 つの値について、最新を読めるか」（新しさの保証）。直列化可能性は「複数の値をまたぐトランザクションが互いに干渉しないか」（分離の保証）。Part 9 の分離レベルは後者、この Part は前者

### 2.5 CAP 定理、PACELC、HAT、CALM、CRDT

- **CAP 定理**：Gilbert・Lynch（ACM SIGACT News 33(2)、2002）。定義は §2：一貫性は atomic（＝線形化可能）なデータオブジェクト（§2.1）、可用性は「故障していないノードが受け取ったすべての要求が応答を返す」こと（§2.2）、分断耐性はノード間のメッセージが任意に失われても成り立つこと（§2.3）。定理 1（§3.1）：非同期ネットワークでは、この 3 つを全実行で満たす読み書きオブジェクトは実装できない。部分同期モデルでも同じ不可能性（定理 2、§4.2）。弱めた一貫性（Delayed-t）なら達成できる（§4.4）[19]
- **CAP の誤用**（論文の定義から言えること）：
  - C は線形化可能性であり、ACID の C でも「整合性一般」でもない [19]
  - A は「故障していない全ノードが必ず応答する」という強い性質で、稼働率（SLA の可用性）ではない [19]
  - 定理が語るのは分断が起きているあいだの選択。「3 つから 2 つ選ぶ」ではない。Abadi も、分断がないときまで一貫性を捨てる理由に CAP を使うのは誤りだと指摘している [20]
  - 遅延については何も言わない [20]
- **PACELC**：Abadi（IEEE Computer 45(2)、2012）。分断（P）があれば可用性（A）と一貫性（C）、なければ（E）遅延（L）と一貫性（C）の選択になる。複製をした時点で一貫性と遅延の取引が生じ、WAN 越しでは避けられないとする [20]。個別製品の分類（Dynamo・Cassandra・Riak が PA/EL など）は論文中にあるが、今回は表まで確かめていない（記憶・要確認）
- **HAT（Highly Available Transactions）**：Bailis ほか（PVLDB 7(3)、VLDB 2014 発表）。表 3 が、分断中も達成できる保証を 3 つに分ける [21]

| 区分 | 保証 |
| --- | --- |
| 高可用（どのノードでも応答できる） | Read Uncommitted、Read Committed、Monotonic Atomic View、Item／Predicate Cut Isolation、Writes Follow Reads、Monotonic Reads、Monotonic Writes |
| sticky 可用（同じノードにつながり続ければ可） | Read Your Writes、PRAM、Causal |
| 達成不能 | Cursor Stability、Snapshot Isolation、Repeatable Read、One-Copy Serializability、Recency、Safe、Regular、Linearizability、Strong 1SR |

  達成不能の理由は 3 つ：更新の消失を防ぐ、書き込みスキューを防ぐ、新しさを保証する（§5.2）。同論文は、調べた 18 の DB のうち既定で直列化可能だったのは 3 つだけと報告している（2013 年時点、表 2）[21]
- **CALM 定理**：Hellerstein・Alvaro（arXiv 1901.01930、のち CACM 2020）。定理 1：プログラムが「一貫していて、調整のいらない分散実装」を持つのは、単調（入力が増えても、出した結論を取り消さない）であるとき、かつそのときに限る。CAP が「いつ無理か」を言うのに対し、CALM は「何なら調整なしでできるか」を言う [22]
- **CRDT**：調整なしでどのレプリカも更新でき、同じ更新の集合を受け取ったレプリカは決定的に同じ状態に収束するデータ型（Preguiça・Baquero・Shapiro、arXiv 1805.06358 の要旨）[24]。原典は Shapiro ほか（SSS 2011）で、強い結果整合性（Strong Eventual Consistency）を定義したとされるが、本文は今回開けなかった（題名のみ）[23]。位置づけ：CALM の「単調なら調整不要」を、データ型の形で使えるようにしたもの。一意性制約や残高の下限のような非単調な不変条件は守れない

### 2.6 合意

- **FLP**：Fischer・Lynch・Paterson（JACM 32(2)、1985）。完全に非同期なシステムでは、故障するプロセスが 1 つでもあれば、必ず停止する合意プロトコルは存在しない（定理 1）[25]。実用のアルゴリズムは、タイムアウト（部分同期の仮定）や乱択で「安全性は常に守り、進行は状況がよいときだけ」とする
- **Paxos**：Lamport「Paxos Made Simple」（2001）。proposer・acceptor・learner の役割と、**過半数**の acceptor による受理。任意の 2 つの過半数は必ず 1 つを共有する、が安全性の核（§2）。状態機械の複製への適用は §3 [26]
- **Raft**：Ongaro・Ousterhout（USENIX ATC 2014 の拡張版）[27]
  - リーダー選出（§5.2）：フォロワーは election timeout のあいだ連絡がなければ候補になり、**クラスタ全体の過半数**の票で、その任期（term）のリーダーになる。任期ごとにリーダーは高々 1 つ（Election Safety）。票割れは、乱数で散らした election timeout で避ける
  - コミット（§5.3・§5.4）：過半数に複製されたエントリがコミットされる。新しいリーダーは、コミット済みのエントリをすべて持つ（Leader Completeness）
  - 時間の条件（§5.6）：broadcastTime ≪ electionTimeout ≪ MTBF。論文は election timeout を 10〜500 ms の範囲と見込み、評価（§9.3）では 150〜300 ms を使っている。**安全性はタイミングに依存しないが、可用性は依存する**
  - メンバー変更（§6）：旧構成と新構成の両方の過半数を要する joint consensus を経由する 2 段階。直接切り替えると、同じ任期に 2 つのリーダーが生じうる
  - 読み取り（§8）：線形化可能な読み取りには、リーダーが任期の最初に no-op をコミットし、応答の前に過半数とハートビートを交わす必要がある。リースで省く方法は「安全性をタイミングに頼る」と明記している
- **Viewstamped Replication**：Liskov・Cowling「Viewstamped Replication Revisited」（MIT-CSAIL-TR-2012-021、2012-07-23）。クラッシュ故障を扱う複製の手法で、要求の処理、レプリカ故障時の再編成、復帰、構成変更（メンバーと許容故障数の変更）を述べる（要旨のみ確認）[28]
- **全順序ブロードキャストとの等価性**：Chandra・Toueg（JACM 43(2)、1996）は、クラッシュ故障のある非同期システムで、合意と atomic broadcast（全順序ブロードキャスト）が互いに帰着できる（等価である）ことを示した [29]。つまり「全員が同じ順序のログを持つ」ことと「1 つの値に合意する」ことは同じ難しさ
- **合意が要る場面**（DDIA 10.1.2 p.423、10.3.1 p.441）[50]：リーダー選出（リーダーは 1 つ）、一意性制約（同じ名前・同じ席を 2 人に与えない）、アトミックコミット（全員がコミットか全員が中断か）、ロックとリース、線形化可能な compare-and-set、全順序のログ
- **合意が要らない場面**：単調な計算（集合への追加、カウンタの加算、最大値）、CRDT で表せる状態、HAT の表で高可用に分類される保証、冪等な再試行で足りる処理 [21][22]

### 2.7 ID の生成（RFC 9562）

RFC 9562（2024-05、Standards Track、RFC 4122 を廃止）[37]：

| 節 | 内容 |
| --- | --- |
| §2.1 | 見直しの動機。DB のキーとして使われるようになり、時刻順でない版（UUIDv4 など）は索引の局所性が悪い |
| §5.4 | UUIDv4。乱数 122 ビット |
| §5.7 | UUIDv7。先頭 48 ビットが Unix 時刻（ミリ秒）、rand_a 12 ビット、rand_b 62 ビット。可能なら UUIDv1・v6 より v7 を使うべき（SHOULD） |
| §6.2 | 単調性とカウンタ。3 つの方法（固定長の専用カウンタ／単調な乱数／乱数の左側をより細かい時刻に置き換える） |
| §6.9 | 推測されにくさ。CSPRNG を使うべき（SHOULD） |
| §6.11 | 並べ替え。v6・v7 はバイト列のまま並べ替えられる |
| §6.13 | DB での扱い。128 ビットのバイナリで格納すべき（SHOULD） |
| §8 | セキュリティ。UUID を推測困難と仮定するな、権限の証（capability）として使うな（MUST NOT）。埋め込んだ時刻は生成の順序を示す |

## 3. 製品ごとの違い（表。公式文書の URL・版・日付）

### 3.1 時計の扱い

| 製品 | 時計に何を仮定するか | ずれたときの挙動 | 出典（版・日付） |
| --- | --- | --- | --- |
| Spanner | TrueTime が誤差の上限つきの区間を返す | 誤差が大きければ、その分だけ待って遅くなる（commit wait） | 論文 OSDI 2012 §3・§4.1.2 [5]。現行の公式文書は外部整合性（external consistency）を定義するが、誤差の数値は載せていない（ページの日付なし）[6] |
| CockroachDB v26.4 | HLC ＋ `--max-offset`（既定 **500ms**）。新規のマルチリージョンでは 250ms を推奨 | 自ノードの時計が、ほかのノードの半数以上と比べて max-offset の 80% を超えてずれていると検知すると、ノードが自分で停止する。上限内のずれなら SERIALIZABLE は保たれるが、上限を超えると「因果関係のあるトランザクション間の単一キーの線形化可能性」が破れうる。不確かさの区間内の値を読むと再試行（`ReadWithinUncertaintyIntervalError`）| Operational FAQs、`cockroach start`、Transaction Layer（いずれも v26.4。ページの日付なし）[15][16][17] |
| AWS（EC2） | Amazon Time Sync Service。衛星接続と原子時計の基準時計。NTP は 169.254.169.123 | ベンダーの自己申告：NTP 経由で誤差の上限がふつう 100 マイクロ秒未満、PTP ハードウェアクロック経由で 40 マイクロ秒未満（対応インスタンス。2023-11-16 のブログ）。それ以前は 1 ミリ秒 | EC2 User Guide [10]、AWS Compute Blog [11] |
| ClockBound（AWS、OSS） | デーモンが時計の誤差の上限を計算し、ライブラリが `now()` で earliest／latest の区間を返す | 誤差の上限＝|ローカルのずれ|＋root dispersion＋root delay/2（最悪値）。同期の状態（同期中・自走）も返す | GitHub README（例は 3.0.0-rc.0）[13] |
| Cassandra 5.0 | すべての変更にタイムスタンプを付け、列ごとに LWW で解決。タイムスタンプはクライアント、なければコーディネータの時計 | 公式文書は「正しさはこれらの時計に依存する」と明記し、NTP などの同期を勧める | Dynamo のページ（5.0、プレリリース版の表示）[45] |
| TigerBeetle | 同期した時計に依存しない。リーダーリースを使わない。クラスタ内の時計を合成した cluster time | — | 公式文書 Safety（自己申告）[41] |

注：CockroachDB の文書は、同じ挙動を FAQ では「shuts down」、`cockroach start` と Transaction Layer では「crash」と書いている。また FAQ の別の節は「平均のずれが 80% を超える」と表現しており、判定の正確な条件は文書間で揺れている [15][16][17]。

### 3.2 調整サービス

| 項目 | ZooKeeper 3.9 | etcd v3.6 | Consul |
| --- | --- | --- | --- |
| 合意の方式 | Zab（記憶・要確認） | Raft | Raft（サーバーノードのみが参加） |
| 役割 | 設定、グループ管理、リーダー選出、ロックの部品（エフェメラルノード、セッション） | KV、watch、リース。Kubernetes の状態の保存先（記憶・要確認） | サービスディスカバリ、ヘルスチェック、セッションロック、KV |
| 過半数と耐故障 | — | 3 台で 1 台、5 台で 2 台、7 台で 3 台の故障に耐える。偶数は耐故障が増えない。7 台を超えない | 同じ表。本番は 3 台か 5 台を推奨 |
| 読み取りの保証 | 保証は順序一貫性・アトミック性・単一のシステムイメージ・信頼性・適時性。**クライアント間で同時に同じ値が見えることは保証しない**。最新が要るなら読む前に `sync()` | 既定で厳密に直列化可能（Jepsen 3.4.3 の検証）。`serializable` オプションで古い読み取りを許す | 整合性モードがある（default・consistent・stale の中身は記憶・要確認） |
| 過半数を失うと | — | 分断が直り過半数が戻れば自動で再開。遅いディスクのリーダーはコミットできず、選出がやり直される | 新しいログをコミットできず使えなくなる。復旧にはふつう手作業が要る |
| 制限 | セッションのタイムアウトは tickTime の 2〜20 倍 | 保存容量の既定は 2GB、通常の上限の目安は 8GB。リージョンをまたぐ場合は heartbeat を往復時間に合わせ、election timeout をその 5 倍以上に | — |
| 出典 | Programmer's Guide（3.9）[32]、論文 USENIX ATC 2010 [33] | FAQ（v3.6）[30]、Jepsen 3.4.3（2020-01-30）[31] | Consensus（ページの版・日付は未取得）[34] |

- ZooKeeper の論文は、全操作のクライアントごとの FIFO 順と、書き込みの線形化可能性を保証すると述べる。読み取りは線形化可能ではない [33]
- **etcd のロックは相互排他を保証しない**（Jepsen、etcd 3.4.3、2020-01-30）。リースの TTL が 2 秒でプロセスの一時停止を入れた試験では、確認応答済みの更新の約 18% が失われた。報告は、ロックのキーの revision をフェンシングトークンに使い、資源の側で検査することを勧めている [31]
- **Redlock**：Redis の公式文書は今も Redlock を載せつつ、末尾の注意書きで「一貫性と正しさを気にするならフェンシングトークンを実装すべき」「Redis は TTL に単調時計を使っておらず、実時間時計のずれで複数のプロセスがロックを取りうる」と明記し、Kleppmann の分析と antirez の反論の両方にリンクしている（ページの日付なし。Redis 8.4 の `DELEX` に言及）[35]

### 3.3 ID の生成

| 方式 | 構成 | 製品での有無 | 出典 |
| --- | --- | --- | --- |
| UUIDv4 | 乱数 122 ビット | PostgreSQL 18：`gen_random_uuid()`、`uuidv4()`。CockroachDB v26.4：UUIDv4 を「強く推奨」（`gen_random_uuid()`）。ほかの UUID の型は「ほぼ未検証」と書く | [37][38][39] |
| UUIDv7 | Unix 時刻 48 ビット（ミリ秒）＋乱数 74 ビット | **PostgreSQL 18 に `uuidv7([shift interval])` がある**。ミリ秒の時刻＋ミリ秒未満の時刻＋乱数で作る（RFC 9562 §6.2 の方法 3 に当たる）。`uuid_extract_timestamp()` で時刻を取り出せる（v1 と v7）。単調性の保証の範囲は、このページには書かれていない。CockroachDB v26.4 の UUID のページに v7 の記載はない | [37][38][39] |
| Snowflake 方式 | 64 ビット：時刻 41 ビット（ミリ秒、独自の起点で 69 年）＋マシン ID 10 ビット（1024 台）＋連番 12 ビット（ミリ秒あたり 4096） | Twitter の Snowflake（2010）。要件は「調整なし」「おおよそ時刻順（k-sorted）」「64 ビット以内」。時計が戻ったら、最後に発番した時刻を過ぎるまで発番を拒む。NTP を前提にする | README（2010 年版）[40] |
| 類似：`unique_rowid()` | 挿入を実行したノードの時刻とノード ID | CockroachDB v26.4。時刻順で、同じ範囲に固まる。順序は完全には保証されない | [39] |
| 連番（sequence） | 単一の発番元 | 厳密な順序が要るなら、発番元は 1 つ（＝線形化可能な発番器）になる（DDIA 10.2.2、p.437）| [50] |

## 4. 事故・失敗例（一次報告）

### 4.1 調整サービス・制御プレーンが全体を止めた

| 事故 | 何が起きたか | 型 | 出典 |
| --- | --- | --- | --- |
| Roblox、2021-10-28〜31（73 時間）| 1 つの Consul クラスタ（投票権あり 5、なし 5）が全バックエンドを支えていた。ストリーミング機能の有効化による競合と、Raft ログの保存先（BoltDB）の性能問題が重なり、Consul が不調に。Nomad と Vault が Consul に依存していたため、サービスの発見・コンテナの配置・秘密情報の取得が止まった。**監視も Consul に依存する循環**があり、原因の特定が遅れた。データの損失はない | 1 つの調整サービスに全部を載せた。監視が監視対象に依存した | 事後報告 2022-01-20 [46] |
| Cloudflare、2020-11-02（6 時間 33 分）| ネットワークスイッチが**部分的に動く**状態になった（ping には応答しないが LACP と BGP は生きている）。そのラックにいた etcd の 1 ノードはリーダーと話せず、ほかのノードとは話せたため、選挙を繰り返し始め、リーダーが決まらず etcd が読み取り専用になった。スイッチ自体は 6 分で回復。しかし etcd で主系の健全性を確かめられなかった 2 つの DB クラスタが自動で昇格し、昇格後に全レプリカの作り直しが必要になる欠陥のため、認証用 DB が過負荷になった。API の成功率は最低 75%、ダッシュボードは最大 80 倍遅くなった | gray failure ＋ 合意の進行不能 ＋ 自動フェイルオーバーの連鎖 | 事後報告（2020-11-27）[47] |
| OpenAI、2024-12-11（4 時間 22 分）| 新しいテレメトリのサービスが全ノードから Kubernetes API に重い操作を出し、制御プレーンが過負荷に。データプレーンは DNS によるサービスの発見で制御プレーンに依存しており、DNS のキャッシュが切れた約 20 分後から障害が広がった。制御プレーンに入れず、原因のサービスを消せなかった | データプレーンが制御プレーンに依存。復旧手段が壊れた基盤に載っていた | 事後報告 2024-12-13 [48] |

- Cloudflare の報告は、この障害を当初ビザンチン障害と呼んだが、追記で、コミュニティはこれを omission fault（脱落故障）と見ており BFT は要らない、と補っている [47]
- 3 件に共通するのは、**合意そのものが間違った答えを出したのではなく、合意が進まなくなった（可用性を失った）ときに、それに頼る側の作りが被害を決めた**こと

### 4.2 ネットワーク

Bailis・Kingsbury「The Network is Reliable」（ACM Queue 12(7)、2014）が引く数字 [1]：

- Microsoft のデータセンターの調査：平均で 1 日あたり装置 5.2 台・リンク 40.8 本が故障。修復までの中央値は約 5 分。故障 1 回あたりのパケット損失の中央値は 59,000。**冗長化で改善するのは、通信量の中央値で 43% だけ**
- Google Chubby：700 日で 61 回の停止。30 秒を超えた 9 回のうち 4 回はネットワークの保守が原因（残りの内訳は今回の抽出で確認できず）
- CENIC（広域網）の 5 年間：分断の平均は、ソフトウェア起因で 6 分、ハードウェア起因で 8.2 時間超
- NIC やドライバの不良、スイッチの split-brain、片方向だけ通る障害など、多数の公開事例を列挙

### 4.3 時計

- Cloudflare、2017-01-01 00:00 UTC（うるう秒）：DNS のソフトウェアが「時間は戻らない」と仮定し、Go の `time.Now()` の差で応答時間を測っていた。差が負になり、重みつき選択の乱数関数が負の引数でパニック。ピーク時に DNS の問い合わせの約 0.2%、HTTP の 1% 未満が失敗し、影響は 06:45 UTC まで続いた [49]
- 教訓：経過時間を実時間時計の差で測らない。うるう秒の扱い（smear するかどうか）をクラスタ内でそろえる [10][15]

### 4.4 metastable failure と再試行

Huang ほか（OSDI 2022）[4]：

- 11 の組織の 22 件を分析。過去 10 年の AWS の大きな障害 15 件のうち少なくとも 4 件が metastable
- 維持の仕組みで最も多いのは**再試行**で、50% を超える事例に関わる
- 障害の長さは 1.5〜73.53 時間。期間を報告した事例では 4〜10 時間が最多（35%）
- 回復には負荷の削減が要ることが多く、直接の負荷制限（スロットリング、要求の破棄など）が 55% 超の事例で使われた
- 負荷の急増がきっかけの事例は約 35%。きっかけが複数ある事例は 45%

### 4.5 エラー処理

Yuan ほか（OSDI 2014）。Cassandra・HBase・HDFS・Hadoop MapReduce・Redis の、利用者が報告した障害 198 件（うち壊滅的な障害 48 件）[36]：

| 数字 | 何の割合か |
| --- | --- |
| 92% | 壊滅的な障害のうち、ソフトウェアが明示的に通知した**致命的でないエラーの処理の誤り**が原因のもの（Finding 10）|
| 58% | 壊滅的な障害のうち、エラー処理コードの単純なテストで見つけられたもの |
| 35% | 壊滅的な障害のうち、エラー処理が 3 つの自明な型（握りつぶす・ログだけ、過剰な捕捉で中断、TODO のまま）に当たるもの（Finding 11。3 つ目の型は記憶・要確認）|
| 98% | 全障害のうち、3 ノード以下で再現できるもの（Finding 3）|
| 77% | 全障害のうち、単体テストで再現できるもの（Finding 9）。再現に 2 つ以上の入力イベントが要るものも 77%（Finding 1）|
| 74% | 全障害のうち、決定的なもの（Finding 4）|

静的検査ツール Aspirator は、9 つの分散システムで 143 件のバグと悪い実践を見つけた [36]。

### 4.6 ロック

- Redlock 論争（2016-02）：Kleppmann は、Redlock が時計・ネットワーク遅延・プロセス停止の上限という同期的な仮定に安全性を頼り、フェンシングトークンを作れないと批判した。推奨は、効率が目的なら単一の Redis、正しさが目的なら合意に基づく仕組み（ZooKeeper など）か堅いトランザクションを持つ DB ＋フェンシング [14]。antirez は、資源の側がトークンを検査できるならそもそも強いロックは要らないはずだと反論し、絶対時刻ではなく経過の速さだけを仮定していると主張した。単調時計を使うべき点は認めた [51]
- 位置づけ：論争の決着は、Redis の公式文書の注意書き（フェンシングを実装せよ、単調時計を使っていない）に反映されている [35]。Jepsen の etcd の検証は、合意に基づくサービスの上のロックであっても、リースである限り同じ問題が残ることを示した [31]。つまり**「どのロックサービスが安全か」ではなく「資源の側で古い持ち主を拒めるか」が問い**

## 5. 権威の推奨と位置づけ（規範か任意か）

| 出どころ | 推奨 | 位置づけ |
| --- | --- | --- |
| Google SRE 本 23 章 [42] | リーダー選出・重要な共有状態・分散ロックには、形式的に証明され十分に試験された合意のシステムを使う。ハートビートとタイムアウトの手作りは split-brain を招く。ロックは期限つきのリースにする。タイムスタンプは時計が同期している保証がないので問題が多い。レプリカは多くの場合 5（保守中の 1 台＋予期しない 1 台に耐える）。監視：メンバー数と健全性、遅れているレプリカ、リーダーの有無、リーダー交代の頻度、合意済みの番号が進んでいるか、提案の遅延 | 任意（Google の実践の共有）|
| AWS Well-Architected 信頼性の柱 REL05-BP05 [43] | 接続と要求の両方にタイムアウトを設定し、体系的に確かめ、既定値に頼らない。未実施の場合のリスクは「高」。高すぎる値は資源を浪費し、低すぎる値は再試行で負荷を増やし全面停止に至りうる | 任意（自己評価の枠組み）。このページは「歴史的な参照用」と表示されており、最新は Framework 本体を見るよう案内がある |
| Amazon Builders' Library「Timeouts, retries, and backoff with jitter」（2019-12-05）[52] | タイムアウトは、許容する誤タイムアウト率（例 0.1%）を決め、相手の遅延の対応するパーセンタイル（例 p99.9）から決める。5 層の呼び出しで各層が 3 回試行すると最下層の負荷は 243 倍。再試行は 1 か所で行い、トークンバケットで抑える。バックオフには jitter を入れる。副作用のある API は冪等にする | 任意（Amazon の実践。著者個人の見解との注記あり）|
| Amazon Builders' Library「Leader election in distributed systems」（2019-12-05）[53] | リーダーは単一の障害点・拡張の限界点・信頼の集中点になる。リースは実時間の同期ではなく、手元の経過時間だけに頼る。残り時間を副作用の直前に確かめる。GC の停止や遅いネットワークを見込む。リースのハートビートを別スレッドで行わない。冪等性で、新しいリーダーがやり直せるようにする。TLA+ などで検証する | 任意 |
| RFC 9562 [37] | §5.7・§6.9・§6.13・§8 の SHOULD／MUST NOT（2.7 節）| 規範（IETF Standards Track）。ただし UUID を採用するかどうか自体は任意 |
| Raft 論文 §5.6・§8 [27] | 時間の条件、読み取りの扱い | 論文（規範ではない）。各実装が従うかどうかは製品の文書で確かめる |
| Jepsen [31][54] | ロックを安全性の根拠にしない。資源の側で検査する。「バグの存在は示せるが、不在は示せない」 | 第三者の検証報告。対象の版に限る |

## 6. 設計判断の分かれ目（何を選ぶと何を得て何を失うか。表）

### 6.1 一貫性の水準

| 選択 | 得るもの | 失うもの | 向く場面 |
| --- | --- | --- | --- |
| 線形化可能（合意または単一リーダー＋同期）| 最新を読める。一意性制約・ロック・リーダー選出が正しく作れる | 分断中、少数側は応答できない [19]。分断がなくても遅延が増える（過半数への往復、WAN ではリージョン間の往復）[20][21] | 残高、在庫の引当、一意な名前、リーダーの決定 |
| 直列化可能だが線形化可能とは限らない | トランザクションの分離 | 時計のずれなどで、実時間の順序と食い違う読み取りがありうる [15] | CockroachDB の既定の位置（上限内の時計のずれが前提）|
| 因果・read-your-writes（sticky）| 分断中も、同じノードにつながる限り応答できる [21] | 別のクライアントの最新は見えない。一意性は守れない | セッション内の表示、下書き、コメント |
| 結果整合＋ CRDT | どのレプリカでも書ける。調整の遅延がない [22][24] | 非単調な不変条件（下限、一意性）は守れない。削除の扱いが難しい [22] | 共同編集、カウンタ、いいね、カートへの追加 |
| 結果整合＋ LWW | 実装が単純 | 時計のずれで、確認応答済みの書き込みが黙って消える [45][50] | 失ってよいデータ、または書き手が 1 つのキー |

### 6.2 時計に頼るか

| 選択 | 得るもの | 失うもの |
| --- | --- | --- |
| 誤差の上限つきの時計（TrueTime、ClockBound）＋待ち | 実時間と整合する順序。合意なしのスナップショット読み取り | 誤差の分だけ書き込みが待つ。基盤（GPS・原子時計・PTP）への依存 [5][11] |
| HLC ＋ max-offset | 専用ハードウェアなし | 上限を超えるずれで保証が崩れる。超えたノードを止める運用。VM の移動で一時的に古い時計になる例が文書にある [15] |
| 論理時計・バージョンベクタ | 時計に頼らない因果の順序 | 実時間との対応がない。メタデータが増える [8] |
| 実時間のタイムスタンプで順序づけ（LWW）| 単純 | 6.1 の最終行 |

### 6.3 排他の作り方

| 選択 | 得るもの | 失うもの |
| --- | --- | --- |
| DB の一意制約・条件つき書き込み（CAS）| 資源の側で直接守る。ロックサービス不要 | 資源が条件つき書き込みを持つ必要がある |
| リース＋フェンシングトークン | 持ち主が止まっても、古い書き込みを資源が拒む [14][31] | 資源の側にトークンの検査を実装する必要がある。外部 API など検査できない資源には使えない |
| リースのみ（Redlock、etcd lock を含む）| 重複した作業を**減らす**（効率）| 相互排他は保証されない。正しさの根拠にできない [14][31][35] |

### 6.4 調整サービスへの依存

| 選択 | 得るもの | 失うもの |
| --- | --- | --- |
| 全サービスが 1 つの調整サービスに依存 | 運用が 1 つ | そこが止まると全部が止まる。影響範囲が最大（Roblox）[46] |
| 用途ごと・重要度ごとにクラスタを分ける | 影響範囲を区切る | 運用の数が増える [46] |
| データプレーンが最後に得た情報で動き続ける（静的な安定性）| 調整サービスが止まっても、既存の処理は続く | 変更は反映されない。古い情報で動く危険の評価が要る [48] |
| 調整サービスの健全性を自動フェイルオーバーの判断に使う | 人手なしの切り替え | 調整サービスの不調が、健全な DB の不要な昇格を引き起こす（Cloudflare）[47] |

### 6.5 ID の方式

| 方式 | 索引の局所性（B ツリー）| 順序 | 推測可能性・漏れる情報 | 調整 | 分散 SQL での偏り |
| --- | --- | --- | --- | --- | --- |
| 連番 | よい（右端に追記）| 厳密（単一の発番元なら）| 次の値を推測できる。件数が分かる | 要る（単一の発番元）| 末尾の範囲に書き込みが集中しうる |
| UUIDv4 | 悪い（全体に散る）[37] | なし | 推測は困難（ただし RFC は権限の証に使うなと言う）[37] | 不要 | 散るので偏らない。CockroachDB はこれを推奨 [39] |
| UUIDv7 | よい [37] | おおよそ時刻順。同一ミリ秒内や生成元をまたぐ順は実装しだい [37] | 生成時刻が分かる [37] | 不要 | 時刻順なので末尾に集中しうる（CockroachDB の文書に v7 の記載はなく、未検証）|
| Snowflake 方式 | よい | おおよそ時刻順（k-sorted）[40] | 時刻とマシン ID が分かる | マシン ID の割り当てに要る。時計が戻ると発番が止まる [40] | 同上 |

## 7. 設計レビューで問うこと（問い｜なぜ問うか｜危ない兆候）

| # | 問い | なぜ問うか | 危ない兆候 |
| --- | --- | --- | --- |
| 1 | すべての遠隔呼び出しに、接続と要求のタイムアウトがあるか。値の根拠は何か | 既定値は無限か長すぎることがある。短すぎると再試行で負荷が増える [43][52] | 「ライブラリの既定のまま」「全部 30 秒」。相手の p99.9 を知らない |
| 2 | 再試行はどの層で、何回、どんな間隔で行うか。層を重ねると何倍になるか | 再試行は metastable failure を維持する最大の要因 [4]。5 層× 3 回で 243 倍 [52] | 全層で再試行。jitter なし。上限なし。再試行の予算（トークンバケット）がない |
| 3 | 過負荷になったとき、負荷を落とす手段があるか。きっかけが消えたあと自力で戻るか | metastable な状態は、きっかけを除いても続く。回復には負荷の削減が要る [3][4] | 負荷制限がない。「原因を直せば戻るはず」。キャッシュが空の状態から起動できるか試していない |
| 4 | ヘルスチェックは、利用者が受けている品質を見ているか | gray failure は、検知器には健全に見える [2] | ハートビートだけ。プロセスの生存だけ。利用者側の成功率・遅延と突き合わせていない |
| 5 | 経過時間・タイムアウト・リースの期限を、どの時計で測っているか | 実時間時計は戻る・飛ぶ [49] | `now()` の差で経過時間を測る。負の経過時間を想定していない |
| 6 | 書き込みの勝ち負けや順序を、タイムスタンプで決めていないか。決めているなら時計の誤差の上限は | LWW は時計のずれで確認応答済みの書き込みを黙って失う [45][50] | 「NTP で同期しているから大丈夫」。クライアントの時計を使っている。ずれの監視がない |
| 7 | 使う DB は時計のずれをどこまで許し、超えたらどうなるか。うるう秒の扱いはそろっているか | CockroachDB は既定 500ms、80% 超でノードが止まる。smear の混在は不可 [10][15] | max-offset を知らない。クラウドをまたいで NTP の源が混在 |
| 8 | この処理に必要なのは、線形化可能性・直列化可能性・因果・結果整合のどれか。なぜその水準か | 水準ごとに、分断中の可用性と平常時の遅延の代償が違う [20][21] | 「強整合」「CP」の一言で済ませる。全部に最強を求める、または全部を結果整合にする |
| 9 | 「CP」「AP」と書いてあるとき、C と A は CAP の定義の意味か | CAP の C は線形化可能性、A は全ノードの応答。製品の宣伝文句とは意味が違う [19] | CAP で製品を 2 分類して選定を終える。分断がないときの遅延の議論がない |
| 10 | 分断・過半数の喪失が起きたとき、各サービスは「止まる」「古い値で続ける」のどちらか。決めてあるか | どちらも正解になりうるが、決めていないと実装の偶然で決まる [19][48] | 調整サービスが落ちたときの動きを誰も答えられない |
| 11 | ロックやリースを取ってから行う書き込みを、資源の側は古い持ち主から拒めるか | リースは止まったプロセスの上で切れる。etcd のロックでも相互排他は破れる [14][31] | 「Redis でロックしているから二重実行はない」。フェンシングトークンも条件つき書き込みもない |
| 12 | そのロックの目的は効率か、正しさか | 効率なら単純なロックで足りる。正しさなら合意＋フェンシングが要る [14] | 目的を区別していない。正しさを Redlock に頼る |
| 13 | リーダー選出を自作していないか。ハートビートとタイムアウトだけで主系を決めていないか | 手作りは split-brain を招く [42] | 自前のフェイルオーバーのスクリプト。2 ノード構成で互いに監視 |
| 14 | 合意のクラスタは何台で、どの障害領域にまたがるか。election timeout は往復時間に対して十分か | 過半数は奇数で。3 台は保守中に 1 台落ちると止まる。可用性はタイミングに依存する [27][30][42] | 偶数台。2 拠点に 2：1 または 1：1。WAN 越しに既定のタイムアウト |
| 15 | 調整サービス・制御プレーンが止まったら、データプレーンは動き続けるか。試したか | Roblox・OpenAI は依存が全体停止に直結した [46][48] | サービスの発見・設定・秘密情報の取得が、毎回の要求で調整サービスを引く。キャッシュの期限が短い |
| 16 | 監視・ログ・復旧の手順は、壊れうる基盤と同じものに載っていないか | 循環した依存は原因の特定を遅らせる [46]。制御プレーンに入れないと直せない [48] | 監視が同じサービスディスカバリを使う。非常用の入口がない |
| 17 | 自動フェイルオーバーの判断は、何を信じているか。判断の材料が壊れたら何が起きるか | 調整サービスの不調が、健全な主系の昇格を引き起こした [47] | 「etcd に書けなければ昇格」。昇格後の作り直しの時間を測っていない |
| 18 | ID は何で作るか。順序・索引の局所性・推測可能性・発番の調整のどれを取ったか | 方式ごとに得失が違い、後から変えにくい [37][40] | UUIDv4 を主キーにして挿入が遅い。連番を URL に出す。UUID を秘密として使う。ID の大小を「どちらが先か」の判定に使う |
| 19 | エラー処理の経路をテストしているか。握りつぶし・TODO のままの例外処理はないか | 壊滅的な障害の 92% は、致命的でないエラーの処理の誤り [36] | `catch` の中がログだけ。障害を注入するテストがない |
| 20 | 選ぼうとしている製品は、第三者の検証（Jepsen など）を受けているか。どの版で、何が見つかり、直ったか | 文書の主張と実際の挙動は食い違いうる [31][54] | 「強整合と書いてあるから」。検証報告の版が、使う版より古い |

## 8. ケーススタディで測れること・測れないこと

測れること（WSL の Docker、単一ホスト）：

- **過半数の喪失**：CockroachDB 3 ノードで 1 台を止める（続く）／2 台を止める（書けなくなる）。応答が返るまでの時間、エラーの種類、復帰後に確認応答済みの書き込みが残っているかを数える（題材 D）
- **gray failure の再現**：Toxiproxy で遅延・帯域制限を入れ、ヘルスチェックは通るのに要求は失敗する状態を作る。検知までの時間を測る
- **プロセスの一時停止とフェンシング**：Pumba の pause で、リースを持つ書き手を期限より長く止める。PostgreSQL を資源として、(a) リースのみ、(b) トークンを条件つき UPDATE で検査、の 2 構成で、古い持ち主の書き込みが通った件数を数える
- **再試行の増幅**：遅延を入れた相手に対し、再試行なし／固定間隔／バックオフ＋ jitter ／予算つき、で相手が受ける要求数を数える。きっかけを外したあと、処理量が戻るまでの時間を測る
- **ID の方式**：PostgreSQL 18 で `bigserial`・`uuidv4()`・`uuidv7()` を主キーにし、挿入時間・索引の大きさ・WAL の量を比べる（題材 C と共通の環境での相対比較）
- **線形化可能でない読み取り**：PostgreSQL の非同期スタンバイで、書いた直後に古い値を読む件数（題材 D と共通）

測れないこと（未検証と明記する）：

- **時計のずれに由来する異常**：単一ホストでは全コンテナが同じ時計を見る。CockroachDB の max-offset 超過時の停止、LWW による書き込みの消失、うるう秒は再現しない（outline の記載どおり）。時刻を偽る仕組みで注入する方法はありうるが、今回の構成の外
- **TrueTime・Amazon Time Sync・ClockBound の誤差**：クラウドの基盤に依存。公式文書と論文の値を引くだけ
- **リージョンをまたぐ遅延と分断**：Toxiproxy で遅延は模擬できるが、実際の WAN の障害の分布は再現しない
- **大規模でのみ現れる metastable failure**：小さな構成では、仕組みの再現にとどまる
- **合意の実装の正しさ**：Jepsen 相当の検証は行わない。製品の検証報告を引く

## 9. 未確定・要確認

- **Shapiro ほか（SSS 2011）の本文**：HAL と Springer のどちらも開けなかった。Strong Eventual Consistency の定義と十分条件（可換性／半束）は記憶に基づく。arXiv 1805.06358（Preguiça・Baquero・Shapiro、2018）の要旨だけ確認した
- **Viewstamped Replication Revisited**：MIT DSpace の要旨のみ。本文（プロトコルの詳細、ディスク書き込みの扱い）は未確認
- **Bailis・Kingsbury の記事**：ACM Queue のページは取得を拒まれた。著者のサイトにある同記事の PDF で確認した。Chubby の停止 9 回の内訳は「4 回がネットワークの保守」までしか確認していない
- **CockroachDB の時計ずれの判定**：FAQ 内で「半数以上のノードに対して 80%」と「平均のずれが 80%」の 2 つの書き方があり、停止の表現も shut down と crash が混在する。v26.4 が「stable」として表示されたが、ページに日付はない。ガイドに書く前に、使う版の文書で確かめ直す
- **CockroachDB と線形化可能性**：文書は SERIALIZABLE は時計のずれに関係なく保たれると書くが、厳密な直列化可能性は主張していない。「causal reverse」などの異常の説明は今回のページにはなかった
- **Spanner の現行の誤差**：論文（2012）の 1〜7 ms は当時の値。現行の公式文書に数値はなかった。「現在は 1 ms 未満」といった数字は一次資料で確認できていない
- **AWS の時計の精度**：100 マイクロ秒未満・40 マイクロ秒未満は 2023-11-16 のブログの自己申告で、対応インスタンスに限る。ClockBound の現行の正式版は README からは特定できなかった（例が 3.0.0-rc.0）
- **PostgreSQL 18 の `uuidv7()` の単調性**：関数のページには、同一バックエンド内での単調増加の保証は書かれていない。ソースやリリースノートは未確認
- **UUIDv7 と分散 SQL のホットスポット**：CockroachDB の UUID のページに v7 の記載はなく、連番キーが偏りを生むという説明もこのページにはなかった（別ページへのリンクのみ）。表 6.5 の「末尾に集中しうる」は範囲分割の一般論からの推論
- **PACELC の製品分類、Consul の整合性モードの中身、etcd の heartbeat・election timeout の既定値、ZooKeeper の Zab、Kubernetes と etcd の関係**：記憶・要確認
- **HAT 論文の「18 のうち 8 つは直列化可能を選択肢としても提供しない」**：抽出した行が途中で切れており、後半は確認できていない。「既定で直列化可能は 3 つ」までを使う
- **Newcombe ほか**：確認したのは 2014-09-29 付の技術報告版（Lamport のサイト）。CACM 58(4)（2015-04）の掲載版との差は未確認
- **Huang ほか（OSDI 2022）**：「きっかけの約 45%」が何の分類かは行が切れていて確認できず、使っていない
- **DDIA 2e のページ**：目次（章・節・ページ）で確認した。各節の本文の主張は、書籍担当のノート（`research/books/notes/21_ddia_ch06-10.md`）と突き合わせる
- 調整サービスが単一障害点になった事例として、ほかに一次報告を探したが、今回確認できたのは 3 件（Roblox・Cloudflare・OpenAI）。ZooKeeper が直接の原因となった事業者自身の事後報告は、今回は見つけていない

## 10. 結論（スライドに書くこと。箇条書き 15〜30 個、各項目に出典の番号）

1. 分散システムで信用できないものは 3 つ：ネットワーク、時計、プロセスが動き続けていること。どれも「壊れた」と「遅い」を相手から区別できない [1][2][50]
2. ネットワークの障害は日常。Microsoft の調査で 1 日あたりリンク 40.8 本が故障し、冗長化で改善するのは中央値で 43% だけ [1]
3. 危ないのは完全な停止より「半分壊れた」状態（gray failure）。検知器には健全に見え、利用者には壊れて見える。Cloudflare 2020-11 の発端は、ping に応答しないのに BGP は生きているスイッチだった [2][47]
4. タイムアウトは既定値に頼らず、許容する誤タイムアウト率と相手の遅延のパーセンタイル（例：0.1% と p99.9）から決める [43][52]
5. 再試行は層を重ねると掛け算で増える（5 層× 3 回で 243 倍）。公開された metastable failure の 5 割超で、再試行が障害を維持していた [4][52]
6. metastable failure は、きっかけを除いても続く。原因はきっかけではなく帰還ループ。回復には負荷を落とす手段が要る [3][4]
7. 実時間時計は戻る・飛ぶ。経過時間は単調時計で測る。Cloudflare は 2017 年のうるう秒で「時間は戻らない」という仮定が破れ、DNS が約 6 時間 45 分にわたり一部失敗した [49][50]
8. 時計の誤差は「ゼロ」ではなく「上限つきの幅」として扱う。Spanner の TrueTime は区間を返し、論文時点の幅は 1〜7 ms。その分だけ待つことで順序を保証する [5]
9. 製品ごとに時計への仮定が違う。CockroachDB（v26.4）は既定で 500ms までのずれを許し、80% を超えたノードは自分で止まる。Cassandra は LWW で、公式文書が「正しさは時計に依存する」と書く [15][16][45]
10. タイムスタンプで書き込みの勝ち負けを決める（LWW）と、時計のずれで確認応答済みの書き込みが黙って消える [45][50]
11. プロセスは任意の時点で止まり、本人は気づかない。リース（期限つきロック）は、持ち主が止まっているあいだに切れる [14][50]
12. ロックだけでは相互排他は守れない。資源の側が、古い番号（フェンシングトークン）の書き込みを拒む必要がある。Redis の公式文書も etcd の Jepsen 検証も同じ結論 [14][31][35]
13. ロックの目的を「効率」と「正しさ」に分ける。効率なら単純なロックで足り、正しさなら合意＋フェンシングか、DB の制約・条件つき書き込みを使う [14]
14. 線形化可能性は「1 つの値の最新が読めること」、直列化可能性は「複数の値をまたぐトランザクションが干渉しないこと」。別の性質で、両方を満たすのが厳密な直列化可能性 [18]
15. CAP 定理の C は線形化可能性、A は「故障していない全ノードが応答する」こと。定理が言うのは、分断中にこの 2 つを両立できないことだけ [19]
16. 「CP か AP か」で製品を選ばない。分断がないときも、複製をすれば一貫性と遅延の取引がある（PACELC）[20]
17. 分断中も応答できる保証は意外に多い。Read Committed、単調な読み取り、因果一貫性（同じノードにつながる場合）は達成でき、スナップショット分離・直列化可能・線形化可能は達成できない [21]
18. 調整なしで一貫した結果が得られるのは、計算が単調なとき、かつそのときに限る（CALM）。CRDT はその性質を持つデータ型 [22][24]
19. 合意が要るのは「1 つに決める」場面：リーダー選出、一意性制約、アトミックコミット、ロック。合意と「全員が同じ順序のログを持つこと」は同じ難しさ [29][50]
20. 合意は理論上、必ず終わる保証ができない（FLP）。実用のアルゴリズムは安全性を常に守り、進行はタイミングがよいときだけ保証する。Raft も「安全性はタイミングに依存しないが、可用性は依存する」[25][27]
21. Raft の骨格は 3 つ：任期ごとに過半数の票で 1 人のリーダー、過半数への複製でコミット、メンバー変更は新旧両方の過半数を経由 [27]
22. 過半数の算数：3 台で 1 台、5 台で 2 台の故障に耐える。偶数は耐故障が増えない。Google SRE 本は多くの場合 5 台を勧める [30][34][42]
23. 合意は自作しない。リーダー選出・ロック・重要な共有状態には、検証された調整サービス（ZooKeeper・etcd・Consul）を使う [42]
24. ただし調整サービスは単一障害点になる。Roblox は 1 つの Consul クラスタに全サービスを載せ、73 時間止まった。監視も同じ Consul に依存していた [46]
25. 3 件の事故（Roblox・Cloudflare・OpenAI）に共通するのは、合意が間違えたのではなく進まなくなったとき、頼る側の作りが被害を決めたこと。調整サービスが止まっても動き続けるか、を設計で決める [46][47][48]
26. ID の方式は 4 つの軸で選ぶ：索引の局所性、順序、推測可能性、発番の調整。UUIDv4 は散って索引に厳しく、UUIDv7 は時刻順で局所性がよいが生成時刻が漏れる。RFC 9562 は UUID を権限の証に使うなと定める [37]
27. PostgreSQL 18 には `uuidv7()` がある。Snowflake 方式は 64 ビットに収まるが、時計とマシン ID の割り当てに依存する [38][40]
28. 壊滅的な障害の 92% は、致命的でないエラーの処理の誤りから起きている。98% は 3 ノード以下で再現でき、77% は単体テストで再現できる。エラー処理の経路をテストする [36]
29. 正しさの検証には層がある：設計の検証（TLA+。AWS は 10 の大きなシステムで使い、35 手順の再現手順が要るバグを見つけた）、決定的シミュレーション（FoundationDB・TigerBeetle・Antithesis）、実物への障害注入（Jepsen）。どれも不在の証明にはならない [41][54][55][56][57]
30. テックリーダーが知るべき範囲：証明は不要。「何が信用できないか」「この処理に要る保証はどれか」「過半数を失うと何が起きるか」「古い持ち主を資源の側で拒めるか」「調整サービスが止まっても動くか」を問えること [14][19][27][42]

### テックリーダーが「合意の理論」をどこまで知れば足りるか

知っておくこと（製品の選定とレビューで使う）：

- 安全性と進行（liveness）の区別。合意は安全性を常に守るが、進行は保証しない（FLP、Raft §5.6）[25][27]
- 過半数の算数と、障害領域への置き方 [30][42]
- 線形化可能な読み取りには追加の往復が要り、製品は既定でそれを省いていることがある（Raft §8、ZooKeeper の `sync()`、etcd の `serializable`）[27][31][32]
- リースはタイミングの仮定に頼る。だからフェンシングが要る [14][27]
- 合意が要る場面と要らない場面の見分け（「1 つに決める」か、単調か）[22][50]
- 調整サービスの監視項目（リーダーの有無、交代の頻度、遅れ、提案の遅延）[42]

知らなくてよいこと（必要になったら調べる）：Paxos の証明、ログの不一致の修復手順の細部、ビザンチン耐性のプロトコル、各種の最適化（Multi-Paxos、Flexible Paxos など）。

製品の選定で問う 5 点：(1) 既定の一貫性の水準と、その名前が指す実際の保証、(2) 時計への仮定と、破れたときの挙動、(3) 過半数を失ったときの挙動と復旧の手順、(4) 第三者の検証の有無・対象の版・見つかった問題、(5) その製品が止まったとき、自分のサービスのどこまでが止まるか。

## 11. 出典（番号｜題名｜発行者｜版・日付｜URL｜確認の深さ）

| # | 題名 | 発行者 | 版・日付 | URL | 確認の深さ |
| --- | --- | --- | --- | --- | --- |
| 1 | The Network is Reliable（Bailis, Kingsbury）| ACM Queue 12(7) | 2014 | https://queue.acm.org/detail.cfm?id=2655736 （取得拒否）／ http://www.bailis.org/papers/partitions-queue2014.pdf | 本文確認（著者サイトの PDF。ACM のページは開けず）|
| 2 | Gray Failure: The Achilles' Heel of Cloud-Scale Systems（Huang ほか）| HotOS '17、ACM | 2017-05 | https://www.microsoft.com/en-us/research/wp-content/uploads/2017/06/paper-1.pdf | 本文確認 |
| 3 | Metastable Failures in Distributed Systems（Bronson, Aghayev, Charapko, Zhu）| HotOS '21、ACM | 2021-05/06 | https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf | 本文確認 |
| 4 | Metastable Failures in the Wild（Huang ほか）| OSDI '22、USENIX | 2022-07、pp.73–90 | https://www.usenix.org/conference/osdi22/presentation/huang-lexiang | 本文確認（要旨と §3 の数字）|
| 5 | Spanner: Google's Globally-Distributed Database（Corbett ほか）| OSDI '12、USENIX | 2012 | https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf | 本文確認（§3・§4.1.2・評価の節）|
| 6 | Spanner: TrueTime and external consistency | Google Cloud 公式文書 | 日付の記載なし（2026-11-18 閲覧）| https://docs.cloud.google.com/spanner/docs/true-time-external-consistency | 本文確認 |
| 7 | （欠番）| — | — | — | — |
| 8 | Logical Physical Clocks and Consistent Snapshots in Globally Distributed Databases（Kulkarni ほか）| Univ. at Buffalo Tech Report 2014-04 | 2014 | https://cse.buffalo.edu/tech-reports/2014-04.pdf | 本文確認（要旨と §1）|
| 9 | RFC 5905: Network Time Protocol Version 4 | IETF | 2010-06 | https://www.rfc-editor.org/rfc/rfc5905.html | 本文確認（§1・§7.3。§10 以降は未読）|
| 10 | Precision clock and time synchronization on your EC2 instance | AWS EC2 User Guide | 日付の記載なし（2026-11-18 閲覧）| https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html | 本文確認 |
| 11 | It's About Time: Microsecond-Accurate Clocks on Amazon EC2 Instances | AWS Compute Blog（自己申告）| 2023-11-16 | https://aws.amazon.com/blogs/compute/its-about-time-microsecond-accurate-clocks-on-amazon-ec2-instances/ | 本文確認 |
| 12 | Leap Smear | Google Public NTP | 日付の記載なし | https://developers.google.com/time/smear | 本文確認 |
| 13 | ClockBound | AWS（GitHub aws/clock-bound）| README の例は 3.0.0-rc.0 | https://github.com/aws/clock-bound | 本文確認（README）|
| 14 | How to do distributed locking（Kleppmann）| 著者のブログ | 2016-02-08 | https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html | 本文確認 |
| 15 | Operational FAQs | CockroachDB 公式文書 | v26.4（stable）。日付の記載なし | https://docs.cockroachlabs.com/docs/stable/operational-faqs | 本文確認 |
| 16 | cockroach start（`--max-offset`）| CockroachDB 公式文書 | v26.4 | https://docs.cockroachlabs.com/docs/stable/cockroach-start | 本文確認 |
| 17 | Transaction Layer | CockroachDB 公式文書 | v26.4 | https://docs.cockroachlabs.com/docs/stable/architecture/transaction-layer | 本文確認 |
| 18 | Linearizability: A Correctness Condition for Concurrent Objects（Herlihy, Wing）| ACM TOPLAS 12(3) | 1990 | https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf | 本文確認（要旨・§1・§3）|
| 19 | Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services（Gilbert, Lynch）| ACM SIGACT News 33(2) | 2002 | https://www.comp.nus.edu.sg/~gilbert/pubs/BrewersConjecture-SigAct.pdf | 本文確認（§2〜§4）|
| 20 | Consistency Tradeoffs in Modern Distributed Database System Design（Abadi）| IEEE Computer 45(2) | 2012-02 | https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf | 本文確認（前半。製品分類の表は未確認）|
| 21 | Highly Available Transactions: Virtues and Limitations（Bailis ほか）| PVLDB 7(3) | 2013（VLDB 2014）| http://www.vldb.org/pvldb/vol7/p181-bailis.pdf | 本文確認（§4・§5・表 3）|
| 22 | Keeping CALM: When Distributed Consistency is Easy（Hellerstein, Alvaro）| arXiv 1901.01930（のち CACM 63(9)、2020。掲載号は記憶）| 2019-01 | https://arxiv.org/abs/1901.01930 | 本文確認（§1・定理 1）|
| 23 | Conflict-free Replicated Data Types（Shapiro, Preguiça, Baquero, Zawirski）| SSS 2011、Springer LNCS 6976 | 2011 | https://inria.hal.science/inria-00609399 | 題名のみ（HAL・Springer とも取得不可）|
| 24 | Conflict-free Replicated Data Types (CRDTs)（Preguiça, Baquero, Shapiro）| arXiv 1805.06358 | 2018-05-16 | https://arxiv.org/abs/1805.06358 | 本文確認（要旨のみ）|
| 25 | Impossibility of Distributed Consensus with One Faulty Process（Fischer, Lynch, Paterson）| JACM 32(2) | 1985 | https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf | 本文確認（要旨・定理 1）|
| 26 | Paxos Made Simple（Lamport）| ACM SIGACT News 32(4)（掲載号は記憶）| 2001 | https://lamport.azurewebsites.net/pubs/paxos-simple.pdf | 本文確認（§2）|
| 27 | In Search of an Understandable Consensus Algorithm (Extended Version)（Ongaro, Ousterhout）| USENIX ATC '14 の拡張版 | 2014 | https://raft.github.io/raft.pdf | 本文確認（§5・§6・§8・§9.3）|
| 28 | Viewstamped Replication Revisited（Liskov, Cowling）| MIT-CSAIL-TR-2012-021 | 2012-07-23 | https://dspace.mit.edu/handle/1721.1/71763 | 本文確認（要旨のみ。PDF は取得不可）|
| 29 | Unreliable Failure Detectors for Reliable Distributed Systems（Chandra, Toueg）| JACM 43(2) | 1996 | https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/p225-chandra.pdf | 本文確認（要旨・§1）|
| 30 | Frequently Asked Questions | etcd 公式文書 | v3.6 | https://etcd.io/docs/v3.6/faq/ | 本文確認 |
| 31 | Jepsen: etcd 3.4.3（Kingsbury）| Jepsen | 2020-01-30。対象は etcd 3.4.3 | https://jepsen.io/analyses/etcd-3.4.3 | 本文確認 |
| 32 | ZooKeeper Programmer's Guide | Apache ZooKeeper | 3.9 | https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html | 本文確認 |
| 33 | ZooKeeper: Wait-free coordination for Internet-scale systems（Hunt ほか）| USENIX ATC '10 | 2010 | https://www.usenix.org/legacy/event/atc10/tech/full_papers/Hunt.pdf | 本文確認（要旨・§1・§2 の一部）|
| 34 | Consensus（Consul architecture）| HashiCorp 公式文書 | 版・日付は未取得 | https://developer.hashicorp.com/consul/docs/architecture/consensus | 本文確認 |
| 35 | Distributed Locks with Redis | Redis 公式文書 | 日付の記載なし（Redis 8.4 の DELEX に言及）| https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/ | 本文確認 |
| 36 | Simple Testing Can Prevent Most Critical Failures（Yuan ほか）| OSDI '14、USENIX | 2014-10 | https://www.usenix.org/conference/osdi14/technical-sessions/presentation/yuan | 本文確認（要旨・§1・Finding 1〜11）|
| 37 | RFC 9562: Universally Unique IDentifiers (UUIDs) | IETF | 2024-05 | https://www.rfc-editor.org/rfc/rfc9562.html | 本文確認（§2.1・§5.4・§5.7・§6.2・§6.9・§6.11・§6.13・§8。末尾の付録は未読）|
| 38 | 9.14. UUID Functions | PostgreSQL 公式文書 | 18 | https://www.postgresql.org/docs/18/functions-uuid.html | 本文確認 |
| 39 | UUID | CockroachDB 公式文書 | v26.4 | https://docs.cockroachlabs.com/docs/stable/uuid | 本文確認 |
| 40 | Snowflake README | Twitter（GitHub twitter-archive/snowflake、タグ snowflake-2010）| 2010 | https://github.com/twitter-archive/snowflake/tree/snowflake-2010 | 本文確認（README。告知のブログ記事は取得拒否）|
| 41 | Safety | TigerBeetle 公式文書（自己申告）| 日付の記載なし | https://docs.tigerbeetle.com/concepts/safety/ | 本文確認 |
| 42 | Managing Critical State: Distributed Consensus for Reliability（SRE 本 23 章）| Google | 2016 年刊（刊行年は記憶）| https://sre.google/sre-book/managing-critical-state/ | 本文確認 |
| 43 | REL05-BP05 Set client timeouts | AWS Well-Architected 信頼性の柱 | 日付の記載なし。「歴史的な参照用」の表示あり | https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_mitigate_interaction_failure_client_timeouts.html | 本文確認 |
| 44 | The Chubby lock service for loosely-coupled distributed systems（Burrows）| OSDI '06、USENIX | 2006 | https://static.googleusercontent.com/media/research.google.com/en//archive/chubby-osdi06.pdf | 本文確認（§2.4 の該当箇所のみ）|
| 45 | Dynamo（Cassandra architecture）| Apache Cassandra 公式文書 | 5.0（プレリリース版の表示）| https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html | 本文確認 |
| 46 | Roblox Return to Service 10/28-10/31 2021 | Roblox | 2022-01-20 | https://about.roblox.com/newsroom/2022/01/roblox-return-to-service-10-28-10-31-2021 | 本文確認 |
| 47 | A Byzantine failure in the real world | Cloudflare | 2020-11-27 | https://blog.cloudflare.com/a-byzantine-failure-in-the-real-world/ | 本文確認 |
| 48 | API, ChatGPT & Sora Facing Issues（事後報告）| OpenAI | 2024-12-13 | https://status.openai.com/incidents/ctrsv3lwd797 | 本文確認 |
| 49 | How and why the leap second affected Cloudflare DNS | Cloudflare | 2017-01-01 | https://blog.cloudflare.com/how-and-why-the-leap-second-affected-cloudflare-dns/ | 本文確認 |
| 50 | データ指向アプリケーションデザイン 第2版（Kleppmann, Riccomini、斉藤 訳）9 章・10 章 | オライリー・ジャパン | ISBN 978-4-8144-0180-2 | — | 目次（節とページ）で確認。本文の主張は書籍担当のノートと要照合 |
| 51 | Is Redlock safe?（antirez）| 著者のブログ | 2016-02（日付は相対表示のみ。Kleppmann の記事の翌日と本文にある）| http://antirez.com/news/101 | 本文確認 |
| 52 | Timeouts, retries, and backoff with jitter（Brooker）| Amazon Builders' Library | 2019-12-05 | https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter | 本文確認 |
| 53 | Leader election in distributed systems（Brooker）| Amazon Builders' Library | 2019-12-05 | https://builder.aws.com/content/3Ev0vH0hfkcUizISUWYTvHibtcp/leader-election-in-distributed-systems | 本文確認 |
| 54 | Jepsen: TigerBeetle 0.16.11（Kingsbury）| Jepsen（TigerBeetle 社の資金による）| 2025-06-06。対象は 0.16.11〜0.16.30 | https://jepsen.io/analyses/tigerbeetle-0.16.11 | 本文確認 |
| 55 | Use of Formal Methods at Amazon Web Services（Newcombe ほか）| 技術報告版。のち CACM 58(4)「How Amazon Web Services Uses Formal Methods」| 2014-09-29（CACM 版は 2015-04。掲載号は記憶）| https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf | 本文確認（技術報告版。CACM 版は未確認）|
| 56 | Simulation and Testing | FoundationDB 公式文書（自己申告）| 日付の記載なし | https://apple.github.io/foundationdb/testing.html | 本文確認 |
| 57 | Deterministic Simulation Testing | Antithesis 公式文書（自己申告）| 日付の記載なし | https://antithesis.com/docs/resources/deterministic_simulation_testing/ | 本文確認 |

出典 [52][53] の著者名（Brooker）は、ページの表示が「Marc」のみだったための補い（記憶）。

### 検証の手法についての補足（結論 29 の根拠）

- **TLA+（AWS）**：2011 年から使用。10 の大きなシステムに適用し、7 チームが使用。S3 で 2 件、DynamoDB で 3 件（うち一部は 35 手順の再現手順が要る）など、設計段階のバグを見つけた。エンジニアは 2〜3 週間で使えるようになったと報告 [55]
- **決定的シミュレーション**：FoundationDB は、クラスタ全体を単一スレッドのプロセス内で決定的に模擬し、ネットワーク・マシン・データセンターの障害を注入する。毎晩数万回を実行（自己申告）[56]。TigerBeetle の VOPR は、実コードのクラスタを模擬環境で動かし、ネットワーク・ストレージ・プロセスの障害を入れる（自己申告）[41]。Antithesis は、決定的なハイパーバイザの上で、作り替えていないソフトウェアを動かす点が違うと説明する [57]
- **限界**：Jepsen の TigerBeetle の検証（2025-06-06）は、シミュレーションが多くのバグを捕らえていたと評価しつつ、4 つのファザーが見逃した問い合わせのバグ、アップグレードの経路の試験不足を指摘した。生成するデータや障害の形が届かない経路は見つからない [54]
