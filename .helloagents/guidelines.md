# 项目约定

<!-- 只记录从代码看不出来的约定。AI 能从代码推断的风格不需要写在这里。 -->

## 编码风格
- 仓库以内容和 manifest 为主，新增逻辑优先使用已有 Bash/Node 验证脚本。
- 分发 manifest 需要保持版本、技能数组、安装说明和平台声明一致。

## 命名规范
- 插件和技能 slug 使用小写 kebab-case。
- Codex plugin name 使用 `aaron-seo-geo`，与现有 Claude/CodeBuddy 插件名保持一致。

## Git 工作流
- Commit 使用 Conventional Commits。
- 分发面变更需要同步 README、marketplaces/README.md、distribution/platforms.json 与相关 manifest。

## 测试
- manifest 变更后运行 `node .github/scripts/sync-skills.js --check`。
- 发布/瘦身守护运行 `bash scripts/validate-slimming-guardrails.sh`。
