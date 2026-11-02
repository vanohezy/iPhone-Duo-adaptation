#!/usr/bin/env python3
"""Read-only, heuristic layout search. Findings are review candidates, not diagnoses."""

import argparse
import json
import os
from pathlib import Path
import re
import sys


SOURCE_SUFFIXES = {".swift", ".m", ".mm", ".h", ".js", ".jsx", ".ts", ".tsx", ".dart", ".css", ".scss"}
SKIP_DIRS = {"pods", "node_modules", "build", "vendor", "deriveddata", "dist", "coverage"}
SENSITIVE_NAME = re.compile(r"(?:^|[._-])(?:env|secrets?|credentials?|private[-_]?keys?)(?:[._-]|$)", re.I)
MAX_FILE_BYTES = 2 * 1024 * 1024


def rule(name, pattern, reason, suffixes=None):
    return (name, re.compile(pattern), reason, suffixes)


RULES = [
    rule("main-screen", r"\bUIScreen\s*\.\s*main\b|\[\s*UIScreen\s+mainScreen\s*\]",
         "确认是否用主屏幕尺寸布置窗口；折叠、分屏及窗口变化时应从当前视图/窗口读取可用空间。"),
    rule("idiom-layout", r"\buserInterfaceIdiom\b|\bUI_USER_INTERFACE_IDIOM\s*\(|\bPlatform\s*\.\s*is(?:IOS|Android)\b",
         "确认此设备/平台分支是否决定布局；手机也可能有 regular 空间，布局通常应取决于当前容器。"),
    rule("orientation-layout", r"UIDevice\s*\.\s*current\s*\.\s*orientation\b|\b(?:statusBarOrientation|interfaceOrientation)\b|MediaQuery\s*\.\s*of\([^)]*\)\s*\.\s*orientation\b|\b(?:window|screen)\s*\.\s*orientation\b|\bOrientation\s*\.\s*(?:portrait|landscape)\b",
         "确认是否把设备方向等同于窗口形状；布局应按当前可用宽高/trait 更新。方向用于相机等用途不一定有问题。"),
    rule("fixed-dimension", r"\.frame\s*\([^\n)]*\b(?:width|height)\s*:\s*\d{3,}\b|\b(?:width|height)\s*:\s*\d{3,}(?:\.\d+)?(?:px\b|\s*[,;}])|\bbounds\s*\.\s*(?:width|height)\s*={2,3}\s*\d+",
         "确认固定尺寸/已知屏幕值是否约束主内容；固定图标、缩略图或合理最大阅读宽度可以保留。"),
    rule("safe-area-bypass", r"\b(?:ignoresSafeArea|edgesIgnoringSafeArea)\s*\(|\bcontentInsetAdjustmentBehavior\s*=\s*\.never\b|\bSafeArea\s*\([^\n)]*\b(?:left|right|top|bottom)\s*:\s*false\b",
         "确认交互内容是否避开侧边系统栏、相机及折叠保留区；纯装饰背景全幅显示可以合理。"),
    rule("media-fill", r"\.scaledToFill\s*\(|\bscaleAspectFill\b|\.aspectRatio\s*\([^\n)]*contentMode\s*:\s*\.fill\b|\bBoxFit\s*\.\s*cover\b|\bobject-fit\s*:\s*cover\b|\bresizeMode\s*(?:=\s*['\"]cover['\"]|:\s*['\"]cover['\"])",
         "在宽窄比例变化时检查主体、字幕和可见区域；按内容选择 fit、焦点裁切或容器自适应。"),
    rule("bar-customization", r"\.toolbar\s*\(\s*\.hidden\b|\b(?:navigationBarHidden|setNavigationBarHidden|setToolbarHidden)\s*\(|\b(?:CustomTabBar|CustomToolbar|BottomNavigationBar|BottomAppBar)\b|\btabBarStyle\s*:\s*\{",
         "确认隐藏/自绘栏是否仍提供导航、动作、溢出与可访问性，并处理 Duo 的系统侧边栏。名称匹配仅是线索。"),
    rule("rn-screen-size", r"\bDimensions\s*\.\s*get\s*\(\s*['\"]screen['\"]\s*\)",
         "React Native 的 screen 不等于应用窗口；布局通常应使用随窗口变化更新的 useWindowDimensions。", {".js", ".jsx", ".ts", ".tsx"}),
    rule("rn-window-snapshot", r"\b(?:const|let|var)\b[^\n;]*\bDimensions\s*\.\s*get\s*\(\s*['\"]window['\"]\s*\)",
         "确认窗口尺寸快照是否位于模块级或只读取一次；应订阅变化或在组件中使用 useWindowDimensions。读取本身并非错误。", {".js", ".jsx", ".ts", ".tsx"}),
]


def positive_int(value):
    try:
        result = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("必须是正整数")
    if result < 1:
        raise argparse.ArgumentTypeError("必须是正整数")
    return result


def source_files(root):
    """Yield source paths without following directory or file symlinks."""
    if root.is_file():
        yield root
        return
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs
                         if not d.startswith(".") and d.lower() not in SKIP_DIRS
                         and not (Path(directory) / d).is_symlink())
        for name in sorted(files):
            yield Path(directory) / name


def audit(root, max_findings=200):
    result = {
        "notice": "只读启发式搜索；所有结果均为人工复核候选，不是错误诊断、完整代码审计或编译验证。",
        "root": str(root), "files_scanned": 0, "files_skipped": 0,
        "total_candidates": 0, "truncated": False, "findings": [], "read_errors": [],
    }
    for path in source_files(root):
        if (path.is_symlink() or path.suffix.lower() not in SOURCE_SUFFIXES
                or path.name.startswith(".") or SENSITIVE_NAME.search(path.name)):
            result["files_skipped"] += 1
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                result["files_skipped"] += 1
                continue
            # Strict UTF-8 decode avoids silently treating binary files as source.
            source = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            result["read_errors"].append({"path": str(path), "error": type(error).__name__})
            continue
        result["files_scanned"] += 1
        label = str(path.relative_to(root)) if root.is_dir() else path.name
        for line_no, line in enumerate(source.splitlines(), 1):
            for name, pattern, reason, suffixes in RULES:
                if (suffixes is None or path.suffix.lower() in suffixes) and pattern.search(line):
                    result["total_candidates"] += 1
                    if len(result["findings"]) < max_findings:
                        result["findings"].append({
                            "path": label, "line": line_no, "rule": name,
                            "snippet": line.strip()[:240], "reason": reason,
                        })
    result["truncated"] = result["total_candidates"] > len(result["findings"])
    return result


def markdown(result):
    lines = [result["notice"], "",
             f"已读取 {result['files_scanned']} 个源码文件；发现 {result['total_candidates']} 条候选，展示 {len(result['findings'])} 条。",
             "默认排除隐藏目录、依赖/构建目录、符号链接、敏感命名文件及超过 2 MiB 的文件。正则可能命中注释，也会漏掉多行表达式与间接调用。", ""]
    for finding in result["findings"]:
        location = f"{finding['path']}:{finding['line']}".replace("`", "'")
        snippet = finding["snippet"].replace("`", "'")
        lines.extend([f"- `{location}` — {finding['rule']}",
                      f"  - 候选：`{snippet}`", f"  - 复核：{finding['reason']}"])
    if result["truncated"]:
        lines.extend(["", "输出已截断；提高 --max-findings 可查看更多候选。"])
    if result["read_errors"]:
        lines.extend(["", f"有 {len(result['read_errors'])} 个文件无法读取；JSON 输出包含路径与错误类型。"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="待搜索的项目目录或源码文件")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--max-findings", type=positive_int, default=200)
    args = parser.parse_args(argv)
    # Reject the caller's symlink before resolving to its target.
    if args.root.is_symlink() or not args.root.exists():
        parser.error("目标必须存在且不能为符号链接")
    if not (args.root.is_file() or args.root.is_dir()):
        parser.error("目标必须是目录或源码文件")
    result = audit(args.root.absolute(), args.max_findings)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(markdown(result), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
