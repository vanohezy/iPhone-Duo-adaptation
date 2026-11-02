# 实现与代码检查

本文件提供实现决策，不提供未经项目验证的“直接替换代码”。新 API 的调用形式和 availability 以当前 Apple 文档、项目使用的 SDK 声明与实际编译结果为准。官方能力索引在 [official-guidance.md](official-guidance.md)。

## 先看最小影响路径

1. 确认构建 SDK 与最低部署版本分别是什么。升级 SDK 与提高最低系统版本是两个决策。
2. 查清导航、数据、会话和自绘视图的所有者。先修尺寸来源与状态生命周期，再调整视觉细节。
3. 标准容器能解决时先用标准容器；只有现有品牌交互或任务确有需要时才补自绘逻辑。
4. 记录兼容策略：新系统用新布局能力，旧系统仍使用空间自适应和安全区；用 availability 包住新增 API。需要旧编译器解析源码时，另做模块/条件编译隔离。

## 诊断对照表

每个命中都要阅读调用上下文。下表不是禁用清单，截图尺寸、像素导出、固定触点和画布坐标常有合理用途。

| 候选模式 | 真正需要确认的问题 | 替代方向 |
| --- | --- | --- |
| `UIScreen.main.bounds` / `mainScreen` | 把屏幕当成当前窗口？仅启动时取一次？ | SwiftUI 容器几何；UIKit 当前 view/window bounds；持续响应变化 |
| 缓存 `UIScreen`、`UIWindow(frame:)` | 屏幕随场景改变但引用未更新？ | 窗口从 `UIWindowScene` 创建；必要时动态取 scene 的 screen |
| idiom `.phone` / `.pad` 分支 | 用设备类别决定栏数？ | size classes 表达结构差异；容器测量表达内容布局 |
| `UIDevice.orientation` / interface orientation | 用物理方向推断可用宽高？ | 当前 bounds/traits；相机与传感器真正需要方向时保留 |
| 固定全页尺寸/已知分辨率比较 | 依赖特定机型或方向？ | 约束、内容最小可读尺寸、动态布局；保留控件合理尺寸 |
| `.ignoresSafeArea()` / 手算 insets | 前景控件也忽略安全区？把左右 inset 当相等？ | 背景与交互层分开；每边独立读取；reserved regions 处理内部区域 |
| 固定底栏/右栏、手绘 overflow | 系统栏变纵向、左分屏或高度变小时还能用？ | 标准 toolbar/tab；由系统确定 edge 和 overflow，按任务设优先级 |
| `aspectFill` / `.scaledToFill()` | 主体、字幕、票券/文档边缘被裁掉？ | 当前容器比例下选 fit/fill、焦点或独立背景；保持媒体比例 |
| 几何变化回调重建 view model | 折叠是否丢草稿、选择、音频会话、引擎？ | 生命周期稳定的状态所有者，只让布局值随几何改变 |
| onAppear / init / task 发请求 | 改布局会重复请求、保存、支付或发送？ | 任务以业务 ID 驱动；取消/去重；用户提交保持单一事务 |
| 固定折痕坐标/角度阈值 | 误把铰链当布局断点？ | Arrangement 与 reserved region；无需猜物理姿态 |

工具：`python3 scripts/audit_layout.py /path/to/project --format json --max-findings 200`。扫描是启发式静态发现，可能误报和漏报，不能验证生命周期、运行时布局、平台桥接或实际可访问性。

## SwiftUI

**导航与状态**

- 列表详情优先 `NavigationSplitView`；显式维护稳定业务 ID 的选择、各 tab 路径与返回语义。核查 compact 折叠时当前详情而不是随机列表项成为前景。
- 几何条件分支不要各自创建一个独立播放器、编辑器、草稿模型或游戏会话。必要时把模型移到共同祖先或合适场景中；不要把所有窗口的 UI 选择都变成单个全局单例。
- 用稳定 ID 与合适状态容器保持身份。审查 `.id(width)`、`.id(sizeClass)` 等强制重建，以及 `if` 两支中相同业务视图是否失去局部状态。
- 系统组件提供很多行为，但应用仍负责业务状态。滚动以段落/项目 ID 等语义锚点保存，避免直接沿用变宽前的像素偏移。

**布局**

- 用两个 size class 选择布局结构，细节依赖当前容器。`GeometryReader` / `onGeometryChange` 用在需要的局部，避免反复读写尺寸造成布局反馈循环。
- 双内容区先检查 `ArrangementView`；split 对应互不遮挡的两区，overlay 对应前景/背景。导航容器在外；不要把 arrangement 放进 `List`/`ScrollView`。
- 自绘前景需要内部避让时读取 `GeometryProxy.reservedRegions(...)` 的 division/occlusion 语义。不要把所有滚动内容整体挪开，也不要永久给中线空出固定宽度。
- 避免按“当前宽度刚过某值”立刻切另一套产品。内容驱动的最小尺寸可以决定卡片/行的排布，但不得冒充 Apple 官方设备断点。

**工具栏**

- 使用语义 placement、`Label`、工具分组和系统 overflow。symbol 与 title 同时提供，兼顾侧栏、overflow 和辅助功能。
- 布局必须知道栏在哪一侧时，查 `toolbarVerticalEdge`；普通内容通常只需遵守 safe area，无须自建一套栏方向规则。
- 导航优先的页面接受默认压缩；编辑任务可检查 `.toolbarVerticalCompressionBehavior(.prefersToolbarItems)` 的适用性，并验证 tab 仍有可恢复入口。
- 为关键动作选择 visibility priority，不要让每个按钮都变成最高优先级。确认 Dynamic Island/Live Activity 扩大时的结果。

这些符号的证据来自 Apple [Raise the bar](https://developer.apple.com/videos/play/tech-talks/111462/) 与 [adaptive layouts](https://developer.apple.com/videos/play/tech-talks/111463/) 的代码章节。口述简称不能用来推造方法名。

## UIKit

- 用 Auto Layout、`safeAreaLayoutGuide`、layout margins 与动态 traits；在布局周期重算依赖 bounds 的值。状态变化发生在会话中途，`viewDidLoad` 或启动时计算不足。
- `UISplitViewController`、`UITabBarController`、系统 sheet/alert 优先。核查 collapse/expand 后的 selection、导航栈与控制器身份；不要在每次旋转/折叠都重建根控制器。
- 两块内容的布局检查 `UIArrangementViewController`；自绘区域使用 `UIView.reservedRegions(...)`。内部保留区变化要触发布局更新，不仅处理旋转事件。
- 读取 `traitCollection.verticalBarEdge` 处理必要的自绘边缘；不要用 RTL 方向或左右手偏好自行翻转系统垂直栏。
- 系统 toolbar 分组、`navigationItem.additionalOverflowItems`、条目 visibility priority 和 `verticalBarCompressionBehavior` 各自承担分组、溢出和压缩职责。
- 渲染缩放取 traits；需要 screen 时从当前 `view.window?.windowScene` 动态获取。多场景下数据可共享，导航选择与编辑焦点通常按 scene 隔离。

## Flutter / React Native / Web

同样的设计目标不意味着 Apple 自动适配这些框架的自绘组件。先查项目版本、导航库和已有原生桥接，再决定实现。

| 框架 | 正常尺寸来源 | 容易遗漏 | 新平台能力不足时 |
| --- | --- | --- | --- |
| Flutter | `LayoutBuilder` 约束；响应 `MediaQuery` 的实际窗口信息 | 单次缓存尺寸、按平台/方向决定栏数、自绘 bottom nav、重复 SafeArea | 核实插件是否暴露 reserved regions/栏边缘；必要时最小原生桥接，普通自适应保留为降级 |
| React Native | `useWindowDimensions` / 局部 `onLayout`；按所用库正确使用 safe-area 数据 | `Dimensions.get('screen')`、模块顶层缓存、原生导航与自绘栏重复、键盘重复扣 inset | 检查导航库真实行为；原生布局能力是否可用需当前库和真机证据 |
| Web / WKWebView | 当前 layout/visual viewport、容器查询和 safe-area env 的实际值 | UA 机型检测、固定 vh、输入法后按钮消失、网页手画折痕 | 先验证 Safari/WebKit 当前支持；CSS posture/viewport segments 必须 feature-detect，不能照搬 Chromium 行为 |

纯框架扫描无命中不能证明 native 的新栏、sheet 与保留区都正确。验证边界包括宿主与内嵌网页；不要从 iPad/Android 演示推断 iOS 上的自动行为。

## 兼容与高级能力

- **铰链交互**：普通布局不用角度。产品确有交互价值时才考虑 `onHingeChange` / `UIHingeInteraction`，处理无铰链、不可用与状态重置。
- **多个场景**：动态判断是否能创建，处理失败。外屏不等于可以随时新开窗口；不要仅因 App 声明 multiple scenes 就展示永久可点的新窗口按钮。
- **相机/双屏**：区分正常折叠连续性与专用 scene accessory。`CameraCaptureAccessory` 受当前场景、全屏状态和相机会话等可用性约束，不是任意内容镜像到两块屏幕。
- **方向限制**：检查项目既有策略与官方实际行为；锁方向不能替代内屏重排。游戏仍要处理可变渲染面与触控映射。

## 实现完成的证据

记录实际 SDK、部署版本、改动路径、构建命令/结果、运行目标与测试场景；行为按 [validation.md](validation.md) 验证。只交付代码时明确未运行；已安装也不等于已手工验收。
