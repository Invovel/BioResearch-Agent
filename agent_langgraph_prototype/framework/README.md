# Framework Index

这个目录只定义 `framework`，不定义具体 `skill -> tool` 绑定。

目标是先把编排层单独稳定下来，后续再把 skill 和 tools 挂上来。

## Framework 包含什么

- `graph/`
  定义执行图、节点关系、子图、LangGraph 桥接

- `router/`
  定义 query 到 agent role 的路由策略

- `state/`
  定义运行态 state 模型及序列化边界

- `runtime/`
  定义运行时策略，如默认拒绝执行、审批要求、网络策略、D 盘落盘根目录

## Framework 不包含什么

- 具体工具 ID 列表
- 具体 skill 实现细节
- 具体业务 tool 执行代码

这些属于后续挂载层：

- `skills/`
- `adapters/`

## 当前建议阅读顺序

1. `../docs/framework_first_partition.md`
2. `graph/topology.py`
3. `graph/local_graph.py`
4. `router/role_router.py`
5. `state/state_model.py`
6. `runtime/runtime_policy.py`


