# 防护等级判定

## T0 — 源码可读

**特征**：
- 无压缩无打包，JS/CSS 直接暴露
- 函数名、变量名有语义（如 `signMessage`, `buildLoginPayload`）
- React DevTools 可直接看到组件树和 props

**判定方法**：Sources 面板 → 随便点一个 JS 文件 → 代码像教科书示例一样清晰

**应对策略**：直接阅读源码还原逻辑，无需任何工具

---

## T1 — Webpack 打包 + 变量名缩短

**特征**：
- 文件名如 `26057-8322daa47a4f566f.js`（chunk hash 命名）
- 模块内变量被压缩为 `a`、`b`、`cX`，但模块边界清晰
- 关键字符串**没有被加密**（如 `"AES.encrypt"`、`"signMessage"`、`"Chain ID"` 可直接搜索）
- webpack 的 `__webpack_require__` 或类似的模块加载器可见

**判定方法**：
```bash
# 搜索关键字符串，看是否能直接定位到逻辑
grep -r "AES.encrypt" ./chunks/
grep -r "signMessage" ./chunks/
grep -r "Chain ID" ./chunks/
```

**应对策略**：
- 搜索关键字符串定位模块
- 追溯变量引用还原数据流
- 不需要 AST 或反混淆工具

---

## T2 — 字符串混淆 + 控制流平坦化

**特征**：
- 字符串被加密/编码（如 `_0x3a4b("0x1f")` 而不是 `"signMessage"`）
- 控制流被 `switch-case` 打乱（控制流平坦化）
- 可能存在虚假分支、死代码

**判定方法**：
- 搜索已知字符串（如 `"signMessage"`）→ 找不到
- JS 代码中出现大量 `_0x` 前缀变量
- 函数体是巨大的 `switch(true)` 结构

**应对策略**：
- 需要去混淆（de4js、synchrony 等工具）
- 动态调试（断点 + 变量 watch）比静态分析更有效

---

## T3 — WASM / VMP 虚拟机保护

**特征**：
- 核心逻辑编译为 WASM，JS 仅做胶水层
- 或实现自定义字节码解释器（虚拟机保护）
- 静态分析几乎不可能

**判定方法**：
- Sources 中大量 `.wasm` 文件
- 核心函数只是一个 `wasm.exports.xxx()` 调用

**应对策略**：
- 纯动态分析（抓包 + 黑盒测试）
- 除非有 WASM 反编译能力，否则接受黑盒分析的结果
