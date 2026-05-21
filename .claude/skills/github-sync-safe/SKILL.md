---
name: github-sync-safe
description: Silver Tree Coffee Roasterリポジトリで、必要なファイルだけを安全にcommit/pull --rebase/pushし、rebase衝突やvi画面で詰まったユーザーを案内するためのSkill。GitHub反映、コミット、プッシュ、rebase、コンフリクト、x-post-log.md衝突、git status確認、未コミット変更の棚卸しで使用する。git add .や破棄系コマンドを避ける。
argument-hint: [反映したい変更内容またはgit status画面]
---

# /github-sync-safe — GitHub反映・rebase衝突対応

このSkillは、Silver Tree Coffee Roasterリポジトリの変更をGitHubへ安全に反映するために使う。
目的は「必要な変更だけを反映し、未整理変更を巻き込まない」こと。

## 原則

- `git add .` は使わない。
- ユーザーの未コミット変更を勝手に破棄しない。
- 反映対象を先に絞る。
- `git status --short --branch` を最初と最後に確認する。
- push前に `main` と `origin/main` の位置を確認する。
- 衝突した場合は、衝突ファイルと目的を見て判断する。
- ユーザーに案内するコマンドは少なく、1〜3行ずつに分ける。

## 最初に確認するコマンド

```bash
git status --short --branch
git log --oneline --decorate --max-count=5
```

見ること:

- `main...origin/main` が一致しているか。
- `ahead` / `behind` / `diverged` が出ているか。
- staged / unstaged / untracked のどれがあるか。
- 反映したいファイルだけがstageされているか。

## 反映対象を絞る

焙煎・在庫・HTML反映なら、基本対象は以下。

```text
ops/inventory-log.md
ops/inventory/index.html
ops/inventory/YYYY-MM-DD.html
ops/inventory/green-bean-purchase-plan-YYYY-MM-DD.md
roast-logs/*.md
roast-profiles/index.html
roast-profiles/*.html
roast-profiles/generated-preview/
scripts/generate_roast_profiles.py
```

SNSや方針ファイルが混ざっている場合は、ユーザーに確認する。

## 基本手順

1. 変更範囲を確認する。
2. 必要なファイルだけ `git add` する。
3. `git status` でstage内容を確認する。
4. commitする。
5. `git pull --rebase --autostash origin main` を実行する。
6. 衝突がなければ `git push origin main`。
7. 最後に `git status --short --branch` と `git log` で確認する。

例:

```bash
git add ops/inventory-log.md roast-logs/2026-05-19_brazil-bellavista-2batch.md roast-profiles/index.html
git status
git commit -m "焙煎プロファイルと在庫管理を更新"
git pull --rebase --autostash origin main
git push origin main
```

## rebase中の判断

`git pull --rebase --autostash` 後に衝突したら、まず状態確認。

```bash
git status
```

`interactive rebase in progress` と出ていても慌てない。

やること:

1. `Unmerged paths` を見る。
2. 衝突ファイルを確認する。
3. 解決方針を決める。
4. `git add <file>` で解決済みにする。
5. `git rebase --continue`。

## x-post-log.md衝突の扱い

`x-post-log.md` はSNS投稿ログで衝突しやすい。

基本判断:

- 今回の目的が焙煎・在庫・HTML反映なら、`x-post-log.md` は主目的ではない。
- すでにローカル側で現在運用に合わせた内容がある場合は、`--ours` を使う。
- ただし、SNS投稿の反映が目的の場合は差分を必ず読む。

焙煎・在庫反映中に `x-post-log.md` だけ衝突した場合の標準手順:

```bash
git checkout --ours x-post-log.md
git add x-post-log.md
git rebase --continue
```

同じファイルで複数回止まることがある。これは異常ではなく、rebaseで複数コミットを順番に適用しているため。

## vi画面で止まった場合

`git rebase --continue` 後に白い `vi` 画面が出ることがある。

ユーザーへは、以下だけ案内する。

```text
Esc
:wq
Enter
```

意味:

- `Esc`: 編集モードを抜ける
- `:wq`: 保存して終了
- `Enter`: 実行

`:wq` が出ない場合:

- ターミナル画面をクリックする。
- Macの入力を英数にする。
- `Esc` を2〜3回押す。
- もう一度 `:wq` を打つ。

間違って本文に `ZZ` や文字が入った場合:

```text
Esc
u
Esc
:wq
Enter
```

`u` は直前の入力を取り消す。

## push成功の見方

push成功時は以下のような行が出る。

```text
d47f80f..f7121bb  main -> main
```

この場合、GitHubの `main` が新しいコミットまで進んでいる。

最後に確認:

```bash
git status --short --branch
git log --oneline --decorate --max-count=5
```

`HEAD -> main, origin/main` が同じコミットを指していれば反映済み。

## 未コミット変更が残る場合

push後に未コミット変更が残っていても、commit対象に含めていなければGitHubには反映されない。

報告では必ず分ける。

```text
GitHub反映済み:
- commit hash / message

手元に残っている未コミット変更:
- file
- file
```

## 禁止

- `git add .`
- `git reset --hard`
- `git checkout -- <file>` による破棄
- `git clean -fd`
- force push
- 未確認のままSNSログや方針ファイルを巻き込む
- rebase中に焦ってウィンドウを強制終了するよう案内する
