package com.aichat.platform.model;

public enum RunEventType {
    RUN_CREATED("任务创建"),
    RUN_STARTED("任务开始"),
    PYTHON_REQUEST_SENT("已请求 Python Agent Engine"),
    PYTHON_RESPONSE_RECEIVED("收到 Python 响应"),
    RUN_SUCCESS("任务成功"),
    RUN_FAILED("任务失败"),
    RUN_CANCELLED("任务取消"),
    REPORT_INDEXED("报告已索引"),
    ERROR_OCCURRED("发生错误"),
    STATUS_CHANGED("状态变更"),
    WORKFLOW_STARTED("工作流开始执行"),
    AGENT_STARTED("Agent 开始执行"),
    AGENT_FINISHED("Agent 执行完成"),
    AGENT_FAILED("Agent 执行失败"),
    RUNNER_STARTED("Runner 开始执行"),
    RUNNER_FINISHED("Runner 执行完成"),
    TEST_STARTED("测试开始"),
    TEST_FINISHED("测试完成"),
    REPAIR_STARTED("修复分析开始"),
    REPAIR_FINISHED("修复分析完成"),
    QUALITY_EVALUATED("质量评分完成"),
    REPORT_GENERATED("报告生成完成"),
    WORKFLOW_FINISHED("工作流执行完成"),
    HUMAN_APPROVAL_REQUIRED("等待人工确认"),
    HUMAN_APPROVED("人工确认已批准"),
    HUMAN_REJECTED("人工确认已拒绝");

    private final String description;

    RunEventType(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }
}
