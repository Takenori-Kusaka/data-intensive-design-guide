# 03 スキーマと契約（動かしたまま変えるために、何を契約にするか）

調査日：2026-11-18

## 1. 問い（このノートが答えること。対応する Part）

対応する Part：7（ステップ 5「動かしたまま変えるには、何を契約にするか」）、15（置換と更新）。Part 14 の事故の型（設定の一斉配布）にも材料を渡す。

- 前方互換・後方互換とは何で、ローリング更新ではなぜ両方が要るのか
- Avro・Protocol Buffers・JSON Schema は、互換性について仕様として何を定め、何を定めていないか
- スキーマレジストリ（Confluent・Apicurio・Redpanda 内蔵）は何を検査し、既定は何で、どちらを先に更新させるのか
- API・イベント・データの「契約」を名乗る仕様（OpenAPI・AsyncAPI・CloudEvents・Pact・ODCS）は、それぞれ何を標準化し、何をしないか
- DB のスキーマを止めずに変える手順（expand/contract）と、PostgreSQL 18 でのロック・書き換えの実際
- 設定・ルールの配布が原因の大規模事故は、「読み手と書き手の想定のずれ」と「一斉配布」のどちらだったのか
- 頑健性原則（Postel の法則）は今も勧められるのか。未知のフィールドはどう扱うべきか

## 2. 標準・定義（節番号）

### 2.1 前方互換・後方互換

- **後方互換（backward）**：新しいスキーマ（新しいコード）で、古いスキーマで書かれたデータを読める。**前方互換（forward）**：古いスキーマ（古いコード）で、新しいスキーマで書かれたデータを読める。Confluent の文書の定義は「新しいスキーマの消費者が X と X-1 のデータを処理できる」（後方）、「新しいスキーマで書かれたデータを X-1 の消費者が処理できる」（前方）[4]
- DDIA 2e 5 章も同じ向きで定義している（記憶・要確認。章・ページは書籍の担当が確定する）
- ローリング更新で両方が要る理由（定義からの帰結）：更新の途中は新旧のプロセスが同時に動く。新が旧の書いたものを読む（後方）と同時に、まだ更新されていない旧が新の書いたものを読む（前方）。切り戻しをすれば、旧のコードが新の書いたデータを読む。ログや DB に残ったデータは、書いたコードより長く残る
- 「どちらを先に更新するか」は互換の向きで決まる。後方互換だけなら読み手が先、前方互換だけなら書き手が先、両方なら順序を問わない [4]

### 2.2 Avro（Apache Avro 1.12.0 Specification、「Schema Resolution」）[1]

- 読むときに「書き手のスキーマ」と「読み手のスキーマ」の両方を使い、差を解決する。型が一致しなければエラー
- レコード：フィールドは**名前**で対応づける。順序は違ってよい。書き手にあって読み手にないフィールドは無視。読み手にあって書き手にないフィールドは、読み手側に既定値があればそれを使い、**なければエラー**
- enum：書き手のシンボルが読み手にないとき、読み手の enum に default があればそれを使い、なければエラー
- 昇格：int→long/float/double、long→float/double、float→double、string↔bytes
- union：書き手の選んだ枝に一致する読み手の最初の枝で解決。なければエラー
- 別名（aliases）は Schema Resolution の節ではなく Aliases の節で定義され、実装は使っても「よい」（任意）
- 帰結：フィールドの追加・削除が両方向に安全なのは、既定値を持つフィールドだけ。改名は別名に頼ることになり、実装依存

### 2.3 Protocol Buffers（Language Guide (proto3)「Updating A Message Type」、Proto Best Practices）[2][3]

- フィールドは**番号**で対応づける。変更は 3 種類に分けられている：Wire-unsafe（既存フィールドの番号変更、既存 oneof へのフィールドの移動）、Wire-safe（フィールドの追加、番号を再利用しない削除、enum 値の追加など）、Wire-compatible＝条件つき（int32↔int64、string↔bytes など。読めるが失われることがある）[2]
- 互換規則は**バイナリのワイヤ形式について**の規則。ProtoJSON とテキスト形式は名前を直列化するため、安全な変更の範囲が違う [2]
- 削除したフィールドの番号は reserved にする（文書は “must reserve” と書く）。名前も reserved にすることを勧める。reserved にした番号を再利用すると protoc がエラーにする [2]
- 番号の再利用の帰結として、文書はデバッグ時間の浪費、パースエラー、個人情報の漏えい、データ破損を挙げる [2]
- 未知のフィールド：パーサーが知らないフィールドは保持され、再直列化で出力される。JSON への変換やフィールド単位のコピーでは失われる [2]
- ベストプラクティス [3]：タグ番号を再利用しない／削除したフィールドと enum 値の番号を reserved にする／フィールドの型を変えない／required を足さない／既定値を変えない／repeated から scalar にしない／enum の 0 番は UNSPECIFIED にする／交換にテキスト形式を使わない／**RPC の API と保存用で別のメッセージを使う**／あとで状態が増えそうな 2 値に bool を使わない
- enum 値の追加はワイヤ上は安全だが、網羅的な switch を持つコードを壊しうる [2]

### 2.4 JSON Schema（Draft 2020-12、draft-bhutton-json-schema-01、2022-06-16）[5][6]

- 仕様の本文に、2 つのスキーマの間の互換性（進化）の規則は**ない**。「compatib」「evolution」で本文を検索し、規範的な規則が見つからなかった（付録 D.1 に語彙の作者向けの助言があるのみ）[5]
- `additionalProperties`（§10.3.2.3）：省略すると空のスキーマと同じ＝未知のプロパティに制約なし（開いた内容モデル）。`false` にすると、`properties`・`patternProperties` にないプロパティを拒否する（閉じた内容モデル）[5][6]
- `unevaluatedProperties`（§11.3）：`allOf` などで合成した先の宣言も見て判定する [5][6]
- 未知のキーワードは注釈として扱うべき（SHOULD、§4.3.1・§6.5）[5]
- 帰結：`additionalProperties: false` は書き手の誤りを早く見つけるが、フィールドを足した瞬間に古い読み手の検証が落ちる（前方互換を失う）。省略すれば前方互換だが、同じ名前のフィールドをあとから別の型で足すと衝突する。互換性の判定は仕様ではなく**レジストリの実装**が決めている（3.1）

### 2.5 API・イベント・データの契約の仕様

| 仕様 | 版・日付 | 標準化すること | しないこと |
| --- | --- | --- | --- |
| OpenAPI Specification [10] | 3.2.1（2026-09-10） | HTTP API のインタフェースの記述（パス・操作・スキーマ・webhooks）。Schema Object は JSON Schema 2020-12 を基にする | API の版の間の互換規則・破壊的変更の判定は定めない。`info.version` は記述文書の版で、API の版でも仕様の版でもない |
| AsyncAPI [11] | 3.1.0（3.0.0 の後続） | メッセージ駆動 API の記述（channels・operations〔send／receive〕・messages・bindings）。既定のスキーマ形式は AsyncAPI Schema Object、JSON Schema Draft 07 は必須、Avro 1.9.0・Protobuf などは推奨 | トポロジー・アーキテクチャ・パターンを仮定しない（“does not assume any kind of software topology”）。プロトコル固有のことは bindings に出す。互換規則は定めない |
| CloudEvents [12][13] | 1.0.2（2022-02-06 リリース。main は 1.0.3-wip） | イベントの**封筒**（必須：`id`・`source`・`specversion`・`type`。任意：`datacontenttype`・`dataschema`・`subject`・`time`）と、形式・プロトコルへの対応づけ | `data` の中身の形式は制限しない。非目標：関数の構築と呼び出し、言語別 API、単一の ID／アクセス制御、プロトコル層の経路情報、イベントの永続化、認可・完全性・機密性の仕組み。版づけの方式も強制しない |
| Pact [14][15][16] | 公式文書（2026-11-18 閲覧） | 消費者のテストから契約（具体例）を生成し、提供者を検証する。can-i-deploy で配備の可否を判定 | スキーマではなく例による契約。公開 API や消費者を特定できない API には向かない |
| ODCS [18][19][20] | v3.2.0（2026-09-08） | データ契約の YAML（基本情報・スキーマ・品質・SLA・チーム・役割・価格・サーバーなど） | 検査の実行は道具（Data Contract CLI など）の役目 |

- CloudEvents の `dataschema`：非互換の変更は別の URI にすべき（SHOULD）[12]。Primer は、後方互換の変更では `type` を変えず、非互換の変更では `type` を変え、しばらく新旧の両方を出すことを勧める（任意）[13]
- コンシューマ駆動契約の原典は Ian Robinson の記事（2006-06-12）。提供者契約・消費者契約・消費者駆動契約を区別し、拡張点での「Must Ignore」（知らない要素は無視する）も扱う [17]
- 「データ契約」の定義：ODCS の README は “defines the agreement between a data producer and consumers” と書く [19]。Confluent は上流と下流の合意と定義し、“A schema is only one element of a data contract.” と書く（スキーマ＋整合性の制約＋メタデータ＋規則＋移行規則）[9]。**標準化団体による規範的な定義は見つからなかった**。語の出どころは Andrew Jones（GoCardless、2021-12）と PayPal の Data Contract Template（2023-05 公開、ODCS の元）とされるが、これは二次情報（Wikipedia など）で見ただけで、一次資料は未確認

### 2.6 頑健性原則（Postel の法則）と RFC 9413

- RFC 9413「Maintaining Robust Protocols」（IAB、Informational、2023-06、Thomson・Schinazi）[21]。標準化過程の文書ではなく、IAB の見解
- §2：想定外の入力を許容することは “no longer considered best practice in all scenarios”
- §2.2：拡張性は「未知・不正な入力をどう扱うか」を**仕様で決めておく**ことで得る。実装の寛容さに頼るのは拡張の戦略として良くない
- §4.1：寛容さは欠陥を事実上の標準として定着させ、実装は互いのバグに合わせることになる（プロトコルの腐食）
- §5・§5.1：仕様と実装を能動的に保守する。規定のない状態は致命的エラーにして、欠陥を早く表に出す（virtuous intolerance）
- §3：実装を更新できる環境に限った助言。更新できないソフトウェアには当てはまらない
- このノートの読み方：「未知のフィールドを無視する」のは、**契約に書いた拡張点**であって寛容さではない（Protobuf の未知フィールドの保持、Avro の「読み手にないフィールドは無視」、Must Ignore [17]）。契約にない逸脱（型の違い、上限超え、必須の欠落）を黙って通すのが、RFC 9413 が戒める寛容さにあたる

## 3. 製品ごとの違い（表。公式文書の URL・版・日付）

### 3.1 スキーマレジストリ

| 項目 | Confluent Schema Registry（Confluent Platform 8.4 文書）[4][9] | Apicurio Registry（3.0.x／3.2.x 文書）[7][8] | Redpanda 内蔵 Schema Registry（26.2 文書）[22][23][24][25] |
| --- | --- | --- | --- |
| 対応形式 | Avro・Protobuf・JSON Schema | Avro・Protobuf・JSON Schema・OpenAPI・AsyncAPI・GraphQL・Kafka Connect・WSDL・XML・XSD | Avro・Protobuf・JSON Schema |
| 互換性の種類 | BACKWARD・FORWARD・FULL と各 _TRANSITIVE、NONE | 互換性の規則は同じ 7 値。ほかに妥当性（FULL／SYNTAX_ONLY／NONE）と整合性（参照の検査）の規則 | 同じ 7 値 |
| 既定 | **BACKWARD**（直前の版とだけ比べる） | **規則なし**。全体の規則を設定しなければ何も検査しない | **BACKWARD** |
| 推移的かどうか | 非 TRANSITIVE は直前の 1 版とだけ、TRANSITIVE は全版と比べる | 同左 | 同左 |
| 設定の粒度 | 全体と subject ごと | アーティファクト ＞ グループ ＞ 全体の順に優先（3.2.x）。下位で NONE にして無効化 | 全体と subject ごと |
| 互換性検査の形式ごとの範囲 | Avro・Protobuf は表で規定。Protobuf には BACKWARD_TRANSITIVE を推奨（メッセージ型の追加は前方互換でない）。JSON Schema は内容モデル（開・閉）と compatibilityPolicy（LENIENT／STRICT）で変わる | Avro・Protobuf・JSON Schema・OpenAPI は互換性検査あり。AsyncAPI・GraphQL などは**互換性検査なし**（構文の検査のみ） | JSON Schema は別 subject への外部 `$ref` が未対応 |
| 有償版に限られるもの | スキーマ規則（データ品質・移行規則など）は Enterprise のみ。Community では使えない | —（OSS。Apache 2.0 は記憶・要確認） | **サーバー側のスキーマ ID 検証**、**Schema Registry の認可（ACL）** は Enterprise ライセンスが必要 |
| データ契約の拡張 | メタデータ・規則・移行規則・compatibilityGroup | — | `metadata.properties` のみ対応。`ruleSet`・`metadata.tags`・`compatibilityGroup` などは未対応 |

- どちらを先に更新するか（Confluent の文書）：BACKWARD 系は**消費者を先**、FORWARD 系は**生産者を先**、FULL 系は順序を問わない [4]。既定が BACKWARD である理由として、文書は「消費者をトピックの先頭まで巻き戻せること」を挙げる [4]
- BACKWARD（非推移）の落とし穴：直前の版としか比べないので、v1→v2→v3 の各段は通っても、v3 の読み手が v1 のデータを読めないことがある。ログを先頭から再処理する設計（Part 12）では TRANSITIVE が要る（定義からの帰結）
- Redpanda のコミュニティ版（BSL）に含まれるもの：スキーマの登録・取得、7 種類の互換性検査、参照、モード（READWRITE／READONLY／IMPORT）、コンテキスト（26.2 から既定で有効）[23]。**企業版限定**は、ライセンスの一覧にある「Schema Registry Authorization」「Server-Side Schema ID Validation」の 2 つ [24]。新しいクラスタには 30 日の試用ライセンスがつく [24]
- Redpanda のサーバー側スキーマ ID 検証は、レコードに埋められたスキーマ ID が登録済みかだけを見る。**ペイロードがスキーマに合うかは検査しない** [25]
- 帰結：コミュニティ版の Redpanda では、ブローカーは契約を強制しない。互換性の検査が働くのは**登録時**だけで、登録せずに書く生産者は止められない。強制は生産者側（シリアライザ＋`auto.register.schemas=false`＋CI での互換性検査）に置くことになる。Redpanda の文書も共有・本番環境では自動登録を切ることを勧める [23]

### 3.2 PostgreSQL 18 の ALTER TABLE（公式文書 18「ALTER TABLE」「CREATE INDEX」「19.11 Client Connection Defaults」「13.3 Explicit Locking」）[26][27][28][29]

| 操作 | ロック | 全表の書き換え・走査 | 止めずに行う手順 |
| --- | --- | --- | --- |
| 既定 | 明記がなければ ACCESS EXCLUSIVE。複数の副コマンドは最も強いものになる | — | 1 文に詰め込まない |
| ADD COLUMN（DEFAULT なし、または非 volatile な DEFAULT） | ACCESS EXCLUSIVE（短時間） | 書き換えなし。既定値はメタデータに記録 | そのまま実行できる。ただしロック待ちに注意（下記） |
| ADD COLUMN（volatile な DEFAULT、stored の生成列、identity 列） | ACCESS EXCLUSIVE | **表と索引を全部書き換える** | 列を足す→分割して埋める→制約を足す、に分ける |
| ADD COLUMN（virtual の生成列） | ACCESS EXCLUSIVE | 書き換えなし | — |
| ADD CONSTRAINT（CHECK・外部キー・NOT NULL）＋ NOT VALID | 多くは ACCESS EXCLUSIVE。外部キーは両表に SHARE ROW EXCLUSIVE | 走査しない。すぐコミットできる | NOT VALID で足し、あとで VALIDATE |
| VALIDATE CONSTRAINT | **SHARE UPDATE EXCLUSIVE**（外部キーは参照先に ROW SHARE も） | 全表を走査するが、読み書きは止めない | 上の続き |
| SET NOT NULL | ACCESS EXCLUSIVE（明記なし＝既定） | 通常は全表を走査。NULL がないことを示す有効な CHECK 制約があれば走査を省く。無効な NOT NULL 制約があればそれを検証する | NOT NULL 制約を NOT VALID で足す→VALIDATE、または CHECK を NOT VALID→VALIDATE→SET NOT NULL |
| ALTER COLUMN TYPE | ACCESS EXCLUSIVE | 通常は表と索引を書き換え。バイナリ互換の型（例：text↔varchar）なら表の書き換えは不要 | 新しい列を足して二重書き込み→切り替え（expand/contract） |
| CREATE INDEX | SHARE（書き込みを止める。読み取りは可） | — | CONCURRENTLY を使う |
| CREATE INDEX CONCURRENTLY | SHARE UPDATE EXCLUSIVE（書き込みを止めない） | 表を 2 回走査。失敗すると INVALID の索引が残る（DROP して再実行か REINDEX CONCURRENTLY）。トランザクションブロック内では不可。パーティション表は親に対して直接は不可 | — |
| ADD PRIMARY KEY／UNIQUE … USING INDEX | ACCESS EXCLUSIVE（短時間） | 既存の一意索引を使う。列が NOT NULL なら速い | 先に CREATE UNIQUE INDEX CONCURRENTLY |

- NOT VALID が使える制約は、18 の文書では外部キー・CHECK・NOT NULL（“foreign-key, CHECK, and not-null constraints”）[26]
- `lock_timeout`：既定 0（無効）。ロックの取得ごとに待ち時間を制限する。`statement_timeout` は文全体の時間で、ロック待ちも含む [28]
- ACCESS EXCLUSIVE は SELECT を含むすべてのロックと衝突する [29]。**待っている ACCESS EXCLUSIVE の要求が、後から来た読み書きを待たせる（ロックの行列）ことは、公式文書の該当節には明記が見つからなかった**。広く知られたふるまいだが、根拠は実測（題材 B）で示す
- 帰結：「速い DDL」でも、長いトランザクションの後ろに並ぶと表全体を止めうる。DDL には `lock_timeout` を付けて再試行する、が手順の中心になる（文書の規定からの推論。実測で確かめる）

### 3.3 オンラインスキーマ変更の道具

| 道具 | 対象 | 仕組み | 版・日付 | 位置づけ |
| --- | --- | --- | --- | --- |
| pgroll [30] | PostgreSQL 14 以降 | expand/contract を自動化。物理表の上にビューで「版つきスキーマ」を作り、新旧を同時に見せる。列の変更は新しい列＋埋め戻し＋トリガーで双方向に同期。クライアントは `search_path` で切り替える | v0.16.3（2026-09-08）。Apache 2.0。**0.x** | 新旧のスキーマを同時に提供する。まだ 1.0 前 |
| gh-ost [31] | MySQL | トリガーを使わず、バイナリログを読んで影の表に反映し、最後に表を入れ替える（cut-over） | 版は未確認 | 表の作り直しを本番の負荷を見ながら行う。新旧の同時提供はしない |
| pt-online-schema-change、pg-osc など | MySQL／PostgreSQL | トリガー方式の影の表 | 未確認（記憶・要確認） | — |

- gh-ost 型の「影の表を作って入れ替える」方式でも、最後の入れ替え（rename）は危険な一瞬として残る。GitHub の 2021-11-27 の障害は、その最後の rename で起きた（4 節）[36]

## 4. 事故・失敗例（一次報告）

分類の軸：**(a) 読み手と書き手の想定のずれ**（契約の不一致・検査の漏れ）、**(b) 一斉配布**（段階を踏まずに全体へ届いた）。

| 事故 | 何が起きたか（一次報告の要約） | (a) 想定のずれ | (b) 一斉配布 | 分類 |
| --- | --- | --- | --- | --- |
| CrowdStrike 2024-07-19（Channel File 291、RCA 2024-08-06）[32] | 新しい IPC Template Type は入力を 21 個と定義したが、センサー側のコードが渡すのは 20 個。21 番目に非ワイルドカードの条件を持つ内容が配られ、Content Interpreter が配列の範囲外を読んだ | あり（主因）。フィールド数がコンパイル時に検証されず、実行時の境界検査もなく、Content Validator に論理の誤りがあり、試験は 21 番目がワイルドカードの場合だけだった | あり。所見 6「Template Instances should have staged deployment」。対策に段階配布と顧客側の制御 | **両方**。(a) が引き金、(b) が被害の範囲を決めた |
| Cloudflare 2025-11-18 [33] | ClickHouse の権限変更で、Bot Management の特徴量ファイルを作る問い合わせが重複行を返し、ファイルが約 2 倍に。読む側は特徴量 200 個を上限に事前確保しており、超過でエラー→Rust の `unwrap()` がパニック | あり（主因）。生成側の問い合わせの暗黙の前提（DB 名で絞らない）と、読み手の上限が、どこにも契約として書かれていなかった | あり。ファイルは 5 分ごとに再生成され、全ネットワークへ配られた | **両方**。対策の 1 番目は、自社が生成した設定ファイルの取り込みを、利用者の入力と同じように堅くすること |
| Google Cloud 2025-06-12（Service Control）[34] | 2025-05-29 に入った割り当てポリシー検査のコードに、エラー処理もフィーチャーフラグもなかった。2025-06-12 に意図しない空欄を含むポリシーがリージョンの Spanner の表に書かれ、数秒で全世界へ複製。null 参照で全リージョンがクラッシュループ | あり。読み手が空欄を想定していなかった | あり（被害の範囲を決めた）。対策に、全世界へ複製されるデータを検証の時間をとって段階的に伝える、を挙げる | **両方**。コードは段階的に配っていたが、そのコードを通るデータが来るまで欠陥が表に出なかった（この一文は記憶・要確認） |
| Cloudflare 2025-12-05 [35] | WAF の試験用ルールを止める設定を、段階配布をしない全体設定の仕組みで配布。`execute` アクションのルールに killswitch を当てるのは初めてで、Lua が nil を参照して 500 を返した。約 25 分、HTTP トラフィックの約 28% | あり（未使用だった組み合わせ） | あり（主因として自ら挙げる）。同時に行ったバッファの変更は段階配布だった | **両方**。同じ変更でも、コードは段階、設定は一斉だった |
| GitHub 2021-11-27 [36] | 大きな MySQL の表のスキーマ移行の最後の rename で、読み取りレプリカの多くがセマフォのデッドロックに。2 時間 50 分 | —（互換性ではなく、変更の操作そのもの） | 一部。対策に、移行を 1 シャードでカナリア実行できるようにする | **変更操作の危険**。オンライン変更の道具を使っても、最後の入れ替えは残る |
| Knight Capital 2012-08-01（SEC の命令 34-70694、2013-10-16。**規制当局の文書で、事業者自身の報告ではない**）[37] | 新しい RLP のコードが、かつて Power Peg を起動していた**フラグを別の意味で再利用**した。8 台のうち 1 台に新しいコードが入らず、その 1 台は再利用されたフラグで古いコードを動かした（¶13〜16） | あり（主因）。同じフラグの意味が新旧で違った | 逆。配備が不完全で新旧が混在した | **(a)**。「番号・フラグを再利用しない」の実例。新旧が混在する間は、古い意味も生きている |

- 3 つの指定事故（CrowdStrike・Cloudflare 2025-11-18・Google Cloud 2025-06-12）は、どれも**両方**だった。共通の形：コードは段階的に配られていたか、すでに配備済みだった。引き金は**データ（ルール・特徴量ファイル・ポリシー）**で、それは一斉に届いた。読み手は、想定外のデータを受けたときに「以前の良い版で動き続ける」のではなく、落ちた
- 3 件とも、対策に「読み手の側の検査」（境界検査、取り込みの堅牢化、エラー処理と fail open）と「データの段階配布」の両方を挙げている [32][33][34]
- Stripe 2019-07-10 [38]：DB の副版の更新で入った選出の欠陥が 3 か月後に表面化し、復旧のために選出プロトコルを前の版に戻したところ、最近入れた設定と組み合わさって 2 度目の停止を起こした。スキーマの事故ではないが、「切り戻した版」と「後から入った設定」の組み合わせは試験されていない、という型の例
- スキーマレジストリの互換性検査をすり抜けたことが原因と事業者自身が書いた事後報告は、今回の調査では**見つからなかった**

## 5. 権威の推奨と位置づけ（規範か任意か）

| 出どころ | 何を勧めるか | 性格 |
| --- | --- | --- |
| Protocol Buffers 公式 [2][3] | 番号の再利用禁止、reserved、型・既定値を変えない、API 用と保存用のメッセージを分ける | 製品の公式の指針。reserved は文書上 “must”、番号の再利用はコンパイラが検出 |
| Avro 仕様 [1] | Schema Resolution の規則 | 仕様（規範）。別名の利用は任意 |
| RFC 9413 [21] | 寛容さに頼らず、未知の入力の扱いを仕様に書き、能動的に保守する | IAB の Informational。規範ではない。更新できる実装が対象 |
| CloudEvents Primer [13] | 非互換の変更では `type` を変え、新旧を並行して出す | 非規範の手引き |
| Fowler サイト「ParallelChange」（Danilo Sato、2014-05-13）[39] | 後方非互換の変更を expand→migrate→contract の 3 段に分ける。費用は 2 版の並行維持と、contract をやり残す危険 | 実務家の記事（任意） |
| 「Evolutionary Database Design」（Sadalage・Fowler、2003-01、2016-05 全面改訂）[40] | DB の変更はすべて移行スクリプトにする。破壊的な変更には移行期間（新旧の両方のアクセスを支える）を置く。複数のアプリが DB を共有するなら、DB を別リポジトリにしてコンシューマ駆動契約で試験する | 実務家の記事（任意） |
| Thoughtworks Technology Radar | Consumer-driven contract testing：**Adopt**（2015-05、2015-11、2016-11。現行の号には載っていない）[41]。Pact & Pacto：Trial（2015-01）、Pactflow：Trial（2022-03）[42]。Data Contract CLI：**Trial**（2025-11。現行の号には載っていない）[43]。ODCS：**Adopt**（2026-11、Languages & Frameworks）[44] | 一企業の経験に基づく意見。網羅的な調査ではない。「データ契約」そのものを技法として載せた項目は見つからなかった |
| Pact 公式 [15] | 消費者と提供者の両方を自分たちで制御できる場合に向く。公開 API、消費者を特定できない場合、相手が Pact を使わない場合には向かない | 製品の公式文書 |
| ODCS／Bitol [18][19][20] | データ契約を YAML で宣言する標準。v3.2.0（2026-09-08）。Bitol は LF AI & Data のプロジェクトで、サイトは Graduated と表示。Radar は 2026-07 に卒業と書く | 業界団体の標準（任意）。公的な標準ではない |
| Data Contract CLI [45] | ODCS を主形式とし、lint・import・export・test（実データに接続してスキーマと品質を検査）。v1.2.11（2026-11-17）、MIT。旧 Data Contract Specification は legacy 扱い | OSS の道具 |

## 6. 設計判断の分かれ目（何を選ぶと何を得て何を失うか。表）

| 判断 | 選択肢 | 得るもの | 失うもの・条件 |
| --- | --- | --- | --- |
| 互換性の水準 | BACKWARD（既定） | 読み手を先に更新すれば安全。古いデータを新しい読み手で読める | 古い読み手は新しいデータを読めない。更新の順序を守る運用が要る |
|  | FORWARD | 書き手を先に出せる | 読み手を巻き戻して古いデータを読む用途に弱い |
|  | FULL | 更新の順序を問わない。ローリング更新・切り戻しと相性がよい | 許される変更は、既定値つき（任意）フィールドの追加・削除にほぼ限られる |
|  | _TRANSITIVE をつける | ログの先頭からの再処理・長期保存に耐える | 過去のすべての版に縛られる。古い誤りを直しにくい |
|  | NONE | 自由 | 壊れたことを消費者の障害で知る |
| 直列化の形式 | Avro | 書き手のスキーマと突き合わせて解決。既定値で両方向に進化 | 読むのに書き手のスキーマが要る（レジストリへの依存）。改名は別名で実装依存 |
|  | Protobuf | 番号で対応づけ、未知フィールドを保持。レジストリなしでも読める | 番号の管理が規律頼み。JSON にすると規則が変わる |
|  | JSON Schema | 人が読める。既存の JSON にあとから当てられる | 互換性の規則が仕様になく、レジストリの実装依存 |
| JSON の内容モデル | 開（`additionalProperties` 省略） | 前方互換（知らないフィールドを通す） | 打ち間違いを通す。あとで同名の別の型を足すと衝突 |
|  | 閉（`false`） | 書き手の誤りを早く検出 | フィールドの追加が古い読み手を壊す |
| 契約の検査をどこに置くか | CI（登録前の互換性検査） | 配備の前に止まる | CI を通らない書き手は止められない |
|  | レジストリ（登録時） | 中央で一貫 | 登録しない書き手は止められない。レジストリが単一障害点になる |
|  | ブローカー（書き込み時） | 書き手を選ばず強制 | Redpanda では企業版限定で、しかも ID の存在しか見ない |
|  | 読み手（取り込み時） | 最後の砦。事故 3 件の対策はここ | 拒否したあとの動作（前の良い版で続ける／止まる）を決めておく必要 |
| API の契約 | スキーマ（OpenAPI／AsyncAPI） | 全体を宣言。消費者が不明でも使える | 実際に誰が何を使っているかは分からない。互換の判定は別の道具 |
|  | 例による契約（Pact） | 使われている部分だけを守る。使われていない部分は自由に変えられる | 消費者を全員把握し、協力できる場合に限る |
| DB の非互換な変更 | 一度に変える（停止あり） | 単純 | 停止時間、切り戻しが難しい |
|  | expand/contract を手で | 各段階で配備・切り戻しができる | 二重書き込みの期間、contract のやり残し |
|  | pgroll などで自動化 | 新旧のスキーマを同時に提供 | 道具への依存（0.x）、ビューとトリガーの負荷 |
| 設定・ルールの配布 | 即時に全体へ | 脅威への対応が速い | 誤りが全体に同時に届く（4 節） |
|  | 段階配布＋健全性の確認 | 被害を最初の段に閉じ込める | 反映が遅れる。緊急用の経路をどうするかが残る |
| 未知の入力 | 契約に書いた範囲で無視（Must Ignore） | 前方互換 | 「無視してよいもの」の定義が要る |
|  | 契約外も黙って受ける | 目先の相互運用 | 欠陥が事実上の標準になる（RFC 9413 §4.1） |
|  | 契約外は拒否して目立たせる | 欠陥が早く見つかる | 拒否が全体停止にならない設計が要る |

## 7. 設計レビューで問うこと（問い｜なぜ問うか｜危ない兆候）

| # | 問い | なぜ問うか | 危ない兆候 |
| --- | --- | --- | --- |
| 1 | この変更は後方互換か、前方互換か。配備の途中で新旧が混ざる時間に、どちらがどちらを読むか | ローリング更新と切り戻しは両方向を要する | 「全部同時に更新するから大丈夫」 |
| 2 | 生産者と消費者の、どちらを先に更新する決まりか。それは互換性モードと合っているか | BACKWARD は消費者が先、FORWARD は生産者が先 [4] | 順序が決まっていない。モードを誰も知らない |
| 3 | レジストリの互換性モードは何か。既定のままか。意図して選んだか | Confluent・Redpanda の既定は BACKWARD、Apicurio の既定は規則なし | 「Apicurio を入れたので検査されている」 |
| 4 | ログを先頭から再処理する・長く保存するデータに、TRANSITIVE を使っているか | 非推移は直前の版としか比べない | 再処理を設計に含むのに BACKWARD のまま |
| 5 | 互換性の検査は CI で、マージの前に走るか | 登録時に落ちるのは配備の途中 | 本番のレジストリへの自動登録が有効 |
| 6 | 登録せずに書く生産者を、何が止めるか | コミュニティ版の Redpanda はブローカーで強制しない [24][25] | 「レジストリがあるから壊れたデータは来ない」 |
| 7 | 削除したフィールドの番号・名前・フラグを reserved にしたか。再利用していないか | 再利用は検出できない破損と漏えいを生む [2][37] | 「もう誰も使っていないはず」 |
| 8 | 新しい必須フィールド、既定値のないフィールド、enum の値を足していないか。古い読み手はどうふるまうか | Avro は既定値がなければエラー、enum は網羅的な分岐を壊す [1][2] | enum に default や UNSPECIFIED がない |
| 9 | JSON のスキーマは開いているか閉じているか。それは意図か | `additionalProperties` が前方互換を決める [5] | 一部のスキーマだけ `false` |
| 10 | 未知のフィールドを、読み手は無視するのか、保持して渡すのか、拒否するのか。仕様に書いてあるか | 中継するサービスが未知のフィールドを落とすと、下流でデータが消える [2] | 読んで、オブジェクトに詰め直して、書き戻している |
| 11 | API 用のスキーマと保存用のスキーマは別か | 保存形式の変更が API の利用者に漏れる [3] | DB の行の型をそのまま API とイベントに出している |
| 12 | このイベント・API の消費者は誰か。一覧はあるか。消費者が何を使っているかを知る手段は | 消費者を知らなければ、壊したことを知る手段がない | 「たぶん誰も使っていない」で削除 |
| 13 | 非互換の変更をするとき、新旧を並行して出す期間と、旧をやめる条件・期日は | expand/contract は contract をやり残すと負債になる [39] | 旧の版の利用状況を測っていない |
| 14 | この DDL はどのロックを取り、表を書き換えるか、全表を走査するか | 3.2 の表。volatile な DEFAULT・型変更は書き換え | ORM の移行をそのまま本番に流す |
| 15 | DDL に `lock_timeout` を設定し、失敗時に再試行するか。長いトランザクションを監視しているか | 既定は無制限に待つ [28][29] | `lock_timeout` が 0 のまま |
| 16 | 制約は NOT VALID→VALIDATE、索引は CONCURRENTLY で足しているか。INVALID の索引が残っていないか | 強いロックを持つ時間を短くする [26][27] | 移行ツールが 1 トランザクションに全部包む |
| 17 | 設定・ルール・特徴量・ポリシーも、コードと同じく段階的に配っているか | 事故 3 件はデータの一斉配布 [32][33][34] | 「設定の変更なので配備の手順は不要」 |
| 18 | 読み手は、想定外の設定（大きすぎる、空欄、項目数が違う）を受けたとき、どうなるか。前の良い版で動き続けるか | 3 件とも読み手が落ちた | 上限・必須を読み手が検査していない。`unwrap` や境界検査の欠落 |
| 19 | 設定の書き手と読み手の間の前提（上限、項目数、必須）は、どこに書かれ、何が検査するか | 暗黙の前提は、別の変更で破られる [33] | 生成する側と読む側が別のチームで、スキーマがない |
| 20 | 切り戻したとき、その古い版は、いまあるデータ・設定を読めるか | 切り戻しは前方互換を要する。Stripe の 2 度目の停止 [38] | 切り戻しの試験が「コードだけ戻す」 |

## 8. ケーススタディで測れること・測れないこと

測れる（題材 B。Redpanda 内蔵 Schema Registry＋PostgreSQL 18）：

- 互換性の検査なし（NONE）／あり（BACKWARD・FULL・_TRANSITIVE）で、同じ一連のスキーマ変更（任意フィールドの追加、必須フィールドの追加、削除、型の変更、改名）を流し、登録が拒否された数と、拒否されずに壊れた消費者の数を数える
- 非推移と推移の差：v1→v2→v3 が段ごとには通り、v3 の読み手が v1 を読めない例を作り、先頭からの再処理で落ちる件数を数える
- 更新の順序：BACKWARD で生産者を先に出した場合と消費者を先に出した場合の、失敗したメッセージの数
- Avro・Protobuf・JSON Schema（開・閉）で、同じ変更の判定がどう変わるか（Redpanda の実装での結果として記録）
- レジストリを通さずに書く生産者が、コミュニティ版の Redpanda では止められないこと
- PostgreSQL 18：ADD COLUMN（定数の DEFAULT／volatile な DEFAULT）、SET NOT NULL（素のまま／CHECK NOT VALID→VALIDATE 経由）、CREATE INDEX（通常／CONCURRENTLY）、ALTER COLUMN TYPE について、書き込みが止まった時間と待たされた問い合わせの数
- ロックの行列：長いトランザクション＋ALTER TABLE＋後続の SELECT で、`lock_timeout` の有無による差（公式文書に明記が見つからなかったふるまいを実測で示す）
- expand/contract（列の追加→二重書き込み→埋め戻し→読み替え→削除）を、新旧のアプリを混在させて流し、各段階での失敗の数
- 設定の配布の模擬：上限を超える設定ファイルを、読み手の検査あり／なし、一斉／段階で配り、止まった読み手の数を比べる（除去実験の 1 要素）

測れない・測らない：

- Confluent Schema Registry、Apicurio Registry の実際のふるまい（文書に基づく比較のみ。未検証と明記）
- Redpanda のサーバー側スキーマ ID 検証と Schema Registry の認可（企業版限定。30 日の試用ライセンスで試せるが、再現性のため基準の構成には入れない）
- Confluent のデータ契約の規則・移行規則（Enterprise 限定）
- 大きな表（数億行）での書き換え時間の絶対値。単一ホストの相対比較にとどまる
- pgroll・gh-ost（容量しだい。入れるなら pgroll だけ）
- Pact、Data Contract CLI の運用上の効果（道具の動作確認まではできるが、組織の規模での効果は測れない）

## 9. 未確定・要確認

- DDIA 2e 5 章の前方・後方互換の定義の章・節・ページ（書籍の担当に確認）
- Avro の最新版：1.12.0 の仕様を本文確認。文書サイトの版の一覧では 1.12.0 が最新だったが、それより新しいリリースがないことまでは確かめていない
- Confluent の文書の後半（JSON Schema の内容モデルごとの許される変更の表、推移性の説明の本文）は、ページが長く取得できなかった。前半の要約に基づく
- Apicurio Registry：3.0.x の規則の参照ページと 3.2.x の入門ページを見た。3.2.x が最新の系列か、3.x での互換性検査の実装の差は未確認。ライセンスは記憶
- OpenAPI 3.2.1 の日付（2026-09-10）は取得結果の冒頭による。Schema Object の節の本文は取得できず、JSON Schema 2020-12 との関係は冒頭の記述と記憶に基づく
- AsyncAPI 3.1.0 で 3.0.0 から何が変わったか（リリースノート未読）
- CloudEvents：リリース済みの最新は 1.0.2（GitHub のリリース一覧）。main の文書は 1.0.3-wip
- PostgreSQL：ロックの行列のふるまいは公式文書の該当節に明記なし。SET NOT NULL のロック水準も明記なし（既定の ACCESS EXCLUSIVE と読んだ）
- CrowdStrike の RCA：PDF の本文は抽出の断片で確認（所見 2・3・4・5 の本文と、所見 1〜6 の見出し）。発生時刻（2024-07-19 04:09 UTC）は記憶・要確認
- Google Cloud 2025-06-12：「コードは段階的に配備されたが、該当の経路は実行されなかった」という記述は今回の取得結果に含まれず、記憶・要確認。影響時間は状況ページ（10:51〜18:18 PDT）と報告本文（約 3 時間）で表記が分かれる
- 「データ契約」の語の出どころ（Andrew Jones 2021-12、PayPal 2023-05）は二次情報のみ。一次資料（GoCardless のブログ、PayPal のリポジトリ）は未確認
- Thoughtworks Radar：ODCS の Adopt（2026-11）は項目ページで本文確認。Pact 単独の項目のページは開けず、「Pact & Pacto」「Pactflow」は検索結果の本文で確認
- gh-ost・pt-online-schema-change の最新版と保守の状況
- Knight Capital は SEC の命令で、事業者自身の報告ではない。使うなら「規制当局の認定した事実」と明記する

## 10. 結論（スライドに書くこと。箇条書き 15〜30 個、各項目に出典の番号）

1. 後方互換は「新しい読み手が古いデータを読める」、前方互換は「古い読み手が新しいデータを読める」[4]
2. ローリング更新と切り戻しでは新旧が同時に動くので、両方向の互換が要る。データは書いたコードより長く残る（定義からの帰結、[4]）
3. どちらを先に更新するかは互換の向きで決まる。BACKWARD は消費者が先、FORWARD は生産者が先、FULL は順序を問わない [4]
4. Avro は名前で対応づけ、書き手と読み手のスキーマを突き合わせる。両方向に安全なのは既定値つきのフィールドの追加・削除 [1]
5. Protobuf は番号で対応づける。番号は再利用せず、削除したら reserved にする。再利用は検出できない破損と漏えいを生む [2][3]
6. Protobuf の互換規則はバイナリ形式のもの。JSON やテキストにすると名前が契約になり、規則が変わる [2][3]
7. JSON Schema の仕様は互換性の規則を定めていない。判定はレジストリの実装が決める [4][5]
8. `additionalProperties` を省略すれば前方互換、`false` にすれば厳密。どちらも代償がある。意図して選ぶ [5][6]
9. Confluent と Redpanda のレジストリの既定は BACKWARD（直前の版とだけ比べる）。Apicurio は既定では何も検査しない [4][8][23]
10. ログを先頭から再処理する設計なら、非推移の BACKWARD では足りない。TRANSITIVE を選ぶ [4]
11. Redpanda のコミュニティ版は 3 形式と 7 つの互換性モードを備える。サーバー側のスキーマ ID 検証とレジストリの認可は企業版限定 [22][23][24]
12. Redpanda のサーバー側検証は ID が登録済みかを見るだけで、中身は検査しない。契約の強制は生産者側と CI に置く [25]
13. OpenAPI・AsyncAPI はインタフェースの「記述」の標準で、版の間の互換規則は定めない。互換の判定は別の道具と運用の仕事 [10][11]
14. CloudEvents が標準化するのは封筒（必須 4 属性）で、中身（data）の形式と版づけは標準化しない [12][13]
15. 非互換のイベントは `type` を変え、新旧を並行して出す（CloudEvents Primer、非規範）[13]
16. コンシューマ駆動契約は「使われている部分だけを守る」技法。消費者を把握し協力できる範囲で効く。公開 API には向かない [14][15][17]
17. Thoughtworks Radar では、コンシューマ駆動契約テストは Adopt（2015〜2016。現行の号には非掲載）、ODCS は Adopt（2026-11）、Data Contract CLI は Trial（2025-11）[41][43][44]
18. データ契約は、スキーマに品質・SLA・所有者・利用条件を足した、生産者と消費者の合意。スキーマはその一部 [9][19]
19. ODCS は v3.2.0（2026-09-08）。LF AI & Data の Bitol が管理する業界標準で、公的な標準ではない [18][19][20]
20. 「データ契約」の規範的な定義を持つ標準化団体の文書は見つからなかった。定義は ODCS と各ベンダーのもの [9][19]
21. 非互換な変更は expand→migrate→contract の 3 段に分ける。各段で配備も切り戻しもできる。代償は 2 版の並行維持 [39][40]
22. PostgreSQL 18 の ALTER TABLE は、明記がなければ ACCESS EXCLUSIVE を取る。定数の DEFAULT つきの列追加は書き換えなし、volatile な DEFAULT・型変更は全表の書き換え [26]
23. 制約は NOT VALID で足して VALIDATE（SHARE UPDATE EXCLUSIVE）、索引は CONCURRENTLY。強いロックを持つ時間を短くする [26][27]
24. `lock_timeout` の既定は 0（無制限に待つ）。DDL には必ず設定し、失敗したら再試行する [28]
25. オンライン変更の道具を使っても、最後の入れ替えは危険な一瞬として残る（GitHub 2021-11-27）[31][36]
26. 設定・ルール・特徴量・ポリシーもデータで、スキーマと契約が要る。CrowdStrike・Cloudflare・Google Cloud の 3 件は、どれも「想定のずれ」と「一斉配布」の両方だった [32][33][34]
27. 3 件に共通：コードは段階的に配られていたが、引き金のデータは一斉に届き、読み手は想定外の入力で落ちた [32][33][34]
28. 対策も共通：読み手の側の検査（上限・項目数・必須）と、データの段階配布。自分たちが生成した設定も、利用者の入力と同じように疑う [32][33][34][35]
29. フラグ・番号の意味を変えて再利用すると、新旧が混ざった瞬間に古い意味が動く（Knight Capital、SEC の認定）[37]
30. 頑健性原則は無条件の最良の慣行ではない。未知の入力の扱いを契約に書く。契約にある「無視」は拡張点、契約にない逸脱を黙って通すのは腐食の入口 [21][17]

## 11. 出典（番号｜題名｜発行者｜版・日付｜URL｜確認の深さ）

| # | 題名 | 発行者 | 版・日付 | URL | 確認の深さ |
| --- | --- | --- | --- | --- | --- |
| 1 | Apache Avro Specification「Schema Resolution」 | Apache Software Foundation | 1.12.0（ページの最終更新 2026-11-15） | https://avro.apache.org/docs/1.12.0/specification/ | 本文確認 |
| 2 | Language Guide (proto3)「Updating A Message Type」「Unknown Fields」「Deleting Fields」「Consequences of Reusing Field Numbers」 | Google（protobuf.dev） | 日付の記載なし（© 2026）。2026-11-18 閲覧 | https://protobuf.dev/programming-guides/proto3/ | 本文確認 |
| 3 | Proto Best Practices（Dos and Don'ts） | Google（protobuf.dev） | 2026-11-18 閲覧 | https://protobuf.dev/best-practices/dos-donts/ | 本文確認 |
| 4 | Schema Evolution and Compatibility for Schema Registry | Confluent | Confluent Platform 8.4 文書。2026-11-18 閲覧 | https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html | 本文確認（前半のみ。後半は取得できず） |
| 5 | JSON Schema: A Media Type for Describing JSON Documents（Core） | JSON Schema（Internet-Draft） | Draft 2020-12、draft-bhutton-json-schema-01、2022-06-16 | https://json-schema.org/draft/2020-12/json-schema-core | 本文確認 |
| 6 | Understanding JSON Schema「object」 | JSON Schema | 2026-11-18 閲覧 | https://json-schema.org/understanding-json-schema/reference/object | 本文確認 |
| 7 | Apicurio Registry rule reference | Apicurio（Red Hat） | 3.0.x 文書 | https://www.apicur.io/registry/docs/apicurio-registry/3.0.x/getting-started/assembly-rule-reference.html | 本文確認 |
| 8 | Apicurio Registry content rules（入門） | Apicurio（Red Hat） | 3.2.x 文書 | https://www.apicur.io/registry/docs/apicurio-registry/3.2.x/getting-started/assembly-intro-to-registry-rules.html | 本文確認 |
| 9 | Data Contracts for Schema Registry | Confluent | Confluent Platform 文書（current）。2026-11-18 閲覧 | https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html | 本文確認（前半のみ） |
| 10 | OpenAPI Specification | OpenAPI Initiative（Linux Foundation） | v3.2.1、2026-09-10 | https://spec.openapis.org/oas/latest.html | 本文確認（冒頭のみ。Schema Object の節は未読） |
| 11 | AsyncAPI Specification | AsyncAPI Initiative（Linux Foundation） | 3.0.0 と 3.1.0 | https://www.asyncapi.com/docs/reference/specification/v3.1.0 | 本文確認（末尾の約 1 割は未読） |
| 12 | CloudEvents Specification | CNCF | v1.0.2（2022-02-06 リリース） | https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md | 本文確認 |
| 13 | CloudEvents Primer「Design Goals」「Versioning of CloudEvents」 | CNCF | main（1.0.3-wip）。2026-11-18 閲覧。非規範 | https://github.com/cloudevents/spec/blob/main/cloudevents/primer.md | 本文確認 |
| 14 | Pact Docs: Introduction | Pact Foundation | 2026-11-18 閲覧 | https://docs.pact.io/ | 本文確認 |
| 15 | Pact Docs: When to use Pact（What is Pact good for?） | Pact Foundation | 2026-11-18 閲覧 | https://docs.pact.io/getting_started/what_is_pact_good_for | 本文確認 |
| 16 | Pact Docs: Can I Deploy | Pact Foundation | 2026-11-18 閲覧 | https://docs.pact.io/pact_broker/can_i_deploy | 本文確認 |
| 17 | Consumer-Driven Contracts: A Service Evolution Pattern | Ian Robinson（martinfowler.com） | 2006-06-12 | https://martinfowler.com/articles/consumerDrivenContracts.html | 本文確認 |
| 18 | Open Data Contract Standard（文書サイト） | Bitol（LF AI & Data） | latest（v3.1.0 以降の節立て） | https://bitol-io.github.io/open-data-contract-standard/latest/ | 本文確認 |
| 19 | open-data-contract-standard（README とリリース一覧） | Bitol（LF AI & Data） | v3.2.0、2026-09-08（GitHub API で日付を確認） | https://github.com/bitol-io/open-data-contract-standard | 本文確認 |
| 20 | Bitol（プロジェクトのサイト） | Bitol（LF AI & Data） | 2026-11-18 閲覧。「Graduated」と表示 | https://bitol.io/ | 本文確認 |
| 21 | RFC 9413: Maintaining Robust Protocols | IAB（M. Thomson、D. Schinazi） | 2023-06、Informational | https://www.rfc-editor.org/rfc/rfc9413.html | 本文確認 |
| 22 | Redpanda Schema Registry（概要） | Redpanda Data | 26.2 文書（最新タグ v26.2.7） | https://docs.redpanda.com/current/manage/schema-reg/schema-reg-overview/ | 本文確認 |
| 23 | Use the Schema Registry API | Redpanda Data | 26.2 文書 | https://docs.redpanda.com/current/manage/schema-reg/schema-reg-api/ | 本文確認 |
| 24 | Redpanda Licenses and Enterprise Features | Redpanda Data | 26.2 文書 | https://docs.redpanda.com/current/get-started/licensing/overview/ | 本文確認 |
| 25 | Server-Side Schema ID Validation | Redpanda Data | 26.2 文書 | https://docs.redpanda.com/current/manage/schema-reg/schema-id-validation/ | 本文確認 |
| 26 | PostgreSQL 18 Documentation「ALTER TABLE」 | PostgreSQL Global Development Group | 18 | https://www.postgresql.org/docs/18/sql-altertable.html | 本文確認 |
| 27 | PostgreSQL 18 Documentation「CREATE INDEX」（Building Indexes Concurrently） | 同上 | 18 | https://www.postgresql.org/docs/18/sql-createindex.html | 本文確認 |
| 28 | PostgreSQL 18 Documentation「Client Connection Defaults」（lock_timeout ほか） | 同上 | 18 | https://www.postgresql.org/docs/18/runtime-config-client.html | 本文確認 |
| 29 | PostgreSQL 18 Documentation「13.3 Explicit Locking」 | 同上 | 18 | https://www.postgresql.org/docs/18/explicit-locking.html | 本文確認 |
| 30 | pgroll（README） | Xata | v0.16.3、2026-09-08（GitHub API） | https://github.com/xataio/pgroll | 本文確認 |
| 31 | gh-ost（README） | GitHub | 版は未確認。2026-11-18 閲覧 | https://github.com/github/gh-ost | 本文確認 |
| 32 | External Technical Root Cause Analysis — Channel File 291 | CrowdStrike | 2024-08-06（PDF、12 ページ） | https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf | 本文確認（抽出できた断片と目次。全文は未読） |
| 33 | Cloudflare outage on November 18, 2025 | Cloudflare | 2025-11-18 | https://blog.cloudflare.com/18-november-2025-outage/ | 本文確認 |
| 34 | Google Cloud incident report（Service Control、2025-06-12） | Google Cloud | 2025-06 | https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW | 本文確認 |
| 35 | Cloudflare outage on December 5, 2025 | Cloudflare | 2025-12-05 | https://blog.cloudflare.com/5-december-2025-outage/ | 本文確認 |
| 36 | GitHub Availability Report: November 2021 | GitHub | 2021-12 | https://github.blog/news-insights/company-news/github-availability-report-november-2021/ | 本文確認 |
| 37 | In the Matter of Knight Capital Americas LLC（Release No. 34-70694） | U.S. SEC（規制当局） | 2013-10-16 | https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf | 本文確認（¶13〜16 の断片。全文は未読） |
| 38 | Root cause analysis: significantly elevated error rates on 2019-07-10 | Stripe | 2019-07 | https://stripe.com/rcas/2019-07-10 | 本文確認 |
| 39 | ParallelChange | Danilo Sato（martinfowler.com） | 2014-05-13 | https://martinfowler.com/bliki/ParallelChange.html | 本文確認 |
| 40 | Evolutionary Database Design | Pramod Sadalage、Martin Fowler | 2003-01、2016-05 全面改訂 | https://martinfowler.com/articles/evodb.html | 本文確認 |
| 41 | Technology Radar: Consumer-driven contract testing | Thoughtworks | Adopt（2015-05、2015-11、2016-11） | https://www.thoughtworks.com/radar/techniques/consumer-driven-contract-testing | 本文確認 |
| 42 | Technology Radar: Pact & Pacto／Pactflow | Thoughtworks | Trial（2015-01）／Trial（2022-03） | https://www.thoughtworks.com/en-us/radar/tools/pact-pacto 、https://www.thoughtworks.com/en-us/radar/tools/pactflow | 検索結果に出た本文のみ（ページは直接開いていない） |
| 43 | Technology Radar: Data Contract CLI | Thoughtworks | Trial（2025-11、Vol.33） | https://www.thoughtworks.com/en-us/radar/tools/data-contract-cli | 本文確認 |
| 44 | Technology Radar: Open Data Contract Standard (ODCS) | Thoughtworks | Adopt（2026-11-04、Vol.35） | https://www.thoughtworks.com/en-us/radar/languages-and-frameworks/open-data-contract-standard-odcs | 本文確認 |
| 45 | Data Contract CLI | datacontract.com（OSS） | v1.2.11、2026-11-17（GitHub API）。MIT | https://cli.datacontract.com/ | 本文確認 |
