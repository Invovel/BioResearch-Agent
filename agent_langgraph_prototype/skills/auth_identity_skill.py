"""Auth and identity skill placeholder."""

from __future__ import annotations

from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "AuthIdentitySkill"
KIND = "identity_bundle"
TOOLS = [
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
]


class AuthIdentitySkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="auth identity catalog skill",
            outputs={"tools": list(TOOLS), "auth_backend": "placeholder"},
        )

