# Part 16 事実の確かめ直し（verify_p16）

確認日：2026-11-18。対象：`deck/p16.js`（扉＋8 枚）。このPartは法的な助言ではない。日付・制裁事例・製品のふるまいは、下の表のとおり原典を開いて確かめたものだけを載せた。

確かめ方の凡例：本文確認＝URL を取得して該当の文を読んだ／書籍本文で確認＝`research/books/text/<ISBN>.txt` の該当ページを読んだ。

| スライドの題 | 事実 | 出典（URL か書籍ページ） | 確かめ方 | 結果 |
| --- | --- | --- | --- | --- |
| 保持・目的・所在・系譜は流れに埋まり、後から足せない | GDPR 25 条 1 項は「処理の手段を決める時点」と処理の時点の両方で措置を求める | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679 | 本文確認（EUR-Lex。直接の取得は 202 で空、抽出ツール経由で公式ページの本文を取得） | 一致 |
| 同上 | Taxa 4x35：氏名は 2 年で削除、電話番号は 5 年後。会社の説明は電話番号がデータベースのキー。2 年を超えた乗車記録 8,873,333 件。発表 2019-03-25、過料 120 万クローネを勧告 | https://www.datatilsynet.dk/afgoerelser/afgoerelser/2019/mar/datatilsynet-indstiller-taxaselskab-til-boede-paa-12-mio-kr | 本文確認 | 一致。「システムの都合で期限を延ばせないとした」は該当の文を確かめていないので載せるのをやめた。高裁判決（二次資料）も載せるのをやめた |
| 同上 | Deutsche Wohnen：2019-10-30 決定、約 1,450 万ユーロ。不要なデータを取り除く手段のないアーカイブシステム | https://www.datenschutz-berlin.de/fileadmin/user_upload/pdf/pressemitteilungen/2019/20191105-PM-Bussgeld_DW.pdf | 本文確認（PDF） | 一致 |
| 同上 | 2026-06-09、ベルリン第一地方裁判所が 90 万ユーロ。判決は未確定（noch nicht rechtskräftig） | https://www.berlin.de/gerichte/presse/pressemitteilungen-der-ordentlichen-gerichtsbarkeit/2026/pressemitteilung.1679703.php | 本文確認 | 修正した（ノートの「確定したかは未確認」→ 発表に「未確定」と明記あり） |
| 同上 | Meta Platforms Ireland：2024-09-26 決定。パスワードを平文で内部システムに保存。過料 3 件の合計 9,100 万ユーロ（7,500 万＋800 万＋800 万） | https://www.dataprotection.ie/en/dpc-guidance/decisions/inquiry-meta-platforms-ireland-limited-september-2024 | 本文確認（決定ページ。決定文 PDF は開いていない） | 一致。「ロギングの副作用」「数億人規模」は決定文 PDF を開いていないので載せるのをやめた |
| 同上 | DDIA 1.4 節：消去の権利と不変の構成要素・導出データの両立は工学上の課題。どの技術が GDPR 準拠かの明確な指針は無い | DDIA 2e p.23〜24（PDF p.41〜42） | 書籍本文で確認 | 一致 |
| 削除は、導出データまで届いて完了する | delete.retention.ms より遅れた受け手は削除の印を見逃しうる | https://kafka.apache.org/44/design/design/ | 本文確認 | 修正した（ノートは 4.2 のページ → 4.4 のページで同じ文を確認） |
| 同上 | Debezium は削除イベントの後にトゥームストーンを出す（tombstones.on.delete の既定 true） | https://debezium.io/documentation/reference/stable/connectors/postgresql.html（3.7.1.Final） | 本文確認 | 一致 |
| 同上 | 複製が多くの場所にあり、バックアップは意図して不変なことが多い。削除は難しい | DDIA 2e p.508〜509（PDF p.526〜527） | 書籍本文で確認 | 一致 |
| 同上 | EDPB 報告：バックアップを変更しないほうがよい場合がある。請求を追跡し、復元したシステムで満たす手続き | https://www.edpb.europa.eu/system/files/documents/2026-02/edpb_cef-report_2025_right-to-erasure_en.pdf（4.2.6） | 本文確認（PDF） | 一致。採択日は 2026-02-10 |
| 削除を命令しても、すぐには物理的に消えない | PostgreSQL 18：UPDATE・DELETE は古い行の版をすぐには取り除かない。VACUUM が回収する | https://www.postgresql.org/docs/18/routine-vacuuming.html（24.1.2 Recovering Disk Space） | 本文確認 | 一致 |
| 同上 | Kafka 4.4：キーと null の値のレコードが削除。書き込み中のセグメントはコンパクションされない。最大の遅れの設定は確実な保証ではない | https://kafka.apache.org/44/design/design/ | 本文確認 | 一致（版を 4.2 → 4.4 に修正） |
| 同上 | delete.retention.ms の既定は 86400000（1 日） | https://kafka.apache.org/44/configuration/topic-configs/ | 本文確認 | 一致 |
| 同上 | ClickHouse：軽量 DELETE は印を付けるだけ。物理削除は次のマージで、期間は不定。min_age_to_force_merge_seconds か ALTER TABLE … DELETE | https://clickhouse.com/docs/sql-reference/statements/delete | 本文確認 | 一致。文書に版の表示が無いので「版の表示なし」と書いた |
| 同上 | LSM では削除マーカーが行き渡るまで削除済みのレコードが残りうる | DDIA 2e p.128（PDF p.146） | 書籍本文で確認 | 一致 |
| 同上 | Redpanda・CockroachDB・DuckDB・オブジェクトストレージの削除のふるまい | — | 開いていない | 載せるのをやめた |
| 不変のログと消去要求：両立の選択肢は 4 つ | DDIA：個人データをイベントの外に置く／後で捨てられる鍵で暗号化（暗号シュレッディング） | DDIA 2e p.101（PDF p.119） | 書籍本文で確認 | 一致 |
| 同上 | DDIA：鍵を捨てる方法は問題を鍵の保管場所に移す。同じ鍵で暗号化する範囲を事前に決める | DDIA 2e p.509（PDF p.527） | 書籍本文で確認 | 一致 |
| 同上 | NIST SP 800-88 Rev.2（2025-09）：CE は Purge の手法。対象の鍵の全ての複製をサニタイズできること。平文で保存された分には効かない | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf（3.2 節、3.2.3） | 本文確認（PDF） | 修正した（下書きの節番号 3.1.3 は Destroy の節。3.2 節に直した）。公表ページの表示は「September 2025」なので日は書かない |
| 同上 | EDPB Guidelines 02/2025 v2.0（2026-07-07 採択）：暗号化された個人データはなお個人データ | https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202502_blockchain_v2_en.pdf（51 段落付近） | 本文確認（PDF） | 一致 |
| 同上 | 鍵の廃棄が法的に「消去」に当たるか | — | 定めた文書を確認できていない | 「未確定。法務に確認」と書いた |
| 設計の段階で決めること：9 つの決定 | 通則編 3-4-1：消去は、削除のほか、特定の個人を識別できないようにすること等を含む。令和 8 年 6 月一部改正 | https://www.ppc.go.jp/personalinfo/legal/guidelines_tsusoku | 本文確認 | 一致 |
| 同上 | GDPR 5 条 1 項 (b)(c)、17 条 1 項（不当な遅滞なく） | EUR-Lex（上と同じ URL） | 本文確認（抽出ツール経由） | 一致。5 条 1 項 (e)・30 条・33 条は本文を取得できていないので載せるのをやめた |
| 同上 | DM 8 章：データがどこから来て何のために使われているかの文書化が求められる。利用目的の分類を中央で管理 | 『大規模データ管理 第2版』p.217〜218（PDF p.243〜244）、p.237〜238（PDF p.263〜264） | 書籍本文で確認 | 一致 |
| 同上 | 表の 9 行（ノート 11 の 12 節 23 行から絞った） | — | 本ガイドの整理 | スライドに「本ガイドの整理」と明示 |
| 予測は偏りを学び、出力が入力に戻ると強まる | DDIA 14 章：倫理は点検表ではない（p.580）、偏りの学習と増幅・郵便番号（p.581）、説明責任（p.581〜582）、信用スコアの循環（p.582）、データ最小化（p.589〜590） | DDIA 2e PDF p.598〜601・607〜608 | 書籍本文で確認 | 一致。引用符つきの引用はしていない |
| 同上 | EU AI 規則 10 条 2 項 (b)（出所・当初の目的）、(f)（出力が将来の入力に影響する場合の偏りの検査） | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1689 | 本文確認（抽出ツール経由。公布時の本文） | 一致。高リスク AI への適用開始日と 2026 年の改正（規則番号・延期後の日付）は一次資料を開いていないので載せるのをやめた |
| 設計レビューで問うこと：法・プライバシー | EDPB 報告：追加の指針を検討しうる（may consider adopting further guidance） | EDPB 報告（上と同じ URL）要約の Issue 6 | 本文確認（PDF） | 一致 |
| まとめ：消せることと説明できることを設計に入れる | 改正個人情報保護法：2026-07-10 成立、2026-07-17 公布 | https://www.ppc.go.jp/personalinfo/legal/r8kaiseihogohou/ | 本文確認 | 修正した（公布日は下書きでは二次資料 → 委員会のページで確認） |
| 同上 | 施行期日は原則、公布の日から 2 年を超えない範囲内 | https://www.ppc.go.jp/files/pdf/260717_kaiseihounitsuite.pdf | 本文確認（PDF） | 一致。施行日は確認できていないので書かず「未施行（2026-11 確認）、施行日は未確認」とした |
| 同上 | 法律番号（令和 8 年法律第 56 号） | 二次資料のみ | — | 載せるのをやめた |
| （載せなかったもの） | Discord／CNIL、リクルートキャリア／個人情報保護委員会、英 ICO の beyond use（ico.org.uk は 403）、Data Act の日付、Digital Omnibus の審議状況、DS-310・GIF、漏えい報告の期限、税務の保存期間 | — | 一次資料を開けていない、または Part 13・15 の担当 | 載せるのをやめた |

## 残っている不確かな点

- EUR-Lex は直接の取得が拒まれ（HTTP 202、本文なし）、抽出ツール経由で公式 URL の本文の該当箇所だけを読んだ。全文は通読していない
- 改正個人情報保護法の「未施行」は、委員会のページが 2026-11 時点で政令・規則・ガイドラインを検討中としていることによる。施行日を定める政令の有無、一部の規定の先行施行の有無は確かめていない
- Meta の件は決定ページ（要約）だけを読んだ。決定文 PDF は開いていない
- ClickHouse の文書には版の表示が無い。Debezium は stable（3.7.1.Final）のページ
- スライド 3 の「本ガイドの整理」と付けたセル、スライド 4 の得失の列、スライド 5 の表、スライド 6 の右列、スライド 7 の「なぜ問うか」の一部は、一次資料の記述からの推論
- PowerPoint での見た目（はみ出し・重なり）は未検査。表の行の高さは文字量から見積もった
