---
name: terraform-refactor-module
description: Transform monolithic Terraform configurations into reusable, maintainable modules following HashiCorp's module design principles and community best practices.
metadata:
  copyright: Copyright IBM Corp. 2026
  version: "0.0.1"
  jenreh.registry/id: "jenreh:jenreh-terraform"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.3.0"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "43748cbfd1e10079f1c194be5f68b1de59dc359b"
  jenreh.registry/source-license: "MIT"
  jenreh.registry/source-path: "plugins/jenreh-terraform/skills/terraform-refactor-module"
  jenreh.registry/source-digest: "0423246bd1f1ebd6274544da6d3e8fe7520e645c38fec788763fd1c1e9fd2998"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
  jenreh.registry/supported-channels: "beta,stable"
---

# Skill: Refactor Module

## Overview
This skill guides AI agents in transforming monolithic Terraform configurations into reusable, maintainable modules following HashiCorp's module design principles and community best practices.

## Capability Statement
The agent will analyze existing Terraform code and systematically refactor it into well-structured modules with:
- Clear interface contracts (variables and outputs)
- Proper encapsulation and abstraction
- Versioning and documentation
- Testing frameworks
- Migration path for existing state

## Prerequisites
- Existing Terraform configuration to refactor
- Understanding of resource dependencies
- Access to current state file (for migration planning)
- Knowledge of module registry patterns

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_directory` | string | Yes | Path to existing Terraform configuration |
| `module_name` | string | Yes | Name for the new module |
| `abstraction_level` | string | No | "simple", "intermediate", "advanced" (default: intermediate) |
| `preserve_state` | boolean | Yes | Whether to maintain state compatibility |
| `target_registry` | string | No | Target module registry (local, private, public) |

## Execution Steps

### 1. Analysis Phase
```markdown
**Identify Refactoring Candidates**
- Group resources by logical function
- Identify repeated patterns
- Map resource dependencies
- Detect configuration coupling
- Analyze variable usage patterns

**Complexity Assessment**
- Count resource relationships
- Measure variable propagation depth
- Identify cross-resource references
- Evaluate state migration complexity
```

### 2. Module Design

#### Interface Design
```hcl
# Define clear input contract
variable "network_config" {
  description = "Network configuration parameters"
  type = object({
    cidr_block         = string
    availability_zones = list(string)
    enable_nat         = bool
  })

  validation {
    condition     = can(cidrhost(var.network_config.cidr_block, 0))
    error_message = "CIDR block must be valid IPv4 CIDR."
  }
}

# Define output contract
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = { for k, v in aws_subnet.private : k => v.id }
}
```

#### Encapsulation Strategy
```markdown
**What to Include in Module:**
- Tightly coupled resources (VPC + subnets)
- Resources with shared lifecycle
- Configuration with clear boundaries

**What to Keep Separate:**
- Cross-cutting concerns (monitoring, tagging)
- Resources with different lifecycles
- Provider-specific configurations
```

### 3. Code Transformation

**→ Read [`references/worked-example.md`](references/worked-example.md) for a full
before/after (monolithic AWS VPC → `modules/vpc`, with the state migration).** The
transformation rules:

- Replace copy-pasted resources (`public_1`, `public_2`, …) with one resource using
  `for_each` over stable keys (availability zones, names), never `count` over a list
  whose order can change.
- Every variable has `description` and `type`; add `validation` blocks for values
  that can be checked (`can(cidrhost(...))`); give optional inputs a `default`.
- Make optional resources toggles (`count = var.create_x ? 1 : 0` or a conditional
  `for_each`) and read them with `try(resource.x[0].id, null)` in outputs.
- Merge caller tags: `tags = merge(var.tags, { Name = "${var.name}-..." })`.
- Output maps keyed like the `for_each` (`{ for k, v in aws_subnet.public : k => v.id }`)
  so consumers do not depend on ordering.
- Keep the module's `main.tf`, `variables.tf`, and `outputs.tf` separate; the root
  configuration only calls the module.

### 4. State Migration

Map every old address to its new one so nothing is destroyed and recreated. With
Terraform 1.1+, use `moved` blocks (one per resource; `for_each` instances get the
key, toggled resources the `[0]` index):

```hcl
moved {
  from = aws_subnet.public_1
  to   = module.vpc.aws_subnet.public["us-east-1a"]
}
```

Before 1.1, use `terraform state mv` with the same addresses (quote addresses that
contain `[` or `"`). The full mapping for the example is in
[`references/worked-example.md`](references/worked-example.md).

### 5. Module Documentation

Every module ships a README with Overview, Features, Usage, Requirements, Inputs,
Outputs, and Examples. Template:
[`references/module-readme-template.md`](references/module-readme-template.md).

### 6. Testing

Use the `terraform-test` skill to write `.tftest.hcl` tests. Put them in the module's
`tests/` directory and keep plan-mode unit tests apart from apply-mode integration
tests (which create real resources):

```
my-module/
├── main.tf
├── variables.tf
├── outputs.tf
└── tests/
    ├── unit_test.tftest.hcl         # plan mode
    └── integration_test.tftest.hcl  # apply mode, creates real resources
```

## Refactoring Patterns

### Pattern 1: Resource Grouping
Extract related resources into cohesive modules:
- Networking (VPC, Subnets, Route Tables)
- Compute (ASG, Launch Templates, Load Balancers)
- Data (RDS, ElastiCache, S3)

### Pattern 2: Configuration Layering
```hcl
# Base module with defaults
module "vpc_base" {
  source = "./modules/vpc-base"
  # Minimal required inputs
}

# Environment-specific wrapper
module "vpc_prod" {
  source = "./modules/vpc-production"
  # Inherits from base, adds prod-specific config
}
```

### Pattern 3: Composition
```hcl
# Small, focused modules
module "vpc" {
  source = "./modules/vpc"
}

module "security_groups" {
  source = "./modules/security-groups"
  vpc_id = module.vpc.vpc_id
}

module "application" {
  source     = "./modules/application"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  sg_ids     = module.security_groups.app_sg_ids
}
```

## Common Pitfalls

### 1. Over-Abstraction
```hcl
# ❌ Don't create overly generic modules
variable "resources" {
  type = map(map(any))  # Too flexible, hard to validate
}

# ✅ Do use specific, typed interfaces
variable "database_config" {
  type = object({
    engine         = string
    instance_class = string
  })
}
```

### 2. Tight Coupling
```hcl
# ❌ Don't couple modules through direct references
# module A
output "instance_id" { value = aws_instance.app.id }

# module B (in same config)
resource "aws_eip" "app" {
  instance = module.a.instance_id  # Tight coupling
}

# ✅ Do pass dependencies through root module
module "compute" {
  source = "./modules/compute"
}

resource "aws_eip" "app" {
  instance = module.compute.instance_id
}
```

### 3. State Migration Errors
Always test migration in non-production first:
```bash
# Create plan to verify no changes after migration
terraform plan -out=migration.tfplan

# Review carefully
terraform show migration.tfplan

# Apply only if plan shows no changes
terraform apply migration.tfplan
```

## Version Control Strategy

```hcl
# Use semantic versioning for modules
module "vpc" {
  source  = "git::https://github.com/org/terraform-modules.git//vpc?ref=v1.2.0"
  version = "~> 1.2"
}

# Pin to specific versions in production
# Use version ranges in development
```

## Success Criteria

- [ ] Module has single, well-defined responsibility
- [ ] All variables have descriptions and types
- [ ] Validation rules prevent invalid configurations
- [ ] Outputs provide sufficient information for consumers
- [ ] Documentation includes usage examples
- [ ] Tests verify module behavior
- [ ] State migration completed without resource recreation
- [ ] No plan differences after refactoring

## Related Skills
- `terraform-style-guide`: style conventions for the new module's code.
- `terraform-azure-verified-modules`: module specifications for Azure (AVM).
- `terraform-test`: tests for the refactored module.

## Resources
- [Terraform Module Development](https://developer.hashicorp.com/terraform/language/modules/develop)
- [Module Best Practices](https://developer.hashicorp.com/terraform/cloud-docs/registry/design)

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-07 | Initial skill definition |
