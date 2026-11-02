# Apple 官方适配依据

核实日期：2026-11-02（Asia/Shanghai）。本文件是有来源的摘要，不是 Apple 官方发布的 skill，也不保证 Apple 此后不调整 API。功能布局和验收方案中的自主设计判断见其他参考文件。

## 证据基线与使用方式

- **已联网核实**：Apple 产品页、开发者准备页、六场 Tech Talks 的正文/代码、HIG 搜索可读正文及 API 文档可读摘要。iPhone Duo 已由 Apple 发布；这不是依据传闻编写的通用折叠屏假设。[产品页](https://www.apple.com/iphone-duo/)、[开发者入口](https://developer.apple.com/iphone-duo/)、[2026-10-05 开发者公告](https://developer.apple.com/news/?id=kkphp5qo)。
- **已查本机声明**：`<selected iOS SDK>/` 的 SwiftUI/SwiftUICore `.swiftinterface` 与 UIKit headers。下述核心新增布局 API 标注为 27.1 可用。读到声明仅证明此 SDK 包含符号，不能证明示例编译或设备行为。
- **未完成**：没有对业务 App 编译、启动或验证折叠行为；没有导入 Apple 自带 skill；没有实机无障碍、触达、性能或连续性验收。
- **读取限制**：部分 Apple 文档 HTML 只返回 JavaScript 壳；通过官方搜索结果正文和 Tech Talk 补证。实现前应重新打开对应 API 文档并查当前选定 SDK，不能将搜索摘要当作完整接口契约。

## 1. 先区分 SDK 兼容档位

| 构建所用 SDK | Apple 说明的呈现 | 工程含义 |
| --- | --- | --- |
| iOS 26 或更早 | 外屏内容位于状态栏/相机左侧；内屏以熟悉的窗口尺寸居中，周围留白 | 运行兼容不等于完成 Duo 适配 |
| iOS 27 | 内屏可扩展至大部分区域，仍避开右侧状态栏区域 | 应检查动态缩放，尚未获得完整侧栏体验 |
| iOS 27.1 或更新 | 使用完整显示区域；标准工具栏、标签栏可变为竖向 | 交付前必须验证侧栏、遮挡及溢出 |

这是**构建 SDK**带来的行为差异，不代表必须把最低部署版本提高到 27.1。保留产品原有最低版本，用 availability 分支保护新增 API；不要擅自升级项目或切换用户的工具链。[Three steps to make your app shine on iPhone Duo](https://developer.apple.com/iphone-duo/prepare/)。

该准备页还要求消除主屏尺寸、方向、idiom 的布局假设：从当前 view/window 或 SwiftUI geometry 获得尺寸，并在变化时更新；scale 取 trait/environment。`regular` 不再代表 iPad。全幅图像与视频须检查主体裁切。[同页：Fix patterns](https://developer.apple.com/iphone-duo/prepare/)。

## 2. 六场官方 Tech Talks，各自解决什么

### Design for iPhone Duo · 111466

先做好 compact/regular 的可伸缩布局，而不是给每个姿态重做一套界面。外屏到内屏保持功能和层级；内屏可以增加同时可见的层级。桌面半折可提供上内容、下操作的附加优化，但不能把功能锁在姿态里。多数姿态侧置控制；**内屏竖向是保留横栏的例外**。分屏左侧 App 的栏可在左外缘；顶置视频还会压缩 App 的可用高度。[视频与章节](https://developer.apple.com/videos/play/tech-talks/111466/)。

### Prepare your app for iPhone Duo · 111461

用环境/traits 和局部 bounds 判断布局，不依赖 `UIScreen.main`、idiom 或 interface orientation。全屏内屏示例是 regular × regular，但分屏、视频和窗口变化仍需读取实际环境。`NavigationSplitView`/`UISplitViewController` 可在外屏折叠成栈。标准 bars 处理硬件，前景遵守安全区，背景可延伸。四边安全区和 margins 可能不对称，不能用一侧值乘二。Device Hub 提供开合、旋转和折叠控制。[视频，2:46–8:08](https://developer.apple.com/videos/play/tech-talks/111461/)。

### Raise the bar with iPhone Duo · 111462

侧栏适配来自 **navigation/tab 容器管理的 bars**；单独实例化 `UIToolbar`/`UINavigationBar`/`UITabBar` 不等于获得该行为。图标项也应提供标题，供溢出和展开形式使用；纯文字和宽控件可能保持横向。保留分组与相对次序，不手工插固定空白。导航任务默认优先保留 tab；操作任务可优先保留 toolbar。为高频操作和有状态徽标的项设置可见优先级，并合并系统 overflow。[视频，2:00–14:21](https://developer.apple.com/videos/play/tech-talks/111462/)。

### Strike a pose with adaptive layouts on iPhone Duo · 111463

需避让的是系统给出的 reserved regions。移动独立元素或成组关联元素时只做必要位移；连续滚动文章、feed、文档与列表不应整体搬到一侧。两块相关内容可用 arrangement：split 保持两块不互遮挡；overlay 适合前后景关系。导航放在 arrangement 外面；不要把 arrangement 放入滚动容器。系统 alerts、menus、sheets 和 split views 已处理很多折叠适配。[视频，2:26–16:09](https://developer.apple.com/videos/play/tech-talks/111463/)。

### Leverage multiple displays and scenes on iPhone Duo · 111464

hinge API 提供 closed、partially open、fully open 及连续角度，适合互动/效果；**布局使用 arrangement 和 region API**。不存在应默认依赖的单一“pose”枚举。多场景创建的能力可动态变化，外屏不能新建窗口，须处理请求失败。`CameraCaptureAccessory` 可在符合条件的相机会话中为外屏呈现附加 UI；不是任意 App 任意占用双屏的通用授权。[视频，0:49–6:44](https://developer.apple.com/videos/play/tech-talks/111464/)。

### Build a great camera experience for iPhone Duo · 111465

Virtual Front Camera 自动在内外前摄间切换；分别使用物理相机时，App 自行负责切换。`AVCaptureDeviceDirectionCoordinator` 判断相机相对于**对应 UIView**的朝向，不把 `.front` 等同于永远朝向用户。回调通过可发送 descriptor 交给相机 actor，避免在主 actor 直接操作捕获会话。预览检查 fit/fill、镜像、传感器比例和 rotation coordinator；两个显示 view 各自需要方向协调。[视频，0:58–8:03](https://developer.apple.com/videos/play/tech-talks/111465/)。

## 3. API 决策表与容易误写的名称

| 问题 | SwiftUI | UIKit / 相机 | 核实程度 |
| --- | --- | --- | --- |
| 布局分型 | `horizontalSizeClass`、`verticalSizeClass`、当前 geometry | `traitCollection`、当前 view/window bounds | 官方准备文档及 111461 |
| 一对内容适应折叠区域 | `ArrangementView`、`arrangementViewStyle(_:)` | `UIArrangementViewController` | 官方文档/111463；SwiftUI 本地 27.1 声明已核实 |
| 自定义遮挡/分隔避让 | `GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)`、`ReservedRegion` | `UIView.reservedRegions(kind:options:)`、`UIView.ReservedRegion` | 官方 API 摘要及本地 27.1 声明 |
| 查询侧栏位于哪侧 | `@Environment(\.toolbarVerticalEdge)` | `traitCollection.verticalBarEdge` | 111462 10:36；本地 SwiftUI 声明与 UIKit header |
| 工具栏与 tab 的压缩取舍 | `.toolbarVerticalCompressionBehavior(.prefersToolbarItems)` / `.prefersTabBar` | `navigationItem.verticalBarCompressionBehavior = .prefersBarItems` | 111462 **12:23 代码**及本地 SDK |
| 特定自定义项的适用轴 | `.axisBehavior(...)`、`ToolbarItemAxisBehavior` | 查询当前 SDK 对应 item 配置 | 官方 SwiftUI updates / 本地 27.1 声明 |
| 受限空间中的项优先级 | `ToolbarItemVisibilityPriority` | `UIBarButtonItemVisibilityPriority` | HIG/API 链接；实现前核实具体调用点 |
| 合并溢出菜单 | `ToolbarOverflowMenu` | `navigationItem.additionalOverflowItems` | 111462；实现前核实签名 |
| 交互效果观察铰链 | `.onHingeChange(isEnabled:_:)` | `UIHingeInteraction` | 111464；SwiftUI 本地 27.1 声明 |
| 跨屏相机与方向 | `sceneAccessory` / `CameraCaptureAccessory` | `AVCaptureDeviceDirectionCoordinator` | 111464、111465；具体声明/权限需项目实现时核实 |

口述转录里的 `toolbarCompressionBehavior` 和单数 `reservedRegion` **不可直接当 Swift 源码**。当前核实的正确 API 名称如表；不存在经本 skill 验证可直接粘贴的完整业务实现。新 API 需 availability 分支和原布局回退；签名、平台限制、trait 更新方式都以当前项目选中的 SDK 为准。

静态声明核实位置：`SwiftUI.framework/Modules/SwiftUI.swiftmodule/arm64e-apple-ios.swiftinterface`、`SwiftUICore.framework/Modules/SwiftUICore.swiftmodule/arm64e-apple-ios.swiftinterface`、`UIKit.framework/Headers/{UIView,UINavigationItem,UIVerticalBarEdge}.h`（均相对于上方 SDK 根）。

对应原始资料：[ArrangementView](https://developer.apple.com/documentation/swiftui/arrangementview)、[UIArrangementViewController](https://developer.apple.com/documentation/uikit/uiarrangementviewcontroller)、[ReservedRegion](https://developer.apple.com/documentation/swiftui/reservedregion)、[GeometryProxy 查询](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:))、[UIView.ReservedRegion](https://developer.apple.com/documentation/uikit/uiview/reservedregion)、[SwiftUI updates](https://developer.apple.com/documentation/updates/swiftui)、[ToolbarVerticalCompressionBehavior](https://developer.apple.com/documentation/swiftui/toolbarverticalcompressionbehavior)。

## 4. ReservedRegion 的工程边界

- `division` 描述折叠造成的分隔；`occlusion` 描述相机、Dynamic Island 等覆盖。折叠分隔在平展时通常 inactive；外摄区域常在，内摄区域随使用激活。
- region 的 `frame` 使用**所查询 view 的局部坐标，单位为 point，已经包含 margins**；不要再加一次 margins。部分相交可能产生负坐标或超出 view 范围的矩形，不能假定结果全在自身 bounds 内。
- 默认查询当前 active region；确需提前预留或形成稳定网格时才请求 `.includeInactive` 并检查 `isActive`。不要通过空结果推断具体设备型号。
- 容器先于手工避让；自定义浮层、悬浮按钮、显式 frame 控件确有遮挡时才做局部查询。若一对内容需要一起适应，优先 arrangement。UIKit 文档说明，在 `updateConstraints()` 中读取会被追踪并随区域变化更新。

来源：[UIView.ReservedRegion](https://developer.apple.com/documentation/uikit/uiview/reservedregion)、[SwiftUI region frame](https://developer.apple.com/documentation/swiftui/reservedregion/frame)。SwiftUI 查询默认 `layoutDirectionBehavior = .mirrors` 的本地声明已核实；手工几何必须结合 RTL 核实坐标行为，不要把镜像后的区域与未镜像的坐标混算。

## 5. 官方 skill 与工具验证

Apple 官方准备页提供 App Resizability skill：在 Xcode 询问 “get my app ready for iPhone Duo”，其他 agent 可运行 `xcrun agent skills export` 导出。它能辅助发现常见模式，Apple 自己也说明不能发现全部问题。[官方命令来源](https://developer.apple.com/iphone-duo/prepare/)。

本项目独立整理公开资料，并提供自己的只读检查脚本；未分发 Apple 自带 skill。官方 skill 是否可导出取决于当前 Xcode 安装与运行状态。

Apple 提供的动态验证入口是 [Device Hub](https://developer.apple.com/documentation/xcode/device-hub) 的 iPhone Duo 模拟器，同时可用 resizable iPhone 和 macOS 27 iPhone Mirroring 测极端宽高。后两者不能代替 Duo 的侧栏、区域与折叠测试。官方 [Xcode updates](https://developer.apple.com/documentation/updates/xcode) 确认支持在 preview canvas 与 Device Hub 测试 Duo。

## 6. 何时必须重新查证

使用新的 Xcode/iOS 版本、文档标注 beta、准备写具体新 API 代码、框架声称自动适配、遇到与文档不符行为时，重新核对公开文档与选定 SDK。不能从本文件推导固定折叠角阈值、固定硬件尺寸、折痕像素宽度、固定左右业务区、第三方框架自动适配承诺。

Apple 原始总览：[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)、[HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)、[HIG: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)。
