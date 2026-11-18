#!/usr/bin/env python3
"""检查 Codex 自动加载白名单。--write 生成配置，默认只检查。"""

import argparse
from pathlib import Path


# 新技能默认手动调用。只有任务明确、适合自主触发的技能进入白名单。
AUTO_SKILLS = {
    "diagnosing-bugs",  # 用户报告故障时进入诊断。
    "typescript-best-practices",  # 读取或编辑 TypeScript 时使用。
    "writing-for-agents",  # 编写技能和代理说明时使用。
    "unslop",  # 整理交付文字。
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skills-root", type=Path,
        default=Path(__file__).resolve().parents[1] / "skills",
        help="技能目录；也可指定项目的 .agents/skills",
    )
    parser.add_argument("--write", action="store_true", help="写入缺失或漂移的配置")
    args = parser.parse_args()
    skills = sorted(args.skills_root.rglob("SKILL.md"))
    if not skills:
        parser.error(f"未找到技能: {args.skills_root}")

    errors = []
    automatic = []
    changed = 0
    for skill in skills:
        name = skill.parent.name
        enabled = name in AUTO_SKILLS
        if enabled:
            automatic.append(name)
        config = skill.parent / "agents" / "openai.yaml"
        expected = f"policy:\n  allow_implicit_invocation: {str(enabled).lower()}\n"
        actual = config.read_text() if config.exists() else None
        if actual == expected:
            continue
        if args.write:
            # 不覆盖其他人维护的 UI 或依赖字段。
            known = {"policy:\n  allow_implicit_invocation: true\n",
                     "policy:\n  allow_implicit_invocation: false\n", None}
            if actual not in known:
                errors.append(f"保留自定义配置，请手动合并: {config}")
                continue
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text(expected)
            changed += 1
        else:
            errors.append(f"配置缺失或与白名单不一致: {config}")

    print(f"技能 {len(skills)}；自动 {len(automatic)}；手动 {len(skills) - len(automatic)}；写入 {changed}")
    print("自动: " + ", ".join(automatic))
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
