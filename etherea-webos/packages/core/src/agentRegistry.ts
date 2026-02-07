export type AgentAction = "create_ppt" | "summarize_pdf" | "generate_notes";

export interface AgentResult {
  action: AgentAction;
  task: string;
  plan: string[];
  steps: { id: number; status: "pending" | "running" | "done" }[];
  output: Record<string, unknown>;
  offlineDemo: boolean;
}

const deterministicTemplates: Record<AgentAction, (task: string) => Record<string, unknown>> = {
  create_ppt: (task) => ({
    title: `Presentation: ${task}`,
    outline: [
      "Problem framing",
      "Signals and stress/focus telemetry",
      "Prototype walkthrough",
      "Roadmap"
    ],
    speakerNotes: [
      "Open with user problem and emotional ergonomics.",
      "Explain deterministic offline mode for demos.",
      "Show cross-platform release pipeline.",
      "Close with Firebase + desktop/mobile path."
    ]
  }),
  summarize_pdf: (task) => ({
    source: task,
    summary: {
      abstract: "Document parsed and summarized in offline deterministic mode.",
      keyPoints: ["Goal", "Method", "Findings", "Risks", "Next steps"],
      actionItems: ["Validate references", "Draft implementation plan"]
    }
  }),
  generate_notes: (task) => ({
    topic: task,
    sections: [
      { heading: "Concept", bullets: ["Definition", "Context", "Constraints"] },
      { heading: "Implementation", bullets: ["Inputs", "Flow", "Output schema"] },
      { heading: "Follow-up", bullets: ["Testing", "Risks", "Opportunities"] }
    ]
  })
};

export function runAgentAction(action: AgentAction, task: string, offlineDemo = true): AgentResult {
  const plan = ["Intake task", "Generate plan", "Produce structured output"];
  const steps = plan.map((_, i) => ({ id: i + 1, status: "done" as const }));
  return {
    action,
    task,
    plan,
    steps,
    output: deterministicTemplates[action](task),
    offlineDemo
  };
}
