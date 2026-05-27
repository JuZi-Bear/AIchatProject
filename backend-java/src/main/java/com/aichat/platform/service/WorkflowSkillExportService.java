package com.aichat.platform.service;

import com.aichat.platform.repository.WorkflowTemplateRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class WorkflowSkillExportService {

    private final WorkflowTemplateRepository workflowTemplateRepository;
    private final ObjectMapper objectMapper;
    private final Path exportRoot;

    public WorkflowSkillExportService(
            WorkflowTemplateRepository workflowTemplateRepository,
            ObjectMapper objectMapper,
            @Value("${platform.skill-export.root:generated-skills}") String exportRoot
    ) {
        this.workflowTemplateRepository = workflowTemplateRepository;
        this.objectMapper = objectMapper;
        this.exportRoot = Path.of(exportRoot);
    }

    public Optional<Map<String, Object>> exportSkill(String templateKey) {
        return workflowTemplateRepository.findByTemplateKey(templateKey).map(entity -> {
            Map<String, Object> template = parseTemplate(entity.getTemplateJson());
            String resolvedTemplateKey = firstNonBlank(
                    asString(template.get("workflowTemplateKey")),
                    asString(template.get("templateKey")),
                    entity.getTemplateKey()
            );
            String templateName = firstNonBlank(asString(template.get("name")), entity.getName(), resolvedTemplateKey);
            String description = firstNonBlank(
                    asString(template.get("description")),
                    entity.getDescription(),
                    "Run the " + templateName + " workflow through the AIchat Java Gateway."
            );
            String skillName = skillName(templateName, resolvedTemplateKey);
            Path root = exportRoot.normalize();
            Path skillDir = root.resolve(skillName).normalize();

            if (!skillDir.startsWith(root)) {
                throw new IllegalArgumentException("invalid skill export path: " + skillName);
            }

            try {
                Files.createDirectories(skillDir.resolve("references"));
                Files.createDirectories(skillDir.resolve("scripts"));
                writeText(skillDir.resolve("SKILL.md"), skillMarkdown(skillName, templateName, description, template));
                writeText(
                        skillDir.resolve("references").resolve("workflow-template.json"),
                        objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(template)
                );
                writeText(skillDir.resolve("scripts").resolve("run_workflow.py"), runWorkflowScript(resolvedTemplateKey));
            } catch (IOException error) {
                throw new IllegalStateException("failed to export workflow skill: " + error.getMessage(), error);
            }

            Map<String, Object> response = new LinkedHashMap<>();
            response.put("templateKey", resolvedTemplateKey);
            response.put("skillName", skillName);
            response.put("skillPath", normalizePath(skillDir));
            response.put("files", List.of(
                    "SKILL.md",
                    "references/workflow-template.json",
                    "scripts/run_workflow.py"
            ));
            response.put("installed", false);
            response.put("warnings", List.of("Skill 已导出但未自动安装到 Codex。"));

            return response;
        });
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> parseTemplate(String rawJson) {
        if (rawJson == null || rawJson.isBlank()) {
            return Map.of();
        }

        try {
            Object parsed = objectMapper.readValue(rawJson, Object.class);
            if (parsed instanceof Map<?, ?> parsedMap) {
                return new LinkedHashMap<>((Map<String, Object>) parsedMap);
            }
        } catch (Exception ignored) {
            // Broken template JSON should still export a minimal skill shell.
        }

        return new LinkedHashMap<>();
    }

    @SuppressWarnings("unchecked")
    private String skillMarkdown(String skillName, String templateName, String description, Map<String, Object> template) {
        List<Map<String, Object>> nodes = template.get("nodes") instanceof List<?> list
                ? list.stream()
                        .filter(item -> item instanceof Map<?, ?>)
                        .map(item -> (Map<String, Object>) item)
                        .toList()
                : List.of();
        String nodeLines = nodes.isEmpty()
                ? "- No nodes were stored in the exported template."
                : nodes.stream()
                        .map(node -> "- " + firstNonBlank(asString(node.get("name")), asString(node.get("agentKey")), asString(node.get("nodeId"))))
                        .reduce((left, right) -> left + "\n" + right)
                        .orElse("");

        return """
                ---
                name: %s
                description: '%s'
                ---

                # %s

                %s

                This skill runs an exported AIchat Workflow Editor template through the platform API. It does not install itself, bypass CodeAgent safety controls, read API keys, or call Python Agent internals directly.

                ## Workflow Nodes

                %s

                ## How To Run

                Use `scripts/run_workflow.py` when the local AIchat v2 platform is running.

                ```powershell
                python scripts/run_workflow.py --requirement "Describe the task to run"
                ```

                Optional arguments:

                - `--api-base`: Java Gateway base URL. Defaults to `http://127.0.0.1:8088/api`.
                - `--requirement`: task requirement sent as `input_data.requirement`.

                ## References

                - `references/workflow-template.json` contains the exported template.

                ## Safety Boundary

                The script only calls the Java Gateway `execute-langgraph` endpoint. CodeAgent file operations, model calls, workflow validation, events, SSE, and Replay remain controlled by the platform.
                """.formatted(
                skillName,
                yamlSingle("Use this skill when the user wants to run the exported \"" + templateName + "\" workflow template through the AIchat Java Gateway and Dynamic LangGraph runtime."),
                escapeMarkdown(templateName),
                escapeMarkdown(description),
                nodeLines
        );
    }

    private String runWorkflowScript(String templateKey) {
        return """
                import argparse
                import json
                import sys
                import urllib.error
                import urllib.parse
                import urllib.request


                def main():
                    parser = argparse.ArgumentParser(description="Run an exported AIchat workflow template.")
                    parser.add_argument("--api-base", default="http://127.0.0.1:8088/api", help="Java Gateway API base URL")
                    parser.add_argument("--requirement", default="", help="Task requirement for the workflow run")
                    args = parser.parse_args()

                    api_base = args.api_base.rstrip("/")
                    template_key = %s
                    endpoint = f"{api_base}/platform/workflows/templates/{urllib.parse.quote(template_key, safe='')}/execute-langgraph"
                    payload = {
                        "input_data": {
                            "requirement": args.requirement or f"Run exported workflow template: {template_key}",
                            "runtime_mode": "dynamic_langgraph",
                            "skill_export": True,
                        }
                    }
                    request = urllib.request.Request(
                        endpoint,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )

                    try:
                        with urllib.request.urlopen(request, timeout=120) as response:
                            body = response.read().decode("utf-8")
                    except urllib.error.HTTPError as error:
                        body = error.read().decode("utf-8", errors="replace")
                        print(body, file=sys.stderr)
                        raise SystemExit(error.code)
                    except urllib.error.URLError as error:
                        print(f"Failed to connect to AIchat Java Gateway: {error}", file=sys.stderr)
                        raise SystemExit(1)

                    print(json.dumps(json.loads(body), ensure_ascii=False, indent=2))


                if __name__ == "__main__":
                    main()
                """.formatted(quotePythonString(templateKey));
    }

    private void writeText(Path target, String content) throws IOException {
        Files.writeString(
                target,
                content,
                StandardCharsets.UTF_8,
                StandardOpenOption.CREATE,
                StandardOpenOption.TRUNCATE_EXISTING
        );
    }

    private String skillName(String templateName, String templateKey) {
        String base = firstNonBlank(templateName, "workflow-" + templateKey);
        String normalized = base
                .toLowerCase()
                .replaceAll("[^a-z0-9]+", "-")
                .replaceAll("^-+", "")
                .replaceAll("-+$", "");

        if (normalized.isBlank()) {
            normalized = "workflow-" + templateKey.toLowerCase().replaceAll("[^a-z0-9]+", "-");
        }

        if (normalized.length() > 64) {
            normalized = normalized.substring(0, 64).replaceAll("-+$", "");
        }

        return normalized.isBlank() ? "workflow-template" : normalized;
    }

    private String normalizePath(Path path) {
        return path.toString().replace('\\', '/');
    }

    private String quotePythonString(String value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (Exception error) {
            return "\"\"";
        }
    }

    private String escapeMarkdown(String value) {
        return value == null ? "" : value.replace("\r", " ").replace("\n", " ").trim();
    }

    private String yamlSingle(String value) {
        return escapeMarkdown(value).replace("'", "''");
    }

    private String asString(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }

        return "";
    }
}
