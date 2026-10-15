# Mermaid diagram patterns

Use Mermaid in fenced blocks (```mermaid). GitHub, GitLab and most Markdown viewers render it. Keep diagrams small (under ~15 nodes), label edges with verbs, and quote labels that contain spaces or punctuation. Name real components from the code, not generic boxes.

## Architecture (flowchart)

```mermaid
flowchart LR
  subgraph Client
    A["Android app (Compose)"]
    W["Web app (React)"]
  end
  subgraph Backend
    API["Laravel API"]
    CF["Cloud Functions"]
  end
  subgraph Data
    DB[("MySQL")]
    FS[("Firestore")]
  end
  A -->|HTTPS| API
  W -->|HTTPS| API
  A -->|SDK| FS
  API --> DB
  FS -->|trigger| CF
```

## Request or user flow (sequence)

```mermaid
sequenceDiagram
  actor U as User
  participant UI as ChatScreen
  participant VM as ChatViewModel
  participant R as ChatRepository
  participant FS as Firestore
  U->>UI: tap Send
  UI->>VM: sendMessage(text)
  VM->>R: save(message)
  R->>FS: set(messages/{id})
  FS-->>R: ack
  R-->>VM: Result
  VM-->>UI: update state
```

Use `alt`/`opt` blocks for error paths when they matter:

```
alt offline
  R->>R: queue locally
else online
  R->>FS: set()
end
```

## Data model (ER)

```mermaid
erDiagram
  USER ||--o{ ORDER : places
  ORDER ||--|{ ORDER_ITEM : contains
  PRODUCT ||--o{ ORDER_ITEM : "appears in"
  USER { bigint id PK
         string email }
```

## Status lifecycle (state)

```mermaid
stateDiagram-v2
  [*] --> Pending
  Pending --> Paid: payment confirmed
  Paid --> Shipped
  Pending --> Cancelled: timeout
  Shipped --> [*]
```

## Deployment

```mermaid
flowchart TD
  Dev["Developer push"] --> CI["CI build and test"]
  CI --> Img["Docker image"]
  Img --> CR["Cloud Run"]
  CR --> Users
```

## Folder or module dependencies

Use a flowchart with `-->` meaning "depends on". Show only layers that matter and flag any violation of the intended direction.

## Pitfalls
- Avoid parentheses, colons or slashes in unquoted labels. Quote them: `A["POST /api/orders"]`.
- Do not use more than one diagram per idea. If two diagrams overlap, keep the clearer one.
- If you cannot confirm a relationship from code, leave it out rather than guess.
