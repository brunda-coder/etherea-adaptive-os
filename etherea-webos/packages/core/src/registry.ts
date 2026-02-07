export type AgentAction = 'create_ppt' | 'summarize_pdf' | 'generate_notes';

export interface AgentResult {
  task: AgentAction;
  plan: string[];
  steps: string[];
  output: Record<string, unknown>;
}

const templates: Record<AgentAction, AgentResult> = {
  create_ppt: {
    task: 'create_ppt',
    plan: ['Collect topic', 'Draft sections', 'Add speaker notes'],
    steps: ['Title slide', 'Three core slides', 'Q&A'],
    output: {
      outline: ['Problem', 'Solution', 'Roadmap'],
      speakerNotes: ['Hook audience', 'Show metrics', 'Close with CTA']
    }
  },
  summarize_pdf: {
    task: 'summarize_pdf',
    plan: ['Read pages', 'Extract themes', 'Structure summary'],
    steps: ['Context', 'Insights', 'Actions'],
    output: {
      summary: { context: 'Offline template summary', insights: ['Insight A', 'Insight B'], actions: ['Action A'] }
    }
  },
  generate_notes: {
    task: 'generate_notes',
    plan: ['Collect context', 'Expand details', 'Emit notes'],
    steps: ['Scope', 'Evidence', 'Follow-up'],
    output: {
      notes: ['Detailed note 1', 'Detailed note 2', 'Detailed note 3']
    }
  }
};

export function runAgentAction(task: AgentAction): AgentResult {
  return structuredClone(templates[task]);
}
