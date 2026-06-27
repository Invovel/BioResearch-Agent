"""Skill registry with instantiable facades."""

from __future__ import annotations

from agent_langgraph_prototype.llm.routing import describe_llm_routing
from agent_langgraph_prototype.skills.annotation_prep_skill import AnnotationPrepSkill
from agent_langgraph_prototype.skills.archive_skill import ArchiveSkill
from agent_langgraph_prototype.skills.auth_identity_skill import AuthIdentitySkill
from agent_langgraph_prototype.skills.chat_planning_skill import ChatPlanningSkill
from agent_langgraph_prototype.skills.discovery_skill import ToolDiscoverySkill
from agent_langgraph_prototype.skills.execution_skill import ExecutionSkill
from agent_langgraph_prototype.skills.immune_tme_skill import ImmuneTMESkill
from agent_langgraph_prototype.skills.internal_flow_harness_skill import InternalFlowHarnessSkill
from agent_langgraph_prototype.skills.mil_multimodal_skill import MILMultimodalSkill
from agent_langgraph_prototype.skills.nucleus_pathomics_skill import NucleusPathomicsSkill
from agent_langgraph_prototype.skills.paper_evidence_skill import PaperEvidenceSkill
from agent_langgraph_prototype.skills.project_workspace_skill import ProjectWorkspaceSkill
from agent_langgraph_prototype.skills.qc_preprocess_skill import QCPreprocessSkill
from agent_langgraph_prototype.skills.scheduler_ops_skill import SchedulerOpsSkill
from agent_langgraph_prototype.skills.segmentation_detection_skill import SegmentationDetectionSkill
from agent_langgraph_prototype.skills.session_conversation_skill import SessionConversationSkill
from agent_langgraph_prototype.skills.troubleshooting_readback_skill import TroubleshootingReadbackSkill
from agent_langgraph_prototype.skills.upload_recovery_skill import UploadRecoverySkill


SKILLS = {
    "ChatPlanningSkill": {
        "function": "问答、意图识别与检索规划",
        "kind": "chat_engine_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "core.engine.ask",
            "core.engine.prepare_context",
            "retrieval.intent_classifier.classify_intent_with_confidence",
            "retrieval.hybrid_retriever.search_tools",
            "retrieval.hybrid_retriever.search_examples",
        ],
    },
    "ToolDiscoverySkill": {
        "function": "工具发现与只读规划",
        "kind": "read_only",
        "provenance": "clean_room_stub",
        "tools": [
            "tool_detail",
            "tool_io_spec",
            "tool_compatibility",
            "cpu_tools",
            "flow_plan_debug",
        ],
    },
    "QCPreprocessSkill": {
        "function": "质控与前处理",
        "kind": "tool_bundle",
        "provenance": "catalog_mapping",
        "tools": [
            "29-Summarize-slide-info",
            "30-Get-slide-previews",
            "40-GrandQC",
            "28-Stain-Normalization",
            "52-Global-Macenko",
            "57-estimate-image-spacing",
            "1-foreground-segmentation",
            "48-foreground-segmentation-beta",
        ],
    },
    "AnnotationPrepSkill": {
        "function": "标注准备与格式处理",
        "kind": "tool_bundle",
        "provenance": "catalog_mapping",
        "tools": [
            "23-SAM-point-annotation",
            "24-SAM2.1-point-annotation",
            "25-BiomedParse",
            "31-Summarize-asap-xml-info",
            "32-Transfer-asap-xml-to-tif",
            "33-Generate-segmentation-patches",
            "34-Generate-classification-patches",
            "38-Text-Encoding",
            "54-kfb2svs",
            "55-pkl2h5",
            "56-image2tif",
            "58-value-mapping",
            "59-generate-overlays",
        ],
    },
    "SegmentationDetectionSkill": {
        "function": "分割与检测",
        "kind": "tool_bundle",
        "provenance": "catalog_mapping",
        "tools": [
            "2-lung-cancer-segmentation",
            "3-tissue-segmentation",
            "11-CD34-vessel-segmentation",
            "12-PAS-kidney-glomeruli-segmentation",
            "13-intrahepatic-cholangiocarcinoma-tissue-segmentation",
            "16-liver-tissue-segmentation",
            "17-lung-tertiary-lymphoid-structures-segmentation",
            "18-PAS-kidney-glomeruli-multi-class-segmentation",
            "26-Kidney-Masson-4-class-segmentation",
            "35-Train-segmentation-baseline",
            "36-Infer-segmentation-baseline",
            "60-tissue-segmentation-trial",
            "64-TUZI",
            "68-Train-segmentation-pipeline-from-slides-xml",
            "69-Train-segmentation-pipeline-from-slides-mask",
            "70-Infer-segmentation-pipeline",
            "5-pancreas-tumor-detection",
            "6-breast-tumor-detection",
            "7-gastric-tumor-detection",
            "8-colon-tumor-detection",
            "9-endometrium-tumor-detection",
            "10-ovarian-tumor-detection",
            "14-intrahepatic-cholangiocarcinoma-cancer-detection",
            "51-ssl-luad-classification",
            "62-pancancer-detection-20",
            "63-pancancer-detection-40",
            "75-Gleason-AGGC",
        ],
    },
    "NucleusPathomicsSkill": {
        "function": "核分割、编码与病理组学",
        "kind": "tool_bundle",
        "provenance": "catalog_mapping",
        "tools": [
            "4-nucleus-segmentation-hovernet-pannuke",
            "50-hovernet-pannuke-mp",
            "53-hover-next-mp",
            "49-slide-embedding-all-methods",
            "76-Pathomics-pipeline-from-slides",
            "77-Pathomics-pipeline-from-slides-nucleus",
        ],
    },
    "ImmuneTMESkill": {
        "function": "免疫、TME、TLS 与虚拟染色",
        "kind": "tool_bundle",
        "provenance": "catalog_mapping",
        "tools": [
            "39-HE-transfer-to-SHG",
            "41-Deepliif",
            "42-CycleGAN-Norm-Xiacong",
            "48-foreground-segmentation-beta",
            "61-hooknet-tls",
            "65-PSPStain",
            "66-HistoPlexer",
            "67-GigaTIME",
            "17-lung-tertiary-lymphoid-structures-segmentation",
        ],
    },
    "MILMultimodalSkill": {
        "function": "MIL 与多模态建模",
        "kind": "tool_bundle",
        "provenance": "catalog_mapping",
        "tools": [
            "15-Cerberus",
            "71-Train-MIL-pipeline-from-slides",
            "72-Train-MIL-pipeline-from-h5",
            "73-Infer-MIL-pipeline-for-slides",
            "74-Infer-MIL-pipeline-for-h5",
            "78-Train-MIL-multi-modal-pipeline-from-slides",
            "79-Train-MIL-multi-modal-pipeline-from-h5",
            "80-Infer-MIL-multi-modal-pipeline-for-slides",
            "81-Infer-MIL-multi-modal-pipeline-for-h5",
        ],
    },
    "PaperEvidenceSkill": {
        "function": "文献证据与论文工具链",
        "kind": "service_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "papers_search",
            "paper_upload",
            "paper_library",
            "paper_favorites",
            "paper_analyze",
            "paper_toolchain_plan",
            "paper_toolchain_evidence",
            "paper_toolchain_export",
            "paper_toolchain_reproducibility",
        ],
    },
    "ProjectWorkspaceSkill": {
        "function": "项目、资料、材料与资产工作区",
        "kind": "workspace_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "project_create",
            "project_list",
            "project_update",
            "project_delete",
            "project_pin",
            "project_archive",
            "project_scan",
            "project_materials",
            "project_sessions_bind",
            "project_sessions_unbind",
            "project_paper_folders_bind",
            "project_paper_folders_unbind",
            "project_session_map",
            "asset_upload",
            "asset_download",
        ],
    },
    "UploadRecoverySkill": {
        "function": "上传、分块上传、恢复与文件预览",
        "kind": "io_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "upload_file",
            "upload_chunk_init",
            "upload_chunk_save",
            "upload_chunk_complete",
            "upload_recover",
            "uploaded_file_download",
            "uploaded_file_preview",
        ],
    },
    "TroubleshootingReadbackSkill": {
        "function": "结果回读与故障排查",
        "kind": "readback_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "result_manifest_inspect",
            "result_file_preview",
            "result_file_download",
            "tool_result_review",
            "open_reasoning_diagnostics",
        ],
    },
    "ExecutionSkill": {
        "function": "执行控制与提交",
        "kind": "privileged_execution",
        "provenance": "clean_room_stub",
        "tools": [
            "tool_execute",
            "flow_prepare",
            "approval_intent",
            "execution_preflight",
            "flow_execute_real",
            "scheduler_submit",
            "scheduler_get",
            "scheduler_cancel",
            "scheduler_events",
        ],
    },
    "ArchiveSkill": {
        "function": "会话归档与记忆读取",
        "kind": "memory_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "archive_session",
            "get_session_record",
        ],
    },
    "SessionConversationSkill": {
        "function": "会话与对话管理",
        "kind": "session_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "session_bootstrap",
            "session_new",
            "session_history",
            "session_reset",
            "session_archive",
            "session_archive_user_index",
            "conversation_list",
            "conversation_get",
            "conversation_patch",
            "conversation_add_message",
        ],
    },
    "SchedulerOpsSkill": {
        "function": "调度、作业事件与本地 worker 控制",
        "kind": "ops_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "scheduler_submit",
            "scheduler_get",
            "scheduler_cancel",
            "scheduler_events",
            "scheduler_local_run_next",
            "ops_cluster_status",
            "ops_jobs_list",
            "ops_job_get",
            "ops_job_events",
            "ops_queue_metrics",
            "ops_quota_summary",
            "ops_metrics_overview",
        ],
    },
    "InternalFlowHarnessSkill": {
        "function": "内部 flow harness、fake runs、manifest 检查与 contract 探针",
        "kind": "harness_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "internal_flow_health",
            "internal_flow_prepare",
            "internal_flow_preflight",
            "internal_flow_jobs",
            "internal_flow_fake_runs",
            "internal_flow_manifest_inspection",
            "internal_flow_result_manifest_inspection",
            "internal_flow_executor_state",
            "internal_flow_contract_version",
            "internal_flow_smoke_status",
        ],
    },
    "AuthIdentitySkill": {
        "function": "认证、用户身份与 MFA",
        "kind": "identity_bundle",
        "provenance": "clean_room_stub",
        "tools": [
            "auth_register",
            "auth_login",
            "auth_login_phone",
            "auth_refresh",
            "auth_logout",
            "auth_me_get",
            "auth_me_update",
            "auth_mfa_enroll_start",
            "auth_mfa_enroll_confirm",
            "auth_mfa_verify",
            "auth_recovery_start",
            "auth_recovery_confirm",
            "auth_verification_send",
        ],
    },
}


def build_skill_instances() -> dict:
    return {
        "ChatPlanningSkill": ChatPlanningSkill(),
        "ToolDiscoverySkill": ToolDiscoverySkill(),
        "QCPreprocessSkill": QCPreprocessSkill(),
        "AnnotationPrepSkill": AnnotationPrepSkill(),
        "SegmentationDetectionSkill": SegmentationDetectionSkill(),
        "NucleusPathomicsSkill": NucleusPathomicsSkill(),
        "ImmuneTMESkill": ImmuneTMESkill(),
        "MILMultimodalSkill": MILMultimodalSkill(),
        "PaperEvidenceSkill": PaperEvidenceSkill(),
        "ProjectWorkspaceSkill": ProjectWorkspaceSkill(),
        "UploadRecoverySkill": UploadRecoverySkill(),
        "TroubleshootingReadbackSkill": TroubleshootingReadbackSkill(),
        "ExecutionSkill": ExecutionSkill(),
        "ArchiveSkill": ArchiveSkill(),
        "SessionConversationSkill": SessionConversationSkill(),
        "SchedulerOpsSkill": SchedulerOpsSkill(),
        "InternalFlowHarnessSkill": InternalFlowHarnessSkill(),
        "AuthIdentitySkill": AuthIdentitySkill(),
    }


def build_llm_skill_registry() -> dict:
    return {
        "general_planner_llm": describe_llm_routing("general_planner_llm"),
        "paper_reasoning_llm": describe_llm_routing("paper_reasoning_llm"),
        "execution_control_llm": describe_llm_routing("execution_control_llm"),
        "workspace_memory_llm": describe_llm_routing("workspace_memory_llm"),
        "platform_ops_llm": describe_llm_routing("platform_ops_llm"),
    }

