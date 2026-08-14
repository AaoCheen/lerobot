# 我的 LeRobot Git 使用流程

## 记住这两个分支

```text
main          只用来同步官方代码
dataset-notes 用来写我自己的笔记
```

我的 GitHub fork 是 `origin`，官方 LeRobot 是 `upstream`。

## 第一次：上传个人分支

`dataset-notes` 已经创建好了，只需执行一次：

```bash
git switch dataset-notes
git push -u origin dataset-notes
```

这只上传到我自己的 fork，不会提交给官方。

## 平时写笔记

```bash
git switch dataset-notes

# 修改笔记后
git add docs/ git.md
git commit -m "docs: update my notes"
git push
```

## 同步官方更新

先在自己 fork 的 GitHub 页面点击：

```text
Sync fork → Update branch
```

然后在本地执行：

```bash
# 更新本地 main
git switch main
git pull --ff-only origin main

# 让个人笔记分支也获得新版代码
git switch dataset-notes
git merge main
git push
```

## 每次操作前先检查

```bash
git status
```

如果有不理解的报错，先停下来，不要使用 `git reset --hard`、`git clean` 或 `git push --force`。

## 一句话总结

```text
同步官方时切到 main；
写笔记时切到 dataset-notes；
main 更新后，在 dataset-notes 中执行 git merge main。
```
