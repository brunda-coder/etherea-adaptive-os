> 🟡 **CONCEPT / DESIGN DOC**
> This file may describe a broader or planned model. For the **current working demo behavior and commands**, see **ETHEREA_CORE.md**.

# Etherea UI — Main Workspace + Optional Enhancements

> **Note:** This diagram is a conceptual layout. The implemented desktop UI in
`core/ui/main_window_v2.py` uses a two-pane layout (avatar + console) with
command palette controls.

```mermaid
flowchart LR
    %% --------------------------
    %% Main Workspace Layout
    %% --------------------------

    %% Left Panel
    subgraph LeftPanel["Left Panel"]
        A1["Avatar Panel"]
        A2["Status: Calm / Focus / Distracted"]
    end

    %% Main Panel
    subgraph MainPanel["Main Panel"]
        B1["Chat / Interaction History"]
        B2["Avatar Response Area"]
        B3["Suggestions / Tips"]
    end

    %% Bottom Panel
    subgraph BottomPanel["Bottom Panel"]
        C1["User Input Box"]
        C2["Send Button"]
        C3["Quick Actions (Focus Mode)"]
    end

    %% Connections between main panels
    LeftPanel --> MainPanel
    MainPanel --> BottomPanel

    %% --------------------------
    %% Optional UI Cards Block
    %% --------------------------

    subgraph UICards["Optional UI Cards"]
        Card1["Focus Mode Card"]
        Card2["Relax Mode Card"]
        Card3["Notifications Summary"]
        Card4["Recent Tasks"]
    end

    %% Connect cards below BottomPanel
    BottomPanel --> UICards
    Card1 --> Card2 --> Card3 --> Card4
