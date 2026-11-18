# verify_p01 ― Part 1「データ指向と 4 つの性質」の確かめ直し

確認日：2026-11-18。対象：`deck/p01.js`（扉 1 枚＋本文 11 枚）。書籍は `research/books/text/<ISBN>.txt` を直接読んだ。Web は一次資料の URL を開いた（WebFetch の抽出で該当箇所の原文を引用させて確認。ISO のプレビューと CrowdStrike の RCA は PDF を pdftotext でテキスト化して目視）。

| スライドの題 | 事実 | 出典（URL か書籍ページ） | 確かめ方 | 結果 |
| --- | --- | --- | --- | --- |
| データはコードより長く残る | データはシステムやア…（中略） | 『ハードパーツ』1.3 節 p.4（PDF p.22） | 書籍本文で確認 | 一致（要約。章頭の Berners-Lee の引用は 25 字を超えるので引用していない） |
| 同上 | ソフトウェアの費用の大部分は、初期開発ではなく継続的なメンテナンスにある | DDIA 2e 2.5 節 p.50（PDF p.68） | 書籍本文で確認 | 一致 |
| 同上 | 今日作るシステムは、長く生き残ればいつかレガシーシステムになる | DDIA 2e 2.5 節 p.51（PDF p.69） | 書籍本文で確認 | 一致 |
| 同上 | 「データ指向（data-intensive）」＝データの管理が開発の主要な課題の 1 つであるアプリケーション | DDIA 2e 1 章 p.1（PDF p.19） | 書籍本文で確認 | 一致 |
| データ指向とは、正・流れ・契約で見ること | 記録のシステム：最初に書き込まれ、食い違えば定義上こちらが正 | DDIA 2e 1.1.3 節 p.10（PDF p.28） | 書籍本文で確認 | 一致 |
| 同上 | 導出データ：変換・処理した結果で、失っても再作成できる。例はキャッシュ、インデックス、マテリアライズドビュー。区別はツールではなく使い方による | DDIA 2e 1.1.3 節 p.11（PDF p.29） | 書籍本文で確認 | 一致 |
| 同上 | 導出データには更新する仕組みが要る。多くの DB は自分 1 つだけが使われる前提で設計されている | DDIA 2e 1.1.3 節 p.11 | 書籍本文で確認 | 一致 |
| 同上 | 実装を API の背後に隠すと利用側に影響せずに変えられる。DB を共有すると構造全体が実質的に API の一部になる | DDIA 2e 1.3.2 節 p.21（PDF p.39） | 書籍本文で確認 | 一致 |
| 同上 | 「正・流れ・契約」の 3 つにまとめる | ― | ― | 出典なし。スライドに「本ガイド」と明記 |
| 4 つの性質を、このガイドではこう定義する | 更新性＝動かしたまま、利用側を止めずに変えられること | `deck/AUTHORING.md` 7 節 | 本文確認 | 一致（本ガイドの定義） |
| 同上 | 柔軟性・拡張性・置換性の定義文 | ― | ― | 規格の定義文は使っていない。書き手の言葉で書き、lead に「定義は本ガイドのもの」と明記 |
| 同上 | スケーラビリティ＝増大する負荷に対処するシステムの能力 | DDIA 2e 2.4 節 p.47（PDF p.65） | 書籍本文で確認 | 一致 |
| 同上 | 主な Part（柔軟性 3・6、拡張性 8、置換性・更新性 7・12・15） | `research/outline.md`「扱う論点と対応する Part」 | 本文確認 | 一致 |
| 3 つは規格の語に対応し、更新性は対応しない | ISO/IEC 25010:2023 は第 2 版、2023-11。製品品質の特性は 9 つ | ISO のプレビュー PDF（表紙、箇条 1） https://cdn.standards.iteh.ai/samples/78176/13ff8ea97048443f99318920757df124/ISO-IEC-25010-2023.pdf | 本文確認（PDF をテキスト化） | 一致 |
| 同上 | まえがき：portability を flexibility に置き換えた。scalability を flexibility の副特性に加えた | 同 PDF の Foreword | 本文確認 | 一致 |
| 同上 | JIS X 25010:2025 は 2025-12-22 改正、ISO/IEC 25010:2023 と IDT | https://webdesk.jsa.or.jp/books/W11M0090?bunsyo_id=JIS+X+25010%3A2025 | 本文確認 | 一致 |
| 同上 | 日本語名：柔軟性（旧：移植性）の副特性＝適応性・拡張性・インストール性（設置性）・置換性。保守性の副特性＝モジュール性・再利用性・解析性・修正性・テスト可能性 | https://service.valtes.co.jp/s-test/blog/test-first_vol25 （JIS X 25010:2025 を出典に明記する二次資料） | 本文確認（二次資料） | 一致。ただし JIS 本文は未確認。スライドの根拠の行に「二次資料」と書いた。このページは英語名を併記していないので、「拡張性＝scalability」「置換性＝replaceability」の組は、ISO のまえがき（scalability の追加）と 2011 年版の副特性の並びからの対応づけ |
| 同上 | 規格の定義文 | ― | ― | 載せるのをやめた。プレビューは箇条 3.4.4 までで、柔軟性・保守性の定義（3.5 以降）は一次資料で読めない。名前の対応だけにし、その旨をスライドに注記 |
| 同上 | 更新性は「保守性と柔軟性の副特性にまたがる」 | ノート 01 の 2.5 | ― | 修正した。ノートは副特性名（修正性・インストール性・置換性）と「保守性は更新の導入を含む」という注記を挙げるが、注記は arc42 の引用で未確認。スライドは副特性名を挙げず「またがる、と本ガイドは読む」とし、対応欄を「本ガイドの定義」にした |
| DDIA の語では、発展性が最も近い | 運用性・簡潔性・発展性の定義（3 つとも p.51） | DDIA 2e 2.5 節 p.51（PDF p.69） | 書籍本文で確認 | 一致（要約） |
| 同上 | 発展性という語を使う箇所と、不可逆性 | DDIA 2e 2.5.3 節 p.53（PDF p.71） | 書籍本文で確認 | 一致 |
| 同上 | DDIA 2e の副題は「信頼性、拡張性、保守…（中略）」 | 0180-2.txt の奥付（PDF p.664） | 書籍本文で確認 | 一致（ノート欄のみ） |
| 同上 | 「DDIA は 4 つの性質をこの名前では論じていない」 | ― | 書籍本文で確認 | 載せるのをやめた。副題に「拡張性」があり、p.47・p.53 に「柔軟」「柔軟性」の語がある。代わりに「右の列は本ガイドの対応づけで、DDIA の主張ではない」とした |
| 同上 | スケーラビリティは「一次元のラベルではない」 | 対応表 20（p.47〜48） | ― | 載せるのをやめた（p.47 の冒頭しか目視していない） |
| 規格の語彙に入らない 3 つが、このガイドの主題 | 逐次更新＝1 ノードずつ再起動して、サービスに影響を与えずに更新する | DDIA 2e 2.3.2.1 節 p.44（PDF p.62） | 書籍本文で確認 | 一致 |
| 同上 | DB の移行で旧システムに戻せないと、戻せる場合よりリスクがはるかに高い | DDIA 2e 2.5.3 節 p.53 | 書籍本文で確認 | 一致 |
| 同上 | 3 つ（稼働中の切り替え、データの移行、新旧の版の混在）が規格の語彙の外 | ノート 01 の 2.5 | ― | 規格の定義文を一次資料で読めないため、「本ガイドの解釈」の印を付けた。IPA 非機能要求グレードの「移行性」への言及は、原典を開いていないので載せていない |
| 19 件の事後報告で、引き金の 13 件は変更 | 19 件の引き金の分類（下の表） | 各事業者の一次報告（下の表の URL） | 本文確認（18 件は WebFetch で該当箇所の原文を引用させた。CrowdStrike は PDF を目視） | **修正した**（下の「数え方」） |
| 同上 | ある大規模インターネットサービスの調査で、設定変更が機能不全の主要因、ハードウェアの障害が関係したのは 10〜25% | DDIA 2e 2.3.3 節 p.45（PDF p.63） | 書籍本文で確認 | 一致（本書が引く原典 [72] は開いていない。「書籍の記述」として載せた） |
| 性質は、自動で検査できる数字にする | 適応度関数の定義（『進化的アーキテクチャ』からの引用として紹介）。「高パフォーマンスな」と言わず測定可能な値を定める | 『ハードパーツ』1.5.1 節 p.7（PDF p.25） | 書籍本文で確認 | 一致（要約） |
| 同上 | 複合的な特性は分解して測る。範囲はアトミックとホリスティック | 『ハードパーツ』p.8（PDF p.26） | 書籍本文で確認 | 一致（スライドは「測れない特性は、測れる特性に分ける」のみ） |
| 同上 | Azure Architecture Center「Design for change」に「Use fitness functions」の項がある。updated_at 2026-03-06、ms.date 2018-08-30 | https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/design-for-evolution | 本文確認 | 一致 |
| 同上 | Thoughtworks Radar「Architectural fitness function」：Trial（2017-11、2018-05）。現行の版には載っていない | https://www.thoughtworks.com/radar/techniques/architectural-fitness-function | 本文確認 | 一致 |
| 同上 | 右の表（4 つの性質の検査の例） | ノート 01 の 2.9（ノート自身が「提案」と書く） | ― | 出典の例ではない。「本ガイドの提案」の印を付けた。ノートが「記憶・要確認」とした道具の名前（Schema Registry、ArchUnit）は載せていない |
| 戻せない決定を見分け、そこに時間を使う | 大規模システムで変更を困難にする主要な要因の 1 つは不可逆性。不可逆性を最小化すると柔軟性が向上する | DDIA 2e 2.5.3 節 p.53 | 書籍本文で確認 | 一致 |
| 同上 | ADR は 1 つの決定を書く短い文書（通常 1〜2 ページ）。本書の型はコンテキスト・決定・影響 | 『ハードパーツ』1.4 節 p.5〜6（PDF p.23〜24） | 書籍本文で確認 | 一致 |
| 同上 | アーキテクチャ＝後から変更するのが難しいもの、という定義 | 『ハードパーツ』1.1 節 p.2〜3（PDF p.20〜21） | 書籍本文で確認 | 一致（根拠の行のみ） |
| 同上 | 表の 5 つの例と「戻しやすさ」の判定 | `research/outline.md` の Part 7・12・15・16 の結論 | ― | 出典なし。「本ガイドの整理」の印を付け、根拠は各 Part とした。outline の「パーティションは増やせても戻せない」は、自分で確かめていないので例に入れていない |
| 設計レビューでは、性質を数字と手順で問う | 「変更を重ねても、特性を保つため」 | Azure「Design for change」（Fitness functions help to protect architectural characteristics as change occurs over time） | 本文確認 | 一致（要約） |
| 同上 | 危ない兆候の列 | ノート 01 の 7 節 | ― | 出典なし（よくある答えの例として本ガイドが挙げた、とノート欄に明記） |

## 19 件の数え方（8 枚目）

規則：事業者の報告が**最初に挙げる出来事**で、1 件を 1 つに分類する。分類は書き手による。対象はノート 09 の 4.1 節の 19 件（発生日 2015-09-20〜2025-11-18）。

| # | 件 | 報告が最初に挙げる出来事（原文で確認した語句） | 分類 |
| --- | --- | --- | --- |
| 1 | GitLab 2017-01-31 | "increase in database load due to what we suspect was spam"。データ損失の直接の原因は、一次側での誤った削除 | 負荷の増加 |
| 2 | AWS S3 2017-02-28 | "executed a command … one of the inputs to the command was entered incorrectly" | 変更・操作（コマンド） |
| 3 | GitHub 2018-10-21 | "routine maintenance work to replace failing 100G optical equipment"、43 秒の切断 | 変更・操作（保守作業） |
| 4 | AWS DynamoDB 2015-09-20 | "a brief network disruption that impacted a portion of DynamoDB's storage servers" | 故障（ネットワーク） |
| 5 | AWS Kinesis 2020-11-25 | "The trigger … was a relatively small addition of capacity" | 変更・操作（容量の追加） |
| 6 | AWS us-east-1 2021-12-07 | "an automated activity to scale capacity of one of the AWS services" | 変更・操作（自動のスケール） |
| 7 | AWS DynamoDB／DNS 2025-10-19〜20 | "a latent race condition in the DynamoDB DNS management system"。変更・展開・故障の記載なし | 潜在の不具合の発現 |
| 8 | Facebook 2021-10-04 | "a command was issued with the intention to assess the availability of global backbone capacity" | 変更・操作（コマンド） |
| 9 | Roblox 2021-10-28〜31 | "Enabling a relatively new streaming feature on Consul under unusually high read and write load"。"We had ruled out hardware failure" | 変更・操作（機能の有効化） |
| 10 | Atlassian 2022-04-05 | スクリプトが "site IDs in place of Insight app IDs" で実行された | 変更・操作（スクリプト） |
| 11 | Datadog 2023-03-08 | "a security update to systemd was automatically applied to a number of VMs" | 変更・操作（ソフトウェアの更新） |
| 12 | CrowdStrike 2024-07-19 | "On July 19, 2024, two additional IPC Template Instances were deployed" | 変更・操作（ルールの配布） |
| 13 | Google Cloud 2025-06-12 | "a policy change was inserted into the regional Spanner tables" | 変更・操作（ポリシーの変更） |
| 14 | Cloudflare 2025-11-18 | "triggered by a change to one of our database systems' permissions" | 変更・操作（設定の変更） |
| 15 | Cloudflare 2024-11-14 | "we made a change to support an additional dataset for Logpush … a blank configuration being provided" | 変更・操作（設定の変更） |
| 16 | Cloudflare 2023-11-02 | 電力会社の "unplanned maintenance event" と "a ground fault on a PGE transformer" | 故障（電源） |
| 17 | Cloudflare 2020-11-02 | "a network switch started misbehaving" | 故障（機器） |
| 18 | Slack 2021-01-04 | "one of our Transit Gateways became overloaded"、"did not scale fast enough"。当日の変更は原因でなかったと記載 | 負荷の増加 |
| 19 | Slack 2022-02-22 | "The PBR step on February 22 updated Consul on 25% of the fleet" | 変更・操作（ソフトウェアの更新） |

合計：変更・操作 13（設定・ルール・ポリシー 4＝#12・13・14・15／コマンド・スクリプト 3＝#2・8・10／更新・機能の有効化 3＝#9・11・19／容量の追加・自動のスケール 2＝#5・6／保守作業 1＝#3）、故障 3（#4・16・17）、負荷の増加 2（#1・18）、潜在の不具合 1（#7）。計 19。

### ノート 09・outline との違い（修正した点）

- ノート 09（4.3 節、結論 1）と outline は「19 件のうち故障が引き金は 3 件（Cloudflare 2023・2020、GitHub 2018）、**残りは変更**」とする。原文で確かめると、次の 3 点が合わない
  - GitHub 2018 は、故障しかけた光機器を**交換する保守作業**が切断を起こした。自発的な故障ではないので「変更・操作（保守作業）」に移した
  - AWS DynamoDB 2015 の引き金は**短いネットワーク障害**で、変更ではない。「故障」に入れた
  - Slack 2021（負荷で Transit Gateway が飽和）、GitLab 2017（最初の出来事は負荷の増加）、AWS 2025-10（変更を伴わない潜在の競合）は、変更でも故障でもない
- 結果として「故障は 3 件」という数は同じだが、中身が違う。「残り 16 件は変更」は成り立たず、**変更・操作は 13 件**。スライドの題と lead は 13 件と 3 件で書いた
- 境界の判断：#1 を直接の原因（誤操作）で数えれば変更・操作は 14、#6・#7 を「自動化の動作」として 1 つにまとめる数え方もある。どの数え方でも、変更・操作が過半である点は変わらない。スライドのノート欄に GitLab の例を書いた
- 各件の時刻・停止時間・件数はこのスライドに載せていない（Part 14 の担当が確かめる）

## 不確かな点

- JIS X 25010:2025 の本文は読めていない。日本語の副特性名は二次資料（バルテス）による。英語名との 1 対 1 の対応（拡張性＝scalability など）は、JIS 本文で確かめる余地がある
- DDIA 2e p.45 の調査（[72]）の原典は開いていない
- 19 件の分類は書き手の判断。18 件は抽出ツールが返した原文の引用で確かめており、ページ全文を逐語で読んだのは CrowdStrike だけ
- 8 枚目の棒グラフは PowerPoint での見た目を確かめていない（取りまとめ役の QA で確認）
