action "Build" {
    uses = "docker://alpine"
    runs = ["scripts/build"]
}

workflow "Preview" {
    on = "pull_request"
    resolves = "Pulumi Preview (Merged Stack)"
}

action "Pulumi Preview (Merged Stack)" {
    needs = ["Build"]
    uses = "docker://pulumi/actions"
    args = ["preview"]
    env = {
        PULUMI_CI = "pr"
    }
    secrets = [
        "PULUMI_ACCESS_TOKEN"
    ]
}

workflow "Update" {
    on = "push"
    resolves = ["Pulumi Deploy (Current Stack)"]
}

action "Pulumi Deploy (Current Stack)" {
    needs = ["Build"]
    uses = "docker://pulumi/actions"
    args = ["up"]
    env = {
        PULUMI_CI = "up"
    }
    secrets = [
        "PULUMI_ACCESS_TOKEN"
    ]
}