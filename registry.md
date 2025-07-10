# 数据无价，谨慎操作，操作出现问题概不负责
# 数据无价，谨慎操作，操作出现问题概不负责
# 数据无价，谨慎操作，操作出现问题概不负责

# 一、额外字重生效
如需让生成的微软雅黑极细和半粗字重在 Windows 下生效，请新建 reg 文件，内容如下：

```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts]
"Microsoft YaHei Xlight & Microsoft YaHei UI Xlight"="msyhxl.ttc"
"Microsoft YaHei Semibold & Microsoft YaHei UI Semibold"="msyhsb.ttc"
```

## 说明

 `[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts]` 
 
是系统所有**已安装字体的主数据库**，控制所有应用程序可访问的物理字体文件映射（比如 `"Microsoft YaHei (TrueType)"="msyh.ttc"`）

---

# 二、其他与字体有关的注册表说明

```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\FontSubstitutes]
"MS Shell Dlg 2"="Tahoma"
"MS Shell Dlg"="Microsoft Sans Serif"

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\GRE_Initialize]
"GUIFont.Facename"="SimSun"

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FontAssoc\Associated DefaultFonts]
"AssocSystemFont"="simsun.ttc"
"FontPackage"="新宋体"
"FontPackageDontCare"="新宋体"
"FontPackageRoman"="新宋体"
"FontPackageSwiss"="新宋体"
"FontPackageModern"="新宋体"
"FontPackageScript"="新宋体"
"FontPackageDecorative"="新宋体"
```
>上面三项是中文Windows10系统的默认值
>
>接下来逐项说明

1. `[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\FontSubstitutes]`
  - 影响一些旧式应用的设置窗口，比如“系统属性”。[^3]

2. `[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\GRE_Initialize]`
  - 大部分 Qt 程序的默认字体。[^3]

3.  `[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FontAssoc\Associated DefaultFonts]`
  - 旧版系统的**字体回退兼容层**，在Win10/11系统中作用有限。


---

# 三、Font Fallback

## 路径
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\FontLink\SystemLink
```

## 说明
该注册表项用于定义 **字体替换规则（Font Fallback）**。
当某个字体无法显示特定字符（如中日韩文字）时，系统会按照设定的顺序使用替代字体进行渲染，以避免乱码或空白字符。

**示例:**
```reg
"Tahoma":
    SIMSUN.TTC,SimSun
    MINGLIU.TTC,PMingLiU

"Segoe UI":
    TAHOMA.TTF,Tahoma
    MSYH.TTC,Microsoft YaHei UI,128,96
    MSYH.TTC,Microsoft YaHei UI
```
- 第一个条目表示：如果 `Tahoma` 字体遇到不支持的字符，将尝试使用 `SimSun`、`PMingLiU` 等字体替代。
- 第二个条目同理。

---

## 修改
- **值格式：**
    ```
    FontFileName,FontName[参数, 参数]
    ```
    每行定义一个替代字体，例如：
    ```
    MSYH.TTC,Microsoft YaHei UI
    SIMSUN.TTC,SimSun
    ```

> **注意：** 直接导出该注册表项时，数据会以十六进制存储的 Unicode 字符串 (`hex(7)`)。因此不推荐导出 reg 文件修改后再导入，建议直接使用注册表编辑器逐个手动修改值。

### 缩放因子说明
关于值中可能出现的两个数字参数（如 `128,96`），未找到官方权威资料。以下是查找到的两个相关信息：

#### 信息[^1]
> 接下来，我想花点时间说说缩放因子，毫无疑问，当用GDI输出文本时，缩放因子会影响显示效果。我希望能够弄清楚这两个整数是如何被使用的。可惜我找不到任何有用的信息。所有能在网上找到的信息都没有提到具体这两个缩放因子是如何被使用的。而且经过测试后我发现，有些网页上建议把缺省的数值，128和96，分别乘以一个相同的数，然后把结果作为缩放因子写入Fontlink的键值中。这让我感到十分困惑，因为以我自己现有对缩放因子的理解，对两个缺省的数值乘以一个相同的数是不会产生任何不同效果的。
>
> 如前所述，我找不到任何关于这两个缩放因子的详细资料，唯一能找到的相关信息就是开源软件gdipp的一个[源程序文件](https://code.google.com/p/gdipp/source/browse/gdimm/font_link.cpp?name=0.8.2)。在这个文件里，Fontlink里定义的两个缩放因子被用来以如下方式计算另外一个缩放参数：
>
> ```sh
> new_info.scaling = (factor1 / 128.0) * (96.0 / factor2);
> ```
>
> 这至少说明如果给连个缺省的缩放因子乘以一个相关的系数是不会产生任何不同的效果的。根据上面这个公式，以及一些试验结果，我觉得我们至少可以对Fontlink中的缩放因子做出如下一些推断：
>
> 1.  为了能使使用GDI技术输出文本的程序比如TotalCommander能够通过Fontlink使用多个字体，我们必须在Fontlink中给出带有缩放因子的项目
> 2.  合适的缩放因子的数值可能和具体的显示设备有关。也就是说不同的显示设备对于同一个字体可能需要不一样的缩放因子
> 3.  连接字体的显示大小未必和主字体相同。我们可能需要增加或者减小连接字体的大小。为了这个目的，我们可以保持其中一个缩放因子使用缺省数值，而只是相应的改变另外一个因子。具体保持哪个或者修改哪个不影响结果
> 4.  把缩放因子的缺省数值乘以一个相同的数值后并不会导致文本输出后的结果

#### 信息[^2]
> 现在我们需要自己建立一个这样的键，新建多重字符串键"Source Code Pro"（这个是你之前设置的字体名称，键类型为 Multi-String），然后照下图输入：
>
> ![img](https://images0.cnblogs.com/blog/618672/201505/010850593022854.png)
>
> 这里的 SIMYOU.TTF 就是幼圆字体的文件名，其后跟的数字是用来调整中文字体大小使其能和英文字体相匹配（默认是 128,96，这里中文字体 : 英文字体为 1.6 : 1，所以设置为 128×1.2, 96×1.2，即 154, 115）。当一个汉字的宽度等于两个小写字母，即两者匹配。 ![img](https://images0.cnblogs.com/blog/618672/201505/010851008494581.png)
>
> 第二行重复的 SIMYOU.TTF 是为了使 GDI+ 能够识别该字体，第一行则是 GDI 调用。
> 设置完重启系统后就OK了。

---

# 四、Segoe UI 可变字体 [^3]
- Windows 11 新增了 Segoe UI 可变字体，该字体被大部分 UWP 程序使用（如开始菜单、任务栏、新设置面板、应用商店），字体文件名为 `SegUIVar.ttf`。在用户目录 `AppData\Local\Microsoft\Windows\Fonts` 中也有一份副本。
- Win10 IoT LTSC 中未找到该字体，不过微软官方放出了Segoe UI 可变字体的下载链接：
  - The Windows type system helps you create structure and hierarchy in your content in order to maximize legibility and readability in your UI (for more details, see [Segoe UI font family](https://learn.microsoft.com/en-us/typography/font-list/segoe-ui)).
  - The following fonts are recommended:
    - [Segoe UI Variable](https://aka.ms/SegoeUIVariable) (see [Typography in Windows](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography))
    - [Segoe Fluent Icons](https://aka.ms/SegoeFluentIcons) (see [Segoe Fluent Icons font](https://learn.microsoft.com/en-us/windows/apps/design/style/segoe-fluent-icons-font))
    - [Segoe MDL2](https://aka.ms/segoemdl2) (see [Segoe MDL2 Assets icons](https://learn.microsoft.com/en-us/windows/apps/design/style/segoe-ui-symbol-font))

---

# 备注
- Windows 同时保留了传统的 GDI 和现代的 DirectWrite 渲染系统。不同界面部分可能使用不同的渲染方式，导致字体显示效果不一致。此问题源于对旧系统的兼容需求，单纯修改字体配置,无法彻底解决。

[^1]: https://shajisoft.com/shajisoft_wp/cn/%e5%ae%8c%e7%be%8e%e8%a7%a3%e5%86%b3%e4%b8%ad%e6%96%87%e5%9c%a8%e8%8b%b1%e6%96%87windows%e4%b8%8a%e6%98%be%e7%a4%ba%e9%ab%98%e7%9f%ae%e4%b8%8d%e4%b8%80%e7%9a%84%e9%97%ae%e9%a2%98/
[^2]: https://www.cnblogs.com/RhinoC/p/4470338.html

[^3]: https://www.bilibili.com/opus/861311156731510789