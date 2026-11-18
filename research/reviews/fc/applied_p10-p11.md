# ファクトチェックの反映：deck/p10.js・p11.js（S138〜S165）

- 作業日：2026-11-18
- 対象の指摘：C_standards 11 件、C_products 6 件、C_books 7 件、`_quote_hits.txt` 2 行（計 26 行）。A・B・D の各ファイルに S138〜S165 への言及は無かった（grep で確認）
- ビルド：`node build_one.js p10`／`p11` ともエラーなし、content slides 13、without refs 0、without notes 0。PNG の再書き出しはしていない（見た目は未確認）

## 冪等の定義の最終の文言（Part 6・13 はこれに揃える）

S157（`deck/p11.js`「冪等な受け手」の発表者ノートの 1 文目）。**変更していない**。定義そのものへの誤りの指摘は無かった。

> 冪等とは、1 回実行しても、何回実行しても、効果が同じになることです。

同じスライドのリード（変更なし）：「冪等キーは要求を出した端が作り、状態を変える端まで通す」

## 反映の記録

| 指摘の出どころ | スライド | 指摘の要点 | 自分で確かめた一次資料と結果 | 対応 | 直した後の文、または直さない理由 |
|---|---|---|---|---|---|
| C_standards #1／D11 | S140 表・ノート | 「243 倍」は前提（各層 3 回）が落ちている。原文は retries と tries を混ぜている | Builders' Library「Timeouts, retries, and backoff with jitter」（builder.aws.com、2019-12-05。取得ツール経由の引用）："five-deep stack"、"three retries at each layer"、"increase 243x"、"first three tries, then nine tries"。混在を確認 | 直した（D11 に従い数字を外した。指摘の案＝条件を足して 243 を残す、は採らない） | 表：「掛け算で増える｜各層が独立に再試行すると、層を重ねるごとに下の層への負荷が掛け算で増える（Builders' Library）」。ノート：「…層を重ねるごとに再試行が掛け算で増えると説明しています。倍率は層の数と各層の回数で変わります」。表の見出しは「数字・性質／何を指すか（条件）」 |
| C_products #9 | S140 表 | 同上（「3 回」の条件落ち） | 同上 | 直した（同上） | 同上 |
| C_standards #2／D11 | S140 表・ノート | 「公開報告 22 件（11 組織）」。本文と表 1 は 21 件 | Huang ほか 2022（OSDI）の PDF を取得して本文を検索。要旨 "22 metastable failures from 11 different organizations"、§2 "We identify 21 metastable failures (Table 1) that are severe enough to warrant public incident reports"。表 1 の行を数えて 21 行（GGL1〜4、AWS1〜4、AZR1〜4、IBM1、SPF1・2、ELC1、WIK1、CCI1、CAS1・2、FB1） | 直した（表は本文の表の数に合わせた） | 表：「公開報告 21 件（Huang ほか 2022 の表 1）の準安定障害のうち、再試行が障害を保っていた割合（11 件）」。ノート：「要旨は 11 の組織の 22 件と書きますが、公開報告として表 1 に載るのは 21 件で、数字はこの表についての記述です」 |
| C_standards #3／D11 | S140 根拠の行 | 「§3」は誤り。数字は §2 | 同 PDF：50% 超・1.5〜73.53 時間・35% はすべて「2 Metastability in the Wild」（2.2 節）にあり、§3 は「Metastability Framework」。Bronson ほか 2021 の PDF：定義（"persists even when the trigger is removed"、"rebooting the system or dramatically reducing the load"）は §1 Introduction、再試行は §2.1 Request Retries（"One of the most common failure-sustaining mechanisms"） | 直した | 「Huang ほか 2017（HotOS）／Bronson ほか 2021（HotOS）§1／Huang ほか 2022（OSDI）§2・表 1」 |
| C_standards #9 | S140 表 | 「1.5〜73.53 時間」は本文どおりだが、表 1 に 1.15 時間・0.16 時間の行がある | 同 PDF：本文 "a range of 1.5 to 73.53 hours"、表 1 に AZR2 1.15、CAS2 0.16 を確認 | 直した | 表：「同論文の本文が書く停止の長さ（表 1 にはより短い件もある）。記載のある件では 4〜10 時間が最多（35%）」。ノートにも 1 文 |
| C_standards #10 | S140 表 | 「50% 超」の母数を #2 と合わせる | 同 PDF："affecting more than 50% of the studied incidents"、列挙は 11 件 | 直した | 上の行の文（「21 件…（11 件）」）。ノート：「論文は 50% を超える事例に関わるとし、11 件を挙げています」 |
| C_products #2 | S141 カード・ノート | 「異常終了」は原文に無い。パニックは捕捉され、一部の DNS 解決が失敗 | Cloudflare の報告の HTML を取得して本文を検索："a number went negative"、"caused RRDNS to panic. This panic was caught using the recover feature of the Go language. The net effect was that some DNS resolutions … failed"、"rand.Int63n promptly panics if its argument is negative"、"At peak approximately 0.2% of DNS queries"、"06:45 UTC Impact ends" | 直した | カード：「時刻の差で応答時間を測っていた DNS のコードで値が負になり、パニックが起きた（捕捉された）。一部の DNS 解決が失敗し、ピーク時に問い合わせの約 0.2% に影響（事業者の報告）」。ノート：「…その値が負になりました。負の値を乱数の関数に渡した所でパニック（panic）が起き、これは捕捉されましたが、一部の DNS 解決が失敗しました。プロセスが異常終了したとは書かれていません」 |
| C_books #18 | S142 ノート | etcd は p.372 で「リビジョン番号とリース ID の組み合わせ」 | DDIA 2e 本文 p.372（PDF p.390）：「etcd では、リビジ…（中略）」。Jepsen etcd 3.4.3 は "the revision of their lock key as a globally ordered fencing token"（取得ツール経由） | 直した | 「ZooKeeper では zxid、etcd ではリビジョン番号が使えます。書籍は p.372 で、etcd についてリース ID との組み合わせを挙げています」 |
| C_books #19 | S142 図 | 図は DDIA 2e 図 9-6 と同じ構成。もとの図を示す | 本文 p.371〜372 に図 9-6（クライアント 1・2、トークン 33・34）を確認 | 直した | 根拠の行：「DDIA 2e 9.3.4 節 p.362〜365、9.4.2 節 p.369〜373（図は同書の図 9-6 をもとに作図）」 |
| _quote_hits S145（49 字、slide）／D12 | S145 根拠の行 | 書籍の本文（参考文献の欄）と 49 字一致。中身は論文の題 | `_quote_hits.txt` の該当行を確認。一致は論文の題そのもの | 直した（題を書かず、掲載誌・巻号で示す） | 「Bailis ほか PVLDB 7(3)（VLDB 2014。高可用トランザクション HAT の論文）§3・§5、表 3」 |
| C_standards #13 | S145 表 3 行目 | リピータブルリードは Adya の定義。変種は高可用で守れる | Bailis ほかの PDF：表 3 の Unavailable に Repeatable Read (RR)、HA に Item Cut Isolation。§5 冒頭 "variants of Repeatable Read" は高可用。§5.2.1 付近 "Repeatable Read (defined by Gray, Berenson et al., and Adya)"。**指摘の「§4」は §5 の冒頭、「Adya の定義」は Gray・Berenson・Adya の定義が正確** | 直した（確かめた形で） | セル：「スナップショット分離、リピータブルリード（Adya らの定義）、直列化可能性、線形化可能性など」。ノート：「ここのリピータブルリードは Gray、Berenson、Adya らの定義のもので、論文は、切り口の分離（Item Cut Isolation）のような変種なら 1 行目に入るとしています」 |
| C_books #15 | S146 ノート | 「どんな状況でも守ります」は条件落ち（「ほとんどの」、非ビザンチン） | DDIA 2e 本文 p.425（PDF p.443）：「ほとんどの合意アルゴリズムは、安全性…が、過半数のノードが障害を起こしたり…した場合でも常に満たされることを保証します」。同章が非ビザンチンのモデルを前提とする記述も確認 | 直した | 「ほとんどの合意アルゴリズムは、誤った決定をしないという安全性を、過半数のノードが落ちても守ります。ノードが嘘をつかない、つまりビザンチン障害が無いという前提です」 |
| C_books #13 | S138・S146・S147・S150・S151・S154・S157 | 訳語のゆれ（コーディネーションサービス／調整サービス、アボート／中断、ユニーク性制約／一意性） | DDIA 2e 本文を検索：「コーディネーションサービス」35 回・「調整サービス」0 回、「ユニーク性制約」26 回・「一意性制約」0 回 | 直した（対応を初出で書く形。一部は残した） | S138 ノート「調整サービス（書籍の訳語ではコーディネーションサービス）」、S146 注記「コーディネーションサービス（以下、調整サービス）」、S146 カード「全員がアボートか」、S150 ノート「ユニーク性制約（一意性の保証）」、S157 コードのコメント「ユニーク性制約。重複ならアボート」。S147・S151 の「調整サービス」と S150 の表の「一意性」は、リードと表の字数のため、そのまま（対応は S138・S146 で示した） |
| C_standards #5 | S148 注意 | RFC 9562 §6.13 の "where feasible" が落ちている | rfc-editor.org の RFC 9562 本文："Thus, where feasible, UUIDs SHOULD be stored within database applications as the underlying 128-bit binary value." | 直した | 「DB には、可能なら 128 ビットのバイナリで格納する（§6.13、SHOULD）」 |
| C_standards #11 | S149 カード・ノート | 一覧に Amazon RDS for PostgreSQL 17.4（2025-04-29）がある | jepsen.io/analyses（取得ツール経由、2026-11-18）：Spanner・DynamoDB・Aurora は無し、Amazon RDS for PostgreSQL 17.4（2025-04-29）、CockroachDB beta-20160829（2017-02-16）、Redpanda 21.10.1（2022-04-29） | 直した | カード：「Spanner・DynamoDB・Aurora は一覧に無い（RDS for PostgreSQL 17.4 は 2025-04 にある）」。ノート：「マネージド製品では、Amazon RDS for PostgreSQL 17.4 の分析が 2025 年 4 月にあります」 |
| C_standards #12 | S149 カード | 「KV は厳密に直列化可能」は観測の範囲の結論 | Jepsen etcd 3.4.3（取得ツール経由）："key-value operations appear to be strict serializable" | 直した | カード：「etcd 3.4.3：KV は試験の範囲で厳密な直列化可能性に違反なし。ロックは相互排他なし」。ノートにも 1 文 |
| C_standards #8 | S157 根拠の行・ノート | 草案 -08 は 2026-10-22 付。未成立で内容は変わりうる | datatracker（取得ツール経由）：-08、2026-10-22、失効予定 2027-04-25、Active、WG Document。**-00 の年（2021）と過去の版の失効は、このページでは確かめられなかったので書かない** | 直した（確かめられた範囲で） | 根拠の行：「Stripe API Idempotent requests／draft-ietf-httpapi-idempotency-key-header-08（2026-10 付の草案。未成立。2026-11 確認）」。ノート：「IETF の Idempotency-Key は 2026 年 10 月付の草案で、RFC ではなく、内容は変わりえます」 |
| C_products #12（S157 の分） | S157 表 | Stripe の記述に「未検証」の印が無い | スライドを確認（印なし）。Stripe のふるまいは今回開いていない（文言は変えていない） | 直した | 表の見出し：「例（文書の記述。未検証）」。ノート：「Stripe のふるまいは公式文書の記述で、このガイドでは検証していません」。S196・S202 は担当外 |
| C_products #7 | S158 表・ノート | Pub/Sub の厳密に 1 回は pull 型だけ | Pub/Sub 文書（docs.cloud.google.com、取得ツール経由）："Only the pull subscription type supports exactly-once delivery"、"Push and export subscriptions don't support exactly-once delivery"、"only applies when subscribers connect to the service in the same region" | 直した | 表：「pull 型の購読で、購読者が同じリージョンで接続したときの配信｜push・export 型は対象外。複数リージョンにまたがると重複しうる」。ノートにも 1 文 |
| C_products #8 | S158 ノート | Kafka の既定：冪等プロデューサーは有効だが、トランザクションは使われない | Kafka 4.4 Producer Configs（取得ツール経由）：enable.idempotence=true、acks=all、transactional.id=null | 直した | ノート：「プロデューサーの冪等性は既定で有効ですが、これはプロデューサーの再送による重複を防ぐもので、トランザクションは既定では使われません」 |
| C_products #10（S158 の分） | S158 表 | 同期の Express は多くとも 1 回 | Step Functions「Choosing workflow type」（原文がそのまま返った）：Asynchronous Express は At-least-once、Synchronous Express は At-most-once。Standard は "never run more than once, unless you have specified Retry behavior" | 直した | 「Express は非同期が少なくとも 1 回、同期が多くとも 1 回」。S202 は担当外 |
| C_standards #16 | S158・S163 | エンドツーエンド原則の原典（Saltzer ほか 1984）を並記 | DDIA 2e の参考文献 [44]（本文 p.560 付近で「1984 年に Saltzer、Reed、Clark によって」）："ACM Transactions on Computer Systems, volume 2, issue 4, pages 277–288, November 1984"。検索でも同じ書誌。論文の本文は今回読んでいない | S158 は直した。S163 は足さない | S158 根拠の行：「DDIA 2e 13.3.1 節 p.560〜561（エンドツーエンド原則。原典は Saltzer ほか 1984、ACM TOCS 2(4)）」、ノート「Saltzer ほかの 1984 年の論文の…」。S163 は「検査を端から端まで」（p.572）の話で、書籍がそこで同論文を引いていないため、足さない |
| C_books #20 | S161 根拠の行・ノート | 表 12-12 は 4 つの名前だけ。中身は本文（指摘は p.359〜361） | 『ハードパーツ』本文：12.4 節は p.357（PDF p.375）から。副作用・補償の失敗・応答性の説明は p.358〜361、表 12-12 は p.362。**節の範囲は p.357〜362（指摘の案「12.4 節 p.359〜362」は節の始まりが違う）** | 直した（確かめた範囲で） | 根拠の行：「『ハードパーツ』12.4 節 p.357〜362（表 12-12 は p.362）・12.2 節 p.350〜354（表 12-11 は p.354）」。ノート：「12.4 節で補償の問題を説明し、表 12-12 で 4 つにまとめています」 |
| C_books #17 | S162 カード・ノート | 「分離性は得られない」は書籍の記述ではない | DDIA 2e 5.2.3 節（p.180〜183）を検索：トランザクションの分離性への言及は無い | 直した | カード：「分離性（途中の状態は他から見える。本ガイドの整理）」。ノート：「これは書籍の記述ではなく、本ガイドの整理です」 |
| _quote_hits S163（25 字、NOTE）／D12 | S163 ノート | 書籍 p.572 と 25 字一致 | DDIA 2e 本文 p.572（PDF p.590）の該当文を確認 | 直した | 「検査に含める範囲を広げるほど、途中にある記憶装置も、通信も、個々のサービスや計算の手順も、まとめて確かめたことになります」 |
| C_books #6 | S164・S165 根拠の行 | 8.4 節と『ハードパーツ』12 章の、節とページの対応 | DDIA 2e 本文：8.4 節 p.317（PDF p.335）、8.4.1 p.319、8.4.2 p.323、8.4.3 p.328、8.5 節 p.330。『ハードパーツ』：12 章 p.323、12.2 節 p.350、12.4 節の終わり p.362 | 直した | S164「DDIA 2e 8.4.2〜8.4.4 節 p.323〜330・13.3 節 p.558〜573／『ハードパーツ』12.2〜12.4 節 p.350〜362」。S165「DDIA 2e 8.4 節 p.317〜330・…」 |

## 件数

- 反映した：26 行すべて（うち C_standards #16 の S163 の分と、C_books #13 の S147・S151・S150 表の語は、理由を書いて残した）
- 直さなかった：0 行

## 確かめて、指摘のほうが違っていた点

- C_standards #13：「同論文 §4」は §5 の冒頭。「Adya の定義」は、論文では Gray・Berenson・Adya の定義
- C_books #20：12.4 節は p.357 から（指摘の案は p.359〜362）
- C_standards #1・C_products #9：直した文の案（条件を足して 243 倍を残す）は、決定 D11 に従い採らなかった
- C_standards #8：-00 が 2021 年、過去の版が失効、は datatracker の取得結果では確かめられず、書かなかった

## 不確かな点

- Builders' Library、Pub/Sub、Jepsen、Kafka、datatracker は取得ツール（要約モデル経由）の引用で確かめた。原文の全文は読んでいない
- Saltzer ほか 1984 の書誌は、DDIA 2e の参考文献と検索結果による。論文そのものは開いていない
- 見た目：S149 左のカード（3 項目が各 2 行、計 6 行）、S157 の根拠の行（長い）、S140 の表（各行 1 行に収まる見込み）、S158 の Pub/Sub の行（2 行）は、PNG で未確認
- S157 の「未検証」は「このガイドのケーススタディで確かめていない」の意味で付けた。Stripe の文書そのものは今回開いていない
