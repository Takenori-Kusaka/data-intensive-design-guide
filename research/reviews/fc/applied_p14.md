# ファクトチェックの反映：deck/p14.js（S205〜S220、Part 14）

反映日 2026-11-18。`node build_one.js p14`：エラーなし、refs 漏れ 0、ノート漏れ 0。PowerPoint での見た目は確かめていない（配置は AUTHORING.md 3 節の数値で計算した）。

## Part 17 の担当へ（最終の文言と数）

**型②の 2 つの問いの最終の文言**（S209 の一覧表、S219 の設計レビューの表で同じ文字列）

> 全体で 1 つしかないものは何か。この基盤が 1 時間止まったら、どのサービスが止まるか。その一覧は誰が持つか

**型ごとの件数**（24 件。1 件が複数の型に入る）

| 型 | 件数 | S209 の表記 | 変更 |
| --- | --- | --- | --- |
| ① 設定・ルールの一斉配布 | **6** | CrowdStrike 2024、Google 2025、Cloudflare 2025-11 ほか 3 件 | 7 → 6（Datadog 2023 を外した。D5） |
| ② 基盤への集中と循環依存 | 6 | ほか 3 件 | なし |
| ③ 復旧・監視の手段が同じ基盤上 | 9 | ほか 6 件 | なし。9 件の名前：AWS 2021、Roblox 2021、Slack 2021、S3 2017、Kinesis 2020、Google Cloud 2025、Meta 2021、Atlassian 2022、Google 2020-12-14（S212 のノートに全部、9 件目は下の対策の箱にも出した） |
| ④ 自動化の誤動作 | 5 | ほか 2 件 | なし |
| ⑤ 再試行の嵐 | 7 | ほか 4 件 | なし |
| ⑥ 復元できないバックアップ | 3 | — | なし |
| ⑦ 削除の単位の誤り | 5 | ほか 2 件 | なし |
| ⑧ 隠れた共有 | 3 | Datadog 2023、Cloudflare 2023、Google 2025 | なし（Datadog はここだけ） |

**引き金の件数**（指定の 19 件。1 件 1 分類）

- 変更・操作 13 件（境界の取り方で 12〜14 件）／機器・電源・ネットワークの障害や乱れ 3 件／負荷の増加 2 件／変更を伴わない潜在的な不具合 1 件
- 変更・操作の内訳：設定・ルール・ポリシーの変更と配布 3（CrowdStrike 2024、Cloudflare 2024-11・2025-11）、コマンド・スクリプト 3、ソフトウェアの更新・機能の有効化 4（Roblox 2021、Slack 2022、Datadog 2023、Google Cloud 2025）、容量 2、保守作業 1
- 境界の 3 件：Google Cloud 2025-06、Cloudflare 2023-11、GitLab 2017-01
- **この数の出どころ**：反映を始めた時点では `applied_p00-p02.md` が無かったので、決定 D1 の数と内訳で直した。最後にもう一度見たときには出来ており、冒頭の「D1 の最終の数と内訳、境界の 3 件」を読んだ。合計（13／3／2／1）、内訳（3・3・4・2・1 で確定）、各内訳の件名、境界の 3 件のすべてが、p14.js の S207 と一致している。直しは要らなかった
- 題の文言：S207「19 件の事後報告で、引き金の多くは変更・操作」

**Part 17 で文言を合わせる必要がありうる箇所**

- 「段階は範囲を限るが、検出はしない」は Part 14 から無くした（D4）。まとめ（S220）は「互換性検査と段階配布の両方が要る。段階ごとに何を見るかを決める」
- 型①の説明は「数秒で全体に届く」から「短時間で全体に届く」に（S209 の表、S210 の題）。S219 の「なぜ問うか」は「データは数秒で全体に届いた（Google 2025、Cloudflare 2025-12）」（この 2 件は原文が within seconds）
- 「故障」という分類名は「機器・電源・ネットワークの障害や乱れ」に（D1）
- 静的な安定性の 3 つ（先に配る／手元の情報で動く／障害時だけの迂回路を作らない）は「本ガイドの束ね方」と書いた（S218・S220）

## 決定 D4 の結論

Cloudflare 2026-02-20 の事後報告（https://blog.cloudflare.com/cloudflare-outage-february-20-2026/）を取得し、本文を語句で検索して読んだ。

- 段階配布とは呼んでいない：「This incident did not impact all BYOIP customers because the configuration change was applied iteratively and not instantaneously across all BYOIP customers」。staged／gradual rollout の語は、この変更の配り方の説明には無い（gradual・health-mediated は今後の方針の文脈だけ）
- 検出している：「We were able to detect impact on one.one.one.one and revert the impacting change before more prefixes were impacted」
- 結論：「段階的な配布の途中」「検出はしなかった」とは言えない。**S217 の例から外した**。S215（型⑥⑦）と S216（値なしの意味）の事実の記述は残した
- 空いた 3 枚目の箱には、Google Cloud 2025-06-12 を置いた（原文で確認：「This code change and binary release went through our region by region rollout, but the code path that failed was never exercised during this rollout due to needing a policy change that would trigger the code」「If this had been flag protected, the issue would have been caught in staging」）。**取りまとめ役の決定には無い差し替えなので、不要なら 2 枚に戻してほしい**

## 反映の記録（全指摘）

| 指摘の出どころ | スライド | 指摘の要点 | 自分で確かめた一次資料と結果 | 対応 | 直した後の文、または直さない理由 |
| --- | --- | --- | --- | --- | --- |
| D_products #1／決定 D5 | S209・S211・S219 | 型②の問いが、一覧表と設計レビューで別物 | スライドどうしの食い違い（一次資料なし） | 直した | S209 の表と S219 の表を「全体で 1 つしかないものは何か。この基盤が 1 時間止まったら、どのサービスが止まるか。その一覧は誰が持つか」に統一。両方のノートに「型 2 は問いが 2 つ」と書いた。S209 は列幅を [2.45, 3.35, 2.7, 3.6]、rowH 0.47 に。S211 のリードは 1 つ目の問いと合っているのでそのまま |
| D_products #2／決定 D4 | S217・S220 | Cloudflare 2026-02-20 を段階配布の例に並べ「検出はしなかった」 | 原文を取得。上の「D4 の結論」のとおり、指摘は正しい | 直した | S217 から外し、Google Cloud 2025-06-12 に差し替え。リード「段階配布の途中で起きた件と、段階配布を通り抜けたあとに起きた件がある」。ノートに、外した理由と「段階に分けるだけでは見つからず、各段で何を見るかを決める必要がある（本ガイドの読み取り）」。根拠の行も差し替え。S220 は「段階ごとに何を見るかを決める」 |
| D_products #3／決定 D1 | S207 | Google Cloud 2025 が「設定の配布」に分類されている | 原文（status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW）を取得。先に挙がるのは「On May 29, 2025, a new feature was added to Service Control…This code change and binary release went through our region by region rollout」。ポリシーの投入は 6/12。指摘は正しい | 直した | 表：設定 4 → 3、ソフトウェアの更新 3 → 4。該当欄「Google Cloud 2025（境界：先に挙がるのは 5/29 のコードの配布。停止は 6/12 のポリシーの変更から）」 |
| 決定 D1 | S205・S207・S220 | 題を幅のある形に。「故障」を「障害や乱れ」に。境界の 3 件を明示 | DynamoDB 2015 は FC の照合表（network disruption）による。Cloudflare 2023-11 は原文を取得：「Portland General Electric (PGE)…had an unplanned maintenance event affecting one of their independent power feeds」。GitLab 2017 は FC の照合表による（自分では開き直していない） | 直した | S207 題「19 件の事後報告で、引き金の多くは変更・操作」、リード「変更・操作 13 件（境界の取り方で 12〜14 件）、機器・電源・ネットワークの障害や乱れ 3 件」。表の行名「機器・電源・ネットワークの障害や乱れ」、DynamoDB「短いネットワークの乱れ」、境界の 3 件は該当欄に「境界：」と書いた。ノートも同じ数に。S205 の扉の問い「機器の障害と変更のどちらが多いか」、扉のノート。S220 の 1 つ目「変更・操作が 19 件中 13 件（境界の取り方で 12〜14 件）」。「スイッチの部分故障」（Cloudflare 2020、原文 partially operating）は分類名ではないので残した |
| D_products #4／決定 D5 | S210・S209 | Datadog 2023 を型①の「同じ型」に入れている | 原文（datadoghq.com の 2023-03-08 の報告）を取得：「a security update to systemd was automatically applied」「the base OS image…had a legacy security update channel enabled」「a window between 06:00 and 07:00 UTC」。配られたのはデータではなく OS の更新。指摘は正しい | 直した | S210 の注記から Datadog を外し、ノートに「配られたのがデータではなく OS の更新なので、この型には入れず、型 8 に置きました」。S209 の型①「ほか 4 件」→「ほか 3 件」。S207 の引き金（ソフトウェアの更新）と S211・S219 の型⑧はそのまま |
| D_products #6／決定 D5 | S212・S219 | 型③「9 件」のうち名前が出るのは 8 件 | Google 2020-12-14 の原文（status.cloud.google.com/incident/zall/20013）を取得：対策 3「Improve reliability of tools and procedures for posting external communications during outages that affect internal tools」。割り当ては妥当 | 直した | S212 のノートに 9 件の名前を全部書き、9 件目の対策を説明。下の対策の箱に「障害時に外へ掲示する道具と手順を改善する（9 件目の Google 2020-12-14）」。出典の補足に Google 2020-12-14 を足した |
| D_products #7 | S215 | Cloudflare 2026-02-20「検証環境のデータでは再現しなかった」は原文に無い言い回し | 原文：「Our staging environment contains data that matches Production as closely as possible, but was not sufficient in this case and the mock data we relied on…was insufficient」。指摘は正しい | 直した | 「検証環境のデータと模擬データが足りず、事前に見つけられなかった。約 300 は人手で復旧。全体で 6 時間 7 分」 |
| D_products #8 | S212 | Atlassian の対策「連絡先を製品の外にも持つ」は原文に無い | 原文（atlassian.com の post-incident review）を取得：「we will improve the backup of key contacts and retrofit support tooling to enable customers without a valid URL or Atlassian ID to make direct contact with our technical support team」。指摘は正しい | 直した | 「主要な連絡先の控えを改善し、URL や ID が無い顧客も問い合わせられるようにする（Atlassian）」。ノートにも同じ内容。箱の文字は 13.5 → 12.5 |
| D_products #9 | S213 | Cloudflare 2020-11-02 の対策がもう 1 つある | 原文（a-byzantine-failure-in-the-real-world）を取得：「for at least one of our databases, the cure may be worse than the disease, and in fact we may not want to invoke the promotion process so quickly. Immediately after this incident we adjusted that configuration accordingly」「We've since fixed the bug in our cluster management system」 | 直した | 表「作り直しの不具合を修正。自動の昇格を急がない設定に変更」。ノート「少なくとも 1 つの DB では昇格をそれほど急いで始めないほうがよいとして、設定を変えています」 |
| D_products #11 | S212 | 型③に GitHub 2018 を入れる余地（入れれば 10 件） | 原文（github.blog の oct21-post-incident-analysis）を取得：「We use GitHub Pages internally and all builds had been paused several hours earlier, so publishing this took additional effort」 | 直さない | 掲示が遅れたのは、自社で止めていた機能に載っていたためで、壊れた基盤に道具が依存していた件とは少し違う。決定 D5 が 9 件としているので 9 件のまま。分類は書き手による、の断りは S206 にある |
| D_products 照合表 #7・#13（所見） | S209 | AWS 2025 の型⑦、Google Cloud 2025 の型⑧は「読み取りで、やや広い」 | 指摘ではなく所見。原文は開き直していない | 直さない | 分類は本ガイドによる、と S206・S209 に書いてある。件数を変える決定も無い |
| D_products 照合表 #4・#24（所見） | S207・S208 | DynamoDB の原文に年の表記が無い。Azure の原文は「Event Hub」 | 所見 | 直さない | 発生年は AWS の要約ページの掲載で 2015 と分かる件で、誤りではない。Event Hubs は製品の正式名 |
| B_products #2／決定 D2 | S210（表・ノート） | 「空の項目を含む割当ポリシー」。unintended が落ち、「割当ポリシー」は原文の語でない | 原文を取得：「This policy data contained unintended blank fields」「it did not have appropriate error handling nor was it feature flag protected」。指摘は正しい | 直した | 表「意図しない空のフィールド（blank fields）を含むポリシーのデータ。数秒で全世界に複製」「適切なエラー処理が無く、Service Control が null 参照で落ち、再起動を繰り返した」。ノートも同じ。Google 2020-12-14 の「割当」は別の件（原文が quota）なので残した |
| B_products #4／決定 D3 | S210（S209・S216・S219） | 複数の件を「一斉配布」の型にまとめるのは本ガイドの整理。Cloudflare 2025-11-18 は段階配布を対策に挙げていない | Cloudflare 2025-11-18 の原文を取得：対策は「Hardening ingestion of Cloudflare-generated configuration files…／Enabling more global kill switches for features／Eliminating the ability for core dumps…／Reviewing failure modes…」で、段階配布は無い。経過は「rapidly propagated across the network」。Cloudflare 2025-12-05 の原文を取得：「Enhanced Rollouts & Versioning: Similar to how we slowly deploy software with strict health validation, data used for rapid threat response and general configuration needs to have the same safety…」「does not perform gradual rollouts, but rather propagates changes within seconds」。Google は「data replication needs to be propagated incrementally」。CrowdStrike の RCA は自分では開き直していない（FC の確認による） | 直した | S210：題「型①：挙動を決めるデータが、短時間で全体に届く」、リード「設定・ルール・ポリシーが、短時間で全体に届いた 4 件（1 つの型にまとめるのは本ガイド）」、注記「…型にまとめるのは本ガイドの整理。段階的な配布を対策に挙げたのは CrowdStrike・Google Cloud・Cloudflare 2025-12。Cloudflare 2025-11-18 の報告の対策には無い」。ノートの「対策はどれも…段階配布を入れる方向です」を、挙げた件と挙げていない件に分けた文に。S209 の型①の説明を「短時間で」に。S216 の箱「（CrowdStrike・Google Cloud 2025・Cloudflare 2025-12 の対策）」。S219「（Google 2025、Cloudflare 2025-12）」 |
| D_standards #9 | S218・S220 | フォールバックを避けることを静的な安定性の 3 つ目に入れるのは本ガイドの束ね方 | 「Avoiding fallback in distributed systems」を取得。本文に static の語は 0 件。「the credentials are proactively pushed to every instance and remain valid for many hours」は確認。指摘は正しい | 直した | S218 リード「依存先が傷んでも、それまでしていたことを続けられる作り（3 つに分けるのは本ガイド）」。ノート「3 つに分けるのは本ガイドの整理です」「これは 2 つ目の記事の主張で、その記事自身は静的な安定性という語を使っていません。同じ軸に束ねたのは本ガイドです」。S220「…迂回路を作らない（束ね方は本ガイド）」とノート |
| D_books #7 | S207 ノート | 変更管理が前提になる理由の途中（完全な自動化は高くつく）が落ちている | 『プラットフォームエンジニアリング』p.145〜146 を本文で確認。完全な CI/CD は高くつくことが多く、その投資が行われるように変更管理が前提になる。理由は、基盤がステートフルで、中断に敏感な顧客も抱えるから。指摘は正しい | 直した | 「基盤は状態を持ち、中断に敏感な利用者も抱えるので、完全な自動化は高くつき、その投資が進むように変更管理が前提になると述べます」（自分の言葉。逐語の一致は無い） |
| D_books #9（言及） | S207・S217・S220 | 「（考え方）」の印がある、という確認 | — | 直さない | 指摘ではない。印は残っている |
| A_products #13 | S207（Part 1 との整合） | 「3 件」の件名が Part 1 と合うか | p14.js の 3 件は DynamoDB 2015・Cloudflare 2020・Cloudflare 2023。編集中の p01.js のノートと同じ | 直さない | 一致している |
| 決定 D12 | S205〜S220 | 書籍の本文との 25 字以上の一致 | `_quote_hits.txt` に S205〜S220 の行は無い | 直さない | 該当なし。今回足した文も書籍の文を写していない |

## 配置の変更（中身は変えていない）

- S207：表の列幅 [3.4, 0.6, 8.1]、rowH 0.43 → 0.4（境界の説明で 3 行が 2 行に折り返す見込み。表の下端は計算で約 5.8）。下の注記は y 5.97 → 6.02、h 0.5 → 0.46
- S209：列幅と rowH（上に書いた）。型②の行だけ 3 行になる見込みで、表の下端は計算で約 6.35
- S212：対策の箱の文字 13.5 → 12.5
- S220：箇条の文を縮めた（1 行に収めるため）

## 確かめなかったこと

- CrowdStrike の RCA（PDF）、GitLab 2017、DynamoDB 2015、PagerDuty 以外の「変えていない件」の原文。PagerDuty 2025-08 は取得して、1%・5%・25%・75% と「despite having a gradual rollout process in place」を確かめた
- 書き出した後の見た目（折り返しの行数は計算による）
