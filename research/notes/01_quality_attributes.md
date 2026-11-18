# 01 品質特性と非機能要件（柔軟性・拡張性・置換性・更新性を、測れる要件にする）

調査日：2026-11-18

## 1. 問い（このノートが答えること。対応する Part）

対応する Part：1（考え方）、2（ステップ 1：要件と負荷を数字にする）。

- 依頼者の言う「柔軟性・拡張性・置換性・更新性」は、標準の語彙のどれに当たり、どこが当たらないか
- ISO/IEC 25010:2023 は 2011 年版から何を変えたか。日本語の対応規格（JIS）はあるか
- IPA 非機能要求グレード 2018 は何を数字にさせ、何を対象外にしているか
- 性能・信頼性・負荷は、どの数字で書けばレビューできるか（パーセンタイル、SLI・SLO、エラーバジェット、RPO・RTO、負荷のパラメータ）
- 置換性・更新性のように「測りにくい」性質を、自動で検査する方法（適応度関数）はあるか
- クラウド 3 社の設計フレームワークに、変更容易性・置換容易性の柱はあるか
- 進化可能性（evolvability）に学術的な定義はあるか

このノートでの確認の限界を先に書く。ISO/IEC 25010:2023 の本文は有料で、**一次資料として読めたのは公開プレビュー（まえがき・序文・箇条 1〜3.4.4）まで**である [2]。信頼性・保守性・柔軟性の定義（箇条 3.5 以降）は二次資料 [5][6][7] で読んだ。ISO の OBP は利用規約の同意画面から先を開けなかった [3]。

## 2. 標準・定義（節番号）

### 2.1 ISO/IEC 25010:2023 の位置と構成（一次資料で確認できた範囲）

- 題名は「Product quality model」。第 2 版、2023-11 発行（段階 60.60 は 2023-11-15）、22 ページ、ISO/IEC JTC 1/SC 7。2011 年版は廃止（Withdrawn）[1]
- 2011 年版は 3 つに分かれた：製品品質モデル＝25010:2023、品質モデルの概観と使い方＝ISO/IEC 25002、利用時品質モデル＝ISO/IEC 25019 [2: Foreword]
- 適用範囲（箇条 1）：ICT 製品とソフトウェア製品。特性は 9 つ。要求の定義、設計目標、テスト目標、受け入れ基準、測定の確立に使う「参照モデル」[1][2: 1 Scope]
- 引用規格（箇条 2）は無い [2]
- 定義の文型が変わった。2023 年版は「capability of a product to …」で書く [2: 3.1〜3.4.4]。2011 年版は「degree to which …」（JIS では「…度合い」）[9]。**iso25000.com は 9 特性を載せながら文型は「Degree to which」のままで、2023 年版の本文の文言とは一致しない** [5]
- 附属書：A（2011 年版との比較）、B（ディペンダビリティへの対応づけの例）、C（測定への使い方）、D（利害関係者ごとの見方）。いずれも参考（informative）[2: 目次]。附属書の本文は未確認
- 測定量は別の規格 ISO/IEC 25023:2016 が定める。これは 2011 年版の特性に対する測定量で、ISO のページは後継を「ISO/IEC DIS 25000-23.2」と示している（草案段階）[10]。**2023 年版の scalability などに対応する確定した測定量の規格は、確認できなかった**

### 2.2 2011 年版からの変更（まえがきに列挙されているもの）[2: Foreword]

| 変更 | 内容 |
| --- | --- |
| 特性の追加 | Safety（operational constraint、risk identification、fail safe、hazard warning、safe integration） |
| 特性の置き換え | Usability → Interaction capability、**Portability → Flexibility** |
| 副特性の追加 | inclusivity・self-descriptiveness（interaction capability）、resistance（security）、**scalability（flexibility）** |
| 副特性の置き換え | user interface aesthetics → user engagement、**maturity → faultlessness** |
| 副特性の分割 | accessibility → inclusivity と user assistance |
| 対象の拡大 | さまざまな種類の ICT 製品と情報システムを含む |
| そのほか | いくつかの特性・副特性の名前と定義を、より正確にした |

特性は 8 → 9。まえがきは Maintainability の構成の変更を挙げていない [2]。

### 2.3 Flexibility・Maintainability・Reliability の副特性と定義

箇条番号は、プレビューで確かめた 3.1〜3.4 の並びからの**推定**（3.5 Reliability、3.7 Maintainability、3.8 Flexibility）。本文では未確認。定義は二次資料の引用を自分の言葉で要約した。日本語名は JIS X 25010:2025 を引いた二次資料による [7][8]。

| 特性 | 副特性（英／JIS 2025 の日本語名） | 定義の要約 | 出典 |
| --- | --- | --- | --- |
| Flexibility／柔軟性（旧：移植性） | — | 要求・利用状況・システム環境の変化に合わせて製品を適応させられる能力 | [5][6] |
| | adaptability／適応性 | 異なるハードウェア・ソフトウェア・運用環境へ、効果的・効率的に適応または移行できる | [6][7] |
| | **scalability／拡張性** | 増減するワークロードを扱える。または、変動に合わせて容量を調整しやすい | [6][7] |
| | installability／インストール性（設置性） | 明示された環境で、効果的・効率的にインストール・アンインストールできる | [6][7] |
| | **replaceability／置換性** | 同じ環境で、同じ目的の別の明示された製品と置き換えられる。注記：installability と adaptability を含みうる。標準化されたファイル形式などでロックインのリスクを下げる | [6][7] |
| Maintainability／保守性 | — | 意図した保守者が、効果的・効率的に修正できる。注記（arc42 の引用による）：更新・アップグレードの導入を含む | [6] |
| | modularity／モジュール性 | ある構成要素の変更が、他の構成要素に及ばないよう限定できる | [6][7] |
| | reusability／再利用性 | 複数のシステムで、または他の資産を作るために、資産として使える | [6][7] |
| | analysability／解析性 | 変更の影響の評価、欠陥・故障の原因の診断、修正箇所の特定が、効果的・効率的にできる | [6][7] |
| | modifiability／修正性 | 欠陥を持ち込まず、既存の品質を落とさずに、効果的・効率的に修正できる。注記：changeability と stability の組み合わせ | [6][7] |
| | testability／テスト可能性（試験性） | 要求が満たされたかを判断する、客観的で実行可能なテストを設計・実行できる | [6][7] |
| Reliability／信頼性 | — | 明示された条件・期間で、中断や故障なく機能を果たす | [6] |
| | faultlessness／無障害性（旧：成熟性） | 通常の運用で、障害（fault）なしに機能を果たす | [5][7] |
| | availability／可用性 | 使うことを求められたとき、運用可能でアクセスできる | [5][7] |
| | fault tolerance／障害許容性（耐故障性） | ハードウェア・ソフトウェアの障害があっても、意図どおり動く | [5][7] |
| | recoverability／回復性 | 中断・故障のとき、影響を受けたデータを復旧し、望む状態に戻せる | [5][7] |

二次資料どうしの食い違い：

- **testability の所属**。iso25000.com [5]、VALTES（JIS X 25010:2025 を出典に明記）[7]、JUSE の発表資料の抜粋 [8] は Maintainability（保守性）の下に置く。arc42 の規格の一覧ページだけが Flexibility の下に並べている [6]。3 対 1 で、JIS を直接引く資料が保守性としているため、**保守性の下とみるのが妥当**。ISO 本文では未確認
- arc42 の一覧ページの特性の説明文は 2011 年版の文型（degree）のまま [6]。同じサイトの個別ページは 2023 年版の文型（capability）で引いている [6]

### 2.4 JIS の対応版

- **JIS X 25010:2025** がある。2025-12-22 改正（官報掲載日も同日）、対応国際規格は ISO/IEC 25010:2023（IDT＝一致）、和文 34 ページ。履歴：2013-06-20 制定、2018-10-22 確認、2023-06-20 確認、2025-12-22 改正 [4]
- 題名は「システム及びソフトウェア技術－システム及びソフトウェア製品の品質要求及び評価（SQuaRE）－製品品質モデル」[4]
- JSA のプレビュー PDF の序文（検索抜粋で確認）は、JIS X 25010:2013 が JIS X 25010 第 2 版・JIS X 25002・JIS X 25019 に置き換えられたと書く [4]。JIS X 25002・25019 の発行年は、発表資料の抜粋では 2025 [8]（本文未確認）
- JIS X 25010:2013（ISO/IEC 25010:2011）の語：保守性＝モジュール性・再利用性・解析性・修正性・試験性、移植性＝適応性・設置性・置換性 [9]。2013 年版の適応性の注記 1 は「内部容量・能力の拡張性を含む」としていた [9]。つまり 2011 年版では、拡張性は適応性の注記の中にしか無かった

### 2.5 依頼者の 4 つの言葉との対応

**発見：依頼者の 4 語のうち 3 語は、JIS X 25010:2025 の用語と字面が一致する**（柔軟性＝特性、拡張性＝scalability の訳、置換性＝replaceability の訳）[7][8]。ただし意味の範囲は一致しない。

| 依頼者の言葉 | 対応づけられる特性・副特性 | 対応づけられない部分（規格の語彙の外） |
| --- | --- | --- |
| 柔軟性 | 特性 Flexibility（柔軟性）そのもの。中身は adaptability・scalability・installability・replaceability [2][7] | 規格の柔軟性は旧「移植性」の後継で、環境への適応が中心。「あとからの要求の変化に構造を変えずに応じる」は、むしろ Maintainability の modularity・modifiability に入る |
| 拡張性 | (a) 負荷の増減への対応 → scalability（JIS 訳が「拡張性」）[7]。IPA の「性能・拡張性」もこの意味（リソース拡張性、スケールアップ・スケールアウト）[13] | (b) 機能を足しやすいこと（extensibility）は、ISO/IEC 25010 の副特性名に無い。近いのは modifiability と modularity。学術側の進化可能性モデルは extensibility を独立の副特性に立てている [33]。**同じ「拡張性」が 2 つの意味で使われるので、スライドでは必ず言い分ける** |
| 置換性 | replaceability（置換性）[7] | 規格の定義は「製品を、同じ環境の同じ目的の別の製品と置き換える」。次は定義の外：①内部の構成要素（DB・基盤）の差し替え（→ modularity）、②稼働中に止めずに切り替えること（→ availability と、並行稼働のための co-existence・interoperability）、③データの移行と再構築（→ IPA の移行性 [13]）、④切り替え後の結果の一致の検証 |
| 更新性 | 規格に同名の副特性は**無い**。近いのは Maintainability（更新・アップグレードの導入を含むとの注記 [6]）、modifiability、installability、replaceability（2013 年版の注記 1 は新しい版への置換に触れる [9]） | ①更新中の新旧の版の混在（ローリング更新）、②スキーマとデータ形式の前方・後方互換、③更新の頻度と失敗率。arc42 は Updateability を独自の品質として立てているが、ISO の用語ではない [6]。IPA では運用・保守性の「パッチ適用ポリシー」「活性保守」「計画停止」に当たる [13] |

まとめると、4 語は **Flexibility（柔軟性）と Maintainability（保守性）の 2 特性にまたがり**、さらに Compatibility（互換性：co-existence・interoperability）と Reliability（availability）に支えられる。規格の語彙で足りないのは、「動かしたまま」「データを伴って」「版が混在して」という条件である。ここを数字にするには、SLO・DORA の指標・適応度関数を足す（2.7、2.9）。

### 2.6 進化可能性（evolvability）の学術的な定義

- ISO/IEC 25010:2023 の特性・副特性の名前に evolvability は無い [2][5]
- よく引かれる定義は Rowe・Leaney・Lowe（1998）のもので、要約すると「要求の変化を、システムの寿命を通じて、最小の費用で、アーキテクチャの一貫性を保ちながら受け入れる能力」。Breivold と Crnkovic の論文の引用で確認した（原典は未確認）[33][35]
- Breivold らの進化可能性モデルの副特性：analyzability、architectural integrity、changeability、extensibility、portability、testability、領域固有の属性 [33]
- 同論文は McCall・Boehm・FURPS・ISO 9126・Dromey の各品質モデルを調べ、進化可能性の分析に特化したモデルは無いと結論する。とくに architectural integrity はどのモデルにも無いとする [33]。対象は ISO 9126 までで、25010:2023 は扱っていない
- ドイツ情報学会（GI）の用語解説は、保守しやすいことと発展させやすいことは別だと区別する（検索抜粋）[36]
- 定義は複数あり、**合意された単一の定義は無い**。スライドでは「定義の一例」として示す

### 2.7 性能と信頼性の表し方

**パーセンタイルとテールレイテンシ**（Dean・Barroso「The Tail at Scale」、CACM 56 巻 2 号 74–80 ページ、2013-02）[16]

- 1 台の応答が通常 10ms、99 パーセンタイルが 1 秒のとき、1 台だけなら遅いのは 100 回に 1 回。**100 台に並列に問い合わせて全部を待つと、63% の要求が 1 秒を超える**（1 − 0.99^100）[16]
- 1 台で 1 秒超が 1 万回に 1 回でも、2,000 台なら約 5 回に 1 回が 1 秒を超える [16]
- Google の実サービスの測定：ルートで見た 1 つの葉の 99 パーセンタイルは 10ms、全部の葉が終わるまでの 99 パーセンタイルは 140ms、95% の葉が終わるまでは 70ms。遅い 5% を待つことが 99 パーセンタイルの半分を占める [16]
- ばらつきの原因：共有資源、デーモン、グローバルな資源の共有、保守の作業（ログのコンパクション、GC）、キューイング、電力制限、SSD の GC、省電力 [16]
- 対処：hedged requests、tied requests、micro-partitions、latency-induced probation、good-enough、canary requests。hedged requests の例は、BigTable の 1,000 キーの読み出しで、10ms 待って再送すると 99.9 パーセンタイルが 1,800ms から 74ms になり、追加の要求は 2% [16]

**SLI・SLO・SLA**（Google SRE 本 4 章）[17]

- SLI は「a carefully defined quantitative measure」、SLO は SLI の目標値または範囲、SLA は結果（多くは金銭）を伴う利用者との契約 [17]
- 指標は平均でなく分布で見る。例：典型は 50ms、5% が 20 倍遅い場合、平均では裾の変化を見落とす。99・99.9 パーセンタイルは最悪に近い場合、50 パーセンタイルは典型を表す [17]
- 目標の決め方：現状の性能から決めない／単純に保つ／絶対（無限のスケール、常時可用）を避ける／SLO は少なく [17]
- Chubby の例：SLO を大きく上回る可用性が続くと、利用側が「落ちない」前提で依存する。目標を超えた四半期には計画的に停止を起こす [17]
- 測る場所：多くはサーバー側。利用者の体験とずれる場合はクライアント側でも測る [17]

**エラーバジェット**（SRE 本 3 章、SRE Workbook 2 章）[18][19]

- SLO と実測の差が、その期間の残りの予算。予算が残る間はリリースできる。使い切ったらリリースを止めるか遅らせ、信頼性の作業に回す [18]
- 100% は目標として誤り。達成できず、費用が段階ごとに跳ね上がり、利用者は他の要素（回線・端末）に埋もれて差を感じない [18]
- 可用性の測り方は 2 つ：時間ベース（稼働時間の割合）と、要求ベース（成功した要求の割合）。Google は後者を主に使う [18]
- SLI は「良いイベント ÷ 全イベント」で書く。エラーバジェット＝ 100% − SLO。例：99.9% で 300 万件なら 3,000 件まで [19]
- サービスの種類ごとの SLI：要求駆動＝可用性・レイテンシ・品質、パイプライン＝鮮度・正確性・網羅率、ストレージ＝耐久性 [19]
- レイテンシの SLO は複数のしきい値で書く（例：90% が 450ms 未満、99% が 900ms 未満）。期間は 4 週間のローリングが汎用 [19]
- エラーバジェットポリシー：使い切ったときに誰が何をするかを書いた合意文書。プロダクト・開発・SRE が承認する [19]

**RPO・RTO**

- NIST SP 800-34 Rev. 1 の用語：RPO は、停止の後にデータを回復しなければならない時点。RTO は、任務・業務に悪影響が出るまでに、回復の段階にいられる全体の時間 [20]
- AWS の説明：RTO は中断から復旧までの最大の許容遅延、RPO は最後の復旧点からの最大の許容時間（＝許容するデータ損失）。RTO は 1 回の事象の上限、MTTR は複数の事象の平均。可用性は期間の平均、DR の目標は 1 回の事象の目標 [21]
- IPA 非機能要求グレード 2018 は、可用性の継続性に A.1.3.1 RPO、A.1.3.2 RTO、A.1.3.3 RLO（目標復旧レベル）、A.1.5.1 稼働率を置く [13]

### 2.8 負荷の表し方

- **負荷のパラメータ**：IPA は「業務処理量」として、ユーザ数・同時アクセス数・データ量・オンラインリクエスト件数・バッチ処理件数・業務機能数と、それぞれの増大率を挙げる（B.1.1.1〜B.1.1.6、B.1.2.1〜B.1.2.6）[13]。解説編は、性能・拡張性の合意では業務処理量を最初に決めるとする [12]
- **ファンアウトの例の原典**：DDIA 2e の 2.1「ソーシャルネットワークのホームタイムライン」の事例の参考文献は、Raffi Krikorian「Timelines at Scale」（QCon San Francisco、2012-11）と同氏のブログ（2013-08）[38]。InfoQ のページで、講演者（当時 Twitter）、QCon SF 2012、公開日 2013-04-03、38 分を確認した。**講演の中の数値は未確認**（動画を見ていない）[31]。DDIA 2e は事例を一般化し、毎秒 5,800 件の投稿、平均 200 フォロワー、毎秒 100 万件強のタイムライン書き込みという数字で説明する [38]
- **スケールアップとスケールアウト**：IPA はリソース拡張性の「サーバ処理能力増強」に B.3.5.1 スケールアップ、B.3.5.2 スケールアウトを置く [13]。Azure の性能効率の柱は水平スケールを原則に挙げる [23]
- **shared-nothing**：Stonebraker「The Case for Shared Nothing」（IEEE Database Engineering Bulletin 9 巻 1 号、1986-03）[32][38]。高トランザクション率のマルチプロセッサ構成を、shared memory・shared disk・shared nothing（メモリも周辺記憶も共有しない）の 3 つに分け、12 の観点で順位をつけて、shared nothing が最も費用対効果が高いと論じる。代償も書いている：分散デッドロック検出と多相コミットが要り、オブジェクトの配置を決める DB 設計が難しくなる [32]
- **スパイク**：IPA は性能品質保証に B.4.3.1 スパイク負荷対応（トランザクション保護）を置く [13]

### 2.9 アーキテクチャ特性と適応度関数（fitness function）

- 定義（『Building Evolutionary Architectures』の著者サイト）：進化的アーキテクチャは「supports guided, incremental change across multiple dimensions」。適応度関数は、アーキテクチャ特性の客観的な完全性の評価を与えるもの。著者は Neal Ford・Rebecca Parsons・Patrick Kua [30]。第 2 版の書誌（O'Reilly のページ）は開けず未確認 [30]
- **Thoughtworks Technology Radar での位置**：
  - 「Architectural fitness function」：Techniques、**Trial**（2017-11、2018-05 の 2 回）。現行の版には載っておらず、評価が古い可能性があるとの注記つき [27]
  - 「Dependency drift fitness function」：Trial（2019-11）→ **Adopt**（2020-10）。ライブラリ・API・環境の古さをリリースのパイプラインで検査する。現行の版には載っていない [28]
  - 「Run cost as architecture fitness function」：2019 年から Adopt と記載（検索抜粋）[29]
- Azure Architecture Center の「Design for change」は適応度関数の利用を勧め、仕組みの例としてメトリクス・単体テスト・カオスエンジニアリングを挙げる [24]
- **置換性・更新性を自動で検査する例**。確認できた出典に載っているのは、依存の古さの検査 [28] とページ読み込み時間の検査 [24] まで。下の表は、それを置換性・更新性に当てはめた**このノートの提案**であり、出典の例ではない。個々の道具の仕様は対応する Part のノートで裏を取る

| 守りたい性質 | 検査の例（提案） | 出す数字 | 対応する Part |
| --- | --- | --- | --- |
| 更新性：新旧の版が混在しても壊れない | スキーマの互換性検査を CI で必ず通す（Schema Registry の互換性モードなど。記憶・要確認） | 互換性違反の件数（0 が合格） | 7 |
| 更新性：依存が古くなっていない | 依存の古さの検査 [28] | サポート切れの依存の数、最新版からの遅れ | 7・15 |
| 置換性：他サービスの DB を直接読まない | 接続設定・クエリの静的検査、DB の権限の検査 | 所有者以外からの接続の数（0 が合格） | 3 |
| 置換性：派生ストアをログから作り直せる | 定期的に再構築し、正本と突き合わせる | 再構築の所要時間、一致率 | 12・15 |
| 置換性：製品固有の機能への依存を把握している | 固有の SQL・API の使用箇所を数える | 使用箇所の数と増減 | 15 |
| 変更の局所性（modularity） | モジュール間の依存の規則の検査（ArchUnit など。記憶・要確認） | 規則違反の件数、1 変更で触るサービスの数 | 3・6 |
| 変更の速さと安全さ | DORA の指標 [37] | 変更のリードタイム、デプロイ頻度、変更失敗率、失敗したデプロイの復旧時間、デプロイの手戻り率 | 2・7 |

DORA の指標（2026-01-05 更新のページ）：スループット＝変更のリードタイム・デプロイ頻度・失敗したデプロイの復旧時間、不安定さ＝変更失敗率・デプロイの手戻り率 [37]。

## 3. 製品ごとの違い（表。公式文書の URL・版・日付）

このノートの対象は製品ではなく枠組みなので、枠組みどうしを比べる。

| 枠組み | 版・日付 | 発行者 | 柱・大項目 | 変更容易性・置換容易性の扱い | 数字の書き方を与えるか |
| --- | --- | --- | --- | --- | --- |
| ISO/IEC 25010:2023 [1][2] | 第 2 版、2023-11 | ISO/IEC | 9 特性 | Maintainability と Flexibility の 2 特性。replaceability・scalability・modifiability が副特性 | 与えない（測定量は 25023。2011 年版向け [10]） |
| JIS X 25010:2025 [4] | 2025-12-22 | 経済産業大臣（原案：JSA・情報処理学会） | 同上（IDT） | 同上。柔軟性・拡張性・置換性の訳語 [7] | 同上 |
| IPA 非機能要求グレード 2018 [11][12][13] | 2018-04 | IPA | 6 大項目 | 「性能・拡張性」「運用・保守性」「移行性」。移植性は対象外 [12] | 与える（メトリクスごとにレベル 0〜5）|
| AWS Well-Architected Framework [22] | 確認できた直近の Major update は 2024-11-06 | AWS | 6 本柱：運用上の優秀性、セキュリティ、信頼性、パフォーマンス効率、コスト最適化、持続可能性 | **柱は無い**。一般設計原則に「Consider evolutionary architectures」（2022-03-31 版では「Allow for …」）。信頼性の柱に Change management、運用の柱に Evolve の領域 | 柱ごとの質問形式。数値の基準は与えない |
| Azure Well-Architected Framework [23][25] | pillars：2025-01-22、OE principles：2025-05-05 | Microsoft | 5 本柱：信頼性、セキュリティ、コスト最適化、オペレーショナルエクセレンス、パフォーマンス効率 | **柱は無い**。OE の原則「Adopt safe deployment practices」が、小さく頻繁な更新と前方・後方互換のテストを勧める | 与えない |
| Azure Architecture Center「Design for change」[24] | ms.date 2018-08-30、更新 2026-03-06 | Microsoft | 10 の設計原則の 1 つ | **原則がある**。高凝集・疎結合、非同期メッセージング、公開されたインタフェースと版管理、契約に対するテスト、適応度関数、独立したデプロイ | 与えない |
| Google Cloud Well-Architected Framework [26] | 最終更新日は未確認 | Google Cloud | 6 本柱：運用上の優秀性、セキュリティ・プライバシー・コンプライアンス、信頼性、コスト最適化、パフォーマンス最適化、持続可能性。＋横断の視点（AI/ML、金融） | **柱は無い**。中核の原則に「Design for change」「Decouple your architecture」「Use a stateless architecture」など 5 つ | 与えない |
| Google SRE 本・Workbook [17][18][19] | 書籍（Web 公開） | Google | — | 変更の速さと信頼性を、エラーバジェットで釣り合わせる | 与える（SLI の比、SLO、期間） |
| DORA [37] | 2026-01-05 更新 | DORA（Google Cloud） | 5 指標 | 変更の速さと不安定さを直接測る | 与える |

読み取れること：

- **3 社のフレームワークのどれにも、変更容易性・置換容易性・保守性を名前に持つ柱は無い**。3 社とも「原則」の層に置いている（AWS：一般設計原則、Azure：Architecture Center の設計原則と OE の原則、Google Cloud：中核の原則）[22][24][26]
- 柱になっているのは、運用・セキュリティ・信頼性・性能・コスト（＋持続可能性）。ISO の 9 特性のうち Maintainability と Flexibility は、クラウドのフレームワークでは柱として独立していない
- 置換容易性（特定の製品やクラウドからの乗り換え）を扱う原則は、確認した範囲のページには見つからなかった。Google Cloud はハイブリッド・マルチクラウドにも適用できると述べるにとどまる [26]

## 4. 事故・失敗例（一次報告）

この論点（品質特性の定義と要件の書き方）に固有の事故の一次報告は、今回は調べていない。事故の事例は Part 14 のノートに任せる。関連する一次資料の記述だけ挙げる。

- Google の Chubby：障害ではなく運用上の教訓。SLO より高い可用性が続いた結果、利用側が過度に依存した。対策として計画的な停止を入れた [17]。「目標を上回りすぎることも設計上のリスク」の根拠に使える
- The Tail at Scale の測定値は、平均や単体のパーセンタイルだけを要件にすると、ファンアウトのある構成で利用者の体験を見誤ることを示す [16]

## 5. 権威の推奨と位置づけ（規範か任意か）

| 資料 | 位置づけ | 誰に向けたものか |
| --- | --- | --- |
| ISO/IEC 25010:2023 | 任意の国際規格。品質の「参照モデル」。適合の要求事項を定めるものではなく、引用規格も無い [2] | 開発者、取得者、品質保証、独立の評価者 [1] |
| JIS X 25010:2025 | 任意の国家規格（IDT）。法令や契約が引用したときだけ拘束力を持つ [4] | 同上 |
| IPA 非機能要求グレード 2018 | **任意の合意形成ツール**。目的は、ユーザ（発注者）とベンダの認識のずれを防ぐこと。レベルは合意の出発点で、最終的には具体的な数値で合意する [11][12]。事業は 2009〜2018 年度で終了し、問い合わせには対応しない [11]。IPA は内容の誤りや利用による損害に責任を負わない（使用条件）[13] | システム基盤の発注者と受注者。RFP・要件定義書・見積もりで使う想定 [12] |
| AWS・Azure・Google Cloud の Well-Architected | ベンダーの任意の指針。自社クラウド上のワークロードの見直し用 [22][23][26] | 各クラウドの利用者 |
| Google SRE 本・Workbook | 1 社の実践の公開。規範ではない [17][18][19] | 運用・開発の担当者 |
| Thoughtworks Technology Radar | 1 社の見解。リングは同社の経験にもとづく評価 [27][28] | 技術の選定をする人 |
| NIST SP 800-34 Rev. 1 | 米国連邦機関向けの指針。日本の民間には任意 [20] | 連邦の情報システムの緊急時対応計画の担当者 |
| DORA | 調査にもとづく指標の提案。任意 [37] | 開発組織 |

IPA 非機能要求グレード 2018 の中身：

- **6 大項目**：可用性、性能・拡張性、運用・保守性、移行性、セキュリティ、システム環境・エコロジー [13][15]
- 規模：6 大項目・34 中項目・116 小項目・238 メトリクス（2019 年の講義資料の抜粋による）[15]。メトリクスごとにレベル 0〜5 を定める [12]
- 構成：利用ガイド（解説編・利用編・活用編）、グレード表（3 つのモデルシステム）、項目一覧、樹系図、活用シート [11]
- **性能・拡張性**（B）の中項目：業務処理量（通常時の業務量、業務量増大度、保管期間）、性能目標値（オンラインレスポンス、バッチレスポンス、オンラインスループット、バッチスループット、帳票印刷能力）、リソース拡張性（CPU・メモリ・ディスク・ネットワーク、サーバ処理能力増強＝スケールアップ／スケールアウト）、性能品質保証（帯域保証、HW リソース専有、性能テスト、スパイク負荷対応）[13]
  - 性能目標値は「順守率」で書く（B.2.1.1 通常時・B.2.1.2 ピーク時・B.2.1.3 縮退時のレスポンス順守率）[13]。**パーセンタイルと同じ発想**（「何 % の要求が目標時間内か」）で、SRE の SLI の書き方 [19] につながる
- **運用・保守性**（C）の中項目：通常運用（運用時間、バックアップ、運用監視、時刻同期）、保守運用（計画停止、運用負荷削減、パッチ適用ポリシー、活性保守、定期保守頻度、予防保守レベル）、障害時運用、運用環境（開発用・試験用環境、外部システム接続など）、サポート体制（ライフサイクル期間など）、その他の運用管理方針（構成管理・変更管理・リリース管理など）[13]
- **移行性**（D）の中項目：移行時期（システム移行期間、システム停止可能日時、並行稼働の有無）、移行方式（拠点展開・業務展開のステップ数）、移行対象（機器）、移行対象（データ）、移行計画（作業分担、リハーサルの範囲・環境・回数、トラブル対処）[13]
- **対象外**：主に業務アプリケーションで決まる項目（ユーザビリティ、機能性、**移植性**など）と、個別の製品・構成の選択 [12]。FAQ は、ISO/IEC 9126 などを参考にしたが全項目は網羅しないと答える [12]
- 限界：対象は「システム基盤」（ハードウェア、OS、ミドルウェア）で、発注者と受注者が 1 回の構築で合意する前提 [12]。**マイクロサービスの間の契約、スキーマの互換性、継続的な更新、コンポーネントの置換は項目に無い**（項目一覧と樹系図を見た範囲）[13]。置換に最も近いのは移行性だが、1 回の移行計画として書かれている
- 2026-11 の時点でも、経済産業省・IPA（DADC）のガイドライン（1.0 beta 版の附属書）が非機能要件の整理に参照している（検索抜粋。ベータ版）[39]

## 6. 設計判断の分かれ目（何を選ぶと何を得て何を失うか。表）

| 判断 | 選択肢 | 得るもの | 失うもの |
| --- | --- | --- | --- |
| 4 つの性質の語彙 | ISO/JIS の語彙に揃える | 規格で説明でき、社外と通じる。JIS の訳語と字面が合う [7] | 「動かしたまま」「版の混在」「データを伴う」が抜ける（2.5） |
| | 独自に定義する | 現場の関心に合う | 共通の基準にならない。定義の説明責任が増える |
| 「拡張性」の意味 | 負荷への拡張（scalability）だけ | JIS・IPA と一致 [7][13] | 機能の追加しやすさ（extensibility）を別の言葉で扱う必要 |
| 性能の要件 | 平均 | 計算が簡単 | 裾を見落とす [16][17] |
| | パーセンタイル（p50・p99・p99.9） | 利用者の体験に近い。ファンアウトの影響を扱える [16] | 測定の基盤とサンプル数が要る。合算できない（平均のように足せない。記憶・要確認） |
| 可用性の測り方 | 時間ベース（稼働率） | IPA・契約と合う [13] | 部分的な障害を表せない [18] |
| | 要求ベース（成功率） | 分散サービスに合う [18] | 要求が来ない時間帯の障害が見えにくい |
| 信頼性の目標 | 100% を目指す | 説明が簡単 | 達成できず、変更が止まる [18] |
| | SLO ＋エラーバジェット | 変更の速さと信頼性を同じ数字で釣り合わせる [18][19] | 合意文書（ポリシー）と、止める権限が要る |
| 復旧の目標 | RPO・RTO だけ | DR の要件が明確 [20][21] | 日常の小さな障害（平均的な回復力）を表さない [21] |
| 負荷への備え | スケールアップ | 構成が単純。トランザクション管理が容易 [32] | 上限がある。単一障害点 |
| | スケールアウト（shared-nothing） | 費用対効果、上限が高い [32] | 分散デッドロック、多相コミット、配置の設計 [32] |
| 置換性・更新性の検査 | レビューだけ | 道具が要らない | 時間とともに崩れても気づかない |
| | 適応度関数として CI・運用に入れる | 継続して守れる。数字が残る [24][27] | 検査を作って保つ費用。測りやすいものに偏る |
| 非機能要件の枠 | IPA グレードをそのまま使う | 項目の漏れを防ぐ。レベルで費用感を共有 [12] | サービス間の契約・互換性・継続的な更新が項目に無い [13] |
| | IPA ＋ SLO ＋適応度関数 | 基盤の要件と、変化への要件の両方 | 表が大きくなる。保つ責任者が要る |

## 7. 設計レビューで問うこと（問い｜なぜ問うか｜危ない兆候）

| # | 問い | なぜ問うか | 危ない兆候 |
| --- | --- | --- | --- |
| 1 | 「柔軟性・拡張性・置換性・更新性」を、それぞれ何の数字で確かめるか | 数字のない性質はレビューできない | 形容詞だけで書いてある |
| 2 | 「拡張性」は、負荷への対応か、機能の追加か | 同じ言葉で 2 つの意味がある（2.5） | 会議の中で意味が入れ替わる |
| 3 | 負荷のパラメータは何で、3 年後に何倍か | 業務処理量を最初に決めないと性能を合意できない [12] | 「ユーザ数」だけで、読み書きの比や増大率が無い |
| 4 | 1 つの利用者の要求は、内部で何台・何サービスに広がるか | ファンアウトが裾を増幅する [16] | 単体の p99 だけを目標にしている |
| 5 | レイテンシは、どのパーセンタイルを、どこで測るか | 平均は裾を隠す。サーバー側と利用者側はずれる [17] | 平均応答時間だけ。測る場所が未定 |
| 6 | SLI は「良いイベント ÷ 全イベント」で書けているか | 書けない指標は予算にできない [19] | 「高可用」「高速」 |
| 7 | SLO は現状の値から決めていないか。100% になっていないか | 現状追認は無理な維持を強いる。100% は変更を止める [17][18] | 「現行と同等以上」「無停止」 |
| 8 | エラーバジェットを使い切ったら、誰が何を止めるか | 合意と権限が無いと予算は働かない [18][19] | ポリシーの文書が無い |
| 9 | RPO・RTO は、どの障害を想定した数字か。試したか | 1 回の事象の上限であり、平均ではない [21] | 可用性の % と混同。復旧の演習の記録が無い |
| 10 | パイプラインやストレージの SLI（鮮度・正確性・網羅率・耐久性）はあるか | 要求駆動の指標だけでは派生データを守れない [19] | 分析基盤・ETL に SLO が無い |
| 11 | この部品を別の製品に置き換えるとき、何を作り直すか。何日かかるか | 規格の置換性は「同じ目的・同じ環境」まで。データと切り替えは別に問う（2.5） | 「標準 SQL だから大丈夫」 |
| 12 | 更新の途中で新旧の版が混在する時間に、何が起きるか | 更新性は規格に名前が無く、抜けやすい（2.5） | 一斉更新が前提。互換性の検査が無い |
| 13 | 置換性・更新性を守る検査は、自動で毎回動いているか | 性質は時間とともに崩れる [24][27] | 設計書にだけ書いてある |
| 14 | 変更のリードタイム・変更失敗率を測っているか | 変更容易性を結果として測る指標 [37] | デプロイの回数も失敗も数えていない |
| 15 | スケールアウトを選ぶなら、分散トランザクションと配置の設計を誰が持つか | shared-nothing の代償 [32] | 「台数を足せば伸びる」 |
| 16 | 計画停止はあるか。パッチはいつ・どう当てるか | IPA の運用・保守性の項目。更新性の前提 [13] | 「無停止」と「定期保守あり」が同じ文書にある |
| 17 | 並行稼働の期間と、切り戻しの条件はあるか | IPA の移行性の項目 [13] | 一発切り替え。リハーサルなし |
| 18 | その要件は、どの文書のどの位置づけ（規範か任意か）にもとづくか | 任意の推奨を規範として扱うと議論が止まる | 「IPA で決まっている」「AWS がそう言っている」 |
| 19 | 目標を大きく上回っている依存先は無いか | 利用側の過度な依存を生む [17] | 「あの基盤は落ちない」前提の設計 |
| 20 | 共通基盤の SLO は、それに乗るサービスの SLO より高いか | 依存先より高い信頼性は約束できない（一般論。記憶・要確認） | 基盤に SLO が無い |

## 8. ケーススタディで測れること・測れないこと

測れる：

- **パーセンタイルとファンアウトの増幅**：1 つの要求を N 個のバックエンドに広げ、p50・p99 を数える。0.99^N の計算と実測を比べられる（同一ホスト内の相対比較）
- **更新性**：題材 B の「壊れた受け手の数」「書き込みが止まった時間」「ロック待ち」。互換性検査のあり・なしの差
- **置換性**：題材 B の派生ストアの差し替えにかかる時間、ログからの再構築の所要時間と一致率
- **回復**：題材 D の昇格で失われた応答済みコミットの件数（RPO の実測）、昇格までの時間（RTO の実測）
- **SLI の計算**：良いイベント ÷ 全イベントを結果のファイルから数え、エラーバジェットの消費として示す
- **適応度関数**：スキーマの互換性検査と再構築の一致率の検査を、スクリプトとして毎回流す

測れない（未検証と明記する）：

- **拡張性（scalability）の絶対値**：単一ホストの Docker では、台数を足しても資源は増えない。スケールアウトの効果は測れない
- 実運用の裾（p99.9 以上）：サンプル数と環境のばらつきが足りない。The Tail at Scale の原因の多く（共有資源、電力、SSD の GC）は再現できない
- 可用性の % ：数週間の観測が要る
- 製品を丸ごと別の製品に置き換える費用（人の作業時間）
- クラウドの製品の SLA・RPO・RTO

注意：負荷試験の道具によっては、応答が遅れたときに次の要求の送信も遅れ、裾を小さく見積もる（coordinated omission。記憶・要確認）。測り方は決まった送信レートで行い、方法を結果に書く。

## 9. 未確定・要確認

- ISO/IEC 25010:2023 の箇条 3.5〜3.9 の本文と箇条番号、附属書 A の対応表。二次資料の引用 [5][6][7] によった。規格（または JIS X 25010:2025）を入手して確かめる
- testability が保守性の下にあること（2.3）。arc42 の一覧ページだけが異なる
- 「Maintainability は更新・アップグレードの導入を含む」という注記は arc42 の引用による [6]。本文で確かめる。更新性の対応づけの根拠になるため重要
- JIS X 25010:2025 の訳語（拡張性＝scalability、無障害性、インストール性、テスト可能性）は二次資料 [7][8] による。JIS 本文は未確認。JIS X 25002・25019 の発行日も未確認
- 2023 年版に対応する測定量の規格（ISO/IEC DIS 25000-23.2）の内容と発行時期 [10]
- IPA の 34 中項目・116 小項目・238 メトリクスは 2019 年の講義資料の抜粋による [15]。項目一覧から数え直していない。移行対象（機器）・移行対象（データ）の小項目は、抽出したテキストが崩れており一部しか読めていない [14]
- Krikorian の講演の中の数値（タイムラインの読み書きの件数）[31]
- 『Building Evolutionary Architectures』第 2 版の書誌と、適応度関数の分類（atomic／holistic、triggered／continual など）。日本語版『進化的アーキテクチャ』の版と訳語（記憶・要確認）
- Thoughtworks Radar の「Architectural fitness function」は 2018-05 の Trial が最後の掲載 [27]。2026 年の別の項目の関連欄にも Trial と表示されていた（検索抜粋）。その後の再評価は無いとみられるが、Radar の全号は確認していない
- AWS Well-Architected Framework の最新の改訂日。改訂履歴で見えた直近の Major update は 2024-11-06 [22]。それ以降の小さな更新は未確認
- Google Cloud Well-Architected Framework のページの最終更新日 [26]
- Rowe・Leaney・Lowe（1998）の原典、Breivold・Crnkovic の論文の掲載先と年（Euromicro SEAA 2009 とみられる。記憶・要確認）[33][35]
- 2.9 の表の道具（Schema Registry の互換性モード、ArchUnit）の仕様は、このノートでは確かめていない

## 10. 結論（スライドに書くこと。箇条書き 15〜30 個、各項目に出典の番号）

1. ISO/IEC 25010 は 2023-11 に第 2 版になり、製品品質の特性は 8 から 9 になった。2011 年版は廃止 [1][2]
2. 2023 年版は Portability を Flexibility に、Usability を Interaction capability に置き換え、Safety を足した [2]
3. scalability は 2023 年版で初めて副特性になった（Flexibility の下）。2011 年版では適応性の注記にあるだけだった [2][9]
4. Reliability の maturity は faultlessness に置き換わった [2]
5. 日本語の対応版は JIS X 25010:2025（2025-12-22 改正、ISO/IEC 25010:2023 と一致）[4]
6. 依頼者の 4 語のうち、柔軟性・拡張性・置換性は JIS X 25010:2025 の訳語と字面が一致する（柔軟性＝Flexibility、拡張性＝scalability、置換性＝replaceability）。JIS 本文は未確認で、二次資料による [7][8]
7. 「更新性」は規格に同名の副特性が無い。Maintainability・modifiability・installability・replaceability にまたがる [6][7]
8. 「拡張性」は 2 つの意味で使われる。負荷への対応（scalability）は規格にある。機能の追加しやすさ（extensibility）は副特性名に無く、modifiability と modularity で受ける [7][33]
9. 規格の置換性は「同じ環境で、同じ目的の別の製品と置き換える」まで。稼働中の切り替え、データの移行、版の混在は、規格の語彙の外 [6][7]
10. 4 語は Flexibility と Maintainability の 2 特性にまたがり、Compatibility と Reliability に支えられる（このノートの整理）[2][7]
11. ISO/IEC 25010 は参照モデルで、数字の書き方は与えない。測定量の規格（25023:2016）は 2011 年版向けで、後継は草案 [2][10]
12. IPA 非機能要求グレード 2018 は、発注者と受注者が合意するための任意の道具。6 大項目は可用性、性能・拡張性、運用・保守性、移行性、セキュリティ、システム環境・エコロジー [11][12][13]
13. IPA のグレードはシステム基盤が対象で、移植性は対象外。サービス間の契約・互換性・継続的な更新は項目に無い [12][13]
14. IPA は性能を「レスポンス順守率」で、復旧を RPO・RTO・RLO で、拡張をスケールアップ・スケールアウトで書かせる [13]
15. 性能は平均でなく分布で書く。p50 は典型、p99・p99.9 は最悪に近い場合 [17]
16. 1 台の p99 が 1 秒でも、100 台に広げて全部を待てば 63% の要求が 1 秒を超える。裾はファンアウトで増幅する [16]
17. SLI は「良いイベント ÷ 全イベント」、エラーバジェットは 100% − SLO [19]
18. 100% は目標として誤り。エラーバジェットは、変更の速さと信頼性を同じ数字で釣り合わせる [18]
19. SLO は現状から決めない、単純にする、絶対を避ける、少なくする [17]
20. 派生データには別の SLI が要る：鮮度・正確性・網羅率。ストレージは耐久性 [19]
21. RPO は失ってよいデータの時間幅、RTO は戻るまでの時間。どちらも 1 回の事象の上限で、可用性（期間の平均）とは別 [20][21]
22. ファンアウトの例の原典は Krikorian の QCon SF 2012 の講演。DDIA 2e は数字を一般化している [31][38]
23. shared-nothing は 1986 年の Stonebraker の整理。費用対効果と引き換えに、分散デッドロック・多相コミット・配置の設計を負う [32]
24. 適応度関数は、アーキテクチャ特性を客観的に評価する仕組み。テスト・メトリクス・監視を含む [27][30]
25. Thoughtworks Radar で「Architectural fitness function」は Trial（2017-11、2018-05）。「Dependency drift fitness function」は Adopt（2020-10）。どちらも現行の版には載っていない [27][28]
26. 置換性・更新性は、互換性の検査、依存の古さ、再構築の一致率、他サービスの DB への直接接続の数、として自動で検査できる（このノートの提案）[24][28]
27. 変更容易性は結果でも測れる：変更のリードタイム、デプロイ頻度、変更失敗率、失敗したデプロイの復旧時間、手戻り率 [37]
28. AWS・Azure・Google Cloud のフレームワークに、変更容易性・置換容易性の柱は無い。3 社とも原則の層に置く（AWS「Consider evolutionary architectures」、Azure「Design for change」、Google Cloud「Design for change」「Decouple your architecture」）[22][23][24][26]
29. 進化可能性の定義は複数ある。よく引かれるのは「要求の変化を、寿命を通じて、最小の費用で、アーキテクチャの一貫性を保って受け入れる能力」。ISO/IEC 25010 の特性名には無い [33]
30. どの資料も任意の指針であり、規範ではない。規格・IPA・ベンダーの文書を、要件の「根拠」ではなく「語彙と項目の出どころ」として使う [2][12][22]

## 11. 出典（番号｜題名｜発行者｜版・日付｜URL｜確認の深さ）

| 番号 | 題名 | 発行者 | 版・日付 | URL | 確認の深さ |
| --- | --- | --- | --- | --- | --- |
| 1 | ISO/IEC 25010:2023 Product quality model（カタログページ） | ISO | 第 2 版、2023-11 | https://www.iso.org/standard/78176.html | 本文確認（概要・書誌・段階の履歴） |
| 2 | ISO/IEC 25010:2023 のプレビュー PDF | ISO/IEC（iTeh Standards が配布） | 第 2 版、2023-11 | https://cdn.standards.iteh.ai/samples/78176/13ff8ea97048443f99318920757df124/ISO-IEC-25010-2023.pdf | 本文確認（まえがき、序文、目次、箇条 1〜3.4.4 のみ。3.5 以降と附属書は未確認） |
| 3 | ISO Online Browsing Platform の ISO/IEC 25010:2023 | ISO | — | https://www.iso.org/obp/ui/en/#iso:std:iso-iec:25010:ed-2:v1:en | 未確認（利用規約の同意画面まで） |
| 4 | JIS X 25010:2025 の書誌とプレビュー | 日本規格協会 | 2025-12-22 改正 | https://webdesk.jsa.or.jp/books/W11M0090?bunsyo_id=JIS+X+25010%3A2025 ／ https://webdesk.jsa.or.jp/preview/pre_jis_x_25010_000_000_2025_j_ed10_ch.pdf | 題名のみ（検索結果の抜粋で、書誌・履歴・序文の一部を確認。規格の本文は未確認） |
| 5 | ISO/IEC 25010（解説ページ、全 2 ページ） | iso25000.com | 日付なし（フッターは 2024） | https://iso25000.com/index.php/en/iso-25000-standards/iso-25010 | 本文確認（二次資料。9 特性だが定義の文型は 2011 年版） |
| 6 | arc42 Quality Model：ISO/IEC 25010 の一覧、「Update on ISO 25010, version 2023」、各品質のページ（flexibility、scalability、adaptability、installability、replaceability、maintainability、modularity、reusability、analysability、modifiability、testability、reliability、updateability） | Gernot Starke（arc42） | 日付なし | https://quality.arc42.org/standards/iso-25010 ／ https://quality.arc42.org/articles/iso-25010-update-2023 ／ https://quality.arc42.org/qualities/replaceability ほか | 本文確認（二次資料。ISO-25010:2023 からの引用として掲載） |
| 7 | シン・テストファースト（JIS X 25010:2025 の特性・副特性と定義の表） | バルテス | 公開 2023-05-12、更新 2026-04-15 | https://service.valtes.co.jp/s-test/blog/test-first_vol25 | 本文確認（二次資料。出典に JIS X 25010:2025 を明記） |
| 8 | SQuBOK 参照規格の改訂状況（ソフトウェア品質シンポジウム 2026 の発表資料） | 日本科学技術連盟 | 2026 | https://www.juse.jp/sqip/symposium/timetable/files/C2-1_2_happyou.pdf | 題名のみ（検索結果の抜粋。PDF の本文は読めなかった） |
| 9 | JIS X 25010:2013 の転載、および「ソフトウェア品質特性とは？」 | kikakurui.com ／ ベリサーブ | 2013 ／ 2025-06-18 | https://kikakurui.com/x2/X25010-2013-01.html ／ https://www.veriserve.co.jp/helloqualityworld/media/20250618001 | 前者は検索抜粋のみ、後者は本文確認（どちらも二次資料） |
| 10 | ISO/IEC 25023:2016 Measurement of system and software product quality（カタログページ） | ISO | 2016 | https://www.iso.org/standard/35747.html | 本文確認（概要と後継の表示） |
| 11 | システム構築の上流工程強化（非機能要求グレード）紹介ページ | IPA | 2023-08 時点の情報 | https://www.ipa.go.jp/archive/digital/iot-en-ci/jyouryuu/hikinou/ent03-b.html | 本文確認 |
| 12 | 非機能要求グレード 2018 利用ガイド［解説編］ | IPA | 2018-04 | 同ページの一括ダウンロード（000028843.zip） | 本文確認（1.3.3、1.4、FAQ の該当部分） |
| 13 | 非機能要求グレード 2018 システム基盤の非機能要求に関する樹系図 | IPA | 2018-04 | 同上 | 本文確認（A〜D の項目。使用条件） |
| 14 | 非機能要求グレード 2018 システム基盤の非機能要求に関する項目一覧 | IPA | 2018-04 | 同上 | 本文確認（一部。抽出したテキストが崩れた箇所は未確認） |
| 15 | 非機能要求グレードの講義 | IPA | 2019 | https://www.ipa.go.jp/archive/files/000072715.pdf | 題名のみ（検索結果の抜粋で項目数を確認） |
| 16 | The Tail at Scale | Jeffrey Dean・Luiz André Barroso、Communications of the ACM | 56 巻 2 号 74–80 ページ、2013-02 | https://www.barroso.org/publications/TheTailAtScale.pdf ／ https://research.google/pubs/the-tail-at-scale/ | 本文確認（著者公開の PDF） |
| 17 | Site Reliability Engineering 4 章 Service Level Objectives | Google | 書籍（Web 公開） | https://sre.google/sre-book/service-level-objectives/ | 本文確認 |
| 18 | Site Reliability Engineering 3 章 Embracing Risk | Google | 書籍（Web 公開） | https://sre.google/sre-book/embracing-risk/ | 本文確認（式は画像で未確認） |
| 19 | The Site Reliability Workbook 2 章 Implementing SLOs | Google | 書籍（Web 公開） | https://sre.google/workbook/implementing-slos/ | 本文確認 |
| 20 | NIST CSRC Glossary：Recovery Point Objective、Recovery Time Objective（出典 SP 800-34 Rev. 1） | NIST | — | https://csrc.nist.gov/glossary/term/recovery_point_objective ／ https://csrc.nist.gov/glossary/term/recovery_time_objective | 本文確認（用語集。SP 800-34 の本文は未確認） |
| 21 | Reliability Pillar：Disaster Recovery (DR) objectives | AWS | 日付なし（「歴史的参照のみ」の注記あり） | https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/disaster-recovery-dr-objectives.html | 本文確認 |
| 22 | AWS Well-Architected Framework：General design principles、Definitions、Document revisions | AWS | 改訂履歴で見えた直近の Major update は 2024-11-06 | https://docs.aws.amazon.com/wellarchitected/latest/framework/general-design-principles.html ／ https://docs.aws.amazon.com/wellarchitected/latest/framework/definitions.html | 本文確認（原則と改訂履歴の該当部分。全体は通読していない） |
| 23 | Azure Well-Architected Framework pillars | Microsoft | ms.date 2025-01-22 | https://learn.microsoft.com/en-us/azure/well-architected/pillars | 本文確認 |
| 24 | Design for change（Azure Architecture Center の設計原則） | Microsoft | ms.date 2018-08-30、更新 2026-03-06 | https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/design-for-evolution | 本文確認 |
| 25 | Operational Excellence design principles | Microsoft | ms.date 2025-05-05 | https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/principles | 本文確認 |
| 26 | Google Cloud Well-Architected Framework（概要） | Google Cloud | 最終更新日は未確認 | https://docs.cloud.google.com/architecture/framework | 本文確認（柱・視点・中核の原則） |
| 27 | Technology Radar：Architectural fitness function | Thoughtworks | Trial、2017-11・2018-05 | https://www.thoughtworks.com/radar/techniques/architectural-fitness-function | 本文確認 |
| 28 | Technology Radar：Dependency drift fitness function | Thoughtworks | Trial 2019-11、Adopt 2020-10 | https://www.thoughtworks.com/radar/techniques/dependency-drift-fitness-function | 本文確認 |
| 29 | Technology Radar：Run cost as architecture fitness function | Thoughtworks | 2019 年から Adopt と記載 | https://www.thoughtworks.com/radar/techniques/run-cost-as-architecture-fitness-function | 題名のみ（検索結果の抜粋） |
| 30 | Building Evolutionary Architectures（著者サイトの要旨） | Neal Ford・Rebecca Parsons・Patrick Kua | サイトは 2017 | https://evolutionaryarchitecture.com/precis.html | 本文確認（定義の 2 文）。第 2 版の O'Reilly のページは開けず未確認 |
| 31 | Timelines at Scale | Raffi Krikorian、InfoQ | QCon San Francisco 2012、公開 2013-04-03 | https://www.infoq.com/presentations/Twitter-Timeline-Scalability/ | 本文確認（ページの書誌のみ。動画と数値は未確認） |
| 32 | The Case for Shared Nothing | Michael Stonebraker、IEEE Database Engineering Bulletin | 9 巻 1 号、1986-03 | https://dsf.berkeley.edu/papers/hpts85-nothing.pdf | 本文確認（要旨、1〜2 節、表 1 の一部） |
| 33 | Analysis of Software Evolvability in Quality Models | Hongyu Pei Breivold・Ivica Crnkovic | 掲載先と年は記憶・要確認 | https://www.es.mdu.se/pdf_publications/1396.pdf | 本文確認（1〜3.3 節） |
| 34 | A Systematic Review of Software Evolvability | Hongyu Pei Breivold | 日付未確認 | https://www.es.mdh.se/pdf_publications/1739.pdf | 題名のみ（検索結果の抜粋） |
| 35 | Defining systems evolvability - a taxonomy of change | D. Rowe・J. Leaney・D. Lowe | 1998 | —（[33] の参考文献 [15] として確認） | 未確認（原典は開いていない） |
| 36 | Software-Evolvability（Informatiklexikon） | Gesellschaft für Informatik | 日付未確認 | https://gi.de/informatiklexikon/software-evolvability | 題名のみ（検索結果の抜粋） |
| 37 | DORA's software delivery performance metrics | DORA | 2026-01-05 更新 | https://dora.dev/guides/dora-metrics/ | 本文確認 |
| 38 | データ指向アプリケーションデザイン 第2版 2 章（2.1、2.2.2、2.4.2 と参考文献） | Kleppmann・Riccomini 著、斉藤 太郎 訳、オライリー・ジャパン | 第 2 版 | —（手元の書籍） | 本文確認（目次、2.1 のファンアウトの数値、参考文献 [2][3][26][84] の書誌。章全体の対応づけは別の担当） |
| 39 | サプライチェーン上のデータ連携の仕組みに関するガイドライン 1.0 beta 版 附属書 D：非機能要件 | 経済産業省・IPA（DADC） | 1.0 beta、2026-11 | https://www.ipa.go.jp/digital/architecture/documents/rqr7mi000000gpyu-att/annex_d_guide_sc-ba-cfp_1_0_beta.pdf | 題名のみ（検索結果の抜粋。ベータ版） |
