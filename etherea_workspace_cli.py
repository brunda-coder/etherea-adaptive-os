from __future__ import annotations
from corund.workspace_manager import WorkspaceManager
from corund.workspace_ai.workspace_controller import WorkspaceController


def main():
    wm = WorkspaceManager()
    ctl = WorkspaceController(wm)

    print("✅ Etherea Workspace CLI Ready")
    print("Try: coding mode | save session | continue last session | focus 25 minutes")
    print("Type 'exit' to quit\n")

    while True:
        try:
            cmd = input("Etherea> ").strip()
        except EOFError:
            print("\n✅ EOF received — exiting CLI cleanly.")
            break
        if cmd.lower() in ("exit", "quit"):
            break
        out = ctl.handle_command(cmd)
        print(out)
        print()

if __name__ == "__main__":
    main()
