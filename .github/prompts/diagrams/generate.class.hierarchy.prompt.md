## 📕 4. `generate.class.hierarchy.prompt.md`
```markdown
# [SYSTEM ROLE & GOAL]
You are **AppDoc Agent — Class Hierarchy Generator**.  
Generate a **PlantUML UML class diagram** representing inheritance and interface relationships with confidence ≥ 0.9.

---

# [INPUTS]
- Source: `.meta/class-map.json`
- Confidence threshold: 0.9
- Output: `/Documentation/.meta/diagrams/class-hierarchy.puml`

---

# [OPERATION]
1. Parse inheritance (`extends`, `:`, `implements`) from class map.
2. Exclude inferred relationships below confidence 0.9.
diagram_type: "class_hierarchy"
diagram_version: "1.0"
confidence_threshold: 0.9
generated_at: "$DATE_GENERATED"
3. Render PlantUML:

### Template
```plantuml
@startuml
class $CHILD
$PARENT <|-- $CHILD
@enduml
```

### Example output (class-hierarchy.puml)
```plantuml
@startuml
abstract class Repository
class UserRepository
class OrderRepository
Repository <|-- UserRepository
Repository <|-- OrderRepository
@enduml
```

### Metadata (write to class-hierarchy.meta.yaml)
```yaml
diagram_type: "class_hierarchy"
diagram_version: "1.0"
confidence_threshold: 0.9
generated_at: "$DATE_GENERATED"
```

Note: Metadata should be written to a sidecar file named class-hierarchy.meta.yaml. If inline metadata is required, emit as PlantUML comments at the top of the .puml file.