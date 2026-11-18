# ファクトチェック：範囲 C（S138〜S204）／観点「標準と論文」

- 調査日：2026-11-18。対象：`research/deck_text_C.md`（Part 10〜13）
- 方法：原論文は PDF を取得して本文を検索、RFC・草案・仕様は公式サイト（rfc-editor.org、datatracker.ietf.org、openid.net、opentelemetry.io、jepsen.io、GitHub の仕様リポジトリとリリース一覧）を開いて確認した。「自分で開いた」と書いたものは今回すべて原文を確認している
- 結果：**誤り 0 件、不正確 6 件、補足 11 件**。数字・版・節番号の大半は原典と一致した。直すべき点は「条件の落ちた数字」と「出典の節・件数の表記」に集中している

## 指摘（重要な順）

| # | スライド | 問題の記述（短く） | 何が違うか・根拠 | 直した文の案 | 重大度 |
|---|---|---|---|---|---|
| 1 | S140 表・NOTE | 「243 倍｜5 層の呼び出しで各層が独立に再試行したとき」 | 前提の「各層 3 回」が落ちている。原文（Builders' Library「Timeouts, retries, and backoff with jitter」、自分で開いた）は "a five-deep stack of service calls. It ends with a query to a database, and three retries at each layer … If each layer retries independently, the load on the database will increase 243x … first three tries, then nine tries"。243＝3^5 で、回数が変われば倍率も変わる。さらに原文自体が "three retries" と "three tries" を混ぜており、「再試行 3 回（＝試行 4 回）」と読むと 4^5＝1024 になる。243 は「1 層あたり 3 回の試行 × 5 層」と読んだときだけ成り立つ。DB が失敗し続ける最悪の場合の値でもある | 「243 倍｜5 層の呼び出しの末尾に DB があり、各層が独立に 3 回ずつ試みるとき（3 の 5 乗）、失敗し続ける DB が受ける負荷（Builders' Library の例。最悪の場合）」。NOTE にも「各層 3 回の例」を足す | 不正確 |
| 2 | S140 表・NOTE | 「公開報告 22 件（11 組織）」「11 の組織の公開報告 22 件を分析」 | Huang ほか 2022（OSDI、PDF を自分で開いた）の要旨は "22 metastable failures from 11 different organizations" だが、本文 §2 は "We identify 21 metastable failures (Table 1) that are severe enough to warrant public incident reports" で、表 1 も 21 行。差の 1 件は §4 の Twitter の内部事例とみられる（推定。論文は内訳を明記していない）。「50% 超」「1.5〜73.53 時間」「35%」は表 1（公開報告 21 件）についての記述 | 「22 件（11 組織。うち公開報告は 21 件）の準安定障害のうち…」。または「公開報告 21 件（表 1）のうち…」に統一する | 不正確 |
| 3 | S140 根拠の行 | 「Huang ほか 2022（OSDI）§3」 | 表の 3 つの数字（50% 超、1.5〜73.53 時間、35%）はすべて §2「Metastability in the Wild」にある。§3 は「Metastability Framework」（モデルの節）で、これらの数字は無い（PDF で節見出しと該当行の位置を確認） | 「Huang ほか 2022（OSDI）§2・表 1」 | 不正確 |
| 4 | S191 注記 | 「監査ログを書けないとき業務を止めるかは、定める標準が見つからず」 | S199・S185・S203 が引く NIST SP 800-53 Rev.5 AU-5 が、まさにこの点を扱う標準（警告＋組織が定めた追加の行動。例に「システムの停止」）。拡張管理策 AU-5(4) Shutdown on Failure は、代替の監査機能が無い限り全面停止・部分停止・縮退運転のいずれかを起こすことを定める（csf.tools の Rev.5.2.0 掲載文で確認。CPRT 本体は動的ページで取得できず）。「見つからず」は同じデッキの S199 と食い違う。正しくは「どれを選ぶかを一律に決める標準は無い（AU-5 は組織に委ねる）」 | 「監査ログを書けないときの行動は、NIST SP 800-53 AU-5 が『組織が定める』とし、停止を選ぶ拡張（AU-5(4)）も用意する。どれを選ぶかを一律に決める標準は見つからず、法令と業務の要件で決める（法務に確認）」 | 不正確 |
| 5 | S148 注意 | 「DB には 128 ビットのバイナリで格納する（§6.13、SHOULD）」 | RFC 9562 §6.13 の原文は "Thus, where feasible, UUIDs SHOULD be stored within database applications as the underlying 128-bit binary value."（自分で開いた）。「可能な場合は」の条件が落ちている。同節は続けて、他のシステムでは binary でも text でもよい（MAY）とする | 「DB には、可能なら 128 ビットのバイナリで格納する（§6.13、SHOULD）」 | 不正確 |
| 6 | S193 NOTE、S194 | 「OpenID Connect Core の 10.1.1 節は、検証側が知らない kid を見たら鍵の一覧を取り直す、と定めています」 | §10.1.1（errata set 2、2023-12-15。自分で開いた）は「次の方法で実現できる」という手順の説明で、取り直しの文は "The verifier knows to go back to the jwks_uri location…" と記述的。規範語が付くのは「最近やめた署名鍵を妥当な期間残す」ほうだけ（SHOULD）。「定めています」は規範より強い | 「…取り直す、という入れ替えの手順を示しています。古い鍵を妥当な期間残すことは SHOULD です」 | 不正確 |
| 7 | S194 表 1 行目・NOTE | 「発行後の失効や変更が、exp まで届かない｜RFC 9068 §4」「RFC 9068 は、公開鍵を…jwks_uri から得て…と定めています」 | RFC 9068 §4（自分で開いた）が定めるのは typ・iss・aud・署名・exp の検証（いずれも MUST）。「失効が exp まで届かない」という記述は §4 に無く、手元検証からの帰結（本ガイドの整理）。また jwks_uri での鍵の公開は認可サーバー側の SHOULD で、MUST ではない。NOTE は「止まっても動く」には印を付けているが、「失うもの」のセルは根拠列が RFC のままで、RFC がそう述べたと読める | 根拠列を「RFC 9068 §4（検証の手順）からの本ガイドの整理」とする。NOTE は「鍵は認可サーバーのメタデータの jwks_uri で公開することが推奨（SHOULD）され、検証側は typ、iss、aud、署名、exp を確かめなければならない（MUST）」 | 補足 |
| 8 | S157 | IETF Idempotency-Key 草案の状態 | datatracker（自分で開いた）：最新は -08（2026-10-22 付、失効予定 2027-04-25、Active、WG Document、Standards Track 志向）。「草案 -08」「RFC ではない」「422・409 はいずれも SHOULD」「キーはクライアントが生成」は原文どおり。ただし履歴は、2021-07 に -00、2024-01 に WG Last Call に入り 2024-06 に WG Document へ戻り、-05・-06・-07 が一度ずつ失効している（-07 は 2026-04-18 失効、-08 は半年後）。状態コードを含め内容は変わりうる。なお草案は結論の唯一の根拠にはなっていない（結論「キーは要求を出した端が作る」は DDIA、表は Stripe と並記）ので、使い方は妥当 | 根拠の行を「draft-ietf-httpapi-idempotency-key-header-08（2026-10-22 の草案。2021 年から未成立で、内容は変わりうる）」とする | 補足 |
| 9 | S140 表 | 「1.5〜73.53 時間」 | 論文の本文どおり（"a range of 1.5 to 73.53 hours"）。ただし同じ論文の表 1 には 1.15 時間（AZR2）と 0.16 時間（CAS2）の行があり、本文の下限 1.5 と合わない（論文の中の不整合。PDF で確認）。スライドは本文を正しく写しているので誤りではない | 「1.5〜73.53 時間（論文の本文の記述。表 1 にはこれより短い件もある）」 | 補足 |
| 10 | S140 表 | 「50% 超…再試行が障害を維持していた割合」 | 原文 "affecting more than 50% of the studied incidents" と一致。原文が列挙するのは 11 件（GGL2・GGL3・AWS1〜3・AZR2・AZR4・IBM1・SPF1・SPF2・CAS2）で、21 件に対して 52%、22 件に対してはちょうど 50%。#2 の母数の書き方と合わせる | 「50% 超（公開報告 21 件のうち 11 件）」 | 補足 |
| 11 | S149 | 「Spanner・DynamoDB・Aurora の分析は一覧に無い」 | jepsen.io/analyses（自分で開いた、2026-11-18）で 3 つとも無いことを確認。CockroachDB beta-20160829（2017-02-16）、Redpanda 21.10.1（2022-04-29）も一致。ただし一覧には「Amazon RDS for PostgreSQL 17.4（2025-04-29）」がある。「クラウドのマネージド製品の分析は無い」と読まれないよう足すとよい | 「Spanner・DynamoDB・Aurora の分析は一覧に無い（マネージド製品では Amazon RDS for PostgreSQL 17.4 が 2025-04 にある）」 | 補足 |
| 12 | S149 | 「etcd 3.4.3：KV は厳密に直列化可能」 | Jepsen の原文は "we observed nothing but strict-serializable consistency"、"appear to be strict serializable"（自分で開いた）。観測の範囲での結論で、証明ではない。同じスライドの「正しさは証明できない」と揃える | 「KV は、試験の範囲で厳密な直列化可能性の違反が見つからなかった」 | 補足 |
| 13 | S145 表 3 行目 | 「リピータブルリード」を「応答を続けるなら守れない」に分類 | 表 3 の Unavailable に Repeatable Read（RR）があるのは原文どおり（PDF で確認）。ただし同論文 §4 は "variants of Repeatable Read" は高可用で達成できるとし（Item Cut Isolation など）、守れないのは Adya の定義の RR。Part 9 の用語と読み比べる読者のために足すとよい | セルに「リピータブルリード（Adya の定義。切り口の分離など一部の変種は 1 行目）」 | 補足 |
| 14 | S187 | 「表の現在を指す情報はカタログにしか無い」「（文書 1.12.0）」 | Iceberg 表仕様（GitHub の format/spec.md、自分で開いた）は「原子的な入れ替えが直列化可能な分離の基礎」と書き、版 1〜3 は採用済み、"Version 4 is under active development and has not been formally adopted" で、スライドと一致。ただし仕様の付録には、カタログを使わずファイルシステムの原子的な改名でコミットする方式（File System Tables）も載っている（同じ箇所に deprecated・unsafe・v4 で削除と注記）。また表仕様の版は形式の版（v1〜v4）で、1.12.0 は実装・文書サイトのリリース番号（2026-09-30） | 「カタログを使う構成では、表の現在を指す情報はカタログにしか無い」。根拠の行は「Apache Iceberg 表仕様（形式 v1〜v3 が採用済み。文書サイト 1.12.0 時点）」 | 補足 |
| 15 | S190 | 「属性の名前と意味は、セマンティック規約 1.45.0 が領域ごとに定める」 | 版 1.45.0（2026-11-02 公開）、OTLP 1.11.1（2026-09-29）は GitHub のリリース一覧で確認。シグナルごとの安定度の表は仕様のステータスページ（自分で開いた、日付・版の表示なしも確認）と全セル一致。ただしセマンティック規約も領域ごとに安定度が違う（Stable でない領域がある）点が、この規約の箇所には書かれていない（規約の領域別の安定度は今回開いていない。一般的な知識による指摘） | 「…が領域ごとに定める。規約も領域ごとに安定度が違うので、使う領域の安定度を確かめる」 | 補足 |
| 16 | S158・S163 | 「エンドツーエンド原則」の出典が DDIA のみ | 本文は DDIA 経由で引いており誤りは無い。原典は Saltzer・Reed・Clark「End-to-End Arguments in System Design」ACM TOCS 2(4)、1984。今回この論文は開いていない（書誌は記憶による）。一次資料を並記すると「標準と論文」の扱いが他のスライドと揃う | 根拠の行に原典を足す（書誌を確かめたうえで） | 補足 |
| 17 | S177 | 「Kappa：Kreps の代案」 | 日付（2014-07-02）、2 つの分散システムで保守する負担、手順、保存域 2 倍は原文と一致（自分で開いた）。名前について Kreps は "Maybe we could call this the Kappa Architecture, though it may be too simple of an idea to merit a Greek letter" と控えめに書く。Marz の投稿に Lambda の語が無い点を書くなら、こちらも足すと対称になる | 「名前は Kreps 自身が『Kappa と呼べるかもしれない』と控えめに付けた」 | 補足 |

## 指示にあったが、範囲 C の本文に出てこなかったもの

Raft、PACELC、The Dataflow Model（Akidau ほか）、NIST SP 800-207、NIST SP 800-92 は、S138〜S204 の本文・根拠の行・ノートに出てこない（全文を検索）。確かめる対象が無かった。ウォーターマーク（S174）は Flink の文書だけを根拠にしており、The Dataflow Model は引いていない。

## 確かめて一致した主な事実（すべて原文を自分で開いた）

1. グレー障害の定義「現れ方が微妙で、素早く確定的に検知できない」「核心は見え方の違い（differential observability）」— Huang ほか HotOS 2017（PDF）
2. 準安定障害の定義「きっかけを取り除いても悪い状態が続く」「抜け出すには再起動や負荷の大幅な削減」— Bronson ほか HotOS 2021 §1（PDF）
3. 「4〜10 時間が最多（期間の記載がある件の 35%）」「再試行が 50% 超」「最長 73.53 時間（IBM1）」— Huang ほか OSDI 2022 §2・表 1
4. Builders' Library：誤タイムアウトの率 0.1% と p99.9、再試行は 1 か所、トークンバケット（S139・S140）
5. Yuan ほか OSDI 2014：198 件・5 システム、壊滅的 48 件（24%）、Finding 3（98% が 3 ノード以下）、Finding 9（77% が単体テストで再現）、Finding 10（壊滅的な障害の 92% が致命的でないエラーの処理の誤り）。Finding の番号も一致（PDF）
6. Bailis ほか PVLDB 7(3)：表 3 の 3 区分と各保証の配置、守れない理由の 3 つ（ロストアップデート・ライトスキュー・最新性）、18 の DB のうち既定で直列化可能は 3 つ（§3、"as of January 2013"）（PDF）
7. Gilbert・Lynch 2002 §2.2：可用性は「故障していないノードが受けた要求は必ず応答を返す」（cs.cornell.edu の PDF の抜粋で確認）
8. Jepsen etcd 3.4.3（2020-01-30）：リース 2 秒・5 プロセス・5 秒ごとの一時停止で、応答済みの更新の約 18% を失う。ロックは相互排他を与えない。リビジョンをフェンシングトークンに使える
9. RFC 9562（2024-05）：§2.1（時刻順でない UUID は索引の局所性が悪い）、§8（SHOULD NOT assume hard to guess／MUST NOT be used as security capabilities）、v4 は乱数 122 ビット、v7 は先頭 48 ビットが Unix 時刻のミリ秒、ノード間の単調性の保証は無い。§ 番号と規範語はスライドどおり
10. Snowflake の 2010 年版 README：41＋10＋12 ビット、時計が戻ると最後の発番時刻を過ぎるまで発番を拒む
11. Garcia-Molina・Salem「Sagas」SIGMOD 1987：§1 で「紙幅の都合で集中型のシステムだけを扱う」、サーガは他のサーガの途中の結果を見うる、補償は元の状態に戻すとは限らない、補償が完了できないときは人手の介入（「美しくはないが実用的」）（PDF）
12. Idempotency-Key 草案 -08：キーはクライアントが生成、ペイロード違いは 422、処理中の重複は 409（どちらも SHOULD）、状態は Active の WG Document
13. Marz「How to beat the CAP theorem」：2011-10-13、問い合わせは全データの関数、データは不変、本文に「Lambda」の語は無い
14. OpenTelemetry のステータスページ：トレース Stable×3、メトリクス API Stable・SDK Mixed・プロトコル Stable、ログ Bridge API・SDK・プロトコルが Stable、プロファイルはプロトコルが Development で API・SDK の記載なし。ページに日付・版の表示なし
15. OpenLineage 1.55.0（2026-10-30 公開）：Run・Job・Dataset のイベント、実行イベントは実行時に出す、データ品質の結果を載せる facet がある（検査そのものはしない）
16. NIST SP 800-53 Rev.5 リリース 5.2.0（2025-08-27）：AU-5 の本文（警告＋組織が定めた追加の行動）、例（最古の記録の上書き・システムの停止・生成の停止）、「警告後に追加の行動を取らない選択もできる」、AU-9（不正な参照・変更・削除からの保護）（csf.tools の掲載文と NIST の告知で確認）
17. RFC 7662（2015-10）§4：exp を超えてキャッシュしてはならない（MUST NOT）、キャッシュの長さは鮮度と負荷の釣り合い。RFC 9068 は 2021-10 発行
18. AuthZEN Authorization API 1.0：Final、2026-01-11。PEP が呼び PDP が提供する API を定め、方針の言語・PDP の構成・状態管理は範囲外
19. Sculley ほか（NIPS 2015）：不安定なデータ依存への対策は版つきの写し、代償は古さと複数の版を保つ費用。監視の出発点に予測の偏りと行動の上限（達したら警告と人の調査）（PDF）
20. Google「Rules of ML」：#11・#29・#32・#37 の内容、学習と推論のずれの定義と 3 つの原因、#29 の「全件が無理なら一部でも」

## 確かめなかった範囲

- 観点外（製品・事後報告・書籍・機関）：Kafka 4.4、Flink 2.3、Airflow 3.4.0、PostgreSQL 18、ClickHouse、Debezium 3.7、Temporal、OPA、Cedar 4.6、Kubernetes、Entra、KMS、CloudTrail、Stripe の各記述。Roblox・Cloudflare・OpenAI・Google・CrowdStrike の事後報告の数字。DDIA・『ハードパーツ』・『大規模データ管理』・『プラットフォームエンジニアリング』のページ。CNCF 白書、AWS・Azure の指針、SRE Workbook、Dehghani、Fowler（日付 2005-12-12 は記憶と一致するが開いていない）
- 原典を開かなかった論文：Herlihy・Wing 1990（TOPLAS 12(3) の書誌は記憶と一致）、Attiya・Welch の証明、FLP、Saltzer ほか 1984
- 開いたが一部だけ：Gilbert・Lynch は §2.2 の抜粋のみ（§2.1・§2.3 の本文は見ていない）。NIST AU-5・AU-9 は CPRT 本体ではなく csf.tools の転載。Iceberg は表仕様のみで、REST カタログ仕様（OpenAPI、1 つのクライアント実装でどのカタログにも）は開いていない。OTel は仕様のステータスページのみで、Collector の「mixed」表記、Logs 仕様、OTLP の配送保証の文言、サンプリングの「毎秒 1000 トレース」は開いていない
- Jepsen の「誤りは見つかるが正しさは証明できない」という自己記述の出どころ、RFC 7662 の「キャッシュしてよい」の規範語（MAY かどうか）は確かめていない
